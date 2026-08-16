import os
import tempfile
import sqlite3
import json
from datetime import datetime

# Use /tmp on Vercel Serverless environment (read-only filesystem workaround)
if os.environ.get("VERCEL"):
    DB_PATH = os.path.join(tempfile.gettempdir(), "ai_nids.db")
else:
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "ai_nids.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    if not os.environ.get("VERCEL"):
        conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Table 1: Predictions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        prediction TEXT NOT NULL,
        is_attack INTEGER NOT NULL,
        confidence REAL NOT NULL,
        severity TEXT NOT NULL,
        source TEXT NOT NULL,
        top_features TEXT,
        probabilities TEXT
    );
    """)

    # Table 2: Alerts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        attack_type TEXT NOT NULL,
        confidence REAL NOT NULL,
        severity TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'OPEN',
        prediction_id INTEGER,
        FOREIGN KEY (prediction_id) REFERENCES predictions(id)
    );
    """)

    # Table 3: Model Metadata Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS model_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_name TEXT NOT NULL,
        model_version TEXT NOT NULL,
        dataset TEXT NOT NULL,
        trained_date TEXT NOT NULL,
        accuracy REAL NOT NULL,
        macro_f1 REAL NOT NULL,
        metrics_json TEXT
    );
    """)

    conn.commit()
    conn.close()
    print(f"[Database] SQLite schema initialized at {DB_PATH}")

def insert_prediction(pred_data: dict) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO predictions (timestamp, prediction, is_attack, confidence, severity, source, top_features, probabilities)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        pred_data.get("timestamp", datetime.now().isoformat()),
        pred_data.get("prediction"),
        1 if pred_data.get("is_attack") else 0,
        pred_data.get("confidence", 0.0),
        pred_data.get("severity", "LOW"),
        pred_data.get("source", "api"),
        json.dumps(pred_data.get("top_features", [])),
        json.dumps(pred_data.get("probabilities", {}))
    ))
    pred_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return pred_id

def insert_alert(alert_data: dict) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alerts (timestamp, attack_type, confidence, severity, description, status, prediction_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        alert_data.get("timestamp", datetime.now().isoformat()),
        alert_data.get("attack_type"),
        alert_data.get("confidence", 0.0),
        alert_data.get("severity", "HIGH"),
        alert_data.get("description", ""),
        alert_data.get("status", "OPEN"),
        alert_data.get("prediction_id")
    ))
    alert_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return alert_id

def insert_batch_predictions_and_alerts(records: list[dict], source: str = "batch_upload"):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for rec in records:
        ts = rec.get("timestamp", datetime.now().isoformat())
        is_att = 1 if rec.get("is_attack") else 0
        conf = rec.get("confidence", 0.0)
        sev = rec.get("severity", "LOW")
        pred = rec.get("prediction")
        
        cursor.execute("""
            INSERT INTO predictions (timestamp, prediction, is_attack, confidence, severity, source, top_features, probabilities)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ts, pred, is_att, conf, sev, source,
            json.dumps(rec.get("top_features", [])),
            json.dumps(rec.get("probabilities", {}))
        ))
        pred_id = cursor.lastrowid
        
        if is_att:
            desc = f"Detected malicious network pattern: {pred} with {conf*100:.1f}% confidence ({sev} severity)."
            cursor.execute("""
                INSERT INTO alerts (timestamp, attack_type, confidence, severity, description, status, prediction_id)
                VALUES (?, ?, ?, ?, ?, 'OPEN', ?)
            """, (ts, pred, conf, sev, desc, pred_id))
            
    conn.commit()
    conn.close()

