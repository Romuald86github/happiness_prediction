# Base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=app/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV MODEL_PATH=/app/models/best_model.pkl
ENV PIPELINE_PATH=/app/models/preprocessing_pipeline.pkl
ENV PYTHONPATH=/app

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file to the container
COPY requirements.txt /app/

# Install dependencies and gunicorn
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the project files maintaining the structure
COPY app /app/app
COPY src /app/src
COPY models /app/models
COPY config /app/config

# Create necessary directories
RUN mkdir -p /app/logs

# Create a startup script to ensure correct Python path
RUN echo '#!/bin/bash\n\
export PYTHONPATH=/app\n\
cd /app\n\
exec gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 4 \
    --timeout 120 \
    --preload \
    "app.app:app"' > /app/start.sh && \
    chmod +x /app/start.sh

# Expose the port that the Flask app will run on
EXPOSE 5000

# Command to run the application
CMD ["/app/start.sh"]