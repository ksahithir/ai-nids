from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class SingleFlowPredictRequest(BaseModel):
    features: Dict[str, float] = Field(..., description="Map of network flow feature names to their numeric values")

class TopFeatureItem(BaseModel):
    feature: str
    value: float

class PredictResponse(BaseModel):
    prediction_id: int
    timestamp: str
    prediction: str
    is_attack: bool
    confidence: float
    severity: str
    probabilities: Dict[str, float]
    top_features: List[TopFeatureItem]
    alert_created: bool
    alert_id: Optional[int] = None

class BatchPredictSummary(BaseModel):
    total_records: int
    normal_records: int
    attack_records: int
    attack_distribution: Dict[str, int]
    severity_distribution: Dict[str, int]
    avg_confidence: float

class BatchPredictResponse(BaseModel):
    summary: BatchPredictSummary
    sample_records: List[Dict[str, Any]]
    message: str

class AlertResponse(BaseModel):
    id: int
    timestamp: str
    attack_type: str
    confidence: float
    severity: str
    description: str
    status: str
    prediction_id: Optional[int] = None

class AlertStatusUpdate(BaseModel):
    status: str = Field(..., description="Status must be OPEN, INVESTIGATING, or RESOLVED")

class StatisticsResponse(BaseModel):
    total_traffic_analyzed: int
    normal_traffic: int
    attacks_detected: int
    attack_rate: float
    attack_distribution: Dict[str, int]
    severity_distribution: Dict[str, int]
    alerts_by_status: Dict[str, int]
    active_alerts_count: int
    security_threat_status: str

class ModelMetrics(BaseModel):
    accuracy: float
    macro_precision: float
    macro_recall: float
    macro_f1: float
    weighted_f1: float

class PerClassMetric(BaseModel):
    precision: float
    recall: float
    f1_score: float
    support: int
    severity: str

class ModelInfoResponse(BaseModel):
    project_name: str
    edition: Optional[str] = "Enterprise Standalone Edition"
    model_name: str
    model_type: str
    model_version: str
    trained_date: str
    dataset_name: str
    total_classes: int
    classes: List[str]
    total_features: int
    features: List[str]
    metrics: ModelMetrics
    per_class_metrics: Dict[str, PerClassMetric]
    top_features: List[Dict[str, Any]]
