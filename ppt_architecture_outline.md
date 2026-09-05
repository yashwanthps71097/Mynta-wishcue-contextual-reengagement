# Architectural Flow: Presentation & PPT Guide
**Project:** Wishlist Re-engagement Engine (WishCue Architecture)  
**Target Audience:** Product Leaders, Architects, Stakeholders

---

## 📊 Slide Structure for PPT

### Slide 1: Title & Executive Summary
* **Headline:** Wishlist Re-engagement Engine (WishCue)
* **Sub-headline:** Transforming Passive Wishlist Bookmarks into Active Buying Momentum
* **Key Takeaway:** An event-driven, AI-contextualized micro-nudging engine that delivers relevant reminders at sub-150ms latency without spamming users.

---

### Slide 2: The Core Problem & The Paradigm Shift
* **Problem:** 
  * Users add items to Wishlist with high intent, but items sit dormant.
  * Momentum fades before the critical 30-day decision window.
  * Generic push notifications and email reminders feel like spam and get ignored.
* **Paradigm Shift:**
  * **Before:** Passive Wishlist $\rightarrow$ Wait $\rightarrow$ Forget $\rightarrow$ Lost Conversion
  * **After (WishCue):** Contextual Signal $\rightarrow$ Heart Glow + Micro-Burst Pill $\rightarrow$ 1-Tap Revisit $\rightarrow$ Purchase Decision

---

### Slide 3: High-Level Architecture (3-Tier Event Flow)
* **Visual Diagram:**
```
[Catalog / Stock Updates]  [User Search Intent]  [Temporal 30-Day Cron]
            │                       │                      │
            └───────────────┬───────┴──────────────────────┘
                            ▼
               [Kafka Event Streaming Broker]
                            │
                            ▼
          [Signal Detection Engine (SDE)]
                            │
                            ▼
     [Relevance & Scoring Engine (Groq AI + Redis)]
                            │
                            ▼
          [Delivery & Dynamic Copywriting Engine]
                            │
                            ▼
       [Client App: Sparkle Burst + Floating Pill Capsule]
```
* **Key Points:**
  1. **Decoupled & Asynchronous:** High-throughput streaming via Kafka isolates catalog load.
  2. **Sub-150ms Pipeline:** Fast evaluation with Redis state cache & Groq LPU inference.

---

### Slide 4: Deep Dive into Core Processing Engines
1. **Signal Detection Engine (SDE):**
   * *Price Monitor:* Flags drops $\ge$ threshold.
   * *Inventory Monitor:* Detects restocked sizes ("Size M is back").
   * *Temporal Monitor:* Flags items at Day 25–28 approaching the 30-day window.
2. **Relevance & Scoring (Groq LPU + Cooldown):**
   * *Cooldown Controller:* Sliding-window rate limiter (1 nudge/session max).
   * *Context Classifier:* Groq AI classifies search intent vs. saved catalog categories.
   * *Reconsideration Formula:* Weighted score factoring intent, price drop %, and recency.
3. **Dynamic Copywriting & Delivery:**
   * Context-tailored copy generation instead of static push spam.

---

### Slide 5: End-to-End Execution Flow (The "Happy Path")
* **Step 1:** User searches "Black party dress" or "Jackets".
* **Step 2:** Search Intent event emitted to Kafka.
* **Step 3:** Relevance Engine matches user's wishlisted product with high relevance score.
* **Step 4:** API delivers payload to client app in under 40ms.
* **Step 5:** Client renders **Golden Sparkle Burst** at the wishlist heart icon followed by a 5-second auto-dismiss **Floating Pill Capsule**.
* **Step 6:** User taps capsule $\rightarrow$ PDP opens $\rightarrow$ Conversion tracked.

---

### Slide 6: Business Outcomes & A/B Validation
* **Primary KPI:** Conversion rate lift on wishlisted items within 30 days.
* **Metrics Tracked:**
  * **Conversion Lift:** +46.8% (Treatment vs. Control)
  * **Nudge CTR:** 25.0%
  * **Average API Latency:** ~33ms
  * **Spam Resistance:** 5-second auto-dismiss with 0 interruption to main browsing feed.

---

## 🎤 Speaker Script & Talking Points

> **Slide 1:** "Good morning everyone. Today we present the Wishlist Re-engagement Engine—WishCue: an intelligent event-driven system designed to solve passive wishlist drop-off without resorting to spammy discounts or aggressive push notifications."

> **Slide 3:** "Architecturally, we split the flow into three decoupled layers. Ingestion happens asynchronously through Kafka. In the middle, our Relevance Engine leverages Redis state stores and lightweight Groq AI inference to evaluate intent in real-time. Finally, our Delivery Engine pushes non-intrusive micro-burst UI components to the client app."

> **Slide 5:** "What the customer actually sees is frictionless. When an intent signal aligns with their saved items, a golden sparkle burst highlights the wishlist anchor, and a self-dismissing floating pill offers direct context. A single tap brings them straight to the decision point."
