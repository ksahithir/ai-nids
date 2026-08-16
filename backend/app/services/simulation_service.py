import os
import random
import pandas as pd
from datetime import datetime

DATA_DIR = r"C:\Users\Sahithi\Desktop\ainids"
SAMPLE_CSV = os.path.join(DATA_DIR, "data", "processed", "sample_traffic_test.csv")
TEST_PARQUET = os.path.join(DATA_DIR, "data", "processed", "test.parquet")

class SimulationService:
    def __init__(self):
        self.samples_df = None
        self.load_samples()

    def load_samples(self):
        if os.path.exists(SAMPLE_CSV):
            self.samples_df = pd.read_csv(SAMPLE_CSV)
        elif os.path.exists(TEST_PARQUET):
            self.samples_df = pd.read_parquet(TEST_PARQUET).sample(n=500, random_state=42)
        else:
            self.samples_df = pd.DataFrame()

    def get_sample_flow(self) -> dict:
        if self.samples_df is None or self.samples_df.empty:
            self.load_samples()
            
        if self.samples_df.empty:
            return {}
            
        row = self.samples_df.sample(n=1).iloc[0].to_dict()
        actual_label = row.pop("Label", "Unknown") if "Label" in row else row.pop("label", "Unknown")
        
        # Convert numeric values
        features = {k: float(v) if pd.notnull(v) else 0.0 for k, v in row.items()}
        return {
            "features": features,
            "actual_label": actual_label
        }

_sim_service = None

def get_simulation_service():
    global _sim_service
    if _sim_service is None:
        _sim_service = SimulationService()
    return _sim_service
