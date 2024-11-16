import pandas as pd
import numpy as np
import logging
import os
from config import Config
from helpers import setup_logging, calculate_statistics

class DataLoader:
    """
    Class for loading and performing initial data cleaning
    """
    def __init__(self):
        self.logger = setup_logging()
        self.config = Config()

    def load_raw_data(self):
        """Load data from URL"""
        try:
            self.logger.info("Loading data from URL...")
            df = pd.read_csv(self.config.DATA_URL)
            self.logger.info(f"Data loaded successfully. Shape: {df.shape}")
            return df
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise

    def clean_data(self, df):
        """Perform initial data cleaning"""
        try:
            self.logger.info("Starting initial data cleaning...")
            
            # Store original shape
            original_shape = df.shape
            initial_rows = len(df)
            
            # Remove specified columns
            df = df.drop(columns=self.config.COLUMNS_TO_DROP)
            self.logger.info(f"Removed {len(self.config.COLUMNS_TO_DROP)} columns")
            
            # Remove duplicates
            duplicates_count = df.duplicated().sum()
            df = df.drop_duplicates()
            self.logger.info(f"Removed {duplicates_count} duplicate rows")
            
            # Remove rows with missing values
            missing_count = df.isnull().any(axis=1).sum()
            df = df.dropna()
            self.logger.info(f"Removed {missing_count} rows with missing values")
            
            # Remove specific outlier indices
            if hasattr(self.config, 'OUTLIER_INDICES') and self.config.OUTLIER_INDICES:
                rows_before_outliers = len(df)
                df = df.drop(index=self.config.OUTLIER_INDICES, errors='ignore')
                removed_outliers = rows_before_outliers - len(df)
                self.logger.info(f"Removed {removed_outliers} outlier rows")
            
            # Log cleaning results
            self.logger.info(f"Original shape: {original_shape}")
            self.logger.info(f"Cleaned shape: {df.shape}")
            self.logger.info(f"Removed {original_shape[0] - df.shape[0]} rows in total")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error cleaning data: {str(e)}")
            raise

    def validate_data(self, df):
        """Validate data quality"""
        try:
            self.logger.info("Validating data...")
            
            # Check for remaining missing values
            missing = df.isnull().sum()
            if missing.any():
                self.logger.warning(f"Missing values found:\n{missing[missing > 0]}")
            
            # Check data types
            self.logger.info(f"Data types:\n{df.dtypes}")
            
            # Calculate basic statistics
            stats = calculate_statistics(df)
            self.logger.info("Data statistics calculated")
            
            # Validate columns presence
            expected_features = (
                self.config.FEATURES_TO_TRANSFORM['box_cox'] +
                self.config.FEATURES_TO_TRANSFORM['cube_root']
            )
            missing_features = [col for col in expected_features if col not in df.columns]
            if missing_features:
                self.logger.warning(f"Missing expected features: {missing_features}")
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error validating data: {str(e)}")
            raise

    def save_clean_data(self, df):
        """Save cleaned data to CSV file"""
        try:
            self.logger.info(f"Saving cleaned data to {self.config.CLEAN_DATA_PATH}")
            df.to_csv(self.config.CLEAN_DATA_PATH, index=False)
            self.logger.info("Data saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving cleaned data: {str(e)}")
            raise

    def load_and_clean(self):
        """Main method to load and clean data"""
        try:
            # Load raw data
            df = self.load_raw_data()
            
            # Clean data
            df = self.clean_data(df)
            
            # Validate data
            stats = self.validate_data(df)
            
            # Save cleaned data
            self.save_clean_data(df)
            
            self.logger.info("Data loading, cleaning, and saving completed successfully")
            return df, stats
            
        except Exception as e:
            self.logger.error(f"Error in load_and_clean pipeline: {str(e)}")
            raise

    def load_clean_data(self):
        """Load previously cleaned data"""
        try:
            if os.path.exists(self.config.CLEAN_DATA_PATH):
                self.logger.info("Loading previously cleaned data...")
                df = pd.read_csv(self.config.CLEAN_DATA_PATH)
                self.logger.info(f"Cleaned data loaded successfully. Shape: {df.shape}")
                return df
            else:
                self.logger.warning("No cleaned data file found. Running full pipeline...")
                df, _ = self.load_and_clean()
                return df
        except Exception as e:
            self.logger.error(f"Error loading cleaned data: {str(e)}")
            raise


if __name__ == "__main__":
    # Initialize loader
    loader = DataLoader()
    
    # Load and clean data
    df, stats = loader.load_and_clean()
    
    # Print results
    print("\nData Loading and Cleaning Results:")
    print("-" * 50)
    print(f"\nFinal dataset shape: {df.shape}")
    print("\nFeature names:")
    print(df.columns.tolist())
    print("\nData sample:")
    print(df.head())
    print("\nData statistics:")
    print(stats)
    print("\nData loading and cleaning process complete.")
    


