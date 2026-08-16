FROM python:3.11-slim

# Set environment variables for container runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=10000 \
    HOST=0.0.0.0

WORKDIR /app

# Install minimal build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend, ML modules, trained models, reports, and test sample data
COPY backend/ /app/backend/
COPY ml/ /app/ml/
COPY models/ /app/models/
COPY reports/ /app/reports/
COPY data/processed/sample_traffic_test.csv /app/data/processed/sample_traffic_test.csv

# Expose default Render port
EXPOSE 10000

# Launch Uvicorn dynamically binding to $PORT injected by Render (or fallback to 10000)
CMD exec uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-10000} --workers 1
