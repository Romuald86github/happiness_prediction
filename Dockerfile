FROM python:3.9-slim

ENV PYTHONPATH=/app:/app/src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODEL_PATH=/app/models/best_model.pkl \
    PIPELINE_PATH=/app/models/preprocessing_pipeline.pkl \
    DATA_PATH=/app/data/preprocessed_data.csv

    

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY streamlit_requirements.txt .
RUN pip install --no-cache-dir -r streamlit_requirements.txt

# Create directories first
RUN mkdir -p /app/logs /app/models /app/data


# Copy rest of the application
COPY . .

RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "streamlit_app/streamlit_app1.py", "--server.port=8501", "--server.address=0.0.0.0"]