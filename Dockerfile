# Use Python 3.9 slim base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=/app/app/app.py \
    FLASK_RUN_HOST=0.0.0.0 \
    MODEL_PATH=/app/models/best_model.pkl \
    PIPELINE_PATH=/app/models/preprocessing_pipeline.pkl

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create necessary directories and set permissions
RUN mkdir -p /app/logs /app/models /app/data \
    && chown -R appuser:appuser /app

# Copy requirements first to leverage Docker cache
COPY --chown=appuser:appuser requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy project files
COPY --chown=appuser:appuser . .

# Verify directory structure and permissions
RUN ls -la /app/src && \
    python3 -c "import sys; sys.path.append('/app'); from src.preprocessing_pipeline import PreprocessingPipeline; print('Module imports verified')"

# Create volumes for persistent data
VOLUME ["/app/models", "/app/data", "/app/logs"]

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start gunicorn server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--preload", "app.app:app"]