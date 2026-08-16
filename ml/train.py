import os
import sys
import time
import gc
import json
import joblib
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from ml.preprocessing import NIDSPreprocessor, NIDSLabelEncoder, save_preprocessor, CANONICAL_CLASSES

DATA_DIR = r"C:\Users\Sahithi\Desktop\ainids"
PROCESSED_DIR = os.path.join(DATA_DIR, "data", "processed")
MODELS_DIR = os.path.join(DATA_DIR, "models")
REPORTS_DIR = os.path.join(DATA_DIR, "reports")

def train_and_compare_models():
    print("=" * 70)
    print("AI-NIDS: MODEL TRAINING & VALIDATION PIPELINE")
    print("=" * 70)
    
    # 1. Load Train and Validation Splits
    train_path = os.path.join(PROCESSED_DIR, "train.parquet")
    val_path = os.path.join(PROCESSED_DIR, "val.parquet")
    
    print(f"[Train] Loading train data from {train_path}...")
    train_df = pd.read_parquet(train_path)
    print(f"[Train] Loading val data from {val_path}...")
    val_df = pd.read_parquet(val_path)
    
    X_train_raw = train_df.drop(columns=['Label'])
    y_train_raw = train_df['Label']
    
    X_val_raw = val_df.drop(columns=['Label'])
    y_val_raw = val_df['Label']
    
    print(f"[Train] Training Samples: {len(X_train_raw):,}")
    print(f"[Train] Validation Samples: {len(X_val_raw):,}")
    
    # 2. Fit Preprocessor ONLY on Training Data (Zero Leakage)
    print("\n[Train] Fitting NIDSPreprocessor on training data...")
    preprocessor = NIDSPreprocessor()
    preprocessor.fit(X_train_raw)
    
    label_encoder = NIDSLabelEncoder(classes=CANONICAL_CLASSES)
    
    # Transform train and val
    X_train = preprocessor.transform(X_train_raw)
    y_train = label_encoder.transform(y_train_raw)
    
    X_val = preprocessor.transform(X_val_raw)
    y_val = label_encoder.transform(y_val_raw)
    
    print(f"[Train] Selected Features Count: {len(preprocessor.selected_features)}")
    print(f"[Train] Features: {preprocessor.selected_features[:5]} ... (total {len(preprocessor.selected_features)})")
    
    # Save fitted preprocessor immediately
    save_preprocessor(preprocessor, label_encoder, os.path.join(MODELS_DIR, "preprocessing_pipeline.joblib"))
    
    # 3. Define Candidate Models
    candidate_models = {
        "LogisticRegression": LogisticRegression(
            max_iter=300,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        ),
        "DecisionTree": DecisionTreeClassifier(
            max_depth=20,
            random_state=42,
            class_weight='balanced'
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        ),
        "HistGradientBoosting": HistGradientBoostingClassifier(
            max_iter=100,
            random_state=42,
            class_weight='balanced'
        )
    }
    
    comparison_results = []
    trained_models = {}
    
    # 4. Train each candidate sequentially (Memory Safe for 8GB RAM)
    for model_name, model in candidate_models.items():
        print(f"\n--- Training {model_name} ---")
        t_start = time.time()
        
        model.fit(X_train, y_train)
        train_time = round(time.time() - t_start, 2)
        
        # Predict on validation split
        t_val_start = time.time()
        y_val_pred = model.predict(X_val)
        val_time = round(time.time() - t_val_start, 4)
        
        # Calculate validation metrics
        acc = accuracy_score(y_val, y_val_pred)
        prec_macro = precision_score(y_val, y_val_pred, average='macro', zero_division=0)
        rec_macro = recall_score(y_val, y_val_pred, average='macro', zero_division=0)
        f1_macro = f1_score(y_val, y_val_pred, average='macro', zero_division=0)
        f1_weighted = f1_score(y_val, y_val_pred, average='weighted', zero_division=0)
        
        print(f"[{model_name}] Fit Time: {train_time}s | Val Time: {val_time}s")
        print(f"[{model_name}] Val Accuracy:    {acc:.4f}")
        print(f"[{model_name}] Val Macro-F1:    {f1_macro:.4f}")
        print(f"[{model_name}] Val Weighted-F1: {f1_weighted:.4f}")
        print(f"[{model_name}] Val Macro Recall:{rec_macro:.4f}")
        
        result_entry = {
            "model_name": model_name,
            "train_time_sec": train_time,
            "val_time_sec": val_time,
            "accuracy": float(acc),
            "macro_precision": float(prec_macro),
            "macro_recall": float(rec_macro),
            "macro_f1": float(f1_macro),
            "weighted_f1": float(f1_weighted)
        }
        comparison_results.append(result_entry)
        trained_models[model_name] = model
        
        # Save individual candidate model
        cand_path = os.path.join(MODELS_DIR, f"candidate_{model_name}.joblib")
        joblib.dump(model, cand_path)
        
        gc.collect()

    # 5. Model Selection based on Macro-F1 (prioritizes balanced detection across rare and common attacks)
    best_candidate = max(comparison_results, key=lambda x: x["macro_f1"])
    best_model_name = best_candidate["model_name"]
    best_model = trained_models[best_model_name]
    
    print("\n" + "=" * 70)
    print(f"BEST MODEL SELECTED: {best_model_name}")
    print(f"Macro-F1: {best_candidate['macro_f1']:.4f} | Accuracy: {best_candidate['accuracy']:.4f}")
    print("=" * 70)
    
    # Save best model to final_model.joblib
    final_model_path = os.path.join(MODELS_DIR, "final_model.joblib")
    joblib.dump({
        "model_name": best_model_name,
        "model": best_model,
        "classes": CANONICAL_CLASSES,
        "selected_features": preprocessor.selected_features
    }, final_model_path)
    print(f"[Train] Saved final model to {final_model_path}")
    
    # Save validation comparison summary
    with open(os.path.join(REPORTS_DIR, "val_model_comparison.json"), "w") as f:
        json.dump(comparison_results, f, indent=2)
        
    return best_model_name, comparison_results

if __name__ == "__main__":
    train_and_compare_models()
