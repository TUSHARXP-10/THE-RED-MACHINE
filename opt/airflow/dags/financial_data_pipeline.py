from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import requests
import os
import pandas as pd
import numpy as np
import logging
from financial_data_quality_monitor import FinancialDataQualityMonitor
import mlflow
from baseline_models import train_linear_regression, train_arima, train_random_forest, train_xgboost, train_lstm, train_with_risk
from advanced_features import add_advanced_features
from risk_management import evaluate_risk_with_predictions
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_fixed
from datetime import timedelta

# Set up logging
logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def fetch_alpha_vantage_data(symbol, api_key):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
    response = requests.get(url)
    
    if response.status_code == 429:
        logger.error(f"Alpha Vantage API rate limit exceeded. Status: {response.status_code}")
        raise requests.exceptions.HTTPError("Alpha Vantage API rate limit exceeded")
    elif response.status_code != 200:
        logger.error(f"Alpha Vantage API request failed. Status: {response.status_code}, Response: {response.text}")
        response.raise_for_status()
    
    return response.json()

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def fetch_fred_data(series_id, api_key):
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json"
    response = requests.get(url)
    
    if response.status_code == 429:
        logger.error(f"FRED API rate limit exceeded. Status: {response.status_code}")
        raise requests.exceptions.HTTPError("FRED API rate limit exceeded")
    elif response.status_code == 403:
        logger.error(f"FRED API key invalid or expired. Status: {response.status_code}")
        raise requests.exceptions.HTTPError("Invalid FRED API key")
    elif response.status_code != 200:
        logger.error(f"FRED API request failed. Status: {response.status_code}, Response: {response.text}")
        response.raise_for_status()
    
    return response.json()

def extract_financial_data(**context):
    logger.info("Extracting live financial data...")
    alpha_vantage_key = os.getenv('ALPHA_VANTAGE_KEY')
    fred_api_key = os.getenv('FRED_API_KEY')
    symbols = ['IBM', 'MSFT']  # Customize with your assets
    data = []

    # Fetch stock data
    for symbol in symbols:
        try:
            response = fetch_alpha_vantage_data(symbol, alpha_vantage_key)
            time_series = response.get('Time Series (Daily)', {})
            for date, values in time_series.items():
                data.append({
                    'date': pd.to_datetime(date),
                    'stock_price': float(values['4. close']),
                    'volume': int(values['5. volume']),
                    'symbol': symbol
                })
        except Exception as e:
            logger.error(f"Error fetching data for {symbol} from Alpha Vantage: {e}")
            continue

    df = pd.DataFrame(data)
    logger.info(f"Extracted {len(df)} rows from Alpha Vantage. Columns: {df.columns.tolist()}")

    if df.empty:
        logger.error("DataFrame is empty after Alpha Vantage data extraction. Creating dummy data for debugging.")
        df = pd.DataFrame({
            'date': pd.date_range(start='2024-01-01', periods=30),
            'stock_price': [100.0 + i * 0.5 for i in range(30)],
            'volume': [1000000 + i * 10000 for i in range(30)],
            'symbol': ['DUMMY'] * 30
        })

    # Fetch interest rate (FRED example)
    try:
        fred_response = fetch_fred_data('FEDFUNDS', fred_api_key)
        fred_data = fred_response.get('observations', [])
        interest_rates = []
        for obs in fred_data:
            interest_rates.append({
                'date': pd.to_datetime(obs['date']),
                'interest_rate': float(obs['value'])
            })
        fred_df = pd.DataFrame(interest_rates)
        df = pd.merge(df, fred_df, on='date', how='left')
        df['interest_rate'] = df['interest_rate'].fillna(method='ffill')
    except Exception as e:
        logger.error(f"Error fetching data from FRED: {e}")
        df['interest_rate'] = 0.03  # Fallback value

    logger.info(f"Pushing extracted data to XCom. DataFrame shape: {df.shape}, columns: {df.columns.tolist()}")
    context['task_instance'].xcom_push(key='extracted_data', value=df)
    logger.info("Live extraction complete.")

