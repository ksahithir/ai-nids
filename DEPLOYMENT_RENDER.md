# AI-NIDS: Free Deployment Guide (Render)

This guide provides step-by-step instructions to deploy the **AI-NIDS** system (FastAPI ML Backend + React SOC Frontend Dashboard) entirely on **Render's Free Tier** with **zero credit/debit card requirements** and **no cloud billing**.

---

## 1. Architecture Overview

```
                      INTERNET
                         │
                         ▼
             ┌───────────────────────┐
             │  Render Static Site   │
             │   React / Vite SOC    │
             │      (Free Tier)      │
             └───────────┬───────────┘
                         │
                    `VITE_API_URL`
                         │
                         ▼
             ┌───────────────────────┐
             │   Render Web Service  │
             │   FastAPI ML Engine   │
             │   (Docker Runtime)    │
             └───────────┬───────────┘
                         │
                 ┌───────┴───────┐
                 │               │
                 ▼               ▼
        ┌────────────────┐ ┌───────────┐
        │ HistGradBoost  │ │  SQLite   │
        │ 15-Class Model │ │ Database  │
        └────────────────┘ └───────────┘
```

---

## 2. Prerequisites

1. A free GitHub account: [https://github.com](https://github.com)
2. A free Render account: [https://render.com](https://render.com) (Sign up using GitHub — **no credit card required**).

---

## 3. Step 1: Push Code to GitHub

Open PowerShell in the project directory (`C:\Users\Sahithi\Desktop\ainids`):

```powershell
# 1. Initialize git repository (if not already done)
git init

# 2. Add all project files (.gitignore automatically excludes raw 258MB parquet datasets, node_modules, and cache)
git add .

# 3. Create initial commit
git commit -m "feat: complete AI-NIDS standalone production system for Render"

# 4. Create a new repository on GitHub (e.g. named 'ainids') and push
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/ainids.git
git push -u origin main
```

> [!NOTE]
> The `.gitignore` is already configured to exclude the 258MB raw parquet dataset files while preserving the trained models (`models/final_model.joblib`), pipeline (`models/preprocessing_pipeline.joblib`), and test sample data (`data/processed/sample_traffic_test.csv`).

---

## 4. Step 2: Deploy Backend on Render (Web Service)

1. Log into your [Render Dashboard](https://dashboard.render.com).
2. Click **New +** > **Web Service**.
3. Connect your GitHub repository (`ainids`).
4. Configure the Web Service settings:
   - **Name:** `ainids-backend` (or your preferred name)
   - **Region:** Any (e.g., `Oregon (US West)` or `Frankfurt (EU)`)
   - **Branch:** `main`
   - **Root Directory:** *(leave blank — uses root)*
   - **Runtime:** `Docker`
   - **Dockerfile Path:** `./Dockerfile`
   - **Instance Type:** `Free` ($0/month)
5. Under **Advanced**:
   - **Health Check Path:** `/api/health`
6. Click **Create Web Service**.

> Render will build the Docker container, install dependencies, bundle the pre-trained ML model, and deploy the service. Once live, note your backend URL (e.g. `https://ainids-backend.onrender.com`).

---

## 5. Step 3: Deploy Frontend on Render (Static Site)

1. In the Render Dashboard, click **New +** > **Static Site**.
2. Connect the same GitHub repository (`ainids`).
3. Configure the Static Site settings:
   - **Name:** `ainids-frontend` (or your preferred name)
   - **Branch:** `main`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`
4. Under **Environment Variables**, add:
   - **Key:** `VITE_API_URL`
   - **Value:** `https://ainids-backend.onrender.com/api` *(replace with your actual backend URL from Step 2, appending `/api`)*
5. Under **Redirects / Rewrites**, add a rewrite rule for single-page application (SPA) routing:
   - **Type:** `Rewrite`
   - **Source:** `/*`
   - **Destination:** `/index.html`
6. Click **Create Static Site**.

---

## 6. Step 4: Verify the Deployed Application

1. **Verify Backend Health:**
   Open: `https://ainids-backend.onrender.com/api/health`
   - Should return: `{"status": "healthy", "model_loaded": "HistGradientBoosting", "classes_count": 15}`
2. **Verify Interactive API Documentation:**
   Open: `https://ainids-backend.onrender.com/docs`
3. **Verify SOC Dashboard:**
   Open: `https://ainids-frontend.onrender.com`
   - Main dashboard metrics should load automatically.
   - Go to **Traffic Analysis** > Click **Download Sample Traffic CSV** > Upload the CSV > Click **Execute AI-NIDS Analysis**.
   - Go to **Live Monitoring** > Click **Start Stream** to observe live flow inference.

---

## 7. Render Free Tier Notes & Limitations

| Characteristic | Behavior on Render Free Tier | Impact / Handling |
|---|---|---|
| **Cost & Billing** | 100% Free ($0) | **Zero credit/debit card required.** |
| **Inactivity Spin-Down** | Web services sleep after 15 minutes of inactivity | The first request after sleep takes ~30–50 seconds to spin up. Subsequent requests respond instantly. |
| **Filesystem Persistence** | Ephemeral container storage | SQLite database resets upon service redeploy/restart. On startup, `backend/app/main.py` automatically re-initializes and re-seeds baseline telemetry from `sample_traffic_test.csv`. |
| **Single Instance** | 1 active free container (512 MB RAM, 0.1 CPU) | SQLite runs in Single-Writer WAL mode, which is perfectly stable for single-instance web services. |
