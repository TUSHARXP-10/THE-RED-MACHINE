import pandas as pd
import numpy as np
import os
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from statsmodels.tsa.arima.model import ARIMA
import joblib
import mlflow
import logging
import xgboost as xgb
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

logger = logging.getLogger(__name__)

def load_warehouse_data(file_path='/opt/airflow/data/warehouse/financial_data.csv'):
    """Load data from Phase 1 warehouse"""
    df = pd.read_csv(file_path, parse_dates=['date'])
    df.set_index('date', inplace=True)
    return df

def train_linear_regression(df):
    """Baseline linear regression for cash flow prediction"""
    # Use available features from the pipeline
    feature_columns = ['volume', 'interest_rate', 'volatility', 'moving_avg_10', 'trend_indicator', 'rsi', 'macd', 'sentiment']
    available_features = [col for col in feature_columns if col in df.columns]
    
    # Create feature matrix and handle missing values
    X = df[available_features].copy()
    X = X.fillna(X.mean())  # Fill NaN with column means
    y = df['stock_price']  # Proxy for cash flow target; replace with actual target
    model = LinearRegression()
    model.fit(X, y)
    predictions = model.predict(X)
    mae = mean_absolute_error(y, predictions)
    rmse = np.sqrt(mean_squared_error(y, predictions))
    
    with mlflow.start_run():
        mlflow.log_param("model_type", "LinearRegression")
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("rmse", rmse)
        mlflow.sklearn.log_model(model, "model")
    
    logger.info(f"Linear Regression - MAE: {mae}, RMSE: {rmse}")
    return model

def train_arima(df):
    """Baseline ARIMA for time series forecasting"""
    model = ARIMA(df['stock_price'], order=(5,1,0))  # Adjust order based on data
    model_fit = model.fit()
    predictions = model_fit.forecast(steps=30)
    
    with mlflow.start_run():
        mlflow.log_param("model_type", "ARIMA")
        mlflow.log_param("order", "(5,1,0)")
        mlflow.statsmodels.log_model(model_fit, "model")
    
    logger.info("ARIMA model trained and logged.")
    return model_fit

def train_random_forest(df):
    """Basic ML baseline with Random Forest"""
    # Use available features from the pipeline
    feature_columns = ['volume', 'interest_rate', 'volatility', 'moving_avg_10', 'trend_indicator', 'rsi', 'macd', 'sentiment']
    available_features = [col for col in feature_columns if col in df.columns]
    
    # Create feature matrix and handle missing values
    X = df[available_features].copy()
    X = X.fillna(X.mean())  # Fill NaN with column means
    y = df['stock_price']
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    predictions = model.predict(X)
    mae = mean_absolute_error(y, predictions)
    rmse = np.sqrt(mean_squared_error(y, predictions))
    
    with mlflow.start_run():
        mlflow.log_param("model_type", "RandomForest")
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("rmse", rmse)
        mlflow.sklearn.log_model(model, "model")
    
    logger.info(f"Random Forest - MAE: {mae}, RMSE: {rmse}")
    
    # Save the model with a timestamp
    import os
    model_filename = f"/opt/airflow/models/rf_model_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pkl"
    os.makedirs(os.path.dirname(model_filename), exist_ok=True)
    joblib.dump(model, model_filename)
    logger.info(f"Random Forest model saved to {model_filename}")
    
    return model

def train_xgboost(df):
    """Train XGBoost model."""
    feature_cols = ['volume', 'volatility', 'moving_avg_10', 'trend_indicator', 'rsi', 'macd', 'sentiment']
    available_features = [col for col in feature_cols if col in df.columns]
    
    if not available_features:
        logger.warning("No valid features found for XGBoost training")
        return
    
    X = df[available_features]
    y = df['stock_price']
    
    # Drop NaN values
    X = X.fillna(X.mean())
    y = y.fillna(y.mean())
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = xgb.XGBRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    logger.info(f"XGBoost - MAE: {mae}, RMSE: {rmse}")
    
    with mlflow.start_run():
        mlflow.log_param("model_type", "XGBoost")
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("rmse", rmse)
        mlflow.xgboost.log_model(model, "model")
    
    model_filename = f'/opt/airflow/models/xgb_model_{pd.Timestamp.now().strftime("%Y%m%d_%H%M")}.pkl'
    os.makedirs(os.path.dirname(model_filename), exist_ok=True)
    joblib.dump(model, model_filename)
    logger.info(f"XGBoost model saved to {model_filename}")
    return model

