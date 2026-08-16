import urllib.request
import json
import os
import pandas as pd

def test_endpoints():
    base_url = "http://127.0.0.1:8080/api"
    print(f"Testing container API endpoints at {base_url}...\n")
    
    # 1. Test GET /api/health
    health_url = f"{base_url}/health"
    req = urllib.request.Request(health_url)
    with urllib.request.urlopen(req, timeout=10) as resp:
        assert resp.status == 200
        health_data = json.loads(resp.read().decode('utf-8'))
        print("1. [GET /api/health] - SUCCESS")
        print(f"   Status: {health_data.get('status')}")
        print(f"   Model: {health_data.get('model_loaded')}")
        print(f"   Classes Count: {health_data.get('classes_count')}")
        assert health_data.get("status") == "healthy"
        assert health_data.get("model_loaded") == "HistGradientBoosting"
        assert health_data.get("classes_count") == 15

    # 2. Test GET /api/model-info
    model_info_url = f"{base_url}/model-info"
    req = urllib.request.Request(model_info_url)
    with urllib.request.urlopen(req, timeout=10) as resp:
        assert resp.status == 200
        info_data = json.loads(resp.read().decode('utf-8'))
        print("\n2. [GET /api/model-info] - SUCCESS")
        print(f"   Model Name: {info_data.get('model_name')}")
        print(f"   Accuracy: {info_data.get('metrics', {}).get('accuracy') * 100:.2f}%")
        print(f"   Macro F1: {info_data.get('metrics', {}).get('macro_f1') * 100:.2f}%")
        assert info_data.get("model_name") == "HistGradientBoosting"
        assert info_data.get("metrics", {}).get("accuracy") > 0.90

    # 3. Test POST /api/predict with real valid flow sample
    predict_url = f"{base_url}/predict"
    sample_csv_path = r"C:\Users\Sahithi\Desktop\ainids\data\processed\sample_traffic_test.csv"
    if os.path.exists(sample_csv_path):
        df_sample = pd.read_csv(sample_csv_path)
        row = df_sample.iloc[0].to_dict()
        label = row.pop("Label", None)
        features = {k: float(v) for k, v in row.items() if k != "Label"}
    else:
        features = {"Protocol": 6.0, "Flow Duration": 50000.0, "Total Fwd Packets": 10.0}

    payload = json.dumps({"features": features}).encode('utf-8')
    req = urllib.request.Request(predict_url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        assert resp.status == 200
        pred_data = json.loads(resp.read().decode('utf-8'))
        print("\n3. [POST /api/predict] - SUCCESS")
        print(f"   Prediction: {pred_data.get('prediction')}")
        print(f"   Confidence: {pred_data.get('confidence') * 100:.2f}%")
        print(f"   Severity: {pred_data.get('severity')}")
        print(f"   Is Attack: {pred_data.get('is_attack')}")
        print(f"   Alert Created: {pred_data.get('alert_created')}")
        assert "prediction" in pred_data
        assert "confidence" in pred_data
        assert "severity" in pred_data

    # 4. Verify Firebase Hosting rewrites
    firebase_json_path = r"C:\Users\Sahithi\Desktop\ainids\firebase.json"
    with open(firebase_json_path, 'r', encoding='utf-8') as f:
        fb_config = json.load(f)
    
    rewrites = fb_config.get("hosting", {}).get("rewrites", [])
    api_rewrite = next((r for r in rewrites if r.get("source") == "/api/**"), None)
    spa_rewrite = next((r for r in rewrites if r.get("source") == "**"), None)
    
    print("\n4. [Firebase Hosting Rewrite Verification] - SUCCESS")
    print(f"   Public Directory: {fb_config.get('hosting', {}).get('public')}")
    print(f"   API Rewrite to Cloud Run: {api_rewrite}")
    print(f"   SPA Fallback Rewrite: {spa_rewrite}")
    assert api_rewrite is not None
    assert api_rewrite.get("run", {}).get("serviceId") == "ainids-api"
    assert spa_rewrite.get("destination") == "/index.html"

    print("\n==================================================")
    print("ALL CONTAINER & API RUNTIME CHECKS PASSED")
    print("==================================================")

if __name__ == "__main__":
    test_endpoints()
