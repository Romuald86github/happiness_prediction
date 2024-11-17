from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import joblib
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]  # Two levels up to the project root
SRC_DIR = PROJECT_ROOT / 'src'
sys.path.insert(0, str(SRC_DIR))  # Ensure src is prioritized in the import path

from config import Config

# Initialize Flask app
app = Flask(__name__)
config = Config()

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')

handler = RotatingFileHandler(
    'logs/app.log',
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
        model_data = joblib.load(app.config['MODEL_PATH'])
        pipeline = joblib.load(app.config['PIPELINE_PATH'])
        
        app.logger.info("Model artifacts loaded successfully")
        return model_data['model'], model_data['feature_names'], pipeline
    except Exception as e:
        app.logger.error(f"Error loading model artifacts: {str(e)}")
        raise

def validate_input(data, feature_names):
    """Validate input data"""
    # Check for missing features
    missing_features = [feat for feat in feature_names if feat not in data]
    if missing_features:
        raise ValueError(f"Missing required features: {missing_features}")
    
    # Validate feature values
    for feature in feature_names:
        value = data.get(feature)
        if value is None:
            raise ValueError(f"Missing value for feature: {feature}")
        try:
            float_value = float(value)
            # Add basic range validation
            if not (-1000 <= float_value <= 1000):
                raise ValueError(f"Value for {feature} is out of reasonable range")
        except ValueError:
            raise ValueError(f"Invalid value for feature: {feature}")
    
    return True

# Load model artifacts at startup
try:
    model, feature_names, pipeline = load_model_artifacts()
except Exception as e:
    app.logger.error(f"Failed to load model artifacts: {str(e)}")
    model = None
    feature_names = None
    pipeline = None

@app.route('/')
def home():
    """Render home page"""
    if feature_names is None:
        return render_template('error.html', error="Model not loaded"), 503
    return render_template('index.html', feature_names=feature_names)

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
        input_df = pd.DataFrame([{feature: float(data[feature]) for feature in feature_names}])
        
        # Preprocess data
        processed_data = pipeline.transform(input_df)
        
        # Make prediction
        prediction = model.predict(processed_data)[0]
        
        # Log successful prediction
        app.logger.info(f"Successful prediction made: {prediction:.4f}")
        
        return jsonify({
            'success': True,
            'prediction': round(float(prediction), 4)
        })
        
    except Exception as e:
        app.logger.error(f"Prediction error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Server error: {str(error)}")
    return render_template('error.html', error="Internal server error"), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)