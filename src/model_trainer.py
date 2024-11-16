import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import joblib
import logging
from config import Config
from helpers import setup_logging

class ModelTrainer:
    """
    Handles model training, hyperparameter tuning, and evaluation for regression models
    """
    def __init__(self):
        self.config = Config()
        self.logger = setup_logging()
        self.models = self._initialize_models()
        self.best_model = None
        self.best_params = None
        self.model_results = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
    def load_preprocessed_data(self):
        """Load the preprocessed data"""
        try:
            self.logger.info(f"Loading preprocessed data from {self.config.PREPROCESSED_DATA_PATH}")
            df = pd.read_csv(self.config.PREPROCESSED_DATA_PATH)
            self.logger.info(f"Preprocessed data loaded successfully. Shape: {df.shape}")
            return df
        except Exception as e:
            self.logger.error(f"Error loading preprocessed data: {str(e)}")
            raise

    def _initialize_models(self):
        """Initialize models with their hyperparameter grids"""
        models = {
            'LinearRegression': {
                'model': LinearRegression(),
                'params': {
                    'fit_intercept': [True, False]
                }
            },
            'Ridge': {
                'model': Ridge(random_state=self.config.RANDOM_STATE),
                'params': {
                    'alpha': [0.1, 1.0, 10.0],
                    'fit_intercept': [True, False]
                }
            },
            'Lasso': {
                'model': Lasso(random_state=self.config.RANDOM_STATE),
                'params': {
                    'alpha': [0.1, 1.0, 10.0],
                    'fit_intercept': [True, False]
                }
            },
            'RandomForest': {
                'model': RandomForestRegressor(random_state=self.config.RANDOM_STATE),
                'params': {
                    'n_estimators': [100, 200],
                    'max_depth': [10, 20, None],
                    'min_samples_split': [2, 5]
                }
            },
            'GradientBoosting': {
                'model': GradientBoostingRegressor(random_state=self.config.RANDOM_STATE),
                'params': {
                    'n_estimators': [100, 200],
                    'learning_rate': [0.01, 0.1],
                    'max_depth': [3, 5]
                }
            }
        }
        return models
    
    def train_test_split(self, X, y):
        """Split data into training and testing sets"""
        return train_test_split(
            X, y,
            test_size=self.config.TEST_SIZE,
            random_state=self.config.RANDOM_STATE
        )
    
    def train_models(self, X, y):
        """Train and evaluate all models"""
        self.logger.info("Starting model training...")
        
        # Split data
        self.X_train, self.X_test, self.y_train, self.y_test = self.train_test_split(X, y)
        self.model_results = {}
        
        # Train each model
        for model_name, model_info in self.models.items():
            self.logger.info(f"\nTraining {model_name}...")
            
            # Perform grid search
            grid_search = GridSearchCV(
                estimator=model_info['model'],
                param_grid=model_info['params'],
                cv=self.config.CV_FOLDS,
                scoring='r2',
                n_jobs=-1
            )
            
            # Fit model
            grid_search.fit(self.X_train, self.y_train)
            
            # Store results
            self.model_results[model_name] = {
                'model': grid_search.best_estimator_,
                'best_params': grid_search.best_params_,
                'metrics': self._evaluate_model(grid_search.best_estimator_)
            }
            
            # Log results
            self._log_model_results(model_name)
        
        # Select best model
        self._select_best_model()
        return self.model_results
    
    def _evaluate_model(self, model):
        """Calculate performance metrics for a model"""
        # Make predictions
        train_pred = model.predict(self.X_train)
        test_pred = model.predict(self.X_test)
        
        # Calculate metrics
        metrics = {
            'train_r2': r2_score(self.y_train, train_pred),
            'test_r2': r2_score(self.y_test, test_pred),
            'train_mae': mean_absolute_error(self.y_train, train_pred),
            'test_mae': mean_absolute_error(self.y_test, test_pred),
            'train_rmse': np.sqrt(mean_squared_error(self.y_train, train_pred)),
            'test_rmse': np.sqrt(mean_squared_error(self.y_test, test_pred))
        }
        
        # Add cross-validation scores
        cv_scores = cross_val_score(
            model, 
            self.X_train, 
            self.y_train, 
            cv=self.config.CV_FOLDS, 
            scoring='r2'
        )
        
        metrics['cv_mean'] = cv_scores.mean()
        metrics['cv_std'] = cv_scores.std()
        
        return metrics
    
    def _log_model_results(self, model_name):
        """Log model results"""
        results = self.model_results[model_name]
        metrics = results['metrics']
        
        self.logger.info(f"\nResults for {model_name}:")
        self.logger.info(f"Best Parameters: {results['best_params']}")
        self.logger.info(f"Train R2: {metrics['train_r2']:.4f}")
        self.logger.info(f"Test R2: {metrics['test_r2']:.4f}")
        self.logger.info(f"Train RMSE: {metrics['train_rmse']:.4f}")
        self.logger.info(f"Test RMSE: {metrics['test_rmse']:.4f}")
        self.logger.info(f"CV Score: {metrics['cv_mean']:.4f} (+/- {metrics['cv_std']*2:.4f})")
    
    def _select_best_model(self):
        """Select the best model based on test R2 score"""
        best_score = float('-inf')
        best_model_name = None
        
        for model_name, results in self.model_results.items():
            test_score = results['metrics']['test_r2']
            if test_score > best_score:
                best_score = test_score
                best_model_name = model_name
        
        self.best_model = self.model_results[best_model_name]['model']
        self.best_params = self.model_results[best_model_name]['best_params']
        
        self.logger.info(f"\nBest Model: {best_model_name}")
        self.logger.info(f"Test R2 Score: {best_score:.4f}")
    
    def save_best_model(self):
        """Save the best model and its metadata"""
        if self.best_model is None:
            raise ValueError("No model has been trained yet")
        
        model_data = {
            'model': self.best_model,
            'params': self.best_params,
            'feature_names': list(self.X_train.columns)
        }
        
        joblib.dump(model_data, self.config.MODEL_PATH)
        self.logger.info(f"Model saved to {self.config.MODEL_PATH}")
        
    def save_results(self):
        """Save training results to CSV"""
        results_df = pd.DataFrame()
        for model_name, result in self.model_results.items():
            metrics = result['metrics']
            row = {
                'model': model_name,
                'test_r2': metrics['test_r2'],
                'test_rmse': metrics['test_rmse'],
                'cv_score': metrics['cv_mean'],
                'cv_std': metrics['cv_std'],
                'best_params': str(result['best_params'])
            }
            results_df = pd.concat([results_df, pd.DataFrame([row])], ignore_index=True)
        
        results_df.to_csv(self.config.RESULTS_PATH, index=False)
        self.logger.info(f"Results saved to {self.config.RESULTS_PATH}")


if __name__ == "__main__":
    # Initialize trainer
    trainer = ModelTrainer()
    
    # Load preprocessed data
    df = trainer.load_preprocessed_data()
    
    # Prepare features and target
    X = df.drop(columns=[trainer.config.TARGET_COLUMN])
    y = df[trainer.config.TARGET_COLUMN]
    
    # Train models
    results = trainer.train_models(X, y)
    
    # Save best model and results
    trainer.save_best_model()
    trainer.save_results()
    
    # Print summary
    print("\nModel Training Summary:")
    print("-" * 50)
    
    for model_name, result in results.items():
        metrics = result['metrics']
        print(f"\n{model_name}:")
        print(f"Best Parameters: {result['best_params']}")
        print(f"Test R2 Score: {metrics['test_r2']:.4f}")
        print(f"Test RMSE: {metrics['test_rmse']:.4f}")
        print(f"CV Score: {metrics['cv_mean']:.4f} (+/- {metrics['cv_std']*2:.4f})")