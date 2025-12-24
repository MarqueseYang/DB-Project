# Intelligent Insurance Claims System (NYU DB Project Part IV)

## Overview
This is an end-to-end database application that integrates MongoDB (NoSQL), XGBoost (Machine Learning), and Flask (Web API) to predict chronic disease risks for insurance claims.

## Features
* **Hybrid Data Pipeline**: Combines structured customer demographics with unstructured clinical notes.
* **Real-time Inference**: Uses XGBoost + Sentence-BERT to predict risk scores instantly upon claim submission.
* **Seamless Retraining**: Automated pipeline to fetch new data from MongoDB and retrain the model without downtime.
* **ODM Implementation**: Uses MongoEngine for strict schema validation.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Generate synthetic data: `python data_generator.py`
3. Run the server: `python app.py`

## API Endpoints
* `POST /submit_claim`: Submits a new claim and gets a risk prediction.
* `POST /retrain`: Triggers the model retraining process on the latest data.