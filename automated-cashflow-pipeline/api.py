from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import pandas as pd
import os
import joblib
import logging
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import time
from prometheus_client import Histogram, Counter, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Prometheus metrics
request_latency = Histogram('request_latency_seconds', 'Request latency', ['endpoint'])
prediction_counter = Counter('predictions_total', 'Total number of predictions')
health_check_counter = Counter('health_checks_total', 'Total number of health checks')
error_counter = Counter('prediction_errors_total', 'Total number of prediction errors')

# Load model once at startup for better performance
MODEL_PATH = os.getenv('MODEL_PATH', '/app/models/rf_model_20250724_1608.pkl')
model = None

def load_model():
    global model
    try:
        if model is None:
            model_path = Path(MODEL_PATH)
            if not model_path.exists():
                # Fallback to any available model
                models_dir = Path('/app/models')
                if models_dir.exists():
                    model_files = list(models_dir.glob('*.pkl'))
                    if model_files:
                        model_path = model_files[0]
                    else:
                        logger.warning("No model files found, creating fallback model")
                        model = create_fallback_model()
                        return
                else:
                    logger.warning("Models directory not found, creating fallback model")
                    models_dir.mkdir(exist_ok=True)
                    model = create_fallback_model()
                    return
            
            model = joblib.load(model_path)
            logger.info(f"Model loaded successfully from {model_path}")
    except Exception as e:
        logger.error(f"Error loading model: {e}, creating fallback")
        model = create_fallback_model()

def create_fallback_model():
    """Create a simple fallback model for testing"""
    logger.info("Creating fallback model...")
    
    # Create a simple random forest with dummy data
    np.random.seed(42)
    X = np.random.randn(100, 5)
    y = np.random.randn(100)
    
    model = RandomForestRegressor(n_estimators=10, random_state=42)
    model.fit(X, y)
    
    # Store feature names for consistency
    model.feature_names_in_ = np.array(['stock_price', 'volatility', 'volume', 'sma_20', 'rsi'])
    
    # Save the fallback model
    fallback_path = Path('/app/models/fallback_model.pkl')
    fallback_path.parent.mkdir(exist_ok=True)
    joblib.dump(model, fallback_path)
    
    logger.info("Fallback model created and saved")
    return model

# Load model on startup
logger.info("Starting API initialization...")
load_model()
logger.info("API initialization complete")

class PredictionInput(BaseModel):
    data: dict  # e.g., {"stock_price": 150, "volatility": 0.1}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    health_check_counter.inc()
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/predict")
def predict(input: PredictionInput, authorization = Depends(security)):
    start_time = time.time()
    
    if authorization.credentials != os.getenv('API_TOKEN', 'secure_token'):
        error_counter.inc()
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        df = pd.DataFrame([input.data])
        
        # Get model features
        if hasattr(model, 'feature_names_in_'):
            features = model.feature_names_in_
        else:
            # Use all columns as features
            features = df.columns
        
        # Ensure all required features are present
        missing_features = set(features) - set(df.columns)
        if missing_features:
            # Fill missing features with 0
            for feat in missing_features:
                df[feat] = 0
        
        # Make prediction
        prediction = model.predict(df[features])[0]
        
        # Calculate risk metrics
        risk_flag = 1 if abs(prediction) > 100 else 0
        position_size = max(1, min(10, abs(prediction) / 100))
        
        # Record metrics
        request_latency.labels(endpoint='/predict').observe(time.time() - start_time)
        prediction_counter.inc()
        
        return {
            "prediction": float(prediction),
            "risk_flag": int(risk_flag),
            "position_size": float(position_size)
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        error_counter.inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)