FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set up Python path for src directory
ENV PYTHONPATH=/app/src

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create project structure
RUN mkdir -p /app/src /app/app /app/models /app/logs /app/data

# Copy files maintaining directory structure
COPY src/ /app/src/
COPY app/ /app/app/
COPY models/ /app/models/

# Set environment variables
ENV FLASK_APP=/app/app/app.py \
    FLASK_ENV=production \
    PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--log-level", "debug", "app.app:app"]