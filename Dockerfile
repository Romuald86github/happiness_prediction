FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=/app/app/app.py \
    FLASK_RUN_HOST=0.0.0.0 \
    MODEL_PATH=/app/models/best_model.pkl \
    PIPELINE_PATH=/app/models/preprocessing_pipeline.pkl \
    PYTHONPATH=/app/src

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r appuser && useradd -r -g appuser appuser

RUN mkdir -p /app/logs /app/models /app/data \
    && chown -R appuser:appuser /app

COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy src directory first and verify imports
COPY --chown=appuser:appuser src /app/src/
RUN python3 -c "from preprocessing_pipeline import PreprocessingPipeline; print('Module imports verified')"

# Copy remaining files
COPY --chown=appuser:appuser . .

VOLUME ["/app/models", "/app/data", "/app/logs"]

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--preload", "app.app:app"]