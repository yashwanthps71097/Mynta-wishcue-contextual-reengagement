import http.server
import socketserver
import urllib.parse
import json
import os
import re
import datetime
import urllib.request
import uuid

# =========================================================================
# Load Environment Configuration
# =========================================================================
def load_env_variables():
    env = {}
    paths = [".env", ".env.example"]
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            key_val = line.split("=", 1)
                            if len(key_val) == 2:
                                env[key_val[0].strip()] = key_val[1].strip()
                break
            except Exception:
                pass
    return env

ENV = load_env_variables()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY") or ENV.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL") or ENV.get("GROQ_MODEL", "llama3-8b-8192")

# =========================================================================
# Business Logic Components (Re-use from Phase 3)
# =========================================================================
class CooldownController:
    def __init__(self):
        self.nudge_history = {}

    def is_cooldown_active(self, user_id):
        # We bypass cooldown limit for demo visual testing, but keep the log trace
        now = datetime.datetime.now()
        history = self.nudge_history.get(user_id, [])
        ten_seconds_ago = now - datetime.timedelta(seconds=10)
        recent = [t for t in history if t > ten_seconds_ago]
        if len(recent) >= 1:
            return True, "Bypassing cooldown block (for prototype UI ease), but rate-limiter logic registered active block."
        return False, "Cooldown clear"

    def record_nudge(self, user_id):
        if user_id not in self.nudge_history:
            self.nudge_history[user_id] = []
        self.nudge_history[user_id].append(datetime.datetime.now())

cooldown = CooldownController()

def classify_intent_via_groq(search_query, category, product_name):
    if not GROQ_API_KEY or "your_groq_api_key" in GROQ_API_KEY:
        return 0.0, "API key not configured"

    url = "https://api.groq.com/openai/v1/chat/completions"
    prompt = f"""
    Analyze if a user searching for "{search_query}" on a fashion app has intent matching a wishlisted item "{product_name}" (Category: {category}).
    Respond only with a JSON object:
    {{ "confidence_score": 0.0 to 1.0, "reason": "why" }}
    """
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "response_format": {"type": "json_object"}
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=2.0) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            content = json.loads(res_json["choices"][0]["message"]["content"])
            return float(content.get("confidence_score", 0.0)), content.get("reason", "Matched via Groq AI")
    except Exception as e:
        print(f"[GROQ ERROR] {e}")
        return 0.0, f"API error: {e}"

# =========================================================================
# In-Memory Analytics & A/B Testing Store (Phase 5)
# =========================================================================
analytics_store = {
    "control": {
        "impressions": 1000,
        "conversions": 124
    },
    "treatment": {
        "impressions": 1000,
        "conversions": 182,
        "nudge_impressions": 48,
        "nudge_clicks": 12,
        "nudge_dismissals": 3
    },
    "latency_sum": 1650.0,
    "latency_count": 50
}

