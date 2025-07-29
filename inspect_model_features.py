import joblib
import os

MODEL_PATH = "models/rf_model_20250724_1608.pkl"

try:
    model = joblib.load(MODEL_PATH)
    if hasattr(model, 'feature_names_in_'):
        print("Model's expected features:", model.feature_names_in_)
    elif hasattr(model, 'n_features_in_'):
        print("Model expects", model.n_features_in_, "features.")
        print("Cannot determine feature names directly from model. Please check training script.")
    else:
        print("Could not determine model's expected features.")
except FileNotFoundError:
    print(f"Error: Model file not found at {MODEL_PATH}")
except Exception as e:
    print(f"Error loading model: {e}")