import os
import sys
import streamlit as st
import pandas as pd
import joblib
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.append(str(src_path))

from preprocessing_pipeline import PreprocessingPipeline
from config import Config

# Initialize config
config = Config()

def load_artifacts():
    """Load model and preprocessing pipeline"""
    try:
        model_data = joblib.load(config.MODEL_PATH)
        pipeline = joblib.load(config.MODEL_PIPELINE_PATH)
        return model_data['model'], model_data['feature_names'], pipeline
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None, None, None

def main():
    st.title("Happiness Score Predictor")
    st.write("Enter values to predict happiness score")

    # Load model artifacts
    model, feature_names, pipeline = load_artifacts()
    
    if model is None:
        st.error("Failed to load model. Please check the model files.")
        return

    # Create input fields
    input_data = {}
    col1, col2 = st.columns(2)
    
    for i, feature in enumerate(feature_names):
        # Alternate between columns
        with col1 if i % 2 == 0 else col2:
            input_data[feature] = st.number_input(
                f"{feature.replace('_', ' ').title()}", 
                min_value=-100.0,
                max_value=100.0,
                value=0.0,
                step=0.1
            )

    if st.button("Predict"):
        try:
            # Create DataFrame from input
            input_df = pd.DataFrame([input_data])
            
            # Transform input data
            processed_data = pipeline.transform(input_df, is_single_input=True)
            
            # Make prediction
            prediction = model.predict(processed_data)[0]
            
            # Display prediction
            st.success(f"Predicted Happiness Score: {prediction:.2f}")
            
            # Display input summary
            st.subheader("Input Summary")
            st.write(pd.DataFrame([input_data]).T)
            
        except Exception as e:
            st.error(f"Error making prediction: {str(e)}")

if __name__ == "__main__":
    main()