def validate_data_quality(**context):
    """Perform data quality checks"""
    logger.info("Validating data quality...")
    df = context['task_instance'].xcom_pull(key='extracted_data')
    monitor = FinancialDataQualityMonitor()
    quality_config = {
        'required_columns': ['date', 'stock_price', 'volume', 'interest_rate'],
        'validation_rules': {
            'stock_price': {'dtype': 'numeric', 'min_value': 0},
            'volume': {'dtype': 'numeric', 'min_value': 0},
            'interest_rate': {'dtype': 'numeric', 'min_value': 0}
        }
    }
    report = monitor.generate_quality_report(df, quality_config)
    if report is None:
        logger.error("Quality report generation failed: returned None")
        raise ValueError("Data quality report could not be generated")
    
    quality_score = report.get('overall_quality_score', 100)
    if quality_score < 90:
        raise ValueError(f"Data quality below threshold: {report}")
    logger.info(f"Pushing validated data to XCom. DataFrame shape: {df.shape}, columns: {df.columns.tolist()}")
    context['task_instance'].xcom_push(key='validated_data', value=df)
    logger.info("Data quality validation passed.")

def build_features(**context):
    """Build financial features"""
    logger.info("Building features...")
    df = context['task_instance'].xcom_pull(key='validated_data')
    if df is None:
        logger.error("No data received from validate_data_quality task")
        raise ValueError("No data received from validate_data_quality task")

    logger.info(f"Received DataFrame for feature building. Shape: {df.shape}, columns: {df.columns.tolist()}")

    if 'stock_price' not in df.columns:
        logger.error(f"'stock_price' column missing. Available columns: {df.columns.tolist()}")
        raise KeyError("'stock_price' column not found in DataFrame")

    df['volatility'] = df['stock_price'].rolling(window=20).std()
    df['moving_avg_10'] = df['stock_price'].rolling(window=10).mean()
    df['trend_indicator'] = np.where(df['stock_price'] > df['moving_avg_10'], 1, 0)
    
    logger.info(f"Feature building complete. New DataFrame shape: {df.shape}, columns: {df.columns.tolist()}")
    context['task_instance'].xcom_push(key='featured_data', value=df)
    logger.info("Feature building complete.")

def load_to_warehouse(**context):
    """Load processed data to warehouse"""
    logger.info("Loading to warehouse...")
    df = context['task_instance'].xcom_pull(key='featured_data')
    output_dir = '/opt/airflow/data/warehouse'
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(os.path.join(output_dir, 'financial_data.csv'), index=False)
    with mlflow.start_run():
        mlflow.log_param("rows_loaded", len(df))
        mlflow.log_artifact('/opt/airflow/data/warehouse/financial_data.csv')
    logger.info("Data loaded to warehouse.")

# DAG Configuration
default_args = {
    'owner': 'data-engineering',
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': True,
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'financial_data_pipeline_phase1',
    default_args=default_args,
    schedule_interval=timedelta(hours=6),
    catchup=False,
    tags=['finance', 'phase1', 'compliance']
)

# Define tasks
extract_task = PythonOperator(
    task_id='extract_financial_data',
    python_callable=extract_financial_data,
    provide_context=True,
    dag=dag
)

validate_task = PythonOperator(
    task_id='validate_data_quality',
    python_callable=validate_data_quality,
    provide_context=True,
    dag=dag
)

feature_task = PythonOperator(
    task_id='build_features',
    python_callable=build_features,
    provide_context=True,
    dag=dag
)

load_task = PythonOperator(
    task_id='load_to_warehouse',
    python_callable=load_to_warehouse,
    provide_context=True,
    dag=dag
)

# Set task dependencies
extract_task >> validate_task >> feature_task >> load_task