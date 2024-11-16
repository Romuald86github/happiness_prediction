import os
from datetime import datetime

class Config:
    """Configuration settings for the project"""
    def __init__(self):
        # Set up directories
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # src directory
        self.ROOT_DIR = os.path.dirname(self.BASE_DIR)  # root directory of the repo
        self.create_directories()

        # Data source
        self.DATA_URL = 'https://raw.githubusercontent.com/dsrscientist/DSData/master/happiness_score_dataset.csv'

        # Directories at root level
        self.DATA_DIR = os.path.join(self.ROOT_DIR, 'data')
        self.MODEL_DIR = os.path.join(self.ROOT_DIR, 'models')
        self.RESULTS_DIR = os.path.join(self.ROOT_DIR, 'results')
        self.LOGS_DIR = os.path.join(self.ROOT_DIR, 'logs')

        # File paths
        self.LOG_FILE = os.path.join(
            self.LOGS_DIR,
            f'processing_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        )
        self.MODEL_PIPELINE_PATH = os.path.join(
            self.MODEL_DIR,
            'preprocessing_pipeline.pkl'
        )
        self.RESULTS_PATH = os.path.join(
            self.RESULTS_DIR,
            f'model_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        self.CLEAN_DATA_PATH = os.path.join(
            self.DATA_DIR,
            'clean_data.csv'
        )
        self.PREPROCESSED_DATA_PATH = os.path.join(
            self.DATA_DIR,
            'preprocessed_data.csv'
        )
        self.MODEL_PATH = os.path.join(
            self.MODEL_DIR,
            'best_model.pkl'
    )


        # Data processing parameters
        self.RANDOM_STATE = 42
        self.TEST_SIZE = 0.25
        self.Z_SCORE_THRESHOLD = 2.5
        self.CV_FOLDS = 7

        # Outlier indices to remove
        self.OUTLIER_INDICES = [111, 119, 122, 73, 101, 147]

        # Columns configuration
        self.COLUMNS_TO_DROP = [
            'Country',
            'Region',
            'Happiness Rank',
            'Dystopia Residual',
            'Standard Error'
        ]
        self.TARGET_COLUMN = 'Happiness Score'
        self.FEATURES_TO_TRANSFORM = {
            'box_cox': [
                'Health (Life Expectancy)',
                'Family'
            ],
            'cube_root': [
                'Trust (Government Corruption)',
                'Generosity'
            ]
        }
        self.FEATURES_TO_DROP = [
            'Economy (GDP per Capita)'
        ]

        # Model training parameters
        self.MODEL_PARAMS = {
            'linear_regression': {
                'fit_intercept': [True, False],
                'copy_X': [True, False],
                'positive': [True, False]
            },
            'random_forest': {
                'n_estimators': [100, 200, 300],
                'max_depth': [None, 10, 20, 30],
                'min_samples_split': [2, 5, 10],
                'random_state': [self.RANDOM_STATE]
            }
        }

    def create_directories(self):
        """Create necessary directories if they don't exist"""
        # Create all directories in root
        root_directories = ['data', 'models', 'results', 'logs']
        for directory in root_directories:
            dir_path = os.path.join(self.ROOT_DIR, directory)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)


if __name__ == "__main__":
    # Test configuration
    config = Config()
    print("Configuration Settings:")
    print("-" * 50)
    print("\nDirectories:")
    print(f"Root Directory: {config.ROOT_DIR}")
    print(f"Source Directory: {config.BASE_DIR}")
    print(f"Data Directory: {config.DATA_DIR}")
    print(f"Models Directory: {config.MODEL_DIR}")
    print(f"Results Directory: {config.RESULTS_DIR}")
    print(f"Logs Directory: {config.LOGS_DIR}")
    
    print("\nFile Paths:")
    print(f"Clean Data Path: {config.CLEAN_DATA_PATH}")
    print(f"Preprocessed Data Path: {config.PREPROCESSED_DATA_PATH}")
    print(f"Model Pipeline Path: {config.MODEL_PIPELINE_PATH}")
    
    print("\nData Processing Parameters:")
    print(f"Random State: {config.RANDOM_STATE}")
    print(f"Test Size: {config.TEST_SIZE}")
    print(f"Z-Score Threshold: {config.Z_SCORE_THRESHOLD}")
    
    print("\nFeatures to Transform:")
    print(f"Box-Cox: {config.FEATURES_TO_TRANSFORM['box_cox']}")
    print(f"Cube Root: {config.FEATURES_TO_TRANSFORM['cube_root']}")
    
    print("\nOutlier Indices to Remove:")
    print(f"Indices: {config.OUTLIER_INDICES}")