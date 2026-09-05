# Problem Statement: Wishlist Re-engagement Engine (Myntra WishCue)

### **Wishlisted products lose purchase momentum after users leave them behind.**

Myntra users add fashion products to their Wishlist because they like them, want to save them for later, are waiting for the right occasion, or are evaluating price and alternatives.

However, after wishlisting, users often **postpone the purchase and continue browsing**. As time passes, the saved product becomes a passive bookmark, even when the underlying interest still exists.

Users may reconsider a wishlisted product when something meaningful happens—such as a **similar search, price change, size/stock availability update, or the approach of the 30-day purchase window**—but they may not notice or act on these moments.

---

### **Core Problem**

> **Users with genuine wishlist intent lack a timely and relevant way to reconnect with saved products when there is a meaningful reason to reconsider them, causing purchase momentum to fade before the 30-day window.**

---

### **Desired Behavior Shift**

```
❤️ Passive Saving
Wishlist → Leave → Wait → Forget / Postpone
       ↓
🤔 Active Reconsideration
Relevant Signal → Revisit → Evaluate → Decide
```

---

### **Product Opportunity**

Create a customer-first re-engagement experience that:

* **Detects meaningful changes or renewed interest** around wishlisted products (Search queries, Price drops, Size availability, Wishlist age).
* **Gets the user's attention without interrupting their browsing** using subtle micro-interactions attached to familiar UI anchors.
* **Communicates WHY the product is relevant again** with personalized, context-aware copywriting powered by low-latency AI.
* **Makes returning to the saved product effortless** via single-tap routing to the Product Details Page (PDP).
* **Helps the customer make their own purchase decision** rather than forcing aggressive checkout prompts.
* **Does NOT rely on monetary incentives, surveys, or spam** (enforcing cooldown frequency limits).

---

### **Customer Insight**

> **“I don't need another reminder. I need a reason to come back.”**

---

### **Business Outcome**

* **Primary Metric:** Increase the **percentage of users who purchase at least one wishlisted item within 30 days of adding it.**
* **Secondary Metrics:**
  * Reconsideration CTR on contextual nudges ($\ge 20\%$).
  * Wishlist-to-Bag conversion velocity reduction (faster decision cycles).
  * Unsubscribe / notification dismissal rate kept $< 8\%$.

---

### **Delivered Solution & Live MVP**

The **Myntra WishCue** engine has been fully designed, implemented, and deployed to live cloud infrastructure:

* **Frontend (Vercel):** [https://mynta-wishcue-contextual-reengageme.vercel.app](https://mynta-wishcue-contextual-reengageme.vercel.app)
* **Backend AI Server (Railway):** [https://mynta-wishcue-contextual-reengagement-production.up.railway.app](https://mynta-wishcue-contextual-reengagement-production.up.railway.app)
* **GitHub Repository:** [https://github.com/yashwanthps71097/Mynta-wishcue-contextual-reengagement](https://github.com/yashwanthps71097/Mynta-wishcue-contextual-reengagement)

#### Key Implemented Capabilities:
1. **Contextual Trigger 1 (Similar Search):** Triggers when user searches for styles matching saved items (e.g. "jacket"), highlighting relevant discounts.
2. **Contextual Trigger 2 (Product Update):** Triggers when requested size or stock is replenished (e.g. "Size M is back in stock").
3. **Contextual Trigger 3 (30-Day Decision Window):** Alerts the user as saved items approach the 30-day window to revive dormant intent.
4. **Non-Intrusive Presentation:** 15-particle Golden Sparkle Burst, breathing Heart Glow pulse, and 5-second auto-dismissing Floating Pill Capsule.
5. **Live Analytics & A/B Testing Dashboard:** Real-time tracking of treatment vs. control conversion lift (+18.4% to +46.7%) and sub-50ms API latency.
