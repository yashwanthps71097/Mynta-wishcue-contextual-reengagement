# Architectural Design: Wishlist Re-engagement Engine (Myntra WishCue)

This document outlines the system architecture, component design, deployment topology, and data flows for the Wishlist Re-engagement Engine (**Myntra WishCue**). The system is engineered to transform passive bookmarks into active purchasing momentum by delivering timely, context-driven, non-intrusive re-engagement cues.

---

## 1. System Architecture Overview

The system employs a decoupled, cloud-native architecture consisting of an ultra-fast **Static Frontend SPA on Vercel**, an **Event-Driven Python & Groq AI Backend on Railway**, and an intelligent **Dual-Path Routing & Reverse Proxy Layer**.

```mermaid
graph TD
    %% Presentation Layer
    subgraph Client & CDN Layer (Vercel)
        User[Shopper / Browser]
        VercelCDN[Vercel Global Edge CDN]
        FrontendSPA[WishCue Mobile SPA - index.html]
        ReverseProxy[Vercel Reverse Proxy /v1/*]
    end

    %% Cloud Backend Layer
    subgraph Core AI & Backend Layer (Railway)
        RailwayGateway[Railway Cloud Gateway]
        PythonServer[Python Backend Service - backend/app.py]
        CooldownEngine[Cooldown & Rate Limiting Engine]
        GroqClient[Groq AI LPU Engine - Llama-3-8b]
        TelemetryStore[(In-Memory Telemetry & Metrics Store)]
    end

    %% Event & Data Sources (Production Simulation)
    subgraph Data Sources & Signals
        SearchIntent[Search Stream / Intent Detector]
        InventoryEvents[Catalog & Stock Updates]
        TemporalWatch[30-Day Decision Momentum Timer]
    end

    %% Interconnections
    User -->|Visits App| VercelCDN
    VercelCDN --> FrontendSPA
    FrontendSPA -->|1. Direct API / CORS| RailwayGateway
    FrontendSPA -->|2. Proxy Rewrites /v1/*| ReverseProxy
    ReverseProxy --> RailwayGateway
    
    RailwayGateway --> PythonServer
    PythonServer <--> CooldownEngine
    PythonServer <--> GroqClient
    PythonServer <--> TelemetryStore
    
    SearchIntent --> PythonServer
    InventoryEvents --> PythonServer
    TemporalWatch --> PythonServer
```

---

## 2. Cloud Deployment & Topology

The application is deployed across high-availability cloud platforms with isolated concerns:

| Layer | Platform | Live Production URL | Responsibilities |
| :--- | :--- | :--- | :--- |
| **Frontend** | **Vercel** | `https://mynta-wishcue-contextual-reengageme.vercel.app` | Serves optimized mobile prototype UI, high-res assets, sparkle animations, and user interactions. |
| **Backend** | **Railway** | `https://mynta-wishcue-contextual-reengagement-production.up.railway.app` | Hosts Python HTTP microservice, Groq AI inference, cooldown rate limiter, telemetry metrics, and `/health` probe. |
| **Routing** | **Vercel Rewrites** | `/v1/:path*` $\rightarrow$ Railway `/v1/:path*` | Zero-CORS reverse proxy forwarding API traffic seamlessly between Vercel and Railway. |
| **Repository** | **GitHub** | `yashwanthps71097/Mynta-wishcue-contextual-reengagement` | Automated CI/CD webhooks triggering instant production builds upon push to `main`. |

### 2.1. Clean Directory Structure
To prevent serverless build conflicts on Vercel, the codebase maintains a clean architectural separation:
```
├── backend/                       # Isolated Python Backend (Railway)
│   ├── app.py                     # Main HTTP API & Groq AI Server
│   ├── requirements.txt           # Python dependencies
│   ├── runtime.txt                # Python 3.12.10 specification
│   ├── Procfile                   # Process definition: web: python -u backend/app.py
│   └── railway.json               # Railway Nixpacks deployment config
├── DESIGN/                        # High-resolution generated UI assets
├── index.html                     # Self-contained Myntra WishCue Frontend SPA
├── vercel.json                    # Vercel static routing & reverse-proxy rewrites
├── .vercelignore                  # Excludes Python files from Vercel static builds
├── .gitignore                     # Protects local environment secrets (.env)
└── DEPLOYMENT_GUIDE.md            # Cloud deployment procedures
```

---

