
# Happiness Score Prediction

## Problem Statement

The World Happiness Report assesses national happiness levels using various socio-economic indicators, providing crucial insights for policy-making and social development. However, predicting happiness scores presents significant challenges that need urgent attention:

1. **Complex Relationship Understanding**: Traditional statistical methods struggle to capture the intricate, non-linear relationships between socio-economic factors and happiness scores. This limitation hampers policymakers' ability to make informed decisions about resource allocation and policy interventions.

2. **Data Quality and Consistency**: The available happiness data often suffers from missing values, inconsistencies, and quality issues across different countries and years. Without proper handling, these issues can lead to unreliable insights and potentially misguided policy decisions.

3. **Real-time Prediction Capability**: Current methods lack the ability to provide quick, reliable predictions for new scenarios or countries with incomplete data. This gap prevents timely interventions and policy adjustments that could improve societal well-being.

4. **Scalability and Automation**: Manual processing and analysis of happiness data is time-consuming and prone to errors. The lack of an automated system makes it difficult to update predictions efficiently as new data becomes available.

The consequences of not addressing these challenges include:
- Misallocation of resources in social development programs
- Delayed policy responses to declining happiness indicators
- Ineffective interventions due to incomplete understanding of happiness factors
- Inability to make data-driven decisions in social policy planning
- Wasted resources on manual data processing and analysis

## Solution Approach

Machine Learning (ML) has been chosen as the primary solution approach for several compelling reasons:

1. **Why Machine Learning?**
   - Ability to capture complex, non-linear relationships in happiness data
   - Automated feature importance analysis for better understanding of happiness drivers
   - Scalable processing of large datasets with minimal manual intervention
   - Robust handling of missing data and outliers
   - Capability to adapt and improve with new data

2. **ML vs Traditional Methods**
   Traditional approaches like:
   - Statistical regression: Limited to linear relationships
   - Survey analysis: Time-consuming and resource-intensive
   - Expert systems: Rigid and difficult to update
   - Manual analysis: Prone to human bias and errors
   
   ML overcomes these limitations through:
   - Automated pattern recognition
   - Adaptive learning from new data
   - Consistent and reproducible results
   - Scalable processing capabilities

3. **Selected ML Models and Justification**
   - Linear Regression: Baseline model for interpretability
   - Ridge/Lasso Regression: Handle multicollinearity in socio-economic factors
   - Random Forest: Capture non-linear relationships and feature interactions
   - Gradient Boosting: Optimize prediction accuracy through ensemble learning

4. **Specific ML Objectives**
   - Predict happiness scores with RMSE < 0.5
   - Identify top 5 contributing factors to happiness
   - Generate feature importance rankings for policy guidance
   - Provide confidence intervals for predictions
   - Enable real-time predictions through API

## Implementation Methodology

The project follows industry best practices in ML development:

1. **Data Pipeline**
   - Automated data cleaning and validation
   - Systematic handling of missing values and outliers
   - Feature engineering with Box-Cox and cube root transformations
   - consistent features scaling
   

2. **Model Development**
   - Cross-validation for robust evaluation
   - Hyperparameter tuning using GridSearchCV
   - Model comparison using multiple metrics (R², RMSE, MAE)
   - Feature importance analysis
 

3. **Production Pipeline**
   - Airflow DAG for automated workflow
   - Flask API with RESTful endpoints
   - Docker containerization for deployment
   - Comprehensive logging and monitoring
   - CI/CD pipeline for automated updates

4. **Quality Assurance**
   - Unit testing for all components
   - Integration testing for API endpoints
   - Performance monitoring and alerts
   - Regular model retraining triggers
   - Data drift detection

This methodical approach ensures a robust, maintainable solution that can reliably predict happiness scores and provide valuable insights for policy-making.


## how to reproduce the work

1. **setting up the environment**
   
- clone the repo
```bash
git clone https://github.com/Romuald86github/happiness_prediction.git
```
```bash
cd happiness_prediction
```

- initialise conda
```bash
conda init
```

- create a vitual environment
```bash
conda create -n env
```

- activate the environment 
```bash
conda activate env
```

2. **create and export a flask secret**

```bash
python scripts/generate_secret.py
```
```bash
export DEFAULT_SECRET_KEY=your_secret
```

3. **run the scripts for model development**

- you can either choose to run the main script which orchestrates the entire ML development workflow
```bash
python src/main.py
```

- or run scripts individualy

```bash
python src/data_loader.py
```
```bash
python src/preprocessing_pipeline.py
```
```bash
python src/model_trainer.py
```


4. **run the model deployment**

- run the app without docker
```bash
streamlit_app/streamlit_app1.py
```
- access the app at http://127.0.0.1:8501/ (you can navigate with the sidebar to monitor the datadrift and model performance)





