# Build stage
FROM python:3.9-slim as builder

# Set work directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# Final stage
FROM python:3.9-slim

# Create non-root user
RUN useradd -m appuser && \
    mkdir -p /app /app/logs /app/data /app/models && \
    chown -R appuser:appuser /app

# Set work directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels and requirements
COPY --from=builder /wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir /wheels/*

# Copy application
COPY --chown=appuser:appuser . .

# Set environment variables
ENV PYTHONPATH=/app \
    FLASK_APP=app/app.py \
    FLASK_ENV=production \
    PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "60", "app.app:app"]