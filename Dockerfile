# Base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=app/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV MODEL_PATH=/app/models/best_model.pkl
ENV PIPELINE_PATH=/app/models/preprocessing_pipeline.pkl

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file to the container
COPY requirements.txt /app/

# Install dependencies and gunicorn
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Create necessary directories first
RUN mkdir -p /app/app/templates /app/app/static /app/logs /app/data /app/models

# Copy the application code and templates
COPY app/app.py /app/app/
COPY app/templates/ /app/app/templates/
COPY app/static/ /app/app/static/
COPY models/ /app/models/
COPY src/ /app/src/

# Expose the port that the Flask app will run on
EXPOSE 5000

# Command to run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app.app:app"]