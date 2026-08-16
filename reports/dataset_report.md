# CICIDS2017 Comprehensive Dataset Inspection Report

**Project Title:** AI-NIDS: AI-Powered Network Intrusion Detection System  
**Competition / Event:** Smart India Hackathon (SIH 2026) — Problem Statement 40  
**Inspection Date:** 2026-08-15  
**Authoritative Dataset Path:** `C:\Users\Sahithi\Desktop\ainids`  

---

## 1. Executive Summary

A comprehensive, non-destructive inspection of the CICIDS2017 dataset located at `C:\Users\Sahithi\Desktop\ainids` was performed. The dataset consists of **8 Parquet files** representing network traffic captures across different attack scenarios and weekdays.

| Metric | Measured Value |
|---|---|
| **Total Parquet Files** | 8 files |
| **Total Disk Size** | 270,655,555 bytes (258.12 MB) |
| **Total Flow Records** | 2,313,810 records |
| **Total Columns per File** | 78 (77 Traffic Features + 1 Target Label) |
| **Schema Consistency** | 100% Identical Across All 8 Files |
| **Missing / Null Values** | 0 (0.00%) |
| **Infinite Values** | 0 (0.00%) |
| **Total Target Classes** | 15 Distinct Classes (1 Benign + 14 Malicious Attack Types) |
| **Constant (Zero-Variance) Columns** | 8 Columns |

---

## 2. Individual File Inventory & File-Level Distribution

All 8 Parquet files were inspected row-group by row-group without exceeding memory constraints:

| File Name | File Size (MB) | Total Rows | Columns | Attack Labels Present |
|---|---|---|---|---|
| `Benign-Monday-no-metadata.parquet` | 54.14 MB | 458,831 | 78 | Benign (100%) |
| `Botnet-Friday-no-metadata.parquet` | 18.94 MB | 176,038 | 78 | Benign, Bot |
| `Bruteforce-Tuesday-no-metadata.parquet` | 44.00 MB | 389,714 | 78 | Benign, FTP-Patator, SSH-Patator |
| `DDoS-Friday-no-metadata.parquet` | 24.13 MB | 221,264 | 78 | Benign, DDoS |
| `DoS-Wednesday-no-metadata.parquet` | 65.04 MB | 584,991 | 78 | Benign, DoS Hulk, DoS GoldenEye, DoS slowloris, DoS Slowhttptest, Heartbleed |
| `Infiltration-Thursday-no-metadata.parquet` | 22.07 MB | 207,630 | 78 | Benign, Infiltration |
| `Portscan-Friday-no-metadata.parquet` | 12.96 MB | 119,522 | 78 | Benign, PortScan |
| `WebAttacks-Thursday-no-metadata.parquet` | 16.84 MB | 155,820 | 78 | Benign, Web Attack - Brute Force, Web Attack - XSS, Web Attack - SQL Injection |

### Per-File Breakdown of Labels

1. **`Benign-Monday-no-metadata.parquet`** (458,831 rows)
   - `Benign`: 458,831 (100.00%)

2. **`Botnet-Friday-no-metadata.parquet`** (176,038 rows)
   - `Benign`: 174,601 (99.18%)
   - `Bot`: 1,437 (0.82%)

3. **`Bruteforce-Tuesday-no-metadata.parquet`** (389,714 rows)
   - `Benign`: 380,564 (97.65%)
   - `FTP-Patator`: 5,931 (1.52%)
   - `SSH-Patator`: 3,219 (0.83%)

4. **`DDoS-Friday-no-metadata.parquet`** (221,264 rows)
   - `DDoS`: 128,014 (57.86%)
   - `Benign`: 93,250 (42.14%)

5. **`DoS-Wednesday-no-metadata.parquet`** (584,991 rows)
   - `Benign`: 391,235 (66.88%)
   - `DoS Hulk`: 172,846 (29.55%)
   - `DoS GoldenEye`: 10,286 (1.76%)
   - `DoS slowloris`: 5,385 (0.92%)
   - `DoS Slowhttptest`: 5,228 (0.89%)
   - `Heartbleed`: 11 (0.002%)

6. **`Infiltration-Thursday-no-metadata.parquet`** (207,630 rows)
   - `Benign`: 207,594 (99.98%)
   - `Infiltration`: 36 (0.02%)

