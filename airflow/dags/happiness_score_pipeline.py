from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

# Add src directory to Python path
PROJECT_ROOT = Path(__file__).parents[2]
#SRC_DIR = os.path.join(PROJECT_ROOT, 'src')
#sys.path.append(str(SRC_DIR))
sys.path.append(str(PROJECT_ROOT))

from src.config import Config
from src.data_loader import DataLoader
from src.preprocessing_pipeline import PreprocessingPipeline
from src.model_trainer import ModelTrainer
from src.main import ExperimentManager, PredictionPipeline

# Initialize config
config = Config()

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['romualdtcheutchoua@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def load_data(**context):
    """Load and clean data"""
    loader = DataLoader()
    df, stats = loader.load_and_clean()
    
    # Push data to XCom for next task
    context['task_instance'].xcom_push(key='clean_data_shape', value=df.shape)
    return df.to_json()

def preprocess_data(**context):
    """Preprocess the cleaned data"""
    # Get data from previous task
    df_json = context['task_instance'].xcom_pull(task_ids='load_data')
    df = pd.read_json(df_json)
    
    # Preprocess data
    pipeline = PreprocessingPipeline()
    processed_df = pipeline.fit_transform(df)
    pipeline.save_pipeline()
    
    # Push preprocessed data shape to XCom
    context['task_instance'].xcom_push(
        key='preprocessed_data_shape', 
        value=processed_df.shape
    )
    return processed_df.to_json()

def train_models(**context):
    """Train and evaluate models"""
    # Get preprocessed data
    df_json = context['task_instance'].xcom_pull(task_ids='preprocess_data')
    processed_df = pd.read_json(df_json)
    
    # Prepare features and target
    X = processed_df.drop(columns=[config.TARGET_COLUMN])
    y = processed_df[config.TARGET_COLUMN]
    
    # Train models
    trainer = ModelTrainer()
    model_results = trainer.train_models(X, y)
    
    # Save best model
    trainer.save_best_model()
    
    # Push results to XCom
    context['task_instance'].xcom_push(
        key='model_results',
        value=str(model_results)  # Convert to string for XCom
    )
    return model_results

def save_experiment(**context):
    """Save experiment results"""
    # Get data and results from previous tasks
    model_results = eval(context['task_instance'].xcom_pull(
        task_ids='train_models',
        key='model_results'
    ))
    clean_data_shape = context['task_instance'].xcom_pull(
        task_ids='load_data',
        key='clean_data_shape'
    )
    preprocessed_data_shape = context['task_instance'].xcom_pull(
        task_ids='preprocess_data',
        key='preprocessed_data_shape'
    )
    
    # Create experiment manager and save results
    experiment = ExperimentManager()
    experiment_dir = experiment.create_experiment_dir()
    
    # Create preprocessing stats
    preprocessing_stats = {
        'initial_shape': clean_data_shape,
        'final_shape': preprocessed_data_shape,
        'removed_rows': clean_data_shape[0] - preprocessed_data_shape[0],
    }
    
    # Save results
    experiment.save_experiment_results(
        model_results=model_results,
        processed_df=pd.read_json(context['task_instance'].xcom_pull(task_ids='preprocess_data')),
        pipeline=joblib.load(config.MODEL_PIPELINE_PATH),
        preprocessing_stats=preprocessing_stats
    )
    
    return str(experiment_dir)

def test_prediction(**context):
    """Test the prediction pipeline"""
    experiment_dir = eval(context['task_instance'].xcom_pull(task_ids='save_experiment'))
    
    # Initialize prediction pipeline
    predictor = PredictionPipeline(experiment_dir)
    predictor.load_artifacts()
    
    # Load sample data
    loader = DataLoader()
    sample_data = loader.load_and_clean()[0].head(1)
    
    # Make and explain prediction
    prediction = predictor.predict(sample_data)
    explanation = predictor.explain_prediction(sample_data, prediction[0])
    
    # Log results
    results = {
        'prediction': float(prediction[0]),
        'actual': float(sample_data[config.TARGET_COLUMN].iloc[0]),
        'explanation': explanation
    }
    context['task_instance'].xcom_push(key='prediction_test', value=str(results))
    return results

# Create DAG
dag = DAG(
    'happiness_score_pipeline',
    default_args=default_args,
    description='ML pipeline for happiness score prediction',
    schedule_interval=timedelta(days=1),  # or '@daily', '@weekly', etc.
    catchup=False
)

# Define tasks
load_data_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    provide_context=True,
    dag=dag,
)

preprocess_task = PythonOperator(
    task_id='preprocess_data',
    python_callable=preprocess_data,
    provide_context=True,
    dag=dag,
)

train_models_task = PythonOperator(
    task_id='train_models',
    python_callable=train_models,
    provide_context=True,
    dag=dag,
)

save_experiment_task = PythonOperator(
    task_id='save_experiment',
    python_callable=save_experiment,
    provide_context=True,
    dag=dag,
)

test_prediction_task = PythonOperator(
    task_id='test_prediction',
    python_callable=test_prediction,
    provide_context=True,
    dag=dag,
)

# Set task dependencies
load_data_task >> preprocess_task >> train_models_task >> save_experiment_task >> test_prediction_task