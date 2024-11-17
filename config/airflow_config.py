import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parents[1]
DAGS_DIR = os.path.join(PROJECT_ROOT, 'airflow', 'dags')
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')

# Airflow configuration
AIRFLOW_CONFIG = {
    'dags_folder': DAGS_DIR,
    'plugins_folder': os.path.join(PROJECT_ROOT, 'airflow', 'plugins'),
    'sql_alchemy_conn': 'sqlite:////' + os.path.join(PROJECT_ROOT, 'airflow', 'airflow.db'),
    'executor': 'LocalExecutor',
    'load_examples': False,
}

# ML Pipeline configuration
ML_PIPELINE_CONFIG = {
    'schedule_interval': '@daily',  # or '@weekly', '@monthly', etc.
    'email_on_failure': True,
    'email': ['your-email@example.com'],
    'retries': 1,
    'retry_delay': 5,  # minutes
}