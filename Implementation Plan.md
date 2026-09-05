# Implementation Plan: Wishlist Re-engagement Engine

This implementation plan outlines the phased approach, task breakdown, timeline, and validation strategies for deploying the Wishlist Re-engagement Engine. The plan is designed to transition from architecture to full production release over five sequential phases.

---

## 1. Project Phases & Timeline

```
┌────────────────────────────────────────────────────────┐
│  Phase 1: Data Ingestion & Event Streams (Weeks 1-2)    │
└───────────┬────────────────────────────────────────────┘
            ▼
┌────────────────────────────────────────────────────────┐
│  Phase 2: Core Processing Engines (Weeks 3-5)           │
└───────────┬────────────────────────────────────────────┘
            ▼
┌────────────────────────────────────────────────────────┐
│  Phase 3: Relevance, Rules & Scoring (Weeks 6-7)       │
└───────────┬────────────────────────────────────────────┘
            ▼
┌────────────────────────────────────────────────────────┐
│  Phase 4: Client SDK & Layout Engine (Weeks 8-9)       │
└───────────┬────────────────────────────────────────────┘
            ▼
┌────────────────────────────────────────────────────────┐
│  Phase 5: Verification, A/B Testing & Rollout (Week 10) │
└────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Task Breakdown

### Phase 1: Data Ingestion & Event Streams (Weeks 1-2)
Establish the pipeline infrastructure required to capture real-time signals without impacting catalog or checkout latency.
* **Task 1.1: Kafka Topic Configuration**
  * Set up and configure topics: `wishlist-events`, `catalog-updates`, and `user-search-intent`.
  * Ensure partition keys are set to `userId` to maintain event order for individual shoppers.
* **Task 1.2: State Store Setup**
  * Deploy a Redis cluster to serve as the low-latency **Re-engagement State Store** (storing user cooldown metadata, recently viewed items, and active nudge history).
* **Task 1.3: Producer Instrumentation**
  * Instrument the catalog service to emit price change and stock replenish events to `catalog-updates`.
  * Instrument the search service to stream user search intent keywords to `user-search-intent`.

### Phase 2: Core Processing Engines (Weeks 3-5)
Build the services responsible for analyzing events and detecting actionable re-engagement signals.
* **Task 2.1: Signal Detection Engine (SDE) Core**
  * Develop the consumer application listening to Kafka topics.
  * Implement the **Price Monitor** to flag price drops on wishlisted items.
  * Implement the **Inventory Monitor** to flag "back in stock" or "last few items left in size" conditions.
* **Task 2.2: Temporal Trigger Service**
  * Develop a daily cron job that queries the primary Wishlist database for items nearing their 30-day window (specifically at days 25-28) to trigger the purchase momentum warning signal.

### Phase 3: Relevance, Rules & Scoring (Weeks 6-7)
Implement logic to ensure high relevance and prevent user fatigue/spam.
* **Task 3.1: Cooldown Controller**
  * Implement sliding-window rate-limiting logic in Redis (e.g., maximum 1 nudge per session, max 3 nudges per week across all channels).
* **Task 3.2: Context Classifier (Groq API Integration)**
  * Set up the Groq client and configure connections to Groq LPU endpoints using lightweight models (e.g., Llama-3-8b).
  * Build semantic matching prompts and logic to classify user search intent and align it with the category/metadata of their wishlisted items.
* **Task 3.3: Scoring Algorithm Implementation**
  * Write the ranking function that outputs the `Reconsideration Score` based on:
    * Price drop percentage (higher drop = higher score)
    * Time since wishlisted (closer to 30 days = higher score)
    * Semantic category match (calculated via Groq context classification = higher score)

### Phase 4: Client SDK & Layout Engine (Weeks 8-9)
Expose the APIs and integrate the client interface components.
* **Task 4.1: Delivery Engine & Dynamic Copywriting (Groq API Integration)**
  * Build the API endpoint `/v1/users/{userId}/nudges` that the client app queries.
  * Integrate Groq API within the API handler to dynamically generate customized, context-rich nudge copy (e.g., matching the user's current search category and style tone).
  * Ensure response times are optimized (< 150ms) using parallel execution, fallback static copywriting templates, and Redis caching of generated copy.
* **Task 4.2: Client-side UI Integration (Myntra App)**
  * Create the **Sparkle Burst** animation: a CSS/JS golden particle burst radiating from the header heart icon (notification anchor).
  * Integrate the **Floating Pill Capsule** notification widget: a compact, non-intrusive container floating below the anchor with auto-dismiss (5 seconds) and quick-dismiss (`X`) capabilities.

### Phase 5: Verification, A/B Testing & Rollout (Week 10)
Validate the system behavior and test business outcomes.
* **Task 5.1: A/B Testing Framework Integration**
  * Divide users into:
    * **Control Group (50%):** Standard static wishlist experience.
    * **Treatment Group (50%):** Wishlist Re-engagement Engine enabled.
* **Task 5.2: Metrics Dashboard Setup**
  * Set up dashboard tracking to display:
    * Conversion Lift (Primary Metric: difference in conversion rates between Treatment and Control).
    * Average API Latency (computed from live response times).
    * Click-Through Rate (CTR) and Dismiss Rate of the floating capsules.

---

## 3. Verification Plan

### Automated Verification
* **Unit Tests:** Verify scoring logic outputs correct priority scores for mixed scenarios (e.g., high price drop vs. near-expiration items).
* **Integration Tests:** Verify that when a mock price drop event is posted to Kafka, the SDE correctly processes it and stores the potential nudge in Redis.
* **Performance/Load Testing:** Benchmark the `/v1/users/{userId}/nudges` endpoint at 15,000 requests per second using tools like k6 to guarantee latency remains < 150ms under peak load.

### Manual Verification
* **UAT Flow Test:**
  1. Add item "H&M Men Bomber Jacket" to wishlist on a test device.
  2. Simulate a product update or price drop event.
  3. Open the search screen on the test device and query "Men Bomber Jacket".
  4. Verify that the golden **Sparkle Burst** shoots from the wishlist icon, and the **Floating Pill Capsule** appears next to it.
  5. Verify that clicking the pill capsule records click telemetry and navigates directly to the Product Details Page (PDP).
  6. Navigate to the **Metrics Dashboard** tab and verify the conversion rates, CTR, and latency stats update in real-time.