7. **`Portscan-Friday-no-metadata.parquet`** (119,522 rows)
   - `Benign`: 117,566 (98.36%)
   - `PortScan`: 1,956 (1.64%)

8. **`WebAttacks-Thursday-no-metadata.parquet`** (155,820 rows)
   - `Benign`: 153,677 (98.62%)
   - `Web Attack - Brute Force`: 1,470 (0.94%)
   - `Web Attack - XSS`: 652 (0.42%)
   - `Web Attack - SQL Injection`: 21 (0.01%)

---

## 3. Global Class Distribution & Imbalance Analysis

Across all 2,313,810 records, the dataset shows a realistic cybersecurity class distribution:

| Class Label | Exact Sample Count | Percentage of Dataset | Category / Nature |
|---|---|---|---|
| **Benign** | 1,977,318 | 85.457% | Normal Traffic |
| **DoS Hulk** | 172,846 | 7.470% | Volumetric Denial of Service |
| **DDoS** | 128,014 | 5.533% | Distributed Denial of Service |
| **DoS GoldenEye** | 10,286 | 0.445% | Application-layer DoS |
| **FTP-Patator** | 5,931 | 0.256% | Brute Force Authentication |
| **DoS slowloris** | 5,385 | 0.233% | Low-and-Slow DoS |
| **DoS Slowhttptest** | 5,228 | 0.226% | Slow HTTP DoS |
| **SSH-Patator** | 3,219 | 0.139% | Brute Force Authentication |
| **PortScan** | 1,956 | 0.085% | Reconnaissance / Scanning |
| **Web Attack - Brute Force** | 1,470 | 0.064% | Web Application Attack |
| **Bot** | 1,437 | 0.062% | Command & Control / Botnet |
| **Web Attack - XSS** | 652 | 0.028% | Cross-Site Scripting |
| **Infiltration** | 36 | 0.002% | Multi-stage APT Infiltration |
| **Web Attack - SQL Injection** | 21 | 0.001% | Database Injection Attack |
| **Heartbleed** | 11 | 0.0005% | SSL/TLS Information Leak Vulnerability |
| **Total** | **2,313,810** | **100.00%** | |

### Imbalance Observations:
- **Benign Traffic** constitutes ~85.5% of total flows, reflecting real-world network operational baselines.
- **Volumetric attacks** (`DoS Hulk`, `DDoS`) have large sample sizes (>100,000 flows).
- **Targeted and critical attacks** (`Heartbleed`: 11, `SQL Injection`: 21, `Infiltration`: 36, `XSS`: 652) represent extreme minority classes.
- **Sampling Strategy Requirement:** Pure random undersampling without stratification would completely eliminate `Heartbleed`, `SQL Injection`, and `Infiltration`. Therefore, stratified sampling that preserves 100% of ultra-rare minority attacks while selectively subsampling the massive Benign/DDoS/Hulk pools is strictly necessary.

---

## 4. Feature Space & Schema Analysis

The dataset contains **78 columns** in total: 77 input features + 1 target (`Label`).

### Data Types Present
- `int8` (13 columns): Protocol, TCP flags (`FIN`, `SYN`, `RST`, `PSH`, `ACK`, `URG`, `CWE`, `ECE`), Down/Up Ratio, Bulk statistics.
- `int16` (6 columns): Min/Max packet lengths (`Fwd/Bwd/Overall`).
- `int32` (28 columns): Duration, packet totals, byte totals, IAT values, header lengths, window sizes, active/idle time extremes.
- `float32` (28 columns): Mean/Std values for lengths, IATs, packet rates, active/idle means.
- `float64` (2 columns): `Flow Bytes/s`, `Flow Packets/s`.
- `category` (1 column): `Label`.

### Zero-Variance / Constant Features
Statistical analysis across all 2,313,810 records identified **8 constant features** where standard deviation is 0 (min == max == 0.0):
1. `Bwd PSH Flags` (all 0)
2. `Bwd URG Flags` (all 0)
3. `Fwd Avg Bytes/Bulk` (all 0)
4. `Fwd Avg Packets/Bulk` (all 0)
5. `Fwd Avg Bulk Rate` (all 0)
6. `Bwd Avg Bytes/Bulk` (all 0)
7. `Bwd Avg Packets/Bulk` (all 0)
8. `Bwd Avg Bulk Rate` (all 0)

