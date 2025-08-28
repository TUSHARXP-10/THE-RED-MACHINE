from breeze_connect import BreezeConnect
import os
from dotenv import load_dotenv
from datetime import datetime
import joblib  # for saving models
import pandas as pd
import numpy as np
import ta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import schedule
import time
import csv # For trade logging
from alerts import send_alert
import sys # Added for sys.argv check
import argparse # Import for command-line argument parsing
from prompt_tracker import log_prompt # Import the logging function

MODEL_DIR = "models"
LOG_FILE = "model_log.txt"
os.makedirs(MODEL_DIR, exist_ok=True)

def validate_data(df):
    print(f"Effective shape: {df.shape}")
    print("\nFeatures:", list(df.columns) if df.shape[1] > 5 else "INSUFFICIENT")
    print("\nSample head:\n", df.head())

def check_data_integrity(df):
    print("\nData Shape:", df.shape)

    print("\nClass Distribution:")
    print(df['target'].value_counts(normalize=True))

    print("\nMissing Values:")
    print(df.isnull().sum())

def retrain_model(df, args):
    # Ensure df is a copy to avoid SettingWithCopyWarning
    df = df.copy()

    df = df.dropna()

    # Define all 27 features based on previous validation output
    features = [
        'IV_zscore', 'oi_change', 'rsi', 'sma_10', 'minute_sin', 'minute_cos',
        'spread_pct', 'oi_momentum', 'open', 'high', 'low', 'close', 'volume',
        'VWAP', 'ATR', 'ADX', 'CCI', 'MACD', 'MACD_signal', 'OBV', 'Stochastic_K',
        'Stochastic_D', 'Ultimate_Oscillator', 'Williams_R', 'Bollinger_Bands_Upper',
        'Bollinger_Bands_Lower', 'Donchian_Channel_Upper', 'Donchian_Channel_Lower'
    ]

    # Calculate target if not already present (for original data)
    if 'target' not in df.columns:
        df['target'] = (df['last_traded_price'].shift(-1) > df['last_traded_price']).astype(int).loc[df.index]

    # Filter out NaN values that might result from shift operations on target
    df = df.dropna(subset=['target'])
    from imblearn.over_sampling import SMOTE
    # Determine the DataFrame to use (original or augmented)
    current_df = df.copy() # Start with a copy of the original df

    if args.augmented_data:
        try:
            current_df = pd.read_csv(args.augmented_data)
            print(f"Loaded augmented data with {len(current_df)} samples")
        except Exception as e:
            print(f"Error loading augmented data: {e}")
            return

    # Ensure 'target' column exists in current_df before proceeding
    if 'target' not in current_df.columns:
        print("Error: 'target' column not found in the dataset. Cannot proceed with retraining.")
        return

    X = current_df.drop('target', axis=1)
    y = current_df['target']

    if args.data_validation:
        validate_data(current_df)

    if args.use_smote:
        print("Applying SMOTE for class balancing...")
        smote = SMOTE()
        X, y = smote.fit_resample(X, y)
        print(f"After SMOTE: {len(X)} samples")
        print(f"Class distribution: {pd.Series(y).value_counts(normalize=True)}")

    if args.show_sample > 0:
        print(f"\nShowing {args.show_sample} raw data samples:")
        print(df.head(args.show_sample))

    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=args.shuffle_data, test_size=args.test_size)

    print(f"\nShape of X_train: {X_train.shape}")
    print(f"Shape of y_train: {y_train.shape}")
    print(f"Shape of X_test: {X_test.shape}")
    print(f"Shape of y_test: {y_test.shape}")
    print(f"\nSample y_train values:\n{y_train.head()}")
    print(f"\nSample y_test values:\n{y_test.head()}")

    clf = RandomForestClassifier()
    clf.fit(X_train, y_train)
    accuracy = clf.score(X_test, y_test)

    # Save model with timestamp
    model_file = os.path.join(MODEL_DIR, f"rf_model_{datetime.now().strftime('%Y%m%d_%H%M')}.pkl")
    joblib.dump(clf, model_file)

    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} | {model_file} | Accuracy: {accuracy:.4f}\n")

    return clf, accuracy