def train_lstm(df):
    # For LSTM, we typically need sequential data. This is a simplified example.
    # You might need to prepare your data differently for a real LSTM.
    data = df['stock_price'].values.reshape(-1, 1)
    # Simple sequence creation for demonstration
    X, y = [], []
    for i in range(len(data) - 1):
        X.append(data[i:i+1])
        y.append(data[i+1])
    X, y = np.array(X), np.array(y)

    model = Sequential([
        LSTM(50, activation='relu', input_shape=(X.shape[1], X.shape[2])),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=10, verbose=0)

    predictions = model.predict(X).flatten()
    mae = mean_absolute_error(y, predictions)
    rmse = np.sqrt(mean_squared_error(y, predictions))

    with mlflow.start_run():
        mlflow.log_param("model_type", "LSTM")
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("rmse", rmse)
        mlflow.tensorflow.log_model(model, "model")

    logger.info(f"LSTM - MAE: {mae}, RMSE: {rmse}")
    return model

# Example usage (integrate into DAG)
def compute_sharpe(df):
    # Placeholder for Sharpe Ratio calculation
    # In a real scenario, this would involve portfolio returns and risk-free rate
    return 1.5 # Dummy value

def train_with_risk(df):
    # Example: Train XGBoost with risk features
    # Ensure 'volatility' column is present, if not, add a dummy or compute it
    if 'volatility' not in df.columns:
        df['volatility'] = df['stock_price'].rolling(window=20).std().fillna(df['stock_price'].std())
        
    # Use available features from the pipeline
    feature_columns = ['volume', 'interest_rate', 'volatility', 'moving_avg_10', 'trend_indicator', 'rsi', 'macd', 'sentiment']
    available_features = [col for col in feature_columns if col in df.columns]
    
    # Create feature matrix and handle missing values
    X = df[available_features].copy()
    X = X.fillna(X.mean())  # Fill NaN with column means
    y = df['stock_price']
    
    # Handle NaN values in X by filling with 0 or mean, depending on context
    X = X.fillna(0) # Or X.fillna(X.mean())

    model = xgb.XGBRegressor()
    model.fit(X, y)
    predictions = model.predict(X)
    
    # Ensure evaluate_risk_with_predictions is imported or defined
    from risk_management import evaluate_risk_with_predictions
    risk_df = evaluate_risk_with_predictions(df.copy(), predictions)
    
    # Log risk metrics to MLflow
    with mlflow.start_run(run_name="XGBoost_with_Risk_Features"):
        mlflow.log_param("model_type", "XGBoost_Risk_Adjusted")
        mlflow.log_metric("sharpe_ratio", compute_sharpe(risk_df))
        # Log other relevant metrics or artifacts
        mlflow.sklearn.log_model(model, "xgboost_risk_model")
        

if __name__ == "__main__":
    # Example Usage:
    # Create a dummy DataFrame for demonstration
    data = {
        'date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']),
        'stock_price': [100, 102, 101, 103, 105],
        'volume': [1000000, 1100000, 950000, 1050000, 1200000],
        'interest_rate': [0.01, 0.011, 0.012, 0.011, 0.013],
        'volatility': [1.5, 1.8, 1.6, 1.9, 2.1],
        'moving_avg_10': [100.5, 101.2, 100.8, 102.1, 103.5],
        'trend_indicator': [0, 1, 0, 1, 1],
        'rsi': [50, 55, 52, 58, 60],
        'macd': [0.5, 0.6, 0.55, 0.65, 0.7],
        'sentiment': [0.1, 0.2, 0.15, 0.25, 0.3]
    }
    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)

    # Train and log models
    train_linear_regression(df.copy())
    train_arima(df.copy())
    train_random_forest(df.copy())
    train_xgboost(df.copy())
    train_lstm(df.copy())
    train_with_risk(df.copy()) # Add this line to train with risk features