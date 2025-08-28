from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os
import joblib
import logging
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cash Flow Prediction API", version="1.0.0")

# Load model once at startup
model = None

class PredictionInput(BaseModel):
    data: dict  # e.g., {"stock_price": 72850.50, "volatility": 0.18, ...}

class PredictionOutput(BaseModel):
    prediction: float
    risk_flag: int
    position_size: float

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
    
    logger.info("Fallback model created")
    return model

def load_model():
    """Load the production model or create fallback"""
    global model
    try:
        model_path = Path("models/rf_model.pkl")
        if model_path.exists():
            model = joblib.load(model_path)
            logger.info(f"Model loaded from {model_path}")
        else:
            logger.warning("Model file not found, using fallback")
            model = create_fallback_model()
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        model = create_fallback_model()

# Load model on startup
load_model()

@app.get("/")
def root():
    """Root endpoint with API info"""
    return {
        "message": "Cash Flow Prediction API",
        "version": "1.0.0",
        "status": "running",
        "model_loaded": model is not None
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/predict", response_model=PredictionOutput)
def predict(input: PredictionInput):
    """Make a prediction based on input features"""
    try:
        if model is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
            
        df = pd.DataFrame([input.data])
        
        # Get model features
        if hasattr(model, 'feature_names_in_'):
            features = model.feature_names_in_
        else:
            features = [
                "stock_price", "volatility", "volume", "sma_20", "sma_50",
                "rsi", "macd", "bollinger_upper", "bollinger_lower",
                "india_vix", "indian_10y_yield", "inr_usd_rate", "rbi_repo_rate",
                "crude_oil_inr", "gold_price_inr", "fii_flows", "nifty_pe",
                "sensex_market_cap", "put_call_ratio"
            ]
        
        # Ensure all required features are present
        missing_features = set(features) - set(df.columns)
        for feat in missing_features:
            df[feat] = 0
        
        # Make prediction
        prediction = float(model.predict(df[features])[0])
        
        # Calculate risk metrics
        risk_flag = 1 if abs(prediction) > 100 else 0
        position_size = float(max(1, min(10, abs(prediction) / 100)))
        
        return PredictionOutput(
            prediction=prediction,
            risk_flag=risk_flag,
            position_size=position_size
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sample")
def get_sample_input():
    """Get sample input for testing"""
    return {
        "sample_input": {
            "stock_price": 72850.50,
            "volatility": 0.18,
            "volume": 2500000000,
            "sma_20": 71200.30,
            "sma_50": 69800.25,
            "rsi": 72.5,
            "macd": 850.2,
            "bollinger_upper": 74200.80,
            "bollinger_lower": 70100.70,
            "india_vix": 15.8,
            "indian_10y_yield": 7.25,
            "inr_usd_rate": 83.15,
            "rbi_repo_rate": 6.50,
            "crude_oil_inr": 6890.25,
            "gold_price_inr": 62450.00,
            "fii_flows": -1250.5,
            "nifty_pe": 22.4,
            "sensex_market_cap": 28500000,
            "put_call_ratio": 0.87
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)