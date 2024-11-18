FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/models

# Copy the application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app \
    FLASK_APP=app/app.py \
    FLASK_ENV=production \
    PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "-m", "gunicorn", "app.app:app", "--bind", "0.0.0.0:5000", "--workers", "4", "--log-level", "debug"]