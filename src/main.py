import logging
import pandas as pd
import numpy as np
from pathlib import Path
import joblib
from datetime import datetime

from config import Config
from helpers import setup_logging
from data_loader import DataLoader
from preprocessing_pipeline import PreprocessingPipeline
from model_trainer import ModelTrainer

class ExperimentManager:
    """Manages machine learning experiments"""
    def __init__(self):
        self.config = Config()
        self.logger = setup_logging()
        self.experiment_dir = None
        
    def create_experiment_dir(self):
        """Create directory for experiment results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.experiment_dir = Path(self.config.EXPERIMENTS_DIR) / f"experiment_{timestamp}"
        self.experiment_dir.mkdir(parents=True, exist_ok=True)
        return self.experiment_dir

    def save_experiment_results(self, model_results, processed_df, pipeline, preprocessing_stats):
        """Save all experiment artifacts"""
        # Save model results
        results_df = pd.DataFrame()
        for model_name, result in model_results.items():
            metrics = result['metrics']
            row = {
                'model': model_name,
                'test_r2': metrics['test_r2'],
                'test_rmse': metrics['test_rmse'],
                'cv_mean': metrics['cv_mean'],
                'cv_std': metrics['cv_std'],
                'best_params': str(result['best_params'])
            }
            results_df = pd.concat([results_df, pd.DataFrame([row])], ignore_index=True)
        
        # Save results
        results_df.to_csv(self.experiment_dir / 'model_results.csv', index=False)
        processed_df.head(100).to_csv(self.experiment_dir / 'processed_data_sample.csv', index=False)
        joblib.dump(pipeline, self.experiment_dir / 'preprocessing_pipeline.pkl')
        
        # Save experiment metadata
        metadata = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'data_shape': processed_df.shape,
            'preprocessing_stats': preprocessing_stats,
            'features': list(processed_df.columns),
            'best_model': results_df.loc[results_df['test_r2'].idxmax(), 'model']
        }
        pd.Series(metadata).to_json(self.experiment_dir / 'metadata.json')
        
        self.logger.info(f"Experiment results saved to {self.experiment_dir}")

    def run_experiment(self):
        """Run the complete model development experiment"""
        self.create_experiment_dir()
        self.logger.info(f"Starting experiment in directory: {self.experiment_dir}")
        
        try:
            # 1. Load Data
            self.logger.info("Loading data...")
            loader = DataLoader()
            df = loader.load_and_clean()[0]
            self.logger.info(f"Data loaded successfully. Shape: {df.shape}")
            
            # 2. Preprocess Data
            self.logger.info("Preprocessing data...")
            pipeline = PreprocessingPipeline()
            processed_df = pipeline.fit_transform(df)
            pipeline.save_pipeline()  # Save the pipeline for later use
            self.logger.info(f"Data preprocessed. Final shape: {processed_df.shape}")
            
            # 3. Prepare features and target
            X = processed_df.drop(columns=[self.config.TARGET_COLUMN])
            y = processed_df[self.config.TARGET_COLUMN]
            self.logger.info(f"Features prepared. X shape: {X.shape}, y shape: {y.shape}")
            
            # 4. Train Models
            self.logger.info("\nTraining models...")
            trainer = ModelTrainer()
            model_results = trainer.train_models(X, y)
            
            # 5. Save Results
            self.logger.info("\nSaving experiment results...")
            preprocessing_stats = {
                'initial_shape': df.shape,
                'final_shape': processed_df.shape
            }
            self.save_experiment_results(model_results, processed_df, pipeline, preprocessing_stats)
            
            # 6. Save Best Model
            trainer.save_best_model()
            
            # 7. Print Final Summary
            self._print_summary(df, processed_df, model_results)
            
            self.logger.info("Experiment completed successfully")
            return self.experiment_dir, model_results
            
        except Exception as e:
            self.logger.error(f"Error during experiment: {str(e)}")
            raise

    def _print_summary(self, df, processed_df, model_results):
        """Print experiment summary"""
        print("\nExperiment Results Summary:")
        print("-" * 50)
        print(f"\nExperiment Directory: {self.experiment_dir}")
        
        print("\nData Processing:")
        print(f"Initial Shape: {df.shape}")
        print(f"Final Shape: {processed_df.shape}")
        
        print("\nModel Performance:")
        for model_name, result in model_results.items():
            metrics = result['metrics']
            print(f"\n{model_name}:")
            print(f"Test R2 Score: {metrics['test_r2']:.4f}")
            print(f"Test RMSE: {metrics['test_rmse']:.4f}")
            print(f"CV Score: {metrics['cv_mean']:.4f} (+/- {metrics['cv_std']*2:.4f})")

class PredictionPipeline:
    """Handles model predictions"""
    def __init__(self, experiment_dir=None):
        self.config = Config()
        self.logger = setup_logging()
        self.experiment_dir = Path(experiment_dir) if experiment_dir else None
        self.pipeline = None
        self.model_data = None
        
    def load_artifacts(self):
        """Load saved model and pipeline"""
        try:
            # Load preprocessing pipeline
            self.pipeline = joblib.load(self.experiment_dir / 'preprocessing_pipeline.pkl')
            
            # Load best model
            self.model_data = joblib.load(self.config.MODEL_PATH)
            
            self.logger.info("Model artifacts loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading artifacts: {str(e)}")
            raise
    
    def predict(self, data):
        """Make predictions using loaded model"""
        try:
            # Validate input features
            required_features = self.model_data['feature_names']
            if not all(feature in data.columns for feature in required_features):
                raise ValueError("Missing required features in input data")
            
            # Preprocess data
            processed_data = self.pipeline.transform(data)
            
            # Make prediction
            predictions = self.model_data['model'].predict(processed_data)
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error making prediction: {str(e)}")
            raise

if __name__ == "__main__":
    # Run experiment
    experiment = ExperimentManager()
    experiment_dir, model_results = experiment.run_experiment()
    
    # Test prediction pipeline
    print("\nTesting Prediction Pipeline:")
    print("-" * 50)
    
    try:
        # Initialize prediction pipeline
        predictor = PredictionPipeline(experiment_dir)
        predictor.load_artifacts()
        
        # Create sample input
        loader = DataLoader()
        sample_data = loader.load_and_clean()[0].head(1)
        
        # Make prediction
        prediction = predictor.predict(sample_data)
        
        print("\nSample Prediction:")
        print(f"Input Features:\n{sample_data}")
        print(f"\nPredicted Happiness Score: {prediction[0]:.4f}")
        print(f"Actual Happiness Score: {sample_data[Config().TARGET_COLUMN].iloc[0]:.4f}")
        
    except Exception as e:
        print(f"Error testing prediction pipeline: {str(e)}")