def should_deploy_model(current_acc, threshold=0.60):
    if current_acc >= threshold:
        return True
    print(f"Model rejected: Accuracy below threshold ({current_acc:.2f})")
    return False

def fetch_latest_data():
    option_chain = breeze.get_option_chain_quotes(
        stock_code="SENSEX",
        exchange_code="BSE",
        expiry_date="2025-07-31",
        right="Call",
        strike_price="75000"
    )
    df = pd.DataFrame(option_chain['results'])
    df.to_csv("sensex_options.csv", index=False)
    return pd.read_csv("sensex_options.csv")

# 2. ICICI Breeze API Connection
# Load environment variables from .env file
load_dotenv()

api_key = os.getenv('ICICI_API_KEY')
api_secret = os.getenv('ICICI_API_SECRET')
session_token = os.getenv('ICICI_SESSION_TOKEN')

# 3. Fetch SENSEX Options Data (Now part of fetch_latest_data function)

# 4. Data Preprocessing & Feature Engineering
def preprocess_data(df):
    # Convert categorical features to numerical using one-hot encoding
    if 'option_type' in df.columns:
        df = pd.get_dummies(df, columns=['option_type'], drop_first=True)

    # Ensure 'Date' column is datetime for time-based features
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')

        df['IV_zscore'] = (df['implied_volatility'] - df['implied_volatility'].mean()) / df['implied_volatility'].std()
        df['oi_change'] = df['open_interest'].diff()
        df['rsi'] = ta.momentum.RSIIndicator(df['last_traded_price'], window=14).rsi()
        df['sma_10'] = df['last_traded_price'].rolling(window=10).mean()

        # Time-of-day encoded as sin/cos cycles (captures intraday volatility waves)
        df['minute_of_day'] = df.index.hour * 60 + df.index.minute
        df['minute_sin'] = np.sin(2 * np.pi * df['minute_of_day'] / 1440)
        df['minute_cos'] = np.cos(2 * np.pi * df['minute_of_day'] / 1440)

        # Normalized spread estimates (ATM only)
        df['price_spread'] = df['ask_price'] - df['bid_price']
        df['spread_pct'] = df['price_spread'] / (df['ask_price'] + df['bid_price']).replace(0, np.nan)

        # OI momentum
        df['oi_momentum'] = df['open_interest'].diff().rolling(5).mean()

    # Strategy 1: Directional Play
    df['directional_buy'] = (df['rsi'] < 30) & (df['IV_zscore'] < 0)

    # Strategy 2: Gamma scalping (reverse mean reversion)
    df['gamma_buy'] = (df['IV_zscore'] > 1) & (df['rsi'] > 60)

    # Risk-Based Sizing: Volatility-Aware Positioning
    from ta.volatility import AverageTrueRange
    window = 5 if len(df) < 20 else 14
    try:
            df['atr'] = AverageTrueRange(high=df['high'], low=df['low'], close=df['last_traded_price'], window=window).average_true_range()
    except Exception as e:
        print(f"Error calculating ATR: {e}")
        df['atr'] = np.nan # Assign NaN or a default value in case of error
    df['risk_weight'] = 1 / (df['atr'] / df['last_traded_price'])  # lower volatility → bigger size
    # Handle infinite values in risk_weight (e.g., from atr being 0)
    df['risk_weight'] = df['risk_weight'].replace([np.inf, -np.inf], np.nan)
    # Fill NaN values with the mean of the finite risk_weight values
    df['risk_weight'] = df['risk_weight'].fillna(df['risk_weight'].mean())



    max_qty = 50  # lot exposure control
    df['position_size'] = (df['risk_weight'] / df['risk_weight'].max() * max_qty).astype(int)




    # Fill NaN values for specific columns that are likely to have them due to window calculations
    df['rsi'] = df['rsi'].fillna(0) # Or df['rsi'].bfill().ffill() for time-series imputation
    df['sma_10'] = df['sma_10'].fillna(0) # Or df['sma_10'].bfill().ffill()
    df['oi_change'] = df['oi_change'].fillna(0) # Or df['oi_change'].bfill().ffill()
    df['oi_momentum'] = df['oi_momentum'].fillna(0) # Or df['oi_momentum'].bfill().ffill()

    # Drop any remaining non-numeric columns that are not features
    # This is a safeguard to ensure all columns are numeric before model training
    for col in df.columns:
        if df[col].dtype == 'object':
            df = df.drop(columns=[col])

    return df

    # Drop any remaining NaNs that were not specifically handled
    df = df.dropna()



    return df

