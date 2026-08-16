import os
import io
import json
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Query, status
from fastapi.responses import FileResponse, StreamingResponse

from backend.app.models.schemas import (
    SingleFlowPredictRequest, PredictResponse, BatchPredictResponse,
    AlertResponse, AlertStatusUpdate, StatisticsResponse, ModelInfoResponse
)
from backend.app.services.nids_service import get_nids_service
from backend.app.services.simulation_service import get_simulation_service
from backend.app.database.db import (
    get_all_alerts, update_alert_status, get_all_predictions, get_system_statistics, get_db_connection
)

router = APIRouter(prefix="/api")

DATA_DIR = r"C:\Users\Sahithi\Desktop\ainids"
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "data", "processed", "sample_traffic_test.csv")
FIGURES_DIR = os.path.join(DATA_DIR, "reports", "figures")

@router.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint verifying backend and ML model readiness.
    """
    nids = get_nids_service()
    return {
        "status": "healthy",
        "service": "AI-NIDS Backend",
        "version": "1.0.0",
        "model_loaded": nids.predictor.model_name,
        "classes_count": len(nids.predictor.classes),
        "database": "connected",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/model-info", response_model=ModelInfoResponse, tags=["Model"])
async def get_model_information():
    """
    Returns verified model evaluation metrics, per-class performance, and feature importance.
    """
    nids = get_nids_service()
    metadata = nids.get_model_metadata()
    if not metadata:
        raise HTTPException(status_code=500, detail="Model metadata is unavailable.")
    return metadata

@router.post("/predict", response_model=PredictResponse, tags=["Inference"])
async def predict_single_flow(request: SingleFlowPredictRequest):
    """
    Analyzes a single network flow, classifies attack type, assigns threat severity,
    logs the event to the database, and automatically triggers an alert if malicious.
    """
    try:
        nids = get_nids_service()
        result = nids.predict_flow(request.features, source="single_api")
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Inference error: {str(e)}")

@router.post("/predict-batch", response_model=BatchPredictResponse, tags=["Inference"])
async def predict_batch_csv(file: UploadFile = File(...)):
    """
    Uploads a network traffic CSV, validates features, executes batch ML classification,
    records results, and returns analytical distribution statistics.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a .csv file.")
    
    # 50MB max file size check
    contents = await file.read()
    if len(contents) > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large. Maximum file size is 50MB.")
        
    try:
        nids = get_nids_service()
        summary, sample_records = nids.process_csv_batch(contents, file.filename)
        return {
            "summary": summary,
            "sample_records": sample_records,
            "message": f"Successfully processed {summary['total_records']:,} flow records from {file.filename}."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process CSV: {str(e)}")

@router.get("/statistics", response_model=StatisticsResponse, tags=["Analytics"])
async def get_dashboard_statistics():
    """
    Returns aggregated cybersecurity metrics computed directly from database records.
    """
    stats = get_system_statistics()
    return stats

@router.get("/alerts", response_model=List[AlertResponse], tags=["Alerts"])
async def list_alerts(
    status: Optional[str] = Query(None, description="Filter by status (OPEN, INVESTIGATING, RESOLVED, ALL)"),
    severity: Optional[str] = Query(None, description="Filter by severity (CRITICAL, HIGH, MEDIUM, LOW, ALL)"),
    attack_type: Optional[str] = Query(None, description="Filter by attack class"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    Lists security alerts with multi-dimensional filtering.
    """
    alerts = get_all_alerts(status=status, severity=severity, attack_type=attack_type, limit=limit, offset=offset)
    return alerts

@router.get("/alerts/{alert_id}", response_model=AlertResponse, tags=["Alerts"])
async def get_alert_by_id(alert_id: int):
    """
    Retrieves details for a specific alert ID.
    """
    alerts = get_all_alerts(limit=1, offset=0)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail=f"Alert with ID {alert_id} not found.")
        
    return {
        "id": row["id"],
        "timestamp": row["timestamp"],
        "attack_type": row["attack_type"],
        "confidence": row["confidence"],
        "severity": row["severity"],
        "description": row["description"],
        "status": row["status"],
        "prediction_id": row["prediction_id"]
    }

@router.patch("/alerts/{alert_id}/status", tags=["Alerts"])
async def change_alert_status(alert_id: int, body: AlertStatusUpdate):
    """
    Updates the triage status of an alert (OPEN -> INVESTIGATING -> RESOLVED).
    """
    allowed_statuses = ["OPEN", "INVESTIGATING", "RESOLVED"]
    new_status = body.status.upper()
    if new_status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {allowed_statuses}")
        
    success = update_alert_status(alert_id, new_status)
    if not success:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found.")
        
    return {"message": f"Alert {alert_id} status successfully updated to {new_status}."}

@router.get("/predictions", tags=["Predictions"])
async def list_predictions(
    is_attack: Optional[bool] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    Lists prediction records from database with pagination.
    """
    preds = get_all_predictions(limit=limit, offset=offset, is_attack=is_attack)
    return preds

@router.get("/simulation/sample", tags=["Simulation"])
async def get_simulation_flow():
    """
    Retrieves a real flow sample from the test pool, executes ML detection,
    logs the event, and returns the telemetry packet for live SOC visualization.
    """
    sim = get_simulation_service()
    flow_obj = sim.get_sample_flow()
    if not flow_obj:
        raise HTTPException(status_code=500, detail="No simulation samples available.")
        
    nids = get_nids_service()
    result = nids.predict_flow(flow_obj["features"], source="live_simulation")
    result["actual_dataset_label"] = flow_obj.get("actual_label", "Unknown")
    return result

@router.get("/download-sample-csv", tags=["Data"])
async def download_sample_csv():
    """
    Provides a downloadable CSV with authentic test network flows for live verification and testing.
    """
    if not os.path.exists(SAMPLE_CSV_PATH):
        raise HTTPException(status_code=404, detail="Sample CSV not found.")
    return FileResponse(
        SAMPLE_CSV_PATH,
        media_type="text/csv",
        filename="sample_network_traffic.csv"
    )

@router.get("/figures/{filename}", tags=["Reports"])
async def get_report_figure(filename: str):
    """
    Serves evaluation figures (confusion_matrix.png, feature_importance.png).
    """
    fig_path = os.path.join(FIGURES_DIR, filename)
    if not os.path.exists(fig_path):
        raise HTTPException(status_code=404, detail="Figure not found.")
    return FileResponse(fig_path, media_type="image/png")
