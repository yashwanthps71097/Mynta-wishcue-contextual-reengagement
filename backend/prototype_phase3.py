import datetime
import json
import urllib.request
import urllib.error
import re

# =========================================================================
# Load environment variables (from .env.example / .env)
# =========================================================================
def load_groq_key():
    paths = [".env", ".env.example"]
    for path in paths:
        try:
            with open(path, "r") as f:
                content = f.read()
                match = re.search(r"GROQ_API_KEY=(gsk_\w+)", content)
                if match:
                    return match.group(1)
        except Exception:
            pass
    return None

GROQ_API_KEY = load_groq_key()
GROQ_MODEL = "llama3-8b-8192"

# =========================================================================
# Task 3.1: Cooldown Controller (Mock Redis Sliding Window)
# =========================================================================
class CooldownController:
    def __init__(self):
        # Maps userId -> list of event timestamps
        self.nudge_history = {}

    def is_cooldown_active(self, user_id):
        """
        Enforces cooldown rules:
        - Max 1 nudge per session (simulated as max 1 per 10 minutes here)
        - Max 3 nudges per week (7 days)
        """
        now = datetime.datetime.now()
        history = self.nudge_history.get(user_id, [])
        
        # Filter history to keep only events in the last 7 days
        seven_days_ago = now - datetime.timedelta(days=7)
        history = [t for t in history if t > seven_days_ago]
        self.nudge_history[user_id] = history
        
        # Rule 1: Max 3 nudges per week
        if len(history) >= 3:
            return True, "Weekly limit reached (max 3 nudges/week)"
            
        # Rule 2: Max 1 nudge per session (10 min sliding window)
        ten_minutes_ago = now - datetime.timedelta(minutes=10)
        recent_nudges = [t for t in history if t > ten_minutes_ago]
        if len(recent_nudges) >= 1:
            return True, "Session cooldown active (max 1 nudge/10 mins)"
            
        return False, "Cooldown clear"

    def record_nudge(self, user_id):
        if user_id not in self.nudge_history:
            self.nudge_history[user_id] = []
        self.nudge_history[user_id].append(datetime.datetime.now())

# =========================================================================
# Task 3.2: Context Classifier (Groq API Connection)
# =========================================================================
class ContextClassifier:
    def __init__(self, api_key):
        self.api_key = api_key

    def classify_intent_match(self, user_search_query, wishlist_product_category, wishlist_product_name):
        """
        Calls Groq API to determine semantic match between user's search query
        and a wishlisted product. Returns a confidence score (0.0 to 1.0).
        """
        if not self.api_key:
            print("[CLASSIFIER WARNING] No Groq API Key found. Falling back to keyword match.")
            # Fallback keyword match
            match = user_search_query.lower() in wishlist_product_category.lower() or wishlist_product_category.lower() in user_search_query.lower()
            return 1.0 if match else 0.0, "Fallback keyword logic"

        url = "https://api.groq.com/openai/v1/chat/completions"
        
        prompt = f"""
        Analyze if a user searching for "{user_search_query}" on a fashion app has an active interest or intent that aligns semantically with a wishlisted item of category "{wishlist_product_category}" and name "{wishlist_product_name}".
        
        Respond ONLY with a valid JSON object matching this schema:
        {{
          "semantic_match": true/false,
          "confidence_score": 0.0 to 1.0,
          "reason": "short explanation"
        }}
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": "You are a precise JSON classifier. Outputs must strictly be JSON only."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.0,
            "response_format": {"type": "json_object"}
        }

        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
        
        try:
            with urllib.request.urlopen(req, timeout=3.0) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                content_text = res_json["choices"][0]["message"]["content"]
                result = json.loads(content_text)
                return float(result.get("confidence_score", 0.0)), result.get("reason", "")
        except Exception as e:
            print(f"[CLASSIFIER ERROR] Groq API call failed: {e}. Falling back to keyword match.")
            match = user_search_query.lower() in wishlist_product_category.lower() or wishlist_product_category.lower() in user_search_query.lower()
            return 1.0 if match else 0.0, f"Error fallback (error: {e})"

# =========================================================================
# Task 3.3: Scoring Algorithm Implementation
# =========================================================================
class ScoringAlgorithm:
    @staticmethod
    def calculate_reconsideration_score(price_drop_pct, days_since_added, semantic_match_score):
        """
        Ranking formula:
        Reconsideration Score = (Price Drop weight) + (Expiration weight) + (Intent match weight)
        """
        # 1. Price drop component (Max 40 points, scaled up to 40% drop)
        price_component = min(price_drop_pct, 40.0)
        
        # 2. Expiration/Temporal component (Max 30 points, linear scale towards 30 days)
        # Closer to 30 days yields higher score, caps at day 30.
        expiration_component = min((days_since_added / 30.0) * 30.0, 30.0)
        
        # 3. Intent component (Max 30 points)
        intent_component = semantic_match_score * 30.0
        
        total_score = price_component + expiration_component + intent_component
        return round(total_score, 2), {
            "price_component": round(price_component, 2),
            "expiration_component": round(expiration_component, 2),
            "intent_component": round(intent_component, 2)
        }

# =========================================================================
# Execution & Testing
# =========================================================================
if __name__ == "__main__":
    print("--- Phase 3 Initialization ---")
    print(f"Loaded Groq API Key: {'***' + GROQ_API_KEY[-6:] if GROQ_API_KEY else 'None'}")
    
    cooldown = CooldownController()
    classifier = ContextClassifier(GROQ_API_KEY)
    
    user_id = "usr_987654"
    wishlisted_product = {
        "name": "Nike Air Zoom Pegasus 40",
        "category": "Running Shoes",
        "days_saved": 26,
        "price_drop_pct": 15.0 # 15% discount
    }
    
    # Test Scenario 1: Search for matching category
    search_query = "sport shoes workout"
    print(f"\nEvaluating match for search: '{search_query}' against wishlisted: '{wishlisted_product['name']}'...")
    
    # 1. Check Cooldown
    is_blocked, cooldown_msg = cooldown.is_cooldown_active(user_id)
    print(f"[COOLDOWN CHECK] {cooldown_msg}")
    
    if not is_blocked:
        # 2. Classify intent via Groq
        print("[GROQ API] Classifying intent match...")
        confidence, reason = classifier.classify_intent_match(
            user_search_query=search_query,
            wishlist_product_category=wishlisted_product["category"],
            wishlist_product_name=wishlisted_product["name"]
        )
        print(f"[GROQ RESULT] Confidence Score: {confidence} | Reason: {reason}")
        
        # 3. Calculate Reconsideration Score
        score, break_down = ScoringAlgorithm.calculate_reconsideration_score(
            price_drop_pct=wishlisted_product["price_drop_pct"],
            days_since_added=wishlisted_product["days_saved"],
            semantic_match_score=confidence
        )
        print(f"[SCORING ENGINE] Reconsideration Score: {score} / 100")
        print(f"    Breakdown: {break_down}")
        
        # Record the nudge dispatch
        cooldown.record_nudge(user_id)
        
    # Test Scenario 2: Try to immediately trigger another nudge (checks Cooldown Controller)
    print("\nAttempting to trigger another nudge immediately...")
    is_blocked, cooldown_msg = cooldown.is_cooldown_active(user_id)
    print(f"[COOLDOWN CHECK] Blocked: {is_blocked} | Message: {cooldown_msg}")
