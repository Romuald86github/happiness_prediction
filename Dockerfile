# Base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=/app/app/app.py \
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

# Copy the project files
COPY . /app/

# Make sure the PreprocessingPipeline is in the correct state
RUN python3 -c "import sys; sys.path.insert(0, '/app'); from src.preprocessing_pipeline import PreprocessingPipeline; print('Module imports verified')"

# Expose the port that the Flask app will run on
EXPOSE 5000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--preload", "--pythonpath", "/app:/app/src", "app.app:app"]