# test_model_loading.py - Simple script to test model loading

import os
import logging
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_model_loading():
    """Test loading the trading model"""
    logging.info("Testing model loading...")
    
    # Look for model files in the models directory
    model_dir = "./models"
    if not os.path.exists(model_dir):
        model_dir = "./automated-cashflow-pipeline/models"
        if not os.path.exists(model_dir):
            logging.error(f"Model directory not found at ./models or ./automated-cashflow-pipeline/models")
            return False
    
    logging.info(f"Found model directory: {model_dir}")
    
    # Find model files
    model_files = [f for f in os.listdir(model_dir) if f.endswith('.pkl')]
    if not model_files:
        logging.error(f"No model files found in {model_dir}")
        return False
    
    # Sort by date in filename if possible, otherwise just take the first one
    model_files.sort(reverse=True)
    model_path = os.path.join(model_dir, model_files[0])
    
    logging.info(f"Found model file: {model_path}")
    
    try:
        # Load the model
        logging.info(f"Loading model from {model_path}")
        model = joblib.load(model_path)
        logging.info("Model loaded successfully")
        
        # Get model type and info
        model_type = type(model).__name__
        logging.info(f"Model type: {model_type}")
        
        # Try to get model parameters
        try:
            params = model.get_params()
            logging.info(f"Model parameters: {params}")
        except:
            logging.info("Could not retrieve model parameters")
        
        # Create a sample input for prediction
        logging.info("Creating sample input for prediction test...")
        sample_input = pd.DataFrame({
            "stock_price": [150.25],
            "volatility": [0.15],
            "volume": [1000000],
            "sma_20": [148.50],
            "rsi": [55.0]
        })
        
        # Test prediction
        try:
            logging.info("Testing prediction with sample input...")
            prediction = model.predict(sample_input)
            logging.info(f"Prediction result: {prediction}")
            
            # Try to get prediction probability if available
            try:
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(sample_input)
                    logging.info(f"Prediction probability: {proba}")
            except:
                pass
                
            return True
        except Exception as e:
            logging.error(f"Prediction test failed: {e}")
            logging.error("This could indicate that the sample input format doesn't match what the model expects")
            return False
            
    except Exception as e:
        logging.error(f"Failed to load model: {e}")
        return False

if __name__ == "__main__":
    print("\n===== Model Loading Test =====\n")
    result = test_model_loading()
    print("\n===== Test Results =====")
    if result:
        print("✅ Model loading and prediction test successful!")
        print("Your model is ready to be used in the trading system.")
    else:
        print("❌ Model loading or prediction test failed!")
        print("Please check the logs above for details on what went wrong.")
    print("\n=================================")