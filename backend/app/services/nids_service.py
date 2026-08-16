import os
import sys
import io
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from ml.predict import get_predictor
from backend.app.database.db import (
    insert_prediction, insert_alert, insert_batch_predictions_and_alerts,
    get_all_predictions, get_all_alerts, update_alert_status, get_system_statistics
)

class NIDSService:
    def __init__(self):
        self.predictor = get_predictor()

    def predict_flow(self, features: dict, source: str = "api") -> dict:
        result = self.predictor.predict_single(features)
        
        # Save to database
        pred_payload = {
            "timestamp": result["timestamp"],
            "prediction": result["prediction"],
            "is_attack": result["is_attack"],
            "confidence": result["confidence"],
            "severity": result["severity"],
            "source": source,
            "top_features": result["top_features"],
            "probabilities": result["probabilities"]
        }
        pred_id = insert_prediction(pred_payload)
        
        alert_id = None
        alert_created = False
        
        if result["is_attack"]:
            alert_payload = {
                "timestamp": result["timestamp"],
                "attack_type": result["prediction"],
                "confidence": result["confidence"],
                "severity": result["severity"],
                "description": f"Security alert: Malicious {result['prediction']} pattern detected ({result['severity']} severity) with {result['confidence']*100:.1f}% confidence.",
                "status": "OPEN",
                "prediction_id": pred_id
            }
            alert_id = insert_alert(alert_payload)
            alert_created = True
            
        return {
            "prediction_id": pred_id,
            "timestamp": result["timestamp"],
            "prediction": result["prediction"],
            "is_attack": result["is_attack"],
            "confidence": result["confidence"],
            "severity": result["severity"],
            "probabilities": result["probabilities"],
            "top_features": result["top_features"],
            "alert_created": alert_created,
            "alert_id": alert_id
        }

    def process_csv_batch(self, file_bytes: bytes, filename: str) -> tuple[dict, list[dict]]:
        """
        Processes uploaded CSV in memory/chunks safely, validating structure and generating predictions.
        """
        try:
            df = pd.read_csv(io.BytesIO(file_bytes))
        except Exception as e:
            raise ValueError(f"Could not parse CSV file: {str(e)}")

        if df.empty:
            raise ValueError("The uploaded CSV is empty.")

        # Predict batch
        records, summary = self.predictor.predict_batch(df)

        # Batch insert into database
        insert_batch_predictions_and_alerts(records, source=f"batch_csv:{filename}")

        # Return summary and first 100 sample records for dashboard view
        return summary, records[:100]

    def get_model_metadata(self) -> dict:
        return self.predictor.metadata

_nids_service_instance = None

def get_nids_service():
    global _nids_service_instance
    if _nids_service_instance is None:
        _nids_service_instance = NIDSService()
    return _nids_service_instance
