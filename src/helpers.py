# helpers.py

import os
import logging
import numpy as np
import pandas as pd
from scipy import stats
import joblib
from datetime import datetime
from config import Config

def setup_logging():
    """
    Set up logging configuration
    Returns: logger instance
    """
    config = Config()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create handlers
    file_handler = logging.FileHandler(config.LOG_FILE)
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Create logger
    logger = logging.getLogger('happiness_score')
    logger.setLevel(logging.INFO)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def calculate_statistics(df):
    """
    Calculate comprehensive statistics for the dataset
    
    Args:
        df (pd.DataFrame): Input dataframe
    
    Returns:
        dict: Dictionary containing various statistics
    """
    stats_dict = {
        'basic_stats': df.describe(),
        'missing_values': df.isnull().sum(),
        'duplicates': len(df) - len(df.drop_duplicates()),
        'unique_values': df.nunique(),
        'data_types': df.dtypes,
        'skewness': calculate_skewness(df),
        'correlation': df.corr() if df.select_dtypes(include=[np.number]).shape[1] > 1 else None
    }
    return stats_dict

def calculate_skewness(df):
    """
    Calculate skewness for numeric columns
    
    Args:
        df (pd.DataFrame): Input dataframe
    
    Returns:
        pd.Series: Skewness values for numeric columns
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    skewness = pd.Series({
        col: stats.skew(df[col].dropna()) 
        for col in numeric_cols
    })
    return skewness

def save_model_artifacts(model, pipeline, results, metrics, config):
    """
    Save model artifacts, pipeline, and results
    
    Args:
        model: Trained model
        pipeline: Preprocessing pipeline
        results (pd.DataFrame): Model results
        metrics (dict): Model performance metrics
        config (Config): Configuration instance
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save model
    model_path = os.path.join(config.MODEL_DIR, f'model_{timestamp}.pkl')
    joblib.dump(model, model_path)
    
    # Save pipeline
    pipeline_path = os.path.join(config.MODEL_DIR, f'pipeline_{timestamp}.pkl')
    joblib.dump(pipeline, pipeline_path)
    
    # Save results
    results_path = os.path.join(config.RESULTS_DIR, f'results_{timestamp}.csv')
    results.to_csv(results_path, index=False)
    
    # Save metrics
    metrics_path = os.path.join(config.RESULTS_DIR, f'metrics_{timestamp}.json')
    pd.Series(metrics).to_json(metrics_path)

def load_model_artifacts(model_path, pipeline_path):
    """
    Load saved model and pipeline
    
    Args:
        model_path (str): Path to saved model
        pipeline_path (str): Path to saved pipeline
    
    Returns:
        tuple: (model, pipeline)
    """
    model = joblib.load(model_path)
    pipeline = joblib.load(pipeline_path)
    return model, pipeline

def validate_model_inputs(df, expected_columns, config):
    """
    Validate input data for model prediction
    
    Args:
        df (pd.DataFrame): Input dataframe
        expected_columns (list): List of expected column names
        config (Config): Configuration instance
    
    Returns:
        bool: True if validation passes, raises exception otherwise
    """
    logger = logging.getLogger('happiness_score')
    
    # Check if all required columns are present
    missing_cols = set(expected_columns) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Check for missing values
    if df.isnull().any().any():
        raise ValueError("Input data contains missing values")
    
    # Check data types
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if not all(col in numeric_cols for col in expected_columns):
        raise ValueError("All features must be numeric")
    
    logger.info("Input validation passed successfully")
    return True

def generate_model_report(model, metrics, feature_names):
    """
    Generate a comprehensive model report
    
    Args:
        model: Trained model
        metrics (dict): Model performance metrics
        feature_names (list): List of feature names
    
    Returns:
        dict: Model report
    """
    report = {
        'model_type': type(model).__name__,
        'performance_metrics': metrics,
        'feature_importance': get_feature_importance(model, feature_names)
    }
    return report

def get_feature_importance(model, feature_names):
    """
    Get feature importance if available
    
    Args:
        model: Trained model
        feature_names (list): List of feature names
    
    Returns:
        pd.Series or None: Feature importance if available
    """
    if hasattr(model, 'coef_'):
        return pd.Series(model.coef_, index=feature_names)
    elif hasattr(model, 'feature_importances_'):
        return pd.Series(model.feature_importances_, index=feature_names)
    return None

if __name__ == "__main__":
    # Test helper functions
    logger = setup_logging()
    config = Config()
    
    # Create sample data for testing
    sample_data = pd.DataFrame({
        'A': np.random.normal(0, 1, 100),
        'B': np.random.normal(5, 2, 100),
        'C': np.random.exponential(2, 100)
    })
    
    print("Testing Helper Functions:")
    print("-" * 50)
    
    # Test statistics calculation
    print("\nCalculating Statistics:")
    stats = calculate_statistics(sample_data)
    print("\nBasic Stats:")
    print(stats['basic_stats'])
    
    print("\nSkewness:")
    print(stats['skewness'])
    
    # Test validation
    print("\nTesting Input Validation:")
    try:
        validate_model_inputs(sample_data, ['A', 'B', 'C'], config)
        print("Validation passed!")
    except Exception as e:
        print(f"Validation failed: {str(e)}")
    
    logger.info("Helper functions testing completed successfully")