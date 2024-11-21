import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from scipy.stats import ks_2samp
import joblib
from pathlib import Path
from datetime import datetime

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.append(str(src_path))

from preprocessing_pipeline import PreprocessingPipeline
from config import Config

# Initialize config
config = Config()

# Constants
MIN_SAMPLES_FOR_DRIFT = 10  # Minimum number of samples needed for drift analysis
USER_INPUTS_FILE = "user_inputs.csv"  # File to store accumulated user inputs

def load_artifacts():
    """Load model and preprocessing pipeline"""
    try:
        model_data = joblib.load(config.MODEL_PATH)
        pipeline = joblib.load(config.MODEL_PIPELINE_PATH)
        return model_data['model'], model_data['feature_names'], pipeline
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None, None, None

def load_user_inputs():
    """Load accumulated user inputs"""
    try:
        if os.path.exists(USER_INPUTS_FILE):
            return pd.read_csv(USER_INPUTS_FILE)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading user inputs: {str(e)}")
        return pd.DataFrame()

def save_user_input(input_data):
    """Save user input to accumulated data"""
    try:
        df = pd.DataFrame([input_data])
        df['timestamp'] = datetime.now()
        
        if os.path.exists(USER_INPUTS_FILE):
            existing_df = pd.read_csv(USER_INPUTS_FILE)
            df = pd.concat([existing_df, df], ignore_index=True)
        
        df.to_csv(USER_INPUTS_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving user input: {str(e)}")
        return False

def calculate_drift_metrics(reference_data, new_data, feature_names):
    """Calculate drift metrics using KS test"""
    drift_results = {}
    for feature in feature_names:
        statistic, p_value = ks_2samp(reference_data[feature], new_data[feature])
        drift_results[feature] = {
            'statistic': statistic,
            'p_value': p_value,
            'is_drift': p_value < 0.05
        }
    return drift_results

def plot_feature_distributions(reference_data, new_data, feature, title):
    """Plot distribution comparison using plotly"""
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=reference_data[feature], name='Training Data', opacity=0.7))
    fig.add_trace(go.Histogram(x=new_data[feature], name='User Inputs', opacity=0.7))
    fig.update_layout(
        title=title,
        barmode='overlay',
        xaxis_title=feature,
        yaxis_title="Count"
    )
    return fig

def calculate_performance_metrics(y_true, y_pred):
    """Calculate model performance metrics"""
    return {
        'RMSE': float(np.sqrt(mean_squared_error(y_true, y_pred))),
        'MAE': float(mean_absolute_error(y_true, y_pred)),
        'R2': float(r2_score(y_true, y_pred))
    }

def generate_reference_metrics(model, pipeline, feature_names):
    """Generate reference metrics using training data"""
    try:
        # Load training data
        reference_data = pd.read_csv(config.PREPROCESSED_DATA_PATH)
        
        # Calculate metrics on training data
        X = reference_data[feature_names]
        y = reference_data[config.TARGET_COLUMN]
        X_transformed = pipeline.transform(X)
        y_pred = model.predict(X_transformed)
        
        return calculate_performance_metrics(y, y_pred)
    except Exception as e:
        st.error(f"Error generating reference metrics: {str(e)}")
        return None

def calculate_drift_percentage(old_value, new_value):
    """Calculate drift percentage between metrics"""
    return ((new_value - old_value) / old_value) * 100

def plot_metrics_comparison(reference_metrics, new_metrics):
    """Plot metrics comparison"""
    fig = go.Figure()
    metrics = list(reference_metrics.keys())
    
    fig.add_trace(go.Bar(
        name='Original Model',
        x=metrics,
        y=[reference_metrics[m] for m in metrics],
        marker_color='blue'
    ))
    
    fig.add_trace(go.Bar(
        name='New Data',
        x=metrics,
        y=[new_metrics[m] for m in metrics],
        marker_color='red'
    ))
    
    fig.update_layout(
        title='Model Performance Comparison',
        barmode='group',
        yaxis_title='Metric Value'
    )
    return fig

