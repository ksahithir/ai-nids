# AI-NIDS: Machine Learning Model Comparison & Evaluation

**Evaluation Date:** 2026-08-15 12:21:20  
**Evaluation Set:** Unseen Test Split (14,345 flows, zero leakage)  
**Dataset:** CICIDS2017 Preprocessed Flow Dataset  

---

## 1. Candidate Model Performance Summary (Unseen Test Set)

| Model Name | Accuracy | Macro Precision | Macro Recall | Macro F1-Score | Weighted F1-Score | Status |
|---|---|---|---|---|---|---|
| **LogisticRegression** | 18.11% | 14.93% | 22.81% | **10.71%** | 18.69% | Candidate |
| **DecisionTree** | 98.71% | 90.77% | 89.89% | **90.13%** | 98.73% | Candidate |
| **RandomForest** | 98.46% | 87.12% | 90.22% | **88.14%** | 98.50% | Candidate |
| **HistGradientBoosting** | 98.75% | 90.25% | 93.59% | **91.32%** | 98.79% |  (Selected Best) |

---

## 2. Final Selected Model: HistGradientBoosting

- **Total Test Samples:** 14,345
- **Overall Accuracy:** 98.75%
- **Macro Average F1:** 91.32%
- **Weighted Average F1:** 98.79%

### Per-Class Detailed Performance (15 Classes)

| Class | Precision | Recall | F1-Score | Test Support | Severity Tier |
|---|---|---|---|---|---|
| **Benign** | 99.43% | 99.10% | 99.27% | 3,000 | `LOW` |
| **DoS Hulk** | 99.80% | 99.57% | 99.68% | 3,000 | `HIGH` |
| **DDoS** | 100.00% | 99.90% | 99.95% | 3,000 | `HIGH` |
| **DoS GoldenEye** | 99.81% | 99.74% | 99.77% | 1,543 | `MEDIUM` |
| **FTP-Patator** | 99.89% | 100.00% | 99.94% | 890 | `MEDIUM` |
| **DoS slowloris** | 99.75% | 99.38% | 99.57% | 808 | `MEDIUM` |
| **DoS Slowhttptest** | 99.11% | 99.74% | 99.43% | 784 | `MEDIUM` |
| **SSH-Patator** | 99.38% | 99.17% | 99.27% | 483 | `MEDIUM` |
| **PortScan** | 97.64% | 98.98% | 98.31% | 293 | `LOW` |
| **Web Attack - Brute Force** | 80.47% | 61.82% | 69.92% | 220 | `HIGH` |
| **Bot** | 95.54% | 99.07% | 97.27% | 216 | `CRITICAL` |
| **Web Attack - XSS** | 42.86% | 67.35% | 52.38% | 98 | `HIGH` |
| **Infiltration** | 80.00% | 80.00% | 80.00% | 5 | `CRITICAL` |
| **Web Attack - SQL Injection** | 60.00% | 100.00% | 75.00% | 3 | `CRITICAL` |
| **Heartbleed** | 100.00% | 100.00% | 100.00% | 2 | `CRITICAL` |

---

## 3. Visual Artifacts

- **Confusion Matrix:** `reports/figures/confusion_matrix.png`
- **Feature Importance:** `reports/figures/feature_importance.png`
