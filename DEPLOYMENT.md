# AI-NIDS Deployment Guide: Firebase Hosting + Google Cloud Run

This guide details how to deploy the **AI-NIDS** system to **Google Cloud Run** (Backend API & ML Engine) and **Firebase Hosting** (Frontend React SOC Dashboard with global CDN & reverse proxy).

---

## 1. Architecture Overview

```
User Web Browser
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│              Firebase Hosting (Global CDN)                  │
├─────────────────────────────────────────────────────────────┤
│ • Serves React Frontend SPA (static assets from `dist/`)    │
│ • SPA Catch-all Rewrite: `**` -> `/index.html`              │
│ • API Reverse Proxy Rewrite: `/api/**` -> Cloud Run Service │
└─────────────────────────────────────────────────────────────┘
       │
       ▼ (Direct Internal SSL Routing)
┌─────────────────────────────────────────────────────────────┐
│                 Google Cloud Run Service                    │
│                     (`ainids-api`)                          │
├─────────────────────────────────────────────────────────────┤
│ • Containerized FastAPI Python 3.11 Runtime                 │
│ • Pre-trained HistGradientBoosting ML Model & Pipeline      │
│ • Multi-Class Threat Severity & Alert Engine                │
│ • SQLite Database (`ai_nids.db`)                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Prerequisites

1. **Google Cloud SDK (`gcloud` CLI):** [Install gcloud](https://cloud.google.com/sdk/docs/install)
2. **Firebase CLI:** Installed on demand via `npx -y firebase-tools@latest`
3. **Google Cloud Project:** An active GCP project with billing enabled.

---

## 3. Step-by-Step Deployment Instructions

### Step 1: Configure GCP Project & Enable Services
Run in your terminal:
```bash
# Login to Google Cloud
gcloud auth login

# Set your active GCP project ID
gcloud config set project YOUR_PROJECT_ID

# Enable required Google Cloud APIs
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  firebase.googleapis.com
```

---

### Step 2: Deploy Backend to Google Cloud Run

From the project root directory (`C:\Users\Sahithi\Desktop\ainids`):
```bash
gcloud run deploy ainids-api \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300
```
> [!NOTE]
> When prompted for repository creation or source build, select **Yes**. Cloud Build will package the container using the provided `Dockerfile` and deploy the service.

---

### Step 3: Configure Firebase Hosting Project & Region

1. Ensure the `serviceId` and `region` in `firebase.json` match your Cloud Run deployment (defaults to `serviceId: "ainids-api"` and `region: "us-central1"`):
```json
"rewrites": [
  {
    "source": "/api/**",
    "run": {
      "serviceId": "ainids-api",
      "region": "us-central1"
    }
  },
  {
    "source": "**",
    "destination": "/index.html"
  }
]
```

2. Link your Firebase project:
```bash
npx -y firebase-tools@latest use YOUR_PROJECT_ID
```

---

### Step 4: Build Frontend & Deploy to Firebase Hosting

```powershell
# 1. Build the production React frontend bundle
cd frontend
$env:PATH = "C:\Program Files\nodejs;" + $env:PATH
npm run build
cd ..

# 2. Deploy to Firebase Hosting
npx -y firebase-tools@latest deploy --only hosting
```

---

## 4. Local Emulation & Verification

You can test the Firebase Hosting configuration locally using the Firebase Emulator:

```bash
# Start Firebase Hosting emulator
npx -y firebase-tools@latest emulators:start --only hosting
```
Access the emulated site at: `http://localhost:5000`

---

## 5. Security & Production Checklist

- [x] Pre-trained models (`final_model.joblib`) bundled into container image.
- [x] Zero-leakage Scikit-learn preprocessing pipeline initialized at container startup.
- [x] Dynamic Cloud Run `$PORT` binding configured in `Dockerfile` and `main.py`.
- [x] Single-origin routing via Firebase Hosting rewrites (eliminates CORS configuration overhead).
- [x] Static assets cached with long TTL headers (`Cache-Control: max-age=31536000`).
- [x] `index.html` configured with `no-cache` for instant SPA updates.