**Action:** These 8 columns provide zero variance and zero mutual information. They are safely removed in the preprocessing pipeline, reducing feature space from 77 to 69 clean numerical features.

### Metadata / Identifier Leakage Check
- The files are named `*-no-metadata.parquet`.
- Identifier features such as `Flow ID`, `Source IP`, `Source Port`, `Destination IP`, `Destination Port`, and `Timestamp` have **already been removed**.
- This completely prevents IP-based and timestamp-based shortcut learning and data leakage. All remaining 69 features represent genuine statistical network flow attributes (IAT, packet lengths, TCP flags, window parameters, burst dynamics).

---

## 5. Threat Severity Mapping System

For the SIH AI-NIDS dashboard and security operations alert engine, attacks are categorized into transparent, rule-grounded severity tiers:

| Severity Level | Attack Classes Included | Rationale & Impact |
|---|---|---|
| **CRITICAL** | `Heartbleed`, `Infiltration`, `Web Attack - SQL Injection`, `Bot` | Direct system compromise, remote code execution, database exfiltration, active C2 botnet communication. |
| **HIGH** | `DDoS`, `DoS Hulk`, `Web Attack - XSS`, `Web Attack - Brute Force` | Service disruption on production servers, credential compromise, application hijacking. |
| **MEDIUM** | `DoS GoldenEye`, `DoS slowloris`, `DoS Slowhttptest`, `FTP-Patator`, `SSH-Patator` | Resource exhaustion, automated brute-force authentication attacks. |
| **LOW** | `PortScan` | Initial reconnaissance, host/port discovery probes without active exploitation. |
| **INFORMATIONAL / NONE** | `Benign` | Normal network communication; logged as healthy traffic without alert generation. |

---

## 6. Memory-Efficient Processing & ML Strategy (8 GB RAM Constraint)

### Strategy:
1. **Stratified Sampling for Model Training:**
   - Instead of attempting to fit 2.31M rows into a single in-memory training matrix (which would exceed 8 GB RAM during gradient boosting and random forest ensemble fitting):
   - We construct a balanced, stratified dataset:
     - Retain **100% of all rare attacks** (`Heartbleed`, `SQL Injection`, `Infiltration`, `XSS`, `Bot`, `SSH-Patator`, `PortScan`, `FTP-Patator`, `Slowhttptest`, `slowloris`, `GoldenEye`).
     - Sample up to 15,000–25,000 samples each for high-volume classes (`Benign`, `DoS Hulk`, `DDoS`).
     - Resulting training/validation set is ~100,000 to 150,000 carefully stratified samples.
2. **Train / Test Split & Leakage Prevention:**
   - 80% Train / 20% Unseen Test split with exact stratification across all 15 classes.
   - Preprocessing pipeline (`RobustScaler` / `StandardScaler` + constant feature remover) fitted **ONLY on training split**.
   - Test set evaluated independently with strict zero-leakage guarantees.
3. **Candidate Models:**
   - `LogisticRegression` (Baseline linear classifier)
   - `DecisionTreeClassifier` (Interpretable tree-based baseline)
   - `RandomForestClassifier` (Ensemble bagging, n_estimators=100, max_depth=20)
   - `HistGradientBoostingClassifier` (Fast, memory-efficient histogram-based boosting, ideal for 8 GB RAM)
4. **Evaluation Metrics:**
   - Multi-class Accuracy, Precision, Recall, Macro-F1, Weighted-F1, per-class metrics, confusion matrix, ROC-AUC where applicable.
5. **Persistence:**
   - Save the best performing model (`final_model.joblib`), the preprocessing pipeline (`preprocessing_pipeline.joblib`), and comprehensive metadata (`model_metadata.json`).

---

## 7. Next Steps

1. Implement `ml/data_loader.py` and `ml/preprocessing.py`.
2. Implement `ml/train.py` and execute model comparisons.
3. Generate evaluation artifacts (`reports/model_comparison.md`, `reports/figures/confusion_matrix.png`, `reports/figures/feature_importance.png`).
4. Build FastAPI backend (`backend/app/main.py`) with SQLite database (`ai_nids.db`).
5. Build React SOC Dashboard frontend.
6. Run complete end-to-end integration tests.
