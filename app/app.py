from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
from pathlib import Path
from datetime import datetime
import traceback

# Set up project paths
#PROJECT_ROOT = Path(__file__).resolve().parents[1]  # Two levels up to project root
#SRC_DIR = PROJECT_ROOT / 'src'
APP_DIR = PROJECT_ROOT / 'app'
TEMPLATE_DIR = APP_DIR / 'templates'
STATIC_DIR = APP_DIR / 'static'

#sys.path.insert(0, str(SRC_DIR))  # Ensure src is prioritized in import path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))


from src.config import Config
from src.preprocessing_pipeline import PreprocessingPipeline

# Initialize Flask app with correct template and static folders
app = Flask(__name__,
           template_folder=str(TEMPLATE_DIR),
           static_folder=str(STATIC_DIR))

# Enable CORS
CORS(app)

# Load configuration
config = Config()

# Configure logging
log_dir = PROJECT_ROOT / 'logs'
log_dir.mkdir(exist_ok=True)

handler = RotatingFileHandler(
    log_dir / 'app.log',
    maxBytes=10000000,
    backupCount=5
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# Set configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'DEFAULT_SECRET_KEY')
app.config['MODEL_PATH'] = os.environ.get('MODEL_PATH', config.MODEL_PATH)
app.config['PIPELINE_PATH'] = os.environ.get('PIPELINE_PATH', config.MODEL_PIPELINE_PATH)

def load_model_artifacts():
    """Load model and preprocessing pipeline"""
    try:
        app.logger.info("Loading model artifacts...")
        
        # Load model data
        model_data = joblib.load(app.config['MODEL_PATH'])
        
        # Load preprocessing pipeline
        pipeline = PreprocessingPipeline.load(app.config['PIPELINE_PATH'])
        
        app.logger.info("Model artifacts loaded successfully")
        app.logger.info(f"Model type: {type(model_data['model'])}")
        app.logger.info(f"Pipeline type: {type(pipeline)}")
        
        return model_data['model'], model_data['feature_names'], pipeline
    except Exception as e:
        app.logger.error(f"Error loading model artifacts: {str(e)}\n{traceback.format_exc()}")
        raise

def validate_input(data, feature_names):
    """Validate input data"""
    if not isinstance(data, dict):
        raise ValueError("Input must be a JSON object")
    
    missing_features = [feat for feat in feature_names if feat not in data]
    if missing_features:
        raise ValueError(f"Missing required features: {missing_features}")
    
    for feature in feature_names:
        try:
            value = float(data[feature])
            if not (-1000 <= value <= 1000):
                raise ValueError(f"Value for {feature} is out of reasonable range")
        except (TypeError, ValueError):
            raise ValueError(f"Invalid value for feature: {feature}")
    
    return True

def log_prediction(data, prediction, success=True, error=None):
    """Log prediction details"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'input_data': data,
        'prediction': float(prediction) if success else None,
        'success': success,
        'error': str(error) if error else None,
        'client_ip': request.remote_addr
    }
    app.logger.info(f"Prediction log: {log_entry}")

# Load model artifacts at startup
try:
    model, feature_names, pipeline = load_model_artifacts()
    app.logger.info(f"Loaded feature names: {feature_names}")
except Exception as e:
    app.logger.error(f"Failed to load model artifacts: {str(e)}")
    model = None
    feature_names = None
    pipeline = None

@app.route('/health')
def health_check():
    """Health check endpoint"""
    status = 'healthy' if all([model, feature_names, pipeline]) else 'unhealthy'
    return jsonify({
        'status': status,
        'timestamp': datetime.now().isoformat()
    }), 200 if status == 'healthy' else 503

@app.route('/')
def home():
    """Render home page"""
    if feature_names is None:
        return render_template('error.html', 
                             error="Model not loaded"), 503
    return render_template('index.html', 
                         feature_names=feature_names)

@app.route('/predict', methods=['POST'])
def predict():
    """Make prediction based on input data"""
    if model is None or pipeline is None:
        return jsonify({
            'success': False,
            'error': 'Model not loaded'
        }), 503
    
    try:
        # Get input data
        data = request.get_json()
        if not data:
            raise ValueError("No input data provided")
        
        # Validate input
        validate_input(data, feature_names)
        
        # Create DataFrame with proper feature ordering
        input_df = pd.DataFrame([{feature: float(data[feature]) 
                                for feature in feature_names}])
        
        app.logger.info(f"Input data shape: {input_df.shape}")
        app.logger.info(f"Input features: {input_df.columns.tolist()}")
        
        # Transform data
        processed_data = pipeline.transform(input_df, is_single_input=True)
        
        # Make prediction
        prediction = model.predict(processed_data)[0]
        
        # Log successful prediction
        log_prediction(data, prediction)
        
        return jsonify({
            'success': True,
            'prediction': round(float(prediction), 4)
        })
        
    except Exception as e:
        # Log failed prediction
        log_prediction(
            data if 'data' in locals() else None,
            None,
            success=False,
            error=e
        )
        app.logger.error(f"Prediction error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/model/info')
def model_info():
    """Get model information"""
    if model is None:
        return jsonify({
            'success': False,
            'error': 'Model not loaded'
        }), 503
    
    return jsonify({
        'success': True,
        'feature_names': feature_names,
        'model_type': type(model).__name__,
        'pipeline_steps': list(pipeline.feature_means.keys()) if pipeline else None
    })

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', 
                         error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Server error: {str(error)}\n{traceback.format_exc()}")
    return render_template('error.html', 
                         error="Internal server error"), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.logger.info(f"Starting application on port {port}")
    app.run(host='0.0.0.0', port=port)