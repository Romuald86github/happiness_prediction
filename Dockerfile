# Base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app/app.py \
    FLASK_RUN_HOST=0.0.0.0 \
    MODEL_PATH=/app/models/best_model.pkl \
    PIPELINE_PATH=/app/models/preprocessing_pipeline.pkl \
    PYTHONPATH=/app:/app/src

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file to the container
COPY requirements.txt /app/

# Install dependencies and gunicorn
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Create necessary directories
RUN mkdir -p /app/logs /app/models

# Copy the project files maintaining the structure
COPY app /app/app
COPY src /app/src
COPY models /app/models
COPY config /app/config

# Create a startup script that ensures correct imports
RUN echo '#!/bin/bash\n\
cd /app\n\
python -c "\
import sys; \
sys.path.insert(0, \"/app\"); \
sys.path.insert(0, \"/app/src\"); \
from src.preprocessing_pipeline import PreprocessingPipeline; \
print(\"PreprocessingPipeline imported successfully\")" && \
exec gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 4 \
    --timeout 120 \
    --preload \
    --pythonpath /app:/app/src \
    "app.app:app"' > /app/start.sh && \
    chmod +x /app/start.sh

# Expose the port that the Flask app will run on
EXPOSE 5000

# Command to run the application
CMD ["/app/start.sh"]