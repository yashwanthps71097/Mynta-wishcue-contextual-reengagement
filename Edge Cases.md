# Edge Cases & Mitigation Strategies

This document identifies potential edge cases for the Wishlist Re-engagement Engine and details the technical mitigation strategies to ensure system stability, low latency, and a premium user experience.

---

## 1. Latency & External Service Failures

### 1.1. Groq API Timeout or Outage
* **Scenario:** The Groq API experiences high latency (> 100ms) or is temporarily unavailable when trying to classify intent or generate dynamic copy.
* **Risk:** The API response time breaches the 150ms SLA, slowing down the client's search/browsing experience.
* **Mitigation:**
  * **Hard Timeout:** Set a strict timeout of **50ms** on all Groq API calls.
  * **Static Fallback:** If the API fails or times out, immediately fall back to pre-defined static copy templates (e.g., *"An item from your wishlist is now on sale."*) and fallback to exact category/brand taxonomy matching.
  * **Asynchronous Generation:** For temporal or price signals, pre-generate copywriting out-of-band and cache it in Redis instead of generating it on the fly during search requests.

---

## 2. Inventory & Catalog Synchronicity

### 2.2. "Race Condition" on Low Stock
* **Scenario:** The user receives a nudge stating *"Only 1 left in your size!"*, but another shopper buys it while the user is clicking the nudge.
* **Risk:** High customer frustration when landing on an out-of-stock product details page (PDP).
* **Mitigation:**
  * **Render-Time Verification:** The Delivery Engine checks real-time inventory state immediately before serving the nudge payload.
  * **Smart PDP Landing:** If the item sells out post-click, display a graceful banner on the PDP: *"Oops, this sold out fast! Here are similar styles you might like,"* and auto-recommend alternatives.

### 2.3. Rapid Price Fluctuations (Flash Sales)
* **Scenario:** A product's price fluctuates up and down repeatedly due to dynamic pricing rules or coupon integrations.
* **Risk:** Spamming the user with price change alerts or displaying stale price quotes.
* **Mitigation:**
  * **Minimum Threshold:** Only trigger a signal if the price drop is greater than **10%** and lower than the 7-day average price.
  * **Price Lock Cache:** Store the notified price in Redis and do not trigger another price nudge unless the price drops significantly below the previously notified price.

---

## 3. User State & Data Integrity

### 3.1. Delayed Consumption of Wishlist Deletion
* **Scenario:** A user removes a product from their wishlist, but a price drop event for that product is already queued in Kafka.
* **Risk:** The user receives a nudge for an item they just deleted.
* **Mitigation:**
  * **Double-Check State:** Right before calculating the `Reconsideration Score` and dispatching the nudge, the Relevance Engine must perform a quick check against the Redis Wishlist Cache to confirm the product is still wishlisted.

### 3.2. Extreme Wishlist Sizes ("Hoarders")
* **Scenario:** A user has 500+ items in their wishlist.
* **Risk:** High memory usage in Redis and potential classification overload.
* **Mitigation:**
  * **Pre-Filtering:** Only load the top 50 most recently active/added wishlisted items into the active session cache for real-time semantic comparison.

---

## 4. Algorithmic Relevance & Guardrails

### 4.1. Semantic False Positives (Incorrect Matches)
* **Scenario:** A user searches for "garbage bags", and the Groq LLM matches it to a wishlisted "leather handbag" due to semantic proximity of the word "bag".
* **Risk:** The user gets an irrelevant nudge, making the experience feel spammy.
* **Mitigation:**
  * **Taxonomy Guardrails:** Enforce a hard rule that the product category must align at a high level (e.g., both must be under "Accessories" or "Home Utility") before sending the query to the Groq API for semantic nuance matching.
  * **Confidence Scoring:** Reject matches where the LLM return confidence score is below 0.85.
