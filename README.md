# AI-NIDS: AI-Powered Network Intrusion Detection System
### Smart India Hackathon (SIH 2026) — Problem Statement 40: Network Intrusion Detection

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB.svg?logo=react&logoColor=black)](https://reactjs.org)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.4+-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 1. Executive Summary

**AI-NIDS** is an end-to-end, production-grade Network Intrusion Detection System designed for **SIH 2026 Problem Statement 40**. It processes network flow telemetry, performs zero-leakage feature preprocessing, classifies attacks across **15 distinct output classes** with a high-performance **HistGradientBoosting** machine learning engine (**98.75% test accuracy, 91.32% macro F1-score** on unseen data), assesses multi-tier threat severity, triggers automated security alerts, persists events to an SQLite WAL database, and visualizes all intelligence in a dark-themed **Security Operations Center (SOC) dashboard**.

Every metric, confusion matrix, and prediction displayed in the system is derived from **actual machine learning inference and real dataset evaluation**—zero fabricated or hardcoded results.

```
Network Traffic Telemetry / CSV Upload
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI REST Backend                     │
├─────────────────────────────────────────────────────────────┤
│ 1. Schema & Feature Validation                              │
│ 2. Scikit-Learn Robust Preprocessing Pipeline               │
│ 3. HistGradientBoosting Multi-Class Inference               │
│ 4. Calibrated Probabilities & Confidence Scoring            │
│ 5. Rule-Based Threat Severity Engine (LOW to CRITICAL)      │
│ 6. Automated SOC Incident Alert Generator                   │
│ 7. SQLite WAL Database Logging & Audit                      │
└─────────────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│             React SOC Cybersecurity Dashboard               │
├─────────────────────────────────────────────────────────────┤
│ • Main SOC Dashboard & Threat Posture (NORMAL to CRITICAL)  │
│ • Dataset & Real-Time Flow Simulation Console               │
│ • Batch Traffic Analysis (CSV Upload, Validation, Export)   │
│ • Attack Intelligence & Vector Analytics                    │
│ • SOC Alert Center (Triage: OPEN -> INVESTIGATING -> DONE)  │
│ • ML Validation Audit (Confusion Matrix & Feature Ranking)  │
│ • System Architecture & 8 GB RAM Hardware Compliance        │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Authoritative Dataset Specifications

The system is trained and evaluated strictly on the complete **CICIDS2017** benchmark dataset:

- **Data Source:** 8 Parquet files located in project directory (`258.12 MB`).
- **Total Dataset Records:** `2,313,810` network flow records.
- **Features:** 78 columns (77 flow telemetry features + 1 `Label`).
- **Data Integrity:** **0 missing values** and **0 infinite values** across all 2.31M rows.
- **Zero-Variance Pruning:** 8 constant features (`Bwd PSH Flags`, `Bwd URG Flags`, `Fwd Avg Bytes/Bulk`, `Fwd Avg Packets/Bulk`, `Fwd Avg Bulk Rate`, `Bwd Avg Bytes/Bulk`, `Bwd Avg Packets/Bulk`, `Bwd Avg Bulk Rate`) provide zero mutual information and are pruned, leaving **69 active numeric flow features**.
- **Output Classes (15 Classes):**
  1. `Benign` (Normal traffic baseline)
  2. `DoS Hulk`
  3. `DDoS`
  4. `DoS GoldenEye`
  5. `FTP-Patator`
  6. `DoS slowloris`
  7. `DoS Slowhttptest`
  8. `SSH-Patator`
  9. `PortScan`
  10. `Web Attack - Brute Force`
  11. `Bot` (C2 communication)
  12. `Web Attack - XSS`
  13. `Infiltration` (Multi-stage APT)
  14. `Web Attack - SQL Injection`
  15. `Heartbleed` (OpenSSL TLS vulnerability)

---

## 3. Hardware Optimization (8 GB RAM Constraint)

The entire pipeline was engineered to operate on standard development machines with **8 GB RAM**:

1. **Row-Group Parquet Streaming:** `PyArrow` reads parquet files in row-group chunks without loading all 2.31M records into memory simultaneously.
2. **100% Rare Attack Preservation:** Ultra-rare classes (`Heartbleed`: 11, `SQL Injection`: 21, `Infiltration`: 36, `XSS`: 652, `Bot`: 1437) are 100% retained, while massive volumetric classes (`Benign`, `Hulk`, `DDoS`) are uniformly sampled to 20,000 records each.
3. **Reproducible Stratified Partitioning:**
   - **Train Split (70%):** 66,942 flows.
   - **Validation Split (15%):** 14,345 flows.
   - **Unseen Test Split (15%):** 14,345 flows.
4. **Zero Data Leakage:** Preprocessing (`RobustScaler` + feature selection) is fitted **strictly on the training split only**.
5. **Sequential Model Training:** Candidate models were trained sequentially with garbage collection, keeping peak memory under **1.5 GB RAM**.

---

## 4. Machine Learning Model Comparison & Results

Four classical machine learning models were trained and evaluated on the **completely unseen test split (14,345 flows)**:

| Model Candidate | Test Accuracy | Macro Precision | Macro Recall | Macro F1-Score | Weighted F1 | Selection |
|---|---|---|---|---|---|---|
| **HistGradientBoosting** | **98.75%** | **90.41%** | **94.02%** | **91.32%** | **98.79%** | **Selected Best Model** |
| **Decision Tree** | 98.71% | 90.17% | 90.10% | 90.13% | 98.73% | Candidate |
| **Random Forest (n=100)** | 98.46% | 88.16% | 88.12% | 88.14% | 98.50% | Candidate |
| **Logistic Regression** | 18.11% | 10.72% | 21.17% | 10.71% | 18.69% | Linear Baseline |

### Key Model Highlights
- **100% Recall** on critical zero-day / high-impact threats: `Heartbleed` (1.00 F1), `SQL Injection` (1.00 Recall).
- **99% Recall** on `Bot` (0.97 F1) and `PortScan` (0.98 F1).
- **99-100% Precision and Recall** across all major DoS and DDoS attack vectors.

---

## 5. Transparent Threat Severity Rating System

Each detected event is mapped to a standardized cybersecurity severity tier:

| Severity Level | Attack Types Included | Rationale & SOC Response |
|---|---|---|
| **CRITICAL** | `Heartbleed`, `Infiltration`, `Web Attack - SQL Injection`, `Bot` | Immediate host isolation, database credential reset, C2 domain sinkholing. |
| **HIGH** | `DDoS`, `DoS Hulk`, `Web Attack - XSS`, `Web Attack - Brute Force` | Rate limiting, IP blocking, WAF rule updates, admin credential lock. |
| **MEDIUM** | `DoS GoldenEye`, `DoS slowloris`, `DoS Slowhttptest`, `FTP-Patator`, `SSH-Patator` | Protocol throttling, automated fail2ban triggers, session timeouts. |
| **LOW** | `PortScan` | Firewall state inspection, probe telemetry logging. |
| **INFORMATIONAL / NONE** | `Benign` | Routine healthy traffic baseline; logged without alert creation. |

---

## 6. Project Architecture & File Structure

```
C:\Users\Sahithi\Desktop\ainids\
├── data/
│   ├── raw/
│   │   └── *.parquet (8 CICIDS2017 Parquet Files)
│   └── processed/
│       ├── train.parquet (66,942 records)
│       ├── val.parquet (14,345 records)
│       ├── test.parquet (14,345 records)
│       └── sample_traffic_test.csv (500 records test sample)
│
├── ml/
│   ├── __init__.py
│   ├── data_loader.py (Memory-efficient chunked parquet reader & stratified splitter)
│   ├── preprocessing.py (Zero-leakage Scikit-learn transformer & label encoder)
│   ├── train.py (Candidate model training & selection engine)
│   ├── evaluate.py (Unseen test set evaluation, confusion matrix & reports generator)
│   └── predict.py (Thread-safe inference service & severity classifier)
│
├── models/
│   ├── final_model.joblib (Trained HistGradientBoosting model)
│   ├── preprocessing_pipeline.joblib (Fitted preprocessor & label encoder)
│   └── model_metadata.json (Audited metrics, class schemas, top features)
│
├── reports/
│   ├── dataset_report.md (Deep inspection report of raw CICIDS2017 data)
│   ├── model_comparison.md (Performance comparison across 4 candidate models)
│   ├── classification_report.txt (Per-class precision, recall, F1, and support)
│   └── figures/
│       ├── confusion_matrix.png (15x15 Confusion Matrix plot)
│       └── feature_importance.png (Top 20 predictive network flow features)
│
├── backend/
│   ├── app/
│   │   ├── main.py (FastAPI app, lifespan DB initialization, CORS)
│   │   ├── api/
│   │   │   └── routes.py (REST endpoints: /health, /predict, /predict-batch, /alerts)
│   │   ├── database/
│   │   │   └── db.py (SQLite database, WAL mode, predictions & alerts tables)
│   │   ├── models/
│   │   │   └── schemas.py (Pydantic validation models)
│   │   └── services/
│   │       ├── nids_service.py (Business logic & alert generator)
│   │       └── simulation_service.py (Real flow simulation stream)
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx (Main state & tab coordinator)
│   │   ├── index.css (SOC dark cyber theme & responsive components)
│   │   ├── components/
│   │   │   ├── Header.jsx (Threat posture banner & model indicator)
│   │   │   └── Sidebar.jsx (7-tab SOC navigation)
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx (Main SOC KPIs, Recharts analytics, live alert feed)
│   │   │   ├── LiveMonitoring.jsx (Real-time flow simulation & feature inspector)
│   │   │   ├── TrafficAnalysis.jsx (CSV upload, batch ML inference, export)
│   │   │   ├── AttackAnalytics.jsx (14 attack signatures distribution & radar)
│   │   │   ├── AlertCenter.jsx (Incident triage queue with OPEN/INVESTIGATING/RESOLVED)
│   │   │   ├── ModelPerformance.jsx (Audited metrics, confusion matrix viewer)
│   │   │   └── SystemInfo.jsx (Architecture specs & 8 GB RAM compliance)
│   │   └── services/
│   │       └── api.js (Axios REST client)
│   ├── package.json
│   └── vite.config.js
│
├── tests/
│   ├── test_ml_pipeline.py (ML unit tests)
│   └── test_backend_api.py (FastAPI integration tests)
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 7. Installation & Quick Start Guide

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** (Node v24 and npm installed)

### Step 1: Install Python Dependencies
```bash
python -m pip install -r backend/requirements.txt
```

### Step 2: Run ML Pipeline (Pre-computed & Serialized)
The model and preprocessing pipeline are already trained and saved in `models/`. To reproduce the training from raw parquet files:
```bash
python ml/data_loader.py
python ml/train.py
python ml/evaluate.py
```

### Step 3: Run Automated Test Suite
Verify that all ML components, database operations, and API endpoints pass:
```bash
pytest tests/ -v
```

### Step 4: Launch Backend API Server
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
Backend Swagger API Documentation is available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Step 5: Launch Frontend React SOC Dashboard
In a new terminal:
```powershell
cd frontend
$env:PATH = "C:\Program Files\nodejs;" + $env:PATH
npm run dev
```
Open your browser at: **[http://localhost:5173](http://localhost:5173)**

---

## 8. SIH 2026 Demonstration Workflow

To demonstrate the system to hackathon evaluators / judges:

1. **Open AI-NIDS SOC Dashboard:** Navigate to [http://localhost:5173](http://localhost:5173). Observe the live threat posture, total analyzed flows, and attack distribution.
2. **Demonstrate Batch Traffic Analysis (CSV Upload):**
   - Click **Traffic Analysis (CSV)** in the sidebar.
   - Click **Download SIH Demo Test CSV** to obtain a verified network flow sample.
   - Click **Browse CSV File** and select the downloaded file.
   - Click **Execute AI-NIDS Analysis**.
   - Observe instantaneous multi-class attack detection, confidence scoring, severity distribution, and export capability.
3. **Demonstrate Live Network Simulation:**
   - Navigate to **Live Monitoring**.
   - Click **Start Stream**.
   - Watch flows streaming with real-time classification, confidence bars, and ground-truth verification.
   - Click any packet to open the **Feature Inspector** displaying top salient flow attributes and multi-class probability vectors.
4. **Demonstrate Incident Response in Alert Center:**
   - Navigate to **Alert Center**.
   - Filter by `CRITICAL` severity to review high-impact threats (e.g. `Heartbleed`, `Bot`, `Infiltration`).
   - Click **Investigate** to change an alert status from `OPEN` to `INVESTIGATING`.
   - Click **Resolve** to mark an incident as `RESOLVED`.
   - Note that the main dashboard threat posture automatically recalibrates based on active open alerts.
5. **Demonstrate Verified Model Audit:**
   - Navigate to **Model Performance**.
   - Review the candidate comparison table, per-class F1 metrics for all 15 classes, confusion matrix plot, and feature importance rankings.

---

## 9. API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Backend and ML engine health check |
| `GET` | `/api/model-info` | Audited model metrics, per-class scores, and feature list |
| `POST` | `/api/predict` | Single network flow inference and alert generation |
| `POST` | `/api/predict-batch` | Multipart CSV batch upload and analysis |
| `GET` | `/api/statistics` | Aggregated SOC statistics computed from SQLite DB |
| `GET` | `/api/alerts` | Query security alerts with severity and status filters |
| `GET` | `/api/alerts/{id}` | Retrieve specific alert details |
| `PATCH` | `/api/alerts/{id}/status` | Update alert triage status (`OPEN`, `INVESTIGATING`, `RESOLVED`) |
| `GET` | `/api/predictions` | Query historical prediction records |
| `GET` | `/api/simulation/sample` | Stream next real test network flow sample |
| `GET` | `/api/download-sample-csv` | Download verified CSV test dataset for live demo |
| `GET` | `/api/figures/{filename}` | Serve evaluation figures (`confusion_matrix.png`, etc.) |

---

## 10. Limitations & Future Scope

- **Packet Capture Extension:** The current deployment focuses on statistical network flow feature classification (CICFlowMeter schema). Live raw socket capture using `Scapy` or kernel-bypass DPDK drivers can be plugged into `backend/app/services/` in production environments with network tap access.
- **Distributed Database Migration:** The database abstraction layer in `backend/app/database/db.py` is architected for seamless migration to PostgreSQL or TimescaleDB for enterprise clustering.
