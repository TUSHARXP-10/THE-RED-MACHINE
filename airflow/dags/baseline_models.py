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
    # Handle NaN values properly
    X = X.fillna(X.mean())  # Fill NaN with column means
    # Handle any remaining NaNs (in case a column is all NaN)
    X = X.fillna(0)
    
    y = df['stock_price'].copy()  # Proxy for cash flow target; replace with actual target
    y = y.fillna(y.mean())  # Handle NaNs in target
    
    model = LinearRegression()
    model.fit(X, y)
    predictions = model.predict(X)
    mae = mean_absolute_error(y, predictions)
    rmse = np.sqrt(mean_squared_error(y, predictions))
    
    with mlflow.start_run(run_name="Linear Regression Training"):
        mlflow.log_param("model_type", "LinearRegression")
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("rmse", rmse)
        mlflow.sklearn.log_model(model, "linear_regression", input_example=X.sample(1))
    
    logger.info(f"Linear Regression - MAE: {mae}, RMSE: {rmse}")
    return model

def train_arima(df):
    """Baseline ARIMA for time series forecasting"""
    # Ensure datetime index with daily frequency
    df.index = pd.to_datetime(df.index)
    df = df.asfreq('D')  # Set daily frequency to suppress statsmodels warnings
    
    # Handle NaN values in the time series
    ts = df['stock_price'].copy()
    ts = ts.fillna(method='ffill')  # Forward fill
    ts = ts.fillna(method='bfill')  # Backward fill for any remaining NaNs at the beginning
    
    try:
        # Try with a simpler ARIMA model first
        model = ARIMA(ts, order=(1,1,0))  # Simpler model to avoid Schur decomposition errors
        model_fit = model.fit()
        predictions = model_fit.forecast(steps=30)
        
        with mlflow.start_run(run_name="ARIMA Training"):
            mlflow.log_param("model_type", "ARIMA")
            mlflow.log_param("order", "(1,1,0)")
            mlflow.statsmodels.log_model(model_fit, "arima_model")
        
        logger.info("ARIMA model trained and logged.")
        return model_fit
    except Exception as e:
        logger.warning(f"ARIMA model training failed with error: {str(e)}. Using simple moving average instead.")
        # Fallback to a simple moving average model
        ts_mean = ts.mean()
        predictions = [ts_mean] * 30
        
        with mlflow.start_run(run_name="Fallback Moving Average"):
            mlflow.log_param("model_type", "Moving Average Fallback")
            mlflow.log_param("reason", f"ARIMA failed: {str(e)}")
            mlflow.log_metric("mean_value", ts_mean)
        
        logger.info("Fallback moving average model logged.")
        return None  # Return None as we don't have a proper model object

def train_random_forest(df):
    """Basic ML baseline with Random Forest"""
    # Use available features from the pipeline
    feature_columns = ['volume', 'interest_rate', 'volatility', 'moving_avg_10', 'trend_indicator', 'rsi', 'macd', 'sentiment']
    available_features = [col for col in feature_columns if col in df.columns]
    
    # Create feature matrix and handle missing values
    X = df[available_features].copy()
    # Handle NaN values properly
    X = X.fillna(X.mean())  # Fill NaN with column means
    # Handle any remaining NaNs (in case a column is all NaN)
    X = X.fillna(0)
    
    y = df['stock_price'].copy()
    y = y.fillna(y.mean())  # Handle NaNs in target
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    predictions = model.predict(X)
    mae = mean_absolute_error(y, predictions)
    rmse = np.sqrt(mean_squared_error(y, predictions))
    
    with mlflow.start_run(run_name="Random Forest Training"):
        mlflow.log_param("model_type", "RandomForest")
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("rmse", rmse)
        mlflow.sklearn.log_model(model, "random_forest", input_example=X.sample(1))
    
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
    
    X = df[available_features].copy()
    y = df['stock_price'].copy()
    
    # Handle NaN values properly
    X = X.fillna(X.mean())  # Fill NaN with column means
    X = X.fillna(0)  # Handle any remaining NaNs (in case a column is all NaN)
    y = y.fillna(y.mean())  # Handle NaNs in target
    
    # Check if we have enough samples for train-test split
    if len(X) <= 1:
        logger.warning("Not enough samples for train-test split in XGBoost training. Using all data for training.")
        X_train, X_test, y_train, y_test = X, X, y, y  # Use all data for both training and testing
    else:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = xgb.XGBRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    logger.info(f"XGBoost - MAE: {mae}, RMSE: {rmse}")
    
    with mlflow.start_run(run_name="XGBoost Training"):
        mlflow.log_param("model_type", "XGBoost")
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("rmse", rmse)
        mlflow.xgboost.log_model(model, "xgboost", input_example=X_train.sample(1))
    
    model_filename = f'/opt/airflow/models/xgb_model_{pd.Timestamp.now().strftime("%Y%m%d_%H%M")}.pkl'
    os.makedirs(os.path.dirname(model_filename), exist_ok=True)
    joblib.dump(model, model_filename)
    logger.info(f"XGBoost model saved to {model_filename}")
    return model

