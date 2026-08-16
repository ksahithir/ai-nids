import os
import sys
import io
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.main import app
from backend.app.database.db import init_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "model_loaded" in data
    assert data["classes_count"] == 15

def test_model_info_endpoint(client):
    response = client.get("/api/model-info")
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "HistGradientBoosting"
    assert data["total_classes"] == 15
    assert "metrics" in data
    assert data["metrics"]["accuracy"] > 0.90
    assert len(data["classes"]) == 15

def test_predict_single_flow_endpoint(client):
    flow_payload = {
        "features": {
            "Protocol": 6,
            "Flow Duration": 12000,
            "Total Fwd Packets": 10,
            "Total Backward Packets": 8,
            "Fwd Packets Length Total": 1024,
            "Bwd Packets Length Total": 2048
        }
    }
    response = client.post("/api/predict", json=flow_payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction_id" in data
    assert "prediction" in data
    assert "confidence" in data
    assert "severity" in data
    assert "probabilities" in data
    assert 0.0 <= data["confidence"] <= 1.0

def test_statistics_endpoint(client):
    response = client.get("/api/statistics")
    assert response.status_code == 200
    data = response.json()
    assert "total_traffic_analyzed" in data
    assert "attacks_detected" in data
    assert "security_threat_status" in data
    assert data["security_threat_status"] in ["NORMAL", "ELEVATED", "HIGH RISK", "CRITICAL"]

def test_alerts_endpoint_and_status_update(client):
    # Get alerts
    response = client.get("/api/alerts?limit=10")
    assert response.status_code == 200
    alerts = response.json()
    assert isinstance(alerts, list)
    
    if len(alerts) > 0:
        target_id = alerts[0]["id"]
        # Update status
        update_resp = client.patch(f"/api/alerts/{target_id}/status", json={"status": "INVESTIGATING"})
        assert update_resp.status_code == 200
        
        # Verify update
        get_single = client.get(f"/api/alerts/{target_id}")
        assert get_single.status_code == 200
        assert get_single.json()["status"] == "INVESTIGATING"

def test_simulation_sample_endpoint(client):
    response = client.get("/api/simulation/sample")
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "confidence" in data
    assert "severity" in data
    assert "actual_dataset_label" in data

def test_batch_predict_csv_upload(client):
    sample_csv_content = """Protocol,Flow Duration,Total Fwd Packets,Total Backward Packets,Fwd Packets Length Total,Bwd Packets Length Total
6,1000,2,2,100,200
17,500,1,1,50,50
6,50000,50,40,5000,4000
"""
    files = {
        "file": ("test_upload.csv", io.BytesIO(sample_csv_content.encode('utf-8')), "text/csv")
    }
    response = client.post("/api/predict-batch", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert data["summary"]["total_records"] == 3
    assert "attack_distribution" in data["summary"]