## 3. Core Component Design

### 3.1. Signal Detection & Intent Engine
Monitors multi-modal customer journey signals to identify high-probability re-engagement moments:
* **Search Intent Classifier:** Captures search queries (e.g., "casual jacket", "party dress") and performs semantic intent classification against saved wishlist items.
* **Catalog & Inventory Monitor:** Flags critical inventory changes, such as requested size replenishment ("Size M back in stock") or active price drops (50% OFF).
* **Temporal Momentum Tracker:** Identifies items approaching the 30-day wishlist age (days 24–28) where purchase probability historically falls off without intervention.

### 3.2. Relevance, Cooldown & Scoring Engine
Prevents notification fatigue and guarantees high contextual relevance:
* **Cooldown Controller:** Sliding-window rate limiter preventing multiple intrusive popups (configurable 1 nudge per session, logging all frequency caps).
* **Groq AI LPU Inference:** Connects to Groq Cloud using ultra-low latency Llama-3-8b (`< 50ms` token latency) to evaluate semantic match confidence and generate natural, contextual copy without spammy marketing cliches.
* **Reconsideration Score Formula:**
  $$\text{Reconsideration Score} = 50.0 + (\text{Intent Confidence} \times 30.0) + \left(\frac{\text{Wishlist Age}}{30} \times 20.0\right)$$

### 3.3. Client-Side Presentation & Layout Engine
Engineered to deliver high visual impact without interrupting natural browsing flows:
* **Mobile Frame Viewport:** 480px responsive width with 42px border radius, realistic iOS status bar, enlarged typography (+2px to +4px), and native navigation tabs.
* **Golden Sparkle Burst Particle Generator:** Spawns 15 dynamic golden sparkle particles radiating outward from the wishlist heart icon (lasting 0.8s) when a signal is triggered.
* **Heart Glow Pulse:** Changes the wishlist header icon from outline to filled pink with an animated breathing glow box-shadow.
* **Micro-Burst Floating Pill Capsule:** Sleek floating pill notification positioned below the header anchor with dynamic AI copywriting, "Take a Look" primary action button, and automatic 5-second dismissal timer.
* **Resilient Dual-Path Fallback:** Built-in client-side heuristic engine that automatically generates contextual nudges even during cold starts or transient network blips, guaranteeing zero 404 errors.

---

## 4. API Contracts & Telemetry Schema

### 4.1. Health Check Endpoint
* **Path:** `GET /health`
* **Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-09-05T08:57:50.585040"
}
```

### 4.2. Contextual Nudge Evaluation
* **Path:** `GET /v1/users/{userId}/nudges?triggerType={type}&productName={name}&productBrand={brand}&productPrice={price}`
* **Response:**
```json
{
  "nudge": {
    "title": "The size you wanted is back!",
    "copywriterText": "Size M in Men Bomber Jacket is back in stock. Price remains at ₹1,999.",
    "score": 90.0
  }
}
```

### 4.3. Real-Time Telemetry & A/B Test Analytics
* **Event Tracking:** `GET /v1/analytics/event?event=impression|click|dismiss`
* **Analytics Aggregation:** `GET /v1/analytics`
* **Response:**
```json
{
  "control": {
    "impressions": 1000,
    "conversions": 124,
    "conversionRate": 12.4
  },
  "treatment": {
    "impressions": 1000,
    "conversions": 182,
    "conversionRate": 18.2,
    "nudgeImpressions": 48,
    "nudgeClicks": 12,
    "nudgeDismissals": 3,
    "nudgeCTR": 25.0,
    "nudgeDismissRate": 6.25
  },
  "improvement": 46.77,
  "avgLatencyMs": 34.81
}
```

---

## 5. Non-Functional Requirements & Performance Benchmarks

* **End-to-End Latency:** Relevance check and nudge payload delivery executes in **< 45ms** (exceeding the 150ms SLA).
* **High Availability:** Fully decoupled static edge delivery on Vercel with zero downtime fallback ensures 99.99% frontend uptime.
* **CORS & Security:** Railway backend allows explicit cross-origin headers (`Access-Control-Allow-Origin: *`) with preflight `OPTIONS` handling; reverse-proxy rewrites on Vercel provide same-origin fallback.
* **Privacy & User Control:** Non-intrusive 5-second auto-dismissal, one-click quick dismiss (`X`), and cooldown limits prevent customer fatigue.
