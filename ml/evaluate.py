import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
from datetime import datetime

from ml.preprocessing import load_preprocessor, CANONICAL_CLASSES, SEVERITY_MAPPING

DATA_DIR = r"C:\Users\Sahithi\Desktop\ainids"
PROCESSED_DIR = os.path.join(DATA_DIR, "data", "processed")
MODELS_DIR = os.path.join(DATA_DIR, "models")
REPORTS_DIR = os.path.join(DATA_DIR, "reports")
FIGURES_DIR = os.path.join(REPORTS_DIR, "figures")

def evaluate_on_unseen_test():
    print("=" * 70)
    print("AI-NIDS: FINAL EVALUATION ON UNSEEN TEST DATA")
    print("=" * 70)
    
    os.makedirs(FIGURES_DIR, exist_ok=True)
    
    # 1. Load Preprocessing Pipeline
    preproc_payload = load_preprocessor(os.path.join(MODELS_DIR, "preprocessing_pipeline.joblib"))
    preprocessor = preproc_payload["preprocessor"]
    label_encoder = preproc_payload["label_encoder"]
    selected_features = preproc_payload["selected_features"]
    
    # 2. Load Unseen Test Data
    test_path = os.path.join(PROCESSED_DIR, "test.parquet")
    print(f"[Evaluate] Loading UNSEEN test set from {test_path}...")
    test_df = pd.read_parquet(test_path)
    
    X_test_raw = test_df.drop(columns=['Label'])
    y_test_raw = test_df['Label']
    
    X_test = preprocessor.transform(X_test_raw)
    y_test = label_encoder.transform(y_test_raw)
    
    print(f"[Evaluate] Test Set Size: {len(X_test):,} flows, {len(selected_features)} features")
    
    # 3. Load Candidate Models
    candidate_names = ["LogisticRegression", "DecisionTree", "RandomForest", "HistGradientBoosting"]
    all_test_metrics = []
    
    for mname in candidate_names:
        c_path = os.path.join(MODELS_DIR, f"candidate_{mname}.joblib")
        if not os.path.exists(c_path):
            print(f"Warning: Candidate model {c_path} not found.")
            continue
        
        cand_model = joblib.load(c_path)
        y_pred = cand_model.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        prec_macro = precision_score(y_test, y_pred, average='macro', zero_division=0)
        rec_macro = recall_score(y_test, y_pred, average='macro', zero_division=0)
        f1_macro = f1_score(y_test, y_pred, average='macro', zero_division=0)
        f1_weighted = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        all_test_metrics.append({
            "model_name": mname,
            "accuracy": float(acc),
            "macro_precision": float(prec_macro),
            "macro_recall": float(rec_macro),
            "macro_f1": float(f1_macro),
            "weighted_f1": float(f1_weighted)
        })
        print(f"[{mname}] Unseen Test Acc: {acc:.4f} | Macro-F1: {f1_macro:.4f} | Weighted-F1: {f1_weighted:.4f}")

    # 4. Load Final Chosen Model
    final_payload = joblib.load(os.path.join(MODELS_DIR, "final_model.joblib"))
    final_model_name = final_payload["model_name"]
    final_model = final_payload["model"]
    
    print(f"\n[Evaluate] Selected Best Model: {final_model_name}")
    y_pred_final = final_model.predict(X_test)
    
    # Per-Class Metrics
    cls_report_dict = classification_report(
        y_test,
        y_pred_final,
        target_names=CANONICAL_CLASSES,
        output_dict=True,
        zero_division=0
    )
    cls_report_str = classification_report(
        y_test,
        y_pred_final,
        target_names=CANONICAL_CLASSES,
        zero_division=0
    )
    
    # Save text classification report
    with open(os.path.join(REPORTS_DIR, "classification_report.txt"), "w") as f:
        f.write(f"AI-NIDS FINAL MODEL EVALUATION REPORT\n")
        f.write(f"Model: {final_model_name}\n")
        f.write(f"Evaluation Time: {datetime.now().isoformat()}\n")
        f.write(f"Test Samples: {len(X_test):,}\n")
        f.write("=" * 70 + "\n\n")
        f.write(cls_report_str)
    print(f"[Evaluate] Saved classification report to reports/classification_report.txt")

    # 5. Confusion Matrix
    cm = confusion_matrix(y_test, y_pred_final, labels=list(range(len(CANONICAL_CLASSES))))
    
    # Plot Confusion Matrix
    plt.figure(figsize=(14, 11))
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=CANONICAL_CLASSES,
        yticklabels=CANONICAL_CLASSES
    )
    plt.title(f"Confusion Matrix: {final_model_name} on Unseen CICIDS2017 Test Set", fontsize=14, pad=15)
    plt.xlabel("Predicted Attack Class", fontsize=12)
    plt.ylabel("Actual Attack Class", fontsize=12)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.yticks(rotation=0, fontsize=9)
    plt.tight_layout()
    cm_path = os.path.join(FIGURES_DIR, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=200)
    plt.close()
    print(f"[Evaluate] Saved confusion matrix to {cm_path}")

    # 6. Feature Importance (using model feature_importances_ or RandomForest fallback)
    feat_importances = []
    if hasattr(final_model, "feature_importances_"):
        importances = final_model.feature_importances_
    else:
        # Load RandomForest candidate for tree-based feature importance
        rf_path = os.path.join(MODELS_DIR, "candidate_RandomForest.joblib")
        if os.path.exists(rf_path):
            rf_model = joblib.load(rf_path)
            importances = rf_model.feature_importances_
        else:
            importances = np.ones(len(selected_features)) / len(selected_features)

    indices = np.argsort(importances)[::-1]
    top_k = 20
    
    top_indices = indices[:top_k]
    top_names = [selected_features[i] for i in top_indices]
    top_scores = importances[top_indices]
    
    for idx in top_indices:
        feat_importances.append({
            "feature": selected_features[idx],
            "importance": float(importances[idx])
        })
        
    plt.figure(figsize=(12, 8))
    sns.barplot(x=top_scores, y=top_names, palette='viridis')
    plt.title(f"Top 20 Predictive Network Flow Features (Random Forest Ensemble)", fontsize=14, pad=15)
    plt.xlabel("Feature Importance (Gini)", fontsize=12)
    plt.ylabel("Network Flow Attribute", fontsize=12)
    plt.tight_layout()
    fi_path = os.path.join(FIGURES_DIR, "feature_importance.png")
    plt.savefig(fi_path, dpi=200)
    plt.close()
    print(f"[Evaluate] Saved feature importance plot to {fi_path}")

    # 7. Generate reports/model_comparison.md
    comp_md = f"""# AI-NIDS: Machine Learning Model Comparison & Evaluation

**Evaluation Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Evaluation Set:** Unseen Test Split ({len(X_test):,} flows, zero leakage)  
**Dataset:** CICIDS2017 Preprocessed Flow Dataset  

---

## 1. Candidate Model Performance Summary (Unseen Test Set)

| Model Name | Accuracy | Macro Precision | Macro Recall | Macro F1-Score | Weighted F1-Score | Status |
|---|---|---|---|---|---|---|
"""
    for m in all_test_metrics:
        is_best = " (Selected Best)" if m["model_name"] == final_model_name else ""
        comp_md += f"| **{m['model_name']}** | {m['accuracy']*100:.2f}% | {m['macro_precision']*100:.2f}% | {m['macro_recall']*100:.2f}% | **{m['macro_f1']*100:.2f}%** | {m['weighted_f1']*100:.2f}% | {is_best or 'Candidate'} |\n"

    comp_md += f"""
---

## 2. Final Selected Model: {final_model_name}

- **Total Test Samples:** {len(X_test):,}
- **Overall Accuracy:** {cls_report_dict['accuracy']*100:.2f}%
- **Macro Average F1:** {cls_report_dict['macro avg']['f1-score']*100:.2f}%
- **Weighted Average F1:** {cls_report_dict['weighted avg']['f1-score']*100:.2f}%

### Per-Class Detailed Performance (15 Classes)

| Class | Precision | Recall | F1-Score | Test Support | Severity Tier |
|---|---|---|---|---|---|
"""
    for cname in CANONICAL_CLASSES:
        if cname in cls_report_dict:
            cdata = cls_report_dict[cname]
            sev = SEVERITY_MAPPING.get(cname, "UNKNOWN")
            comp_md += f"| **{cname}** | {cdata['precision']*100:.2f}% | {cdata['recall']*100:.2f}% | {cdata['f1-score']*100:.2f}% | {int(cdata['support']):,} | `{sev}` |\n"

    comp_md += f"""
---

## 3. Visual Artifacts

- **Confusion Matrix:** `reports/figures/confusion_matrix.png`
- **Feature Importance:** `reports/figures/feature_importance.png`
"""
    with open(os.path.join(REPORTS_DIR, "model_comparison.md"), "w", encoding="utf-8") as f:
        f.write(comp_md)
    print(f"[Evaluate] Generated reports/model_comparison.md")

    # 8. Save Comprehensive model_metadata.json
    final_metrics = next((m for m in all_test_metrics if m["model_name"] == final_model_name), all_test_metrics[0])
    
    metadata = {
        "project_name": "AI-NIDS: AI-Powered Network Intrusion Detection System",
        "edition": "Enterprise Standalone Edition",
        "model_name": final_model_name,
        "model_type": str(type(final_model).__name__),
        "model_version": "1.0.0",
        "trained_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dataset_name": "CICIDS2017 Flow Dataset",
        "total_classes": len(CANONICAL_CLASSES),
        "classes": CANONICAL_CLASSES,
        "severity_mapping": SEVERITY_MAPPING,
        "total_features": len(selected_features),
        "features": selected_features,
        "metrics": {
            "accuracy": float(final_metrics["accuracy"]),
            "macro_precision": float(final_metrics["macro_precision"]),
            "macro_recall": float(final_metrics["macro_recall"]),
            "macro_f1": float(final_metrics["macro_f1"]),
            "weighted_f1": float(final_metrics["weighted_f1"])
        },
        "per_class_metrics": {
            cname: {
                "precision": float(cls_report_dict[cname]["precision"]),
                "recall": float(cls_report_dict[cname]["recall"]),
                "f1_score": float(cls_report_dict[cname]["f1-score"]),
                "support": int(cls_report_dict[cname]["support"]),
                "severity": SEVERITY_MAPPING.get(cname, "LOW")
            } for cname in CANONICAL_CLASSES if cname in cls_report_dict
        },
        "candidate_comparisons": all_test_metrics,
        "top_features": feat_importances[:15]
    }
    
    with open(os.path.join(MODELS_DIR, "model_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"[Evaluate] Saved metadata to models/model_metadata.json")

if __name__ == "__main__":
    evaluate_on_unseen_test()
