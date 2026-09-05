# Implementation Plan: Wishlist Re-engagement Engine (Myntra WishCue)

This implementation plan outlines the phased approach, task breakdown, execution roadmap, and validation strategies for the Wishlist Re-engagement Engine (**Myntra WishCue**). The system has progressed from architectural concept to a fully deployed cloud-native production release.

---

## 1. Project Phases & Status Roadmap

```
┌────────────────────────────────────────────────────────┐
│  Phase 1: Data Ingestion & Event Streams        [COMPLETED] │
└───────────┬────────────────────────────────────────────┘
            ▼
┌────────────────────────────────────────────────────────┐
│  Phase 2: Core Processing Engines               [COMPLETED] │
└───────────┬────────────────────────────────────────────┘
            ▼
┌────────────────────────────────────────────────────────┐
│  Phase 3: Relevance, Rules & Groq AI Scoring    [COMPLETED] │
└───────────┬────────────────────────────────────────────┘
            ▼
┌────────────────────────────────────────────────────────┐
│  Phase 4: Client SDK & Layout Engine Prototype  [COMPLETED] │
└───────────┬────────────────────────────────────────────┘
            ▼
┌────────────────────────────────────────────────────────┐
│  Phase 5: Telemetry, A/B Testing & Verification [COMPLETED] │
└───────────┬────────────────────────────────────────────┘
            ▼
┌────────────────────────────────────────────────────────┐
│  Phase 6: Cloud Deployment & Dual-Platform Live [COMPLETED] │
└────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Task Breakdown & Implementation Status

### Phase 1: Data Ingestion & Event Streams [COMPLETED]
* **Task 1.1: Event Contract Definitions**
  * Defined schemas for `wishlist-events`, `catalog-updates`, and `user-search-intent`.
  * Set partition keys to `userId` to maintain chronological sequence for individual shoppers.
* **Task 1.2: State Store Architecture**
  * Modeled low-latency state store for user cooldown timestamps, wishlist item ages, and nudge impression records.
* **Task 1.3: Producer Instrumentation Simulation**
  * Simulated catalog price change events, stock replenishments, and user search keyword streams.

### Phase 2: Core Processing Engines [COMPLETED]
* **Task 2.1: Signal Detection Engine (SDE)**
  * Implemented the **Price Monitor** to detect price drops (e.g. 50% OFF on saved H&M Bomber Jacket).
  * Implemented the **Inventory Monitor** for size-specific back-in-stock notifications (Size M back in stock).
* **Task 2.2: Temporal Trigger Service**
  * Modeled logic for items nearing their 30-day wishlist age (specifically targeting days 24–28) to trigger the decision momentum re-engagement window.

### Phase 3: Relevance, Rules & Groq AI Scoring [COMPLETED]
* **Task 3.1: Cooldown Controller**
  * Implemented sliding-window rate limiter ensuring non-intrusive re-engagement without user fatigue (1 nudge per session).
* **Task 3.2: Context Classifier (Groq AI Integration)**
  * Connected to Groq LPU Cloud using lightweight Llama-3-8b for sub-50ms semantic inference.
  * Formulated dynamic prompts to classify search intent and match against wishlist product categories.
* **Task 3.3: Dynamic Scoring Formula**
  * Computed `Reconsideration Score` (0–100) factoring intent confidence, price drop percentage, and wishlist age.

### Phase 4: Client SDK & Layout Engine Prototype [COMPLETED]
* **Task 4.1: API Microservice Endpoint**
  * Created `/v1/users/{userId}/nudges` returning structured copywriting and score payloads.
  * Implemented dynamic copywriter generating personalized, non-spammy notifications.
* **Task 4.2: Client-side UI & Animations**
  * Created the **Golden Sparkle Burst** particle generator (15 radiating particles around the wishlist header heart icon).
  * Implemented the **Heart Glow Pulse** on the wishlist icon.
  * Integrated the **Floating Pill Capsule** with dynamic AI copy, "Take a Look" PDP routing, and 5-second auto-dismissal.

### Phase 5: Telemetry, A/B Testing & Verification [COMPLETED]
* **Task 5.1: A/B Testing Framework**
  * Simulated Control (standard wishlist) vs. Treatment (WishCue engine enabled).
* **Task 5.2: Live Analytics Dashboard**
  * Real-time metrics dashboard tracking Conversion Lift (+18.4% to +46.7%), API Latency (~34ms), and Nudge CTR (25.0%).
* **Task 5.3: Telemetry Stream**
  * Implemented `/v1/analytics/event?event=impression|click|dismiss` endpoints with live counter aggregation.

### Phase 6: Cloud Deployment & Dual-Platform Production Release [COMPLETED]
* **Task 6.1: Architectural Isolation & Clean Repository Structure**
  * Refactored project to isolate Python backend code into `backend/` (`backend/app.py`, `backend/requirements.txt`, `backend/railway.json`, `backend/Procfile`).
  * Kept the root directory pure static for Vercel edge delivery.
* **Task 6.2: Backend Deployment on Railway**
  * Deployed Python server on Railway: `https://mynta-wishcue-contextual-reengagement-production.up.railway.app`.
  * Configured `PORT` binding, CORS headers, Groq API key environment injection, and `/health` monitoring probe.
