# Cloud Deployment Guide: WishCue Engine

This guide walks you through deploying the **WishCue Wishlist Re-engagement Engine** to production across cloud providers:
* **Backend:** Hosted on **[Railway](https://railway.app)** (Python HTTP API, Groq AI intent evaluation, Cooldown limiter, Telemetry store).
* **Frontend:** Hosted on **[Vercel](https://vercel.com)** (Interactive Myntra UI, Sparkle Burst particles, Micro-Burst pills, Metrics Dashboard).

---

## 🏗️ Architecture & Traffic Flow

```
   ┌─────────────────────────────────────────────────────────────┐
   │                       Shopper Browser                       │
   └───────────────┬─────────────────────────────┬───────────────┘
                   │                             │
    1. Loads UI Assets (HTML/CSS)   2. API Calls (/v1/users, /v1/analytics)
                   │                             │
                   ▼                             ▼
       ┌───────────────────────┐     ┌───────────────────────┐
       │    Vercel Frontend    │     │    Railway Backend    │
       │  (Static Edge Cache)  │     │  (Python on $PORT)    │
       └───────────────────────┘     └───────────┬───────────┘
                                                 │
                                                 ▼
                                     ┌───────────────────────┐
                                     │     Groq LPU API      │
                                     │   (Llama-3-8b-8192)   │
                                     └───────────────────────┘
```

---

## 📋 Prerequisites
1. A **[GitHub](https://github.com)** account.
2. A **[Railway](https://railway.app)** account (Free starter credit included).
3. A **[Vercel](https://vercel.com)** account (Free Hobby tier).
4. A **[Groq Cloud](https://console.groq.com)** API Key (free).

---

## Step 1: Push Project to GitHub

Open PowerShell or Terminal in your project directory:

```powershell
# 1. Initialize Git repository
git init

# 2. Add all deployment and project files
git add .

# 3. Commit files
git commit -m "feat: complete MVP design and cloud deployment configurations"

# 4. Link your remote GitHub repository
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 5. Push to GitHub
git push -u origin main
```

> [!NOTE]
> Sensitive files such as `.env` are automatically ignored by [.gitignore](file:///c:/Users/ADMIN/Desktop/Product%20Owner%20Project%202/MVP%20Design/.gitignore).

---

## Step 2: Deploy Backend to Railway

Railway automatically detects Python via `requirements.txt` and starts the app via `Procfile` / `railway.json`.

1. Log into **[Railway Dashboard](https://railway.app/dashboard)**.
2. Click **+ New Project** $\rightarrow$ select **Deploy from GitHub repo**.
3. Choose your repository.
4. Click **Add Variables** and configure the following environment variables:
   * `GROQ_API_KEY`: `your_groq_api_key_here` (from console.groq.com)
   * `GROQ_MODEL`: `llama3-8b-8192`
   * *(Note: `PORT` and `HOST` are automatically injected by Railway).*
5. Click **Settings** $\rightarrow$ scroll to **Networking** $\rightarrow$ click **Generate Domain**.
6. Railway will assign you a public URL like:
   ```
   https://wishcue-backend-production.up.railway.app
   ```
7. **Verify Railway Deployment:** Open your browser and navigate to:
   ```
   https://YOUR_RAILWAY_URL.up.railway.app/health
   ```
   You should see:
   ```json
   {"status": "healthy", "timestamp": "2026-..."}
   ```

---

## Step 3: Deploy Frontend to Vercel

Vercel provides instant global CDN caching for the static Myntra prototype.

### Method A: Reverse-Proxy via `vercel.json` (Recommended - Zero CORS)
1. In your local repository, open [vercel.json](file:///c:/Users/ADMIN/Desktop/Product%20Owner%20Project%202/MVP%20Design/vercel.json).
2. Replace `YOUR_RAILWAY_URL` with your actual Railway domain from Step 2:
   ```json
   {
     "$schema": "https://openapi.vercel.sh/vercel.json",
     "cleanUrls": true,
     "rewrites": [
       {
         "source": "/v1/:path*",
         "destination": "https://wishcue-backend-production.up.railway.app/v1/:path*"
       }
     ]
   }
   ```
3. Commit and push this change:
   ```powershell
   git add vercel.json
   git commit -m "chore: point vercel rewrites to live railway backend"
   git push
   ```
4. Go to **[Vercel Dashboard](https://vercel.com/dashboard)** $\rightarrow$ click **Add New...** $\rightarrow$ **Project**.
5. Import your GitHub repository.
6. Leave Framework Preset as **Other** and click **Deploy**.
7. Vercel will deploy your site to:
   ```
   https://your-project-name.vercel.app
   ```

---

## Step 4: Verification Checklist

| Test Item | Action | Expected Outcome |
| :--- | :--- | :--- |
| **Backend Health** | Visit `https://YOUR_RAILWAY_URL/health` | HTTP 200 `{"status": "healthy"}` |
| **API Endpoints** | Visit `https://YOUR_RAILWAY_URL/v1/analytics` | Returns JSON A/B metrics and latency stats |
| **Frontend UI** | Open `https://YOUR_VERCEL_URL` | Myntra mobile frame loads with interactive feed |
| **Micro-Nudge Trigger** | Type "Jacket" in search bar or click "Back In Stock" | Golden sparkle particle burst shoots from heart icon |
| **Floating Capsule** | Observe popup capsule | 5-second auto-dismiss and quick-dismiss (`X`) work |
| **Telemetry & Metrics** | Click the capsule or switch to "Metrics Dashboard" tab | Conversion Lift (+46.8%) and Latency metrics update live |

---

## 🛠️ Troubleshooting & FAQs

### 1. `CORS error` in browser console:
* `app.py` has built-in CORS headers and `do_OPTIONS` handler allowing cross-origin requests from any origin (`*`).
* If you use the recommended `vercel.json` rewrite, all requests are same-origin (`/v1/...` proxied server-side), preventing browser CORS blocks entirely.

### 2. Railway build fails with Python error:
* Check that [runtime.txt](file:///c:/Users/ADMIN/Desktop/Product%20Owner%20Project%202/MVP%20Design/runtime.txt) specifies `python-3.11.9`.
* Ensure [Procfile](file:///c:/Users/ADMIN/Desktop/Product%20Owner%20Project%202/MVP%20Design/Procfile) contains `web: python -u app.py`.

### 3. Groq API rate limit or fallback:
* If `GROQ_API_KEY` is not provided or runs out of credits, `app.py` automatically falls back to static high-converting copywriting templates without crashing or failing requests.