def get_all_predictions(limit: int = 100, offset: int = 0, is_attack: bool = None) -> list[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM predictions"
    params = []
    if is_attack is not None:
        query += " WHERE is_attack = ?"
        params.append(1 if is_attack else 0)
    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "timestamp": r["timestamp"],
            "prediction": r["prediction"],
            "is_attack": bool(r["is_attack"]),
            "confidence": r["confidence"],
            "severity": r["severity"],
            "source": r["source"],
            "top_features": json.loads(r["top_features"]) if r["top_features"] else [],
            "probabilities": json.loads(r["probabilities"]) if r["probabilities"] else {}
        })
    return results

def get_all_alerts(status: str = None, severity: str = None, attack_type: str = None, limit: int = 100, offset: int = 0) -> list[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM alerts WHERE 1=1"
    params = []
    if status and status.upper() != 'ALL':
        query += " AND status = ?"
        params.append(status.upper())
    if severity and severity.upper() != 'ALL':
        query += " AND severity = ?"
        params.append(severity.upper())
    if attack_type and attack_type.upper() != 'ALL':
        query += " AND attack_type = ?"
        params.append(attack_type)
        
    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "timestamp": r["timestamp"],
            "attack_type": r["attack_type"],
            "confidence": r["confidence"],
            "severity": r["severity"],
            "description": r["description"],
            "status": r["status"],
            "prediction_id": r["prediction_id"]
        })
    return results

def update_alert_status(alert_id: int, new_status: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE alerts SET status = ? WHERE id = ?", (new_status.upper(), alert_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def get_system_statistics() -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM predictions")
    total_flows = cursor.fetchone()["total"]
    
    cursor.execute("SELECT COUNT(*) as attacks FROM predictions WHERE is_attack = 1")
    total_attacks = cursor.fetchone()["attacks"]
    total_benign = total_flows - total_attacks
    
    # Attack distribution
    cursor.execute("SELECT prediction, COUNT(*) as cnt FROM predictions WHERE is_attack = 1 GROUP BY prediction ORDER BY cnt DESC")
    attack_dist = {r["prediction"]: r["cnt"] for r in cursor.fetchall()}
    
    # Severity distribution
    cursor.execute("SELECT severity, COUNT(*) as cnt FROM predictions GROUP BY severity")
    sev_dist = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in cursor.fetchall():
        if r["severity"] in sev_dist:
            sev_dist[r["severity"]] = r["cnt"]
            
    # Alert counts by status
    cursor.execute("SELECT status, COUNT(*) as cnt FROM alerts GROUP BY status")
    alert_status_counts = {"OPEN": 0, "INVESTIGATING": 0, "RESOLVED": 0}
    for r in cursor.fetchall():
        if r["status"] in alert_status_counts:
            alert_status_counts[r["status"]] = r["cnt"]
            
    # Active alerts count
    open_alerts = alert_status_counts["OPEN"] + alert_status_counts["INVESTIGATING"]
    
    # Calculate System Security Threat Level based on active open alerts
    cursor.execute("SELECT COUNT(*) as critical_open FROM alerts WHERE severity = 'CRITICAL' AND status != 'RESOLVED'")
    crit_open = cursor.fetchone()["critical_open"]
    cursor.execute("SELECT COUNT(*) as high_open FROM alerts WHERE severity = 'HIGH' AND status != 'RESOLVED'")
    high_open = cursor.fetchone()["high_open"]
    
    if crit_open > 0:
        threat_status = "CRITICAL"
    elif high_open > 5:
        threat_status = "HIGH RISK"
    elif open_alerts > 0:
        threat_status = "ELEVATED"
    else:
        threat_status = "NORMAL"
        
    conn.close()
    
    return {
        "total_traffic_analyzed": total_flows,
        "normal_traffic": total_benign,
        "attacks_detected": total_attacks,
        "attack_rate": round((total_attacks / total_flows * 100), 2) if total_flows > 0 else 0.0,
        "attack_distribution": attack_dist,
        "severity_distribution": sev_dist,
        "alerts_by_status": alert_status_counts,
        "active_alerts_count": open_alerts,
        "security_threat_status": threat_status
    }
