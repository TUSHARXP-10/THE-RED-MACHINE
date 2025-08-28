#!/usr/bin/env python3
"""
Model Retraining System for 3000 Capital
Retrains LSTM model with optimized parameters for small capital trading
"""

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
import joblib
import logging
from datetime import datetime, timedelta
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('model_retraining.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CapitalOptimizedModelTrainer:
    def __init__(self, capital=3000):
        self.capital = capital
        self.model = None
        self.scaler = MinMaxScaler()
        self.sequence_length = 60
        self.features = ['price', 'volume', 'rsi', 'sma_ratio', 'volatility']
        
        # Optimize for small capital
        self.risk_tolerance = 0.02  # 2% max risk per trade
        self.min_confidence = 0.65  # Higher confidence for small capital
        
    def load_training_data(self, days=60):
        """Load and prepare training data"""
        try:
            # Load historical data
            data_files = ['simulated_prices.csv', 'backtest_results.csv', 'detailed_trades.csv']
            
            for file in data_files:
                if os.path.exists(file):
                    df = pd.read_csv(file)
                    if 'price' in df.columns:
                        logger.info(f"Loaded training data from {file}")
                        return self.prepare_features(df)
            
            # Generate training data if no files exist
            logger.info("Generating training data...")
            return self.generate_training_data(days)
            
        except Exception as e:
            logger.error(f"Error loading training data: {e}")
            return self.generate_training_data(days)
    
    def generate_training_data(self, days=60):
        """Generate realistic training data"""
        np.random.seed(42)
        
        # Generate 1-minute data for training
        minutes_per_day = 375
        total_minutes = days * minutes_per_day
        
        # Simulate SENSEX data around 80000
        base_price = 80000
        prices = [base_price]
        
        for i in range(1, total_minutes):
            # Realistic intraday volatility
            volatility = np.random.normal(0, 0.0008)  # 0.08% per minute
            new_price = prices[-1] * (1 + volatility)
            prices.append(max(new_price, base_price * 0.9))
        
        df = pd.DataFrame({
            'timestamp': pd.date_range(
                start=datetime.now() - timedelta(days=days),
                periods=total_minutes,
                freq='1min'
            ),
            'price': prices,
            'volume': np.random.randint(50000, 500000, total_minutes)
        })
        
        return self.prepare_features(df)
    
    def prepare_features(self, df):
        """Create technical indicators for training"""
        df = df.copy()
        
        # Basic indicators
        df['sma_5'] = df['price'].rolling(window=5).mean()
        df['sma_20'] = df['price'].rolling(window=20).mean()
        df['sma_ratio'] = df['sma_5'] / df['sma_20']
        
        # RSI
        delta = df['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Volatility
        df['volatility'] = df['price'].rolling(window=10).std() / df['price']
        
        # Future returns (target)
        df['future_return'] = df['price'].shift(-5) / df['price'] - 1  # 5-minute ahead
        
        # Drop NaN values
        df = df.dropna()
        
        return df
    
    def create_sequences(self, data):
        """Create sequences for LSTM training"""
        X, y = [], []
        
        for i in range(self.sequence_length, len(data)):
            X.append(data[i-self.sequence_length:i])
            y.append(data[i, -1])  # future_return
            
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape):
        """Build optimized LSTM model for small capital"""
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(30, return_sequences=False),
            Dropout(0.2),
            Dense(20, activation='relu'),
            Dropout(0.2),
            Dense(1, activation='linear')
        ])
        
        # Use lower learning rate for stability
        optimizer = Adam(learning_rate=0.0001)
        model.compile(
            optimizer=optimizer,
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def train_model(self):
        """Train the model with capital optimization"""
        logger.info("Starting model training...")
        
        # Load and prepare data
        df = self.load_training_data()
        
        # Select features
        feature_data = df[self.features + ['future_return']].values
        
        # Normalize features
        feature_data[:, :-1] = self.scaler.fit_transform(feature_data[:, :-1])
        
        # Create sequences
        X, y = self.create_sequences(feature_data)
        
        # Split data
        split_idx = int(0.8 * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        logger.info(f"Training data shape: X={X_train.shape}, y={y_train.shape}")
        logger.info(f"Test data shape: X={X_test.shape}, y={y_test.shape}")
        
        # Build and train model
        self.model = self.build_model((X_train.shape[1], X_train.shape[2]))
        
        # Early stopping
        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        # Train model
        history = self.model.fit(
            X_train, y_train,
            epochs=50,
            batch_size=32,
            validation_data=(X_test, y_test),
            callbacks=[early_stopping],
            verbose=1
        )
        
        # Evaluate model
        test_loss, test_mae = self.model.evaluate(X_test, y_test, verbose=0)
        logger.info(f"Test Loss: {test_loss:.6f}, Test MAE: {test_mae:.6f}")
        
        # Save model and scaler
        self.save_model()
        
        return {
            'test_loss': float(test_loss),
            'test_mae': float(test_mae),
            'epochs_trained': len(history.history['loss']),
            'model_path': 'models/capital_optimized_model.h5',
            'scaler_path': 'models/capital_optimized_scaler.pkl'
        }
    
    def save_model(self):
        """Save model and scaler"""
        os.makedirs('models', exist_ok=True)
        
        self.model.save('models/capital_optimized_model.h5')
        joblib.dump(self.scaler, 'models/capital_optimized_scaler.pkl')
        
        # Save training metadata
        metadata = {
            'capital': self.capital,
            'features': self.features,
            'sequence_length': self.sequence_length,
            'risk_tolerance': self.risk_tolerance,
            'min_confidence': self.min_confidence,
            'training_date': datetime.now().isoformat()
        }
        
        with open('models/training_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info("Model saved successfully")
    
    def predict_next_move(self, recent_data):
        """Make prediction for next move"""
        if self.model is None:
            try:
                self.model = load_model('models/capital_optimized_model.h5')
                self.scaler = joblib.load('models/capital_optimized_scaler.pkl')
            except:
                logger.error("Model not found. Please train first.")
                return None
        
        # Prepare features
        df = self.prepare_features(pd.DataFrame(recent_data))
        
        if len(df) < self.sequence_length:
            return None
        
        # Get last sequence
        last_sequence = df[self.features].values[-self.sequence_length:]
        last_sequence = self.scaler.transform(last_sequence)
        
        # Predict
        prediction = self.model.predict(last_sequence.reshape(1, self.sequence_length, len(self.features)))
        
        # Convert to signal
        if prediction[0][0] > self.min_confidence * 0.01:  # 0.65% threshold
            return "BUY"
        elif prediction[0][0] < -self.min_confidence * 0.01:
            return "SELL"
        else:
            return "HOLD"

def main():
    """Main training function"""
    trainer = CapitalOptimizedModelTrainer(capital=3000)
    
    print("=" * 50)
    print("MODEL RETRAINING FOR 3000 CAPITAL")
    print("=" * 50)
    
    # Train model
    results = trainer.train_model()
    
    print(f"Model training completed!")
    print(f"Test Loss: {results['test_loss']:.6f}")
    print(f"Test MAE: {results['test_mae']:.6f}")
    print(f"Model saved to: {results['model_path']}")
    
    return results

if __name__ == "__main__":
    main()