def main():
    st.set_page_config(layout="wide")
    
    # Load model artifacts
    model, feature_names, pipeline = load_artifacts()
    if model is None:
        st.error("Failed to load model. Please check the model files.")
        return

    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Select Page",
        ["Prediction", "Model Monitoring", "User Inputs History"]
    )

    if page == "Prediction":
        st.title("Happiness Score Predictor")
        st.write("Enter values to predict happiness score")

        # Create input fields
        input_data = {}
        col1, col2 = st.columns(2)
        
        for i, feature in enumerate(feature_names):
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
                input_df = pd.DataFrame([input_data])
                processed_data = pipeline.transform(input_df, is_single_input=True)
                prediction = model.predict(processed_data)[0]
                st.success(f"Predicted Happiness Score: {prediction:.2f}")
                
                # Save prediction and input
                input_data['predicted_score'] = prediction
                if save_user_input(input_data):
                    st.info("Input saved for monitoring")
                
                # Show input summary
                st.subheader("Input Summary")
                st.write(pd.DataFrame([input_data]).T)
                
            except Exception as e:
                st.error(f"Error making prediction: {str(e)}")

    elif page == "Model Monitoring":
        st.title("Model Monitoring Dashboard")

        tab1, tab2 = st.tabs(["Data Drift", "Performance Drift"])
        
        with tab1:
            # Load accumulated user inputs
            user_inputs_df = load_user_inputs()
            n_samples = len(user_inputs_df)

            st.info(f"Currently collected {n_samples} user inputs out of minimum {MIN_SAMPLES_FOR_DRIFT} required for drift analysis")

            if n_samples >= MIN_SAMPLES_FOR_DRIFT:
                try:
                    # Load reference data
                    reference_data = pd.read_csv(config.PREPROCESSED_DATA_PATH)

                    # Calculate drift metrics
                    drift_results = calculate_drift_metrics(
                        reference_data[feature_names], 
                        user_inputs_df[feature_names],
                        feature_names
                    )

                    # Display drift results
                    st.subheader("Data Drift Analysis")
                    drift_df = pd.DataFrame([
                        {
                            'Feature': feature,
                            'KS Statistic': results['statistic'],
                            'P-value': results['p_value'],
                            'Drift Detected': results['is_drift']
                        }
                        for feature, results in drift_results.items()
                    ])
                    st.dataframe(drift_df)

                    # Feature distribution plots
                    st.subheader("Feature Distributions Comparison")
                    for feature in feature_names:
                        fig = plot_feature_distributions(
                            reference_data,
                            user_inputs_df,
                            feature,
                            f"Distribution Comparison - {feature}"
                        )
                        st.plotly_chart(fig)

                except Exception as e:
                    st.error(f"Error in drift analysis: {str(e)}")

        with tab2:
            st.subheader("Model Performance Drift Analysis")
            
            # Generate reference metrics
            reference_metrics = generate_reference_metrics(model, pipeline, feature_names)
            if reference_metrics:
                st.write("Original Model Performance Metrics:")
                st.write(pd.Series(reference_metrics))
            
            # Upload new data for performance analysis
            st.write("\nUpload new data to analyze performance drift:")
            uploaded_file = st.file_uploader(
                "Upload CSV file (must contain same features and target column)",
                type=['csv']
            )
            
            if uploaded_file and reference_metrics:
                try:
                    # Load and validate new data
                    new_data = pd.read_csv(uploaded_file)
                    
                    # Validate columns
                    missing_cols = set(feature_names) - set(new_data.columns)
                    if missing_cols:
                        st.error(f"Missing required columns: {missing_cols}")
                        return
                        
                    if config.TARGET_COLUMN not in new_data.columns:
                        st.error(f"Missing target column: {config.TARGET_COLUMN}")
                        return
                    
                    # Calculate performance on new data
                    X_new = new_data[feature_names]
                    y_new = new_data[config.TARGET_COLUMN]
                    
                    X_new_processed = pipeline.transform(X_new)
                    y_new_pred = model.predict(X_new_processed)
                    
                    new_metrics = calculate_performance_metrics(y_new, y_new_pred)
                    
                    # Display metrics comparison
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("Original Model Metrics:")
                        st.write(pd.Series(reference_metrics))
                    with col2:
                        st.write("New Data Metrics:")
                        st.write(pd.Series(new_metrics))
                    
                    # Plot metrics comparison
                    st.plotly_chart(plot_metrics_comparison(reference_metrics, new_metrics))
                    
                    # Calculate and display drift
                    st.subheader("Performance Drift Analysis")
                    drift_data = []
                    for metric in reference_metrics.keys():
                        drift_pct = calculate_drift_percentage(
                            reference_metrics[metric],
                            new_metrics[metric]
                        )
                        drift_data.append({
                            'Metric': metric,
                            'Original Value': f"{reference_metrics[metric]:.4f}",
                            'New Value': f"{new_metrics[metric]:.4f}",
                            'Drift (%)': f"{drift_pct:.2f}%",
                            'Status': 'Significant Drift' if abs(drift_pct) > 10 else 'Stable'
                        })
                    
                    drift_df = pd.DataFrame(drift_data)
                    st.table(drift_df)
                    
                    # Plot actual vs predicted
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=y_new,
                        y=y_new_pred,
                        mode='markers',
                        name='Predictions'
                    ))
                    fig.add_trace(go.Scatter(
                        x=[y_new.min(), y_new.max()],
                        y=[y_new.min(), y_new.max()],
                        mode='lines',
                        name='Perfect Prediction',
                        line=dict(dash='dash')
                    ))
                    fig.update_layout(
                        title='Actual vs Predicted Values on New Data',
                        xaxis_title='Actual Values',
                        yaxis_title='Predicted Values'
                    )
                    st.plotly_chart(fig)
                    
                except Exception as e:
                    st.error(f"Error analyzing new data: {str(e)}")
    
    else:  # User Inputs History
        st.title("User Inputs History")
        user_inputs_df = load_user_inputs()
        
        if not user_inputs_df.empty:
            st.write("Historical User Inputs")
            st.dataframe(user_inputs_df)
            
            if st.button("Clear History"):
                try:
                    os.remove(USER_INPUTS_FILE)
                    st.success("History cleared successfully")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error clearing history: {str(e)}")
        else:
            st.write("No user inputs recorded yet")

if __name__ == "__main__":
    main()