import os
import sys
import joblib
import json
import numpy as np
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.preprocessing import load_preprocessor, CANONICAL_CLASSES, SEVERITY_MAPPING

DATA_DIR = r"C:\Users\Sahithi\Desktop\ainids"
MODELS_DIR = os.path.join(DATA_DIR, "models")

class NIDSPredictor:
    """
    Production-grade Network Intrusion Detection inference engine.
    Loads trained model, preprocessing pipeline, and model metadata.
    """
    _instance = None

    def __init__(self, models_dir=MODELS_DIR):
        self.models_dir = models_dir
        self.load_models()

    def load_models(self):
        # 1. Load Preprocessor
        preproc_path = os.path.join(self.models_dir, "preprocessing_pipeline.joblib")
        if not os.path.exists(preproc_path):
            raise FileNotFoundError(f"Preprocessor file not found at {preproc_path}")
        preproc_payload = load_preprocessor(preproc_path)
        self.preprocessor = preproc_payload["preprocessor"]
        self.label_encoder = preproc_payload["label_encoder"]
        self.selected_features = preproc_payload["selected_features"]
        self.classes = preproc_payload["classes"]
        self.severity_mapping = preproc_payload["severity_mapping"]

        # 2. Load Final Model
        model_path = os.path.join(self.models_dir, "final_model.joblib")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")
        model_payload = joblib.load(model_path)
        self.model_name = model_payload["model_name"]
        self.model = model_payload["model"]

        # 3. Load Metadata
        meta_path = os.path.join(self.models_dir, "model_metadata.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}

        print(f"[NIDSPredictor] Successfully initialized with model: {self.model_name}")

    def predict_single(self, flow_data: dict) -> dict:
        """
        Takes a dictionary of network flow features and returns detection results.
        """
        df_single = pd.DataFrame([flow_data])
        results, _ = self.predict_batch(df_single)
        return results[0]

    def predict_batch(self, df_input: pd.DataFrame) -> tuple[list[dict], dict]:
        """
        Takes a pandas DataFrame of network flows, applies preprocessing,
        performs inference, assigns severity tiers, and computes summary statistics.
        """
        if df_input.empty:
            return [], {
                "total_records": 0,
                "normal_records": 0,
                "attack_records": 0,
                "attack_distribution": {},
                "severity_distribution": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
                "avg_confidence": 0.0
            }

        # Drop label column if present in input
        df_clean = df_input.copy()
        for col in list(df_clean.columns):
            if col.lower() == 'label':
                df_clean.drop(columns=[col], inplace=True)

        # Preprocess features
        X_scaled = self.preprocessor.transform(df_clean)

        # Predict classes and probabilities
        pred_indices = self.model.predict(X_scaled)
        
        has_proba = hasattr(self.model, "predict_proba")
        if has_proba:
            probas = self.model.predict_proba(X_scaled)
        else:
            probas = None

        pred_labels = self.label_encoder.inverse_transform(pred_indices)
        now_iso = datetime.now().isoformat()

        records = []
        attack_dist = {}
        severity_dist = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        total_conf = 0.0
        attack_count = 0
        normal_count = 0

        for idx, label in enumerate(pred_labels):
            is_attack = (label != "Benign")
            if is_attack:
                attack_count += 1
                attack_dist[label] = attack_dist.get(label, 0) + 1
            else:
                normal_count += 1

            # Determine confidence
            if probas is not None:
                class_probs = {self.classes[i]: float(probas[idx][i]) for i in range(len(self.classes))}
                # Confidence is the max predicted probability
                confidence = float(np.max(probas[idx]))
            else:
                class_probs = {label: 1.0}
                confidence = 0.95

            total_conf += confidence
            severity = self.severity_mapping.get(label, "LOW")
            severity_dist[severity] = severity_dist.get(severity, 0) + 1

            # Top non-zero input features for explainability
            row_dict = df_clean.iloc[idx].to_dict()
            sorted_feats = sorted(
                [{"feature": k, "value": float(v) if pd.notnull(v) else 0.0} 
                 for k, v in row_dict.items() if k in self.selected_features],
                key=lambda x: abs(x["value"]),
                reverse=True
            )[:5]

            record = {
                "id": idx + 1,
                "timestamp": now_iso,
                "prediction": label,
                "is_attack": is_attack,
                "confidence": round(confidence, 4),
                "severity": severity,
                "probabilities": class_probs if probas is not None else {},
                "top_features": sorted_feats
            }
            records.append(record)

        total_records = len(records)
        avg_confidence = round(total_conf / total_records, 4) if total_records > 0 else 0.0

        summary = {
            "total_records": total_records,
            "normal_records": normal_count,
            "attack_records": attack_count,
            "attack_distribution": attack_dist,
            "severity_distribution": severity_dist,
            "avg_confidence": avg_confidence
        }

        return records, summary

# Singleton accessor
_predictor_instance = None

def get_predictor():
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = NIDSPredictor()
    return _predictor_instance

if __name__ == "__main__":
    predictor = get_predictor()
    # Test on a single dummy flow with 0s
    dummy_flow = {feat: 0.0 for feat in predictor.selected_features}
    res = predictor.predict_single(dummy_flow)
    print("Single Prediction Test Result:")
    print(json.dumps(res, indent=2))