# 5. Signal Generation: Rule-Based Logic
# Example: Simple Buy/Sell/Hold Signal
def generate_signal(row):
    if row['rsi'] < 30 and row['IV_zscore'] < -1:
        return 'BUY'
    elif row['rsi'] > 70 and row['IV_zscore'] > 1:
        return 'SELL'
    else:
        return 'HOLD'

def validate_trade(row):
    if row['last_traded_price'] <= 10: return False   # Avoid penny options
    if row['open_interest'] < 300: return False        # Avoid illiquid contracts
    if abs(row['IV_zscore']) > 4: return False         # Spikes → Potential manipulation
    if row['signal'] not in ['BUY', 'SELL']: return False
    return True

def log_trade(row, status):
    with open("trade_log.csv", mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            row.get('option_type'),
            row.get('strike_price'),
            row.get('expiry_date'),
            row.get('last_traded_price'),
            row.get('signal'),
            status
        ])

def load_latest_model(model_dir="models"):
    models = sorted([f for f in os.listdir(model_dir) if f.endswith(".pkl")])
    if not models:
        return None
    return joblib.load(os.path.join(model_dir, models[-1]))

def backtest_from_file(file="sensex_options.csv"):
    df = pd.read_csv(file)

    df = preprocess_data(df)

    df['signal'] = df.apply(generate_signal, axis=1)

    # Simulate PnL
    df['future_price'] = df['last_traded_price'].shift(-1)
    df['pnl'] = 0
    df.loc[df['signal'] == 'BUY', 'pnl'] = df['future_price'] - df['last_traded_price']
    df.loc[df['signal'] == 'SELL', 'pnl'] = df['last_traded_price'] - df['future_price']



    # Save for dashboard
    df.to_csv("backtest_results.csv", index=False)

    # Log prompt performance after backtest
    # For now, we'll use a placeholder for the prompt text and a dummy strategy ID.
    # In a real scenario, this prompt text would come from the AI generation process.
    prompt_text = "Strategy based on RSI < 30 and IV_zscore < -1 for BUY, RSI > 70 and IV_zscore > 1 for SELL."
    strategy_id = "rule_based_sensex_strategy_v1"
    # Calculate total PnL from the backtest
    total_pnl = df['pnl'].sum()
    log_prompt(prompt_text, strategy_id, total_pnl, version=1.0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Sensex Trading Model in various modes.")
    parser.add_argument('mode', type=str, nargs='?', default='live', help='Mode to run the script: backtest, retrain, test, live.')
    parser.add_argument('--data-validation', action='store_true', help='Run data integrity checks.')
    parser.add_argument('--augmented-data', type=str, help='Path to augmented data CSV file')
    parser.add_argument('--use-smote', action='store_true', help='Use SMOTE for class balancing')
    parser.add_argument('--shuffle-data', action='store_true', help='Shuffle data before splitting.')
    parser.add_argument('--test-size', type=float, default=0.2, help='Proportion of the dataset to include in the test split.')
    parser.add_argument('--label-smoothing', action='store_true', help='Apply label smoothing during training.')
    parser.add_argument('--augmentation', action='store_true', help='Apply data augmentation.')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for reproducibility.')
    parser.add_argument('--reset-parameters', action='store_true', help='Reset model parameters before retraining.')
    parser.add_argument('--show-sample', type=int, default=0, help='Show N samples of raw data.')
    parser.add_argument('--reset-model', action='store_true', help='Reset model architecture and retrain.')
    parser.add_argument('--paper-trade', action='store_true', help='Enable paper trading mode (no real orders placed).')

    args = parser.parse_args()
    mode = args.mode

    try:
        if mode == "backtest":
            backtest_from_file()
        elif mode == "retrain":
            print("Retraining model...")
            df = pd.read_csv("sensex_options.csv") # Assuming this is the data source
            df = preprocess_data(df)
            clf, accuracy = retrain_model(df, args)
            print(f"Model retrained with accuracy: {accuracy:.4f}")
        elif mode == "test":
            # Placeholder for testing logic
            print("Running tests...")
        else:
            # Live trading mode
            print("Starting live trading...")
            breeze = BreezeConnect(api_key=api_key)
            breeze.generate_session(api_secret=api_secret, session_token=session_token)

            # Schedule the trading logic to run every minute
            schedule.every(1).minute.do(trade_logic, breeze)
            # For debugging, we'll remove the infinite loop for now
            # while True:
            #     schedule.run_pending()
            #     time.sleep(1)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Script finished.")



# 7. Automated Order Placement (Trade Execution)
def get_current_expiry(breeze_instance):
    # Assuming breeze_instance is an initialized BreezeConnect object
    expiries = breeze_instance.get_expiry_dates(stock_code="SENSEX", exchange_code="BSE")
    # This parsing might need adjustment based on actual API response structure
    # Assuming 'success' key contains a comma-separated string of dates
    if 'success' in expiries and expiries['success']:
        current_expiry = min(expiries['success'].split(','))
    elif 'results' in expiries and expiries['results']:
        # If 'results' is a list of dicts, find the expiry date key
        # This is a placeholder, adjust based on actual 'results' structure
        current_expiry = min([d['expiry_date'] for d in expiries['results'] if 'expiry_date' in d])
    else:
        # Fallback or error handling if no expiry dates are found
        print("Could not retrieve expiry dates.")
        return None
    return current_expiry

def place_order(signal, row, is_paper_trade):
    # Use the calculated position_size
    quantity = str(int(row['position_size']))

    if is_paper_trade:
        log_trade(row, "PAPER_EXECUTED")
        print(f"[PAPER TRADE] Signal: {signal}, Quantity: {quantity}, Price: {row['last_traded_price']}")
        return

    if signal == 'BUY':
        try:
            breeze.place_order(
                stock_code="SENSEX",
                exchange_code="BSE",
                product_type="Options",
                action="BUY",
                quantity=quantity,                        # Lot size
                order_type="LIMIT",
                price=str(row['last_traded_price']),
                expiry_date=row['expiry_date'],
                right=row['option_type'],
                strike_price=row['strike_price']
            )
            log_trade(row, "SUCCESS")
        except Exception as e:
            log_trade(row, f"FAILED: {e}")
    elif signal == 'SELL':
        try:
            breeze.place_order(
                stock_code="SENSEX",
                exchange_code="BSE",
                product_type="Options",
                action="SELL",
                quantity=quantity,
                order_type="LIMIT",
                price=str(row['last_traded_price']),
                expiry_date=row['expiry_date'],
                right=row['option_type'],
                strike_price=row['strike_price']
            )
            log_trade(row, "SUCCESS")
        except Exception as e:
            log_trade(row, f"FAILED: {e}")

# 8. Scheduling & Automation
def daily_job():
    print(f"[{datetime.now()}] Starting nightly pipeline...")
    try:
        df = fetch_latest_data()
        df = preprocess_data(df) # Use the new preprocess_data function

        clf, acc = retrain_model(df, args)
        
        if should_deploy_model(acc):
            print(f"✔ Deployment approved. Model accuracy: {acc:.2f}")
            # Load the newly trained model for live inference
            current_model = load_latest_model()
            if current_model:
                # Assuming 'df' here is the live data for signal generation
                # You might need to re-process 'df' or ensure it has the features for prediction
                features = ['IV_zscore', 'oi_change', 'rsi', 'sma_10']
                df_for_prediction = df.dropna(subset=features)
                if not df_for_prediction.empty:
                    df['predicted_signal'] = current_model.predict(df_for_prediction[features])
                    # Map numerical predictions back to 'BUY'/'SELL' if your model predicts 0/1
                    # For now, we'll stick to the rule-based signal for order placement as per previous steps
                    df['signal'] = df.apply(generate_signal, axis=1)

                    for _, row in df.iterrows():
                        if validate_trade(row):
                            place_order(row['signal'], row, args.paper_trade)
                else:
                    print("No data for prediction after dropping NaNs.")
            else:
                print("No model available for deployment.")
        else:
            print("❌ Deployment halted. Model below threshold.")
    except Exception as e:
        send_alert("🚨 SENSEX DAILY FAILURE", str(e))
        print(f"Error in daily_job: {e}")
    
    # Optional: Log daily performance (accuracy, capital used, P&L)
    # This part needs actual values for capital_used and daily_pnl
    # with open("performance_log.csv", "a") as log:
    #     log.write(f"{datetime.now()},{acc:.4f},{capital_used},{daily_pnl}\n")

schedule.every().day.at("09:15").do(daily_job)

# Adjust timing for market hours.

# 9. Risk Management and Monitoring
# Impose limits in code: e.g., max position size, max daily exposure, stop losses.
# Log every trade, all model predictions, and real market outcomes for compliance.
# Set up automated alerts for anomalies (e.g., high drawdown, failed trades).

# 10. Next Steps
# After you confirm each step runs in your TRAE environment, refer back to the PDF for advanced enhancements: hybrid modeling, feature selection, automated nightly retraining, backtesting, performance dashboards, and compliance checks1.
# Always keep your own documentation up to date as you adapt and extend the system.
# Following these steps—replacing the sample code with your real parameters and evolving logic as you go—will result in an automated, high-performance SENSEX BSE options trading system, fully compatible with ICICI Direct Breeze and agentic deployment platforms1.

# Main execution flow (example, to be integrated into daily_job)

    # This block was moved and consolidated. The scheduling loop is now handled below.

if __name__ == "__main__":
    # import sys # Already imported at the top
    # mode = sys.argv[1] if len(sys.argv) > 1 else "live" # Already handled by argparse
    
    # Parse arguments at the beginning of the script
    # parser = argparse.ArgumentParser(description="Run Sensex Trading Model in various modes.")
    # ... (all add_argument calls)
    # args = parser.parse_args()
    mode = args.mode # Use the mode from the parsed arguments

    try:
        if mode == "backtest":
            backtest_from_file()
        elif mode == "retrain":
            print("Retraining model...")
            df = pd.read_csv("sensex_options.csv") # Assuming this is the data source
            df = preprocess_data(df)
            clf, accuracy = retrain_model(df, args)
            print(f"Model retrained with accuracy: {accuracy:.4f}")
        elif mode == "test":
            # Placeholder for testing logic
            print("Running tests...")
        else: # This is the 'live' mode
            print("Starting live trading...")
            breeze = BreezeConnect(api_key=api_key)
            breeze.generate_session(api_secret=api_secret, session_token=session_token)

            # Schedule the trading logic to run every minute
            schedule.every(1).minute.do(trade_logic, breeze)
            schedule.every().day.at("03:15").do(daily_job)  # pre-market retrain 
            schedule.every().day.at("09:15").do(daily_job)  # market open evaluation 
            while True:
                schedule.run_pending()
                time.sleep(60)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Script finished.")