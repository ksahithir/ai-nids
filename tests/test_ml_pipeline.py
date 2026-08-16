import os
import sys
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.preprocessing import (
    NIDSPreprocessor, NIDSLabelEncoder, load_preprocessor,
    CANONICAL_CLASSES, SEVERITY_MAPPING, CONSTANT_FEATURES
)
from ml.predict import get_predictor

def test_canonical_classes_and_severity():
    assert len(CANONICAL_CLASSES) == 15
    assert "Benign" in CANONICAL_CLASSES
    assert "DDoS" in CANONICAL_CLASSES
    assert "Heartbleed" in CANONICAL_CLASSES
    assert "Web Attack - SQL Injection" in CANONICAL_CLASSES
    
    # Check severity mapping
    assert SEVERITY_MAPPING["Heartbleed"] == "CRITICAL"
    assert SEVERITY_MAPPING["Bot"] == "CRITICAL"
    assert SEVERITY_MAPPING["DDoS"] == "HIGH"
    assert SEVERITY_MAPPING["PortScan"] == "LOW"
    assert SEVERITY_MAPPING["Benign"] == "LOW"

def test_label_encoder():
    encoder = NIDSLabelEncoder(CANONICAL_CLASSES)
    indices = encoder.transform(["Benign", "DDoS", "Heartbleed"])
    assert len(indices) == 3
    assert indices[0] == 0
    
    recovered = encoder.inverse_transform(indices)
    assert recovered == ["Benign", "DDoS", "Heartbleed"]

def test_preprocessor_pipeline():
    preproc_payload = load_preprocessor()
    preprocessor = preproc_payload["preprocessor"]
    selected_feats = preproc_payload["selected_features"]
    
    assert len(selected_feats) == 69  # 77 raw features - 8 constant features
    for c in CONSTANT_FEATURES:
        assert c not in selected_feats
        
    # Create dummy DataFrame
    dummy_df = pd.DataFrame([{f: 1.0 for f in preprocessor.input_features}])
    scaled = preprocessor.transform(dummy_df)
    assert scaled.shape == (1, 69)
    assert not np.isnan(scaled).any()
    assert not np.isinf(scaled).any()

def test_nids_predictor_single():
    predictor = get_predictor()
    dummy_flow = {f: 0.0 for f in predictor.selected_features}
    res = predictor.predict_single(dummy_flow)
    
    assert "prediction" in res
    assert "is_attack" in res
    assert "confidence" in res
    assert "severity" in res
    assert "probabilities" in res
    assert 0.0 <= res["confidence"] <= 1.0
    assert len(res["probabilities"]) == 15

def test_nids_predictor_batch():
    predictor = get_predictor()
    rows = [{f: np.random.rand() * 10 for f in predictor.selected_features} for _ in range(5)]
    df = pd.DataFrame(rows)
    records, summary = predictor.predict_batch(df)
    
    assert len(records) == 5
    assert summary["total_records"] == 5
    assert "attack_distribution" in summary
    assert "severity_distribution" in summary
