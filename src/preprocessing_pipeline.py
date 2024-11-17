import pandas as pd
import numpy as np
from scipy import stats
import joblib
import logging
from pathlib import Path
from config import Config
from helpers import setup_logging

class PreprocessingPipeline:
    """
    Handles all data preprocessing steps while properly storing transformation parameters
    for later use with single user inputs
    """
    def __init__(self):
        self.config = Config()
        self.logger = setup_logging()
        
        # Store transformation parameters
        self.feature_means = {}
        self.feature_stds = {}
        self.boxcox_lambdas = {}
        self.feature_names = None
        
    def load_clean_data(self):
        """Load the cleaned data"""
        try:
            self.logger.info(f"Loading clean data from {self.config.CLEAN_DATA_PATH}")
            df = pd.read_csv(self.config.CLEAN_DATA_PATH)
            self.logger.info(f"Clean data loaded successfully. Shape: {df.shape}")
            return df
        except Exception as e:
            self.logger.error(f"Error loading clean data: {str(e)}")
            raise

    def fit(self, df):
        """Learn transformation parameters from training data"""
        try:
            self.logger.info("Fitting preprocessing pipeline...")
            
            # Store feature names
            self.feature_names = [col for col in df.columns 
                                if col != self.config.TARGET_COLUMN]
            
            # Fit z-score parameters
            X = df.drop(columns=[self.config.TARGET_COLUMN])
            for column in X.columns:
                self.feature_means[column] = X[column].mean()
                self.feature_stds[column] = X[column].std()
            
            # Fit Box-Cox parameters
            for column in self.config.FEATURES_TO_TRANSFORM['box_cox']:
                if column in X.columns:
                    # Add small constant to ensure positivity
                    min_val = X[column].min()
                    shift = abs(min_val) + 1 if min_val <= 0 else 0
                    data = X[column] + shift
                    
                    # Store both lambda and shift
                    transformed_data, lambda_param = stats.boxcox(data)
                    self.boxcox_lambdas[column] = {
                        'lambda': lambda_param,
                        'shift': shift
                    }
            
            self.logger.info("Pipeline fitting completed")
            
        except Exception as e:
            self.logger.error(f"Error fitting pipeline: {str(e)}")
            raise
            
    def transform(self, df, is_single_input=False):
        """
        Transform data using stored parameters
        Works for both full datasets and single user inputs
        """
        try:
            self.logger.info("Transforming data...")
            df_transformed = df.copy()
            
            # Verify all required features are present
            missing_features = set(self.feature_names) - set(df_transformed.columns)
            if missing_features:
                raise ValueError(f"Missing features in input data: {missing_features}")
            
            # Handle features marked for Box-Cox
            for column in self.config.FEATURES_TO_TRANSFORM['box_cox']:
                if column in df_transformed.columns:
                    params = self.boxcox_lambdas[column]
                    data = df_transformed[column] + params['shift']
                    
                    if params['lambda'] == 0:
                        df_transformed[column] = np.log(data)
                    else:
                        df_transformed[column] = (data ** params['lambda'] - 1) / params['lambda']
            
            # Handle features marked for cube root
            for column in self.config.FEATURES_TO_TRANSFORM['cube_root']:
                if column in df_transformed.columns:
                    df_transformed[column] = np.cbrt(df_transformed[column])
            
            # Apply z-score normalization
            for column in self.feature_means.keys():
                if column in df_transformed.columns:
                    df_transformed[column] = (
                        df_transformed[column] - self.feature_means[column]
                    ) / self.feature_stds[column]
            
            self.logger.info("Data transformation completed")
            return df_transformed
            
        except Exception as e:
            self.logger.error(f"Error transforming data: {str(e)}")
            raise
            
    def fit_transform(self, df):
        """Fit pipeline and transform data"""
        try:
            # Separate features and target
            X = df.drop(columns=[self.config.TARGET_COLUMN])
            y = df[self.config.TARGET_COLUMN]
            
            # Fit pipeline
            self.fit(df)
            
            # Transform features only
            X_transformed = self.transform(X)
            
            # Recombine with untransformed target
            transformed_df = pd.concat([X_transformed, y], axis=1)
            
            return transformed_df
            
        except Exception as e:
            self.logger.error(f"Error in fit_transform: {str(e)}")
            raise
    
    def save(self, path=None):
        """Save pipeline object"""
        try:
            save_path = path or self.config.MODEL_PIPELINE_PATH
            self.logger.info(f"Saving pipeline to {save_path}")
            joblib.dump(self, save_path)
            self.logger.info("Pipeline saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving pipeline: {str(e)}")
            raise
    
    def save_preprocessed_data(self, df):
        """Save preprocessed data"""
        try:
            path = self.config.PREPROCESSED_DATA_PATH
            self.logger.info(f"Saving preprocessed data to {path}")
            df.to_csv(path, index=False)
            self.logger.info("Preprocessed data saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving preprocessed data: {str(e)}")
            raise
    
    @staticmethod
    def load(path):
        """Load saved pipeline"""
        return joblib.load(path)


if __name__ == "__main__":
    # Initialize pipeline
    pipeline = PreprocessingPipeline()
    
    # Load clean data
    df = pipeline.load_clean_data()
    
    # Fit and transform data
    transformed_df = pipeline.fit_transform(df)
    
    # Save pipeline and preprocessed data
    pipeline.save()
    pipeline.save_preprocessed_data(transformed_df)
    
    # Print results
    print("\nPreprocessing Results:")
    print("-" * 50)
    print(f"\nOriginal Shape: {df.shape}")
    print("\nOriginal Data Sample:")
    print(df.head())
    print(f"\nTransformed Shape: {transformed_df.shape}")
    print("\nTransformed Data Sample:")
    print(transformed_df.head())
    
    # Test single input transformation
    print("\nTesting single input transformation:")
    sample_input = pd.DataFrame([df.iloc[0].drop(pipeline.config.TARGET_COLUMN)])
    transformed_input = pipeline.transform(sample_input, is_single_input=True)
    print("\nSingle Input Transformation Result:")
    print(transformed_input)