def train_lstm(df):
    # For LSTM, we typically need sequential data. This is a simplified example.
    # You might need to prepare your data differently for a real LSTM.
    
    # Handle NaN values in the stock price data
    stock_prices = df['stock_price'].copy()
    stock_prices = stock_prices.fillna(method='ffill')  # Forward fill
    stock_prices = stock_prices.fillna(method='bfill')  # Backward fill for any remaining NaNs
    stock_prices = stock_prices.fillna(stock_prices.mean())  # Handle any remaining NaNs
    
    data = stock_prices.values.reshape(-1, 1)
    
    # Check if we have enough data for sequence creation
    if len(data) <= 1:
        logger.warning("Not enough samples for LSTM training. Need at least 2 data points.")
        # Create dummy data for LSTM if we don't have enough real data
        # This is just to avoid errors, the model won't be useful
        X = np.array([[[stock_prices.mean()]]])
        y = np.array([stock_prices.mean()])
    else:
        # Simple sequence creation for demonstration
        X, y = [], []
        for i in range(len(data) - 1):
            X.append(data[i:i+1])
            y.append(data[i+1])
        X, y = np.array(X), np.array(y)

    from tensorflow.keras.layers import Input
    
    model = Sequential([
        Input(shape=(X.shape[1], X.shape[2])),
        LSTM(50, activation='relu'),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=10, verbose=0)

    predictions = model.predict(X).flatten()
    mae = mean_absolute_error(y, predictions)
    rmse = np.sqrt(mean_squared_error(y, predictions))

    with mlflow.start_run(run_name="LSTM Training"):
        mlflow.log_param("model_type", "LSTM")
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("rmse", rmse)
        mlflow.tensorflow.log_model(model, "lstm", input_example=X[:1])

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
    # Handle NaN values properly
    X = X.fillna(X.mean())  # Fill NaN with column means
    X = X.fillna(0)  # Handle any remaining NaNs (in case a column is all NaN)
    
    y = df['stock_price'].copy()
    y = y.fillna(y.mean())  # Handle NaNs in target

    # Check if we have enough data to train
    if len(X) <= 1:
        logger.warning("Not enough samples for XGBoost with Risk training. Using a simple model.")
        # Create a simple model that just predicts the mean
        mean_value = y.mean()
        predictions = np.array([mean_value] * len(X))
        
        # Create a dummy model that just returns the mean
        model = xgb.XGBRegressor()
        if len(X) > 0:  # Only fit if we have at least one sample
            model.fit(X, y)
            predictions = model.predict(X)
    else:
        model = xgb.XGBRegressor()
        model.fit(X, y)
        predictions = model.predict(X)
    
    # Ensure evaluate_risk_with_predictions is imported or defined
    from risk_management import evaluate_risk_with_predictions
    risk_df = evaluate_risk_with_predictions(df.copy(), predictions)
    
    # Log risk metrics to MLflow
    with mlflow.start_run(run_name="XGBoost with Risk Features"):
        mlflow.log_param("model_type", "XGBoost_Risk_Adjusted")
        mlflow.xgboost.log_model(model, "xgboost_risk", input_example=X.sample(1))
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