import joblib
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from src.preprocessing_pipeline import PreprocessingPipeline
from src.config import Config

def fix_pipeline():
    config = Config()
    # Load the existing pipeline
    try:
        pipeline = joblib.load(config.MODEL_PIPELINE_PATH)
        # Create a new pipeline instance
        new_pipeline = PreprocessingPipeline()
        # Copy all attributes
        new_pipeline.feature_means = pipeline.feature_means
        new_pipeline.feature_stds = pipeline.feature_stds
        new_pipeline.boxcox_lambdas = pipeline.boxcox_lambdas
        new_pipeline.feature_names = pipeline.feature_names
        # Save with explicit module name
        joblib.dump(new_pipeline, config.MODEL_PIPELINE_PATH, protocol=4)
        print("Pipeline successfully fixed and saved!")
    except Exception as e:
        print(f"Error fixing pipeline: {str(e)}")

if __name__ == "__main__":
    fix_pipeline()