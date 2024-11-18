# Base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app/app.py \
    FLASK_RUN_HOST=0.0.0.0 \
    MODEL_PATH=/app/models/best_model.pkl \
    PIPELINE_PATH=/app/models/preprocessing_pipeline.pkl \
    PYTHONPATH=/app

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Create all necessary directories
RUN mkdir -p \
    app/static/css \
    app/static/js \
    app/templates \
    config \
    data \
    experiments \
    logs \
    models \
    results \
    scripts \
    src

# Copy project files maintaining structure
COPY app/static/css/* app/static/css/
COPY app/static/js/* app/static/js/
COPY app/templates/* app/templates/
COPY app/app.py app/
COPY config/* config/
COPY data/*.csv data/
COPY models/*.pkl models/
COPY src/* src/
COPY scripts/* scripts/

# Create .gitignore to prevent __pycache__ issues
RUN echo "**/__pycache__" > .gitignore

# Set permissions
RUN chmod -R 755 /app \
    && chmod -R 777 /app/logs \
    && chmod -R 777 /app/models \
    && chmod -R 777 /app/data

# Verify critical imports and paths
RUN python3 -c "import sys; \
    from src.preprocessing_pipeline import PreprocessingPipeline; \
    from src.model_trainer import ModelTrainer; \
    from app.app import app; \
    from src.config import Config; \
    from src.helpers import setup_logging; \
    print('All modules verified successfully')"

# Expose port
EXPOSE 5000

# Start gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--preload", "app.app:app"]