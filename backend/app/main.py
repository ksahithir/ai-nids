import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.database.db import init_db, get_db_connection
from backend.app.services.nids_service import get_nids_service
from backend.app.api.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ai_nids")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize DB
    logger.info("Initializing SQLite database...")
    init_db()
    
    # 2. Warm up ML model
    logger.info("Loading ML model and preprocessing pipeline...")
    nids = get_nids_service()
    logger.info(f"Loaded model: {nids.predictor.model_name}")
    
    # 3. Seed baseline telemetry if database is empty
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM predictions")
    cnt = cursor.fetchone()["count"]
    conn.close()
    
    if cnt == 0:
        logger.info("Seeding initial baseline telemetry from test sample...")
        sample_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "processed", "sample_traffic_test.csv")
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as f:
                bytes_data = f.read()
            nids.process_csv_batch(bytes_data, "initial_baseline_seed.csv")
            logger.info("Baseline telemetry seeded successfully.")

    yield
    logger.info("AI-NIDS backend shutting down...")

app = FastAPI(
    title="AI-NIDS: AI-Powered Network Intrusion Detection System",
    description="AI-powered Network Traffic Analysis, Intrusion Detection, Attack Classification, and Security Alert System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for hackathon development/demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error at {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred.", "error": str(exc)}
    )

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", os.getenv("HOST", "0.0.0.0"))
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("backend.app.main:app", host=host, port=port, reload=False)
