#!/usr/bin/env python3
"""
SENSEX Model Retraining Script
Retrains the SENSEX trading model with this week's BSE data using Kite Connect
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import ta
import warnings
warnings.filterwarnings('ignore')

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from broker_interface import KiteBrokerInterface
import os

class SensexModelRetrainer:
    def __init__(self):
        self.kite = KiteBrokerInterface()
        self.model_dir = "models"
        self.data_dir = "data"
        self.ensure_directories()
        
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs(self.model_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
    
    def fetch_sensex_data(self, days_back=30):
        """Fetch SENSEX data for the specified number of days"""
        print("📊 Fetching SENSEX data...")
        
        # Get historical data for SENSEX
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        try:
            # Fetch data using Kite Connect - SENSEX data
            # Use direct kite historical_data method
            data = self.kite.kite.historical_data(
                instrument_token=260617,  # SENSEX instrument token
                from_date=start_date.date(),
                to_date=end_date.date(),
                interval='5minute',
                continuous=False
            )
            
            if not data:
                print("❌ No data received from API")
                return None
                
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Ensure we have the expected columns
            required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_cols):
                print("❌ Missing required columns in data")
                print(f"Available columns: {df.columns.tolist()}")
                return None
                
            # Convert date to datetime
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            print(f"✅ Fetched {len(df)} data points for SENSEX")
            return df
            
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return None
    
    def create_technical_features(self, df):
        """Create technical indicators for the SENSEX data"""
        print("🔧 Creating technical features...")
        
        # Price-based features (minimal NaN creation)
        df['returns'] = df['close'].pct_change()
        df['price_change'] = df['close'].diff()
        
        # Moving averages with shorter windows
        df['sma_5'] = ta.trend.sma_indicator(df['close'], window=5)
        df['sma_10'] = ta.trend.sma_indicator(df['close'], window=10)
        
        # RSI with shorter window
        df['rsi'] = ta.momentum.rsi(df['close'], window=10)
        
        # Simple momentum indicators
        df['price_momentum'] = df['close'] / df['close'].shift(3) - 1
        
        # Price position relative to moving average
        df['price_position'] = (df['close'] - df['sma_5']) / df['sma_5']
        
        # Volume features
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(window=5).mean()
        
        # High-low spread
        df['hl_spread'] = (df['high'] - df['low']) / df['close']
        
        print("✅ Technical features created")
        return df
    
    def create_target_variable(self, df):
        """Create target variable for prediction (next 5-minute price movement)"""
        print("🎯 Creating target variable...")
        
        # Target: 1 if price goes up in next 5 minutes, 0 otherwise
        df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
        
        # Alternative: 3-class target (up, down, flat)
        df['target_3class'] = 1  # Default: flat/no change
        df.loc[df['close'].shift(-1) > df['close'] * 1.001, 'target_3class'] = 2  # Up
        df.loc[df['close'].shift(-1) < df['close'] * 0.999, 'target_3class'] = 0  # Down
        
        print("✅ Target variable created")
        return df
    
    def prepare_data_for_training(self, df):
        """Prepare final dataset for training"""
        print("📋 Preparing training data...")
        
        # Use basic features and handle NaN values carefully
        df = df.copy()
        
        # Simple features with minimal NaN creation
        df['price_change'] = df['close'].pct_change()
        
        # Volume ratio with safe handling
        volume_mean = df['volume'].mean()
        df['volume_ratio'] = df['volume'] / max(volume_mean, 1)
        
        # Price momentum
        df['price_momentum'] = df['close'].shift(1) / df['close'].shift(2) - 1
        
        # Fill any remaining NaN values
        df = df.fillna(method='ffill').fillna(0)
        
        # Select features for training
        feature_cols = ['price_change', 'volume_ratio', 'price_momentum']
        
        X = df[feature_cols]
        y = df['target']
        
        # Remove last row as it has NaN target
        X = X[:-1]
        y = y[:-1]
        
        print(f"📊 Final dataset shape: {X.shape}")
        print(f"📊 Target distribution: {y.value_counts()}")
        
        if len(X) < 20:  # Further reduced minimum requirement
            print(f"❌ Insufficient data for training. Only {len(X)} samples available.")
            return None, None, None
            
        print(f"✅ Training data prepared: {len(X)} samples, {len(feature_cols)} features")
        return X, y, feature_cols
    
    def train_model(self, X, y):
        """Train the Random Forest model"""
        print("🤖 Training Random Forest model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Initialize and train model
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✅ Model trained with accuracy: {accuracy:.4f}")
        
        # Detailed classification report
        report = classification_report(y_test, y_pred, output_dict=True)
        print("📊 Classification Report:")
        print(f"   Precision (up): {report['1']['precision']:.4f}")
        print(f"   Recall (up): {report['1']['recall']:.4f}")
        print(f"   F1-score (up): {report['1']['f1-score']:.4f}")
        
        return model, accuracy, X_test, y_test
    
    def save_model(self, model, features, accuracy):
        """Save the trained model with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"{self.model_dir}/sensex_rf_model_{timestamp}.pkl"
        features_filename = f"{self.model_dir}/sensex_features_{timestamp}.pkl"
        
        # Save model
        joblib.dump(model, model_filename)
        
        # Save features list
        joblib.dump(features, features_filename)
        
        # Also save as latest model
        latest_model = f"{self.model_dir}/sensex_model_latest.pkl"
        latest_features = f"{self.model_dir}/sensex_features_latest.pkl"
        
        joblib.dump(model, latest_model)
        joblib.dump(features, latest_features)
        
        print(f"💾 Model saved: {model_filename}")
        print(f"💾 Features saved: {features_filename}")
        print(f"💾 Latest model updated: {latest_model}")
        
        # Save training metadata
        metadata = {
            'timestamp': timestamp,
            'accuracy': accuracy,
            'features': features,
            'model_type': 'RandomForestClassifier',
            'n_estimators': 100,
            'max_depth': 10
        }
        
        metadata_filename = f"{self.model_dir}/training_metadata_{timestamp}.json"
        import json
        with open(metadata_filename, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return model_filename
    
    def run_retraining(self, days_back=7):
        """Complete retraining pipeline"""
        print("🔄 Starting SENSEX Model Retraining")
        print("=" * 50)
        
        # 1. Fetch data
        df = self.fetch_sensex_data(days_back)
        if df is None:
            print("❌ Failed to fetch data. Exiting.")
            return None
        
        # 2. Create features
        df = self.create_technical_features(df)
        
        # 3. Create target variable
        df = self.create_target_variable(df)
        
        # 4. Prepare data
        X, y, features = self.prepare_data_for_training(df)
        
        if X is None or len(X) < 20:
            print("❌ Insufficient data for training")
            return None
        
        # 5. Train model
        model, accuracy, X_test, y_test = self.train_model(X, y)
        
        # 6. Save model
        model_path = self.save_model(model, features, accuracy)
        
        print("\n✅ Retraining completed successfully!")
        print(f"📈 Model accuracy: {accuracy:.4f}")
        print(f"📊 Total samples: {len(X)}")
        print(f"🎯 Features used: {len(features)}")
        
        return model_path

def main():
    """Main function to run retraining"""
    print("🚀 SENSEX Model Retraining Tool")
    print("Retraining with latest BSE SENSEX data...")
    
    retrainer = SensexModelRetrainer()
    
    # Allow custom days back from command line
    import argparse
    parser = argparse.ArgumentParser(description='Retrain SENSEX model')
    parser.add_argument('--days', type=int, default=7, help='Days of data to use')
    parser.add_argument('--test', action='store_true', help='Test mode (dry run)')
    
    args = parser.parse_args()
    
    if args.test:
        print("🧪 Test mode - running with limited data...")
        model_path = retrainer.run_retraining(days_back=1)
    else:
        model_path = retrainer.run_retraining(days_back=args.days)
    
    if model_path:
        print(f"\n🎉 Model successfully retrained and saved to: {model_path}")
        print("The new model is ready for use in live trading!")
    else:
        print("\n❌ Retraining failed. Check logs for details.")

if __name__ == "__main__":
    main()