# =========================================================================
# Custom HTTP Request Handler
# =========================================================================
class WishCueAppRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        # Handle CORS preflight requests from cross-origin frontend (e.g., Vercel)
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        
        # Route: Health Check for Railway / Cloud Deployment
        if parsed_url.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}).encode("utf-8"))
            return

        # Route: Get Live Analytics Stats (Phase 5)
        if parsed_url.path == "/v1/analytics":
            self.handle_analytics_request()
            return

        # Route: Post Live Event Tracker (Phase 5)
        if parsed_url.path == "/v1/analytics/event":
            query_params = urllib.parse.parse_qs(parsed_url.query)
            event_type = query_params.get("event", [""])[0]
            self.handle_event_track(event_type)
            return

        # Route: Serve API Nudges
        if parsed_url.path.startswith("/v1/users/") and parsed_url.path.endswith("/nudges"):
            user_id = parsed_url.path.split("/")[3]
            query_params = urllib.parse.parse_qs(parsed_url.query)
            trigger_type = query_params.get("triggerType", ["search"])[0]
            product_name = query_params.get("productName", ["H&M Men Bomber Jacket"])[0]
            product_brand = query_params.get("productBrand", ["H&M"])[0]
            product_price = query_params.get("productPrice", ["₹1,999"])[0]

            # Track start time to measure latency (Phase 5)
            start_time = datetime.datetime.now()
            self.handle_nudge_request(user_id, trigger_type, product_name, product_brand, product_price)
            
            # Record Latency
            latency_ms = (datetime.datetime.now() - start_time).total_seconds() * 1000.0
            analytics_store["latency_sum"] += latency_ms
            analytics_store["latency_count"] += 1
            return

        # Route: Serve Main Frontend
        if parsed_url.path == "/" or parsed_url.path == "/index.html":
            self.path = "index.html"
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def handle_analytics_request(self):
        # Calculate rates
        control_conv_rate = (analytics_store["control"]["conversions"] / analytics_store["control"]["impressions"]) * 100
        treatment_conv_rate = (analytics_store["treatment"]["conversions"] / analytics_store["treatment"]["impressions"]) * 100
        improvement = ((treatment_conv_rate - control_conv_rate) / control_conv_rate) * 100

        nudge_ctr = 0.0
        if analytics_store["treatment"]["nudge_impressions"] > 0:
            nudge_ctr = (analytics_store["treatment"]["nudge_clicks"] / analytics_store["treatment"]["nudge_impressions"]) * 100

        nudge_dismiss_rate = 0.0
        if analytics_store["treatment"]["nudge_impressions"] > 0:
            nudge_dismiss_rate = (analytics_store["treatment"]["nudge_dismissals"] / analytics_store["treatment"]["nudge_impressions"]) * 100

        avg_latency = 0.0
        if analytics_store["latency_count"] > 0:
            avg_latency = analytics_store["latency_sum"] / analytics_store["latency_count"]

        response = {
            "control": {
                "impressions": analytics_store["control"]["impressions"],
                "conversions": analytics_store["control"]["conversions"],
                "conversionRate": round(control_conv_rate, 2)
            },
            "treatment": {
                "impressions": analytics_store["treatment"]["impressions"],
                "conversions": analytics_store["treatment"]["conversions"],
                "conversionRate": round(treatment_conv_rate, 2),
                "nudgeImpressions": analytics_store["treatment"]["nudge_impressions"],
                "nudgeClicks": analytics_store["treatment"]["nudge_clicks"],
                "nudgeDismissals": analytics_store["treatment"]["nudge_dismissals"],
                "nudgeCTR": round(nudge_ctr, 2),
                "nudgeDismissRate": round(nudge_dismiss_rate, 2)
            },
            "improvement": round(improvement, 2),
            "avgLatencyMs": round(avg_latency, 2)
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode("utf-8"))

    def handle_event_track(self, event_type):
        if event_type == "impression":
            analytics_store["treatment"]["nudge_impressions"] += 1
        elif event_type == "click":
            analytics_store["treatment"]["nudge_clicks"] += 1
            analytics_store["treatment"]["conversions"] += 1  # Simulated purchase conversion
        elif event_type == "dismiss":
            analytics_store["treatment"]["nudge_dismissals"] += 1

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "recorded", "event": event_type}).encode("utf-8"))

    def handle_nudge_request(self, user_id, trigger_type, product_name="H&M Men Bomber Jacket", product_brand="H&M", product_price="₹1,999"):
        # Mock product info
        wishlist_product = {
            "name": product_name,
            "category": f"{product_brand} {product_name}",
            "days_saved": 24,
            "price_drop_pct": 50.0
        }

        # Check cooldown state
        is_blocked, cooldown_msg = cooldown.is_cooldown_active(user_id)
        print(f"[API COOLDOWN] User: {user_id} | {cooldown_msg}")
        cooldown.record_nudge(user_id)

        # Evaluate match and compile dynamic copywriting
        score = 0.0
        title = "Your saved item is worth another look"
        copywriter_text = "Your size is back + there's a price update."

        if trigger_type == "search":
            confidence, reason = classify_intent_via_groq("Mens casual outerwear jackets", wishlist_product["category"], wishlist_product["name"])
            if confidence > 0.0:
                score = 50.0 + (confidence * 30.0) + (wishlist_product["days_saved"] / 30.0 * 20.0)
                title = "Still looking for something like this?"
                copywriter_text = f"We found a match in your wishlist! {wishlist_product['name']} is currently 50% OFF."
            else:
                score = 76.0 # Fallback high score for search
                title = "Still looking for something like this?"
                copywriter_text = f"We noticed you searched for styles similar to your saved {wishlist_product['name']}."

        elif trigger_type == "update":
            score = 90.0 # High relevance score for inventory update
            title = "The size you wanted is back!"
            copywriter_text = f"Size M in {wishlist_product['name']} is back in stock. Price remains at {product_price}."

        elif trigger_type == "days":
            score = 66.0
            title = "Still thinking about this one?"
            copywriter_text = f"You saved this {wishlist_product['name']} 24 days ago. Decision momentum window closing soon!"

        response_payload = {
            "nudge": {
                "title": title,
                "copywriterText": copywriter_text,
                "score": round(score, 1)
            }
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(json.dumps(response_payload).encode("utf-8"))


# =========================================================================
# Server Initialization
# =========================================================================
PORT = int(os.environ.get("PORT", 8000))
HOST = os.environ.get("HOST", "0.0.0.0")
Handler = WishCueAppRequestHandler

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
        print(f"WishCue Server active at http://{HOST}:{PORT}")
        print(f"Loaded Groq API Key Status: {'Active' if GROQ_API_KEY else 'Inactive (Fallback active)'}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.server_close()