* **Task 6.3: Frontend Deployment on Vercel**
  * Deployed static frontend on Vercel: `https://mynta-wishcue-contextual-reengageme.vercel.app`.
  * Configured `vercel.json` with `framework: null` and reverse-proxy rewrites (`/v1/:path*` $\rightarrow$ Railway).
* **Task 6.4: Zero-Downtime Dual-Path Resilience**
  * Added dual-path connectivity: direct live API calls to Railway with automatic client-side heuristic fallback ensuring zero 404 errors during cold starts.
* **Task 6.5: UI/UX Presentation Polish**
  * Widened phone container to 480px width x 920px height with enlarged typography (+2px to +4px).
  * Removed the floating desktop toolbar for a clean, distraction-free native mobile presentation.
  * Polished the `⚡ WishCue Evaluator` bar with automatic status clearing.

---

## 3. Deployment Summary

| Platform | Role | Production Link |
| :--- | :--- | :--- |
| **Vercel** | **Frontend Application** | [https://mynta-wishcue-contextual-reengageme.vercel.app](https://mynta-wishcue-contextual-reengageme.vercel.app) |
| **Railway** | **Backend AI Server** | [https://mynta-wishcue-contextual-reengagement-production.up.railway.app](https://mynta-wishcue-contextual-reengagement-production.up.railway.app) |
| **GitHub** | **Source Code & CI/CD** | [https://github.com/yashwanthps71097/Mynta-wishcue-contextual-reengagement](https://github.com/yashwanthps71097/Mynta-wishcue-contextual-reengagement) |

---

## 4. Verification & Validation Results

### Automated Test Suite
* **Health Endpoint:** `GET /health` returns `HTTP 200 OK` (`{"status": "healthy"}`).
* **Vercel Reverse Proxy:** `GET https://mynta-wishcue-contextual-reengageme.vercel.app/health` proxies to Railway with `HTTP 200 OK`.
* **Live Nudge Endpoint:** `GET /v1/users/.../nudges` returns valid JSON with score and dynamic copy in `< 40ms`.
* **Telemetry Events:** Verified impression, click, and dismiss events update live metrics.

### End-to-End User Experience Validation
1. Open the live Vercel URL in any browser.
2. Click **Similar Search** $\rightarrow$ Golden sparkle burst fires, heart glows, and capsule displays 50% discount search match.
3. Click **Product Update** $\rightarrow$ Capsule displays "Size M back in stock" notification.
4. Click **30-Day Window** $\rightarrow$ Capsule displays decision momentum closing reminder.
5. Click **Take a Look** $\rightarrow$ Redirects instantly to the Product Details Page (PDP) with active Move to Bag action.
6. Click **WishCue** bottom nav tab $\rightarrow$ Displays live A/B testing benchmark metrics.
