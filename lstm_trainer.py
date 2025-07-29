import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

class LSTMTrainer:
    def __init__(self, data: pd.DataFrame, features: list, target: str, look_back: int = 60):
        self.data = data
        self.features = features
        self.target = target
        self.look_back = look_back
        self.scaler_X = MinMaxScaler(feature_range=(0, 1))
        self.scaler_y = MinMaxScaler(feature_range=(0, 1))
        self.model = None

    def _prepare_data(self):
        # Select features and target
        df = self.data[self.features + [self.target]].copy()
        
        # Scale features and target
        X_scaled = self.scaler_X.fit_transform(df[self.features])
        y_scaled = self.scaler_y.fit_transform(df[[self.target]])

        # Create sequences for LSTM
        X, y = [], []
        for i in range(self.look_back, len(df)):
            X.append(X_scaled[i-self.look_back:i, :])
            y.append(y_scaled[i, 0])
        
        return np.array(X), np.array(y)

    def build_model(self, lstm_units=50, dropout_rate=0.2):
        model = Sequential()
        model.add(LSTM(units=lstm_units, return_sequences=True, input_shape=(self.look_back, len(self.features))))
        model.add(Dropout(dropout_rate))
        model.add(LSTM(units=lstm_units))
        model.add(Dropout(dropout_rate))
        model.add(Dense(units=1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        self.model = model

    def train_model(self, epochs=100, batch_size=32, validation_split=0.2, patience=10):
        if self.model is None:
            self.build_model()
        
        X, y = self._prepare_data()
        
        early_stopping = EarlyStopping(monitor='val_loss', patience=patience, restore_best_weights=True)
        
        history = self.model.fit(X, y, epochs=epochs, batch_size=batch_size, validation_split=validation_split, callbacks=[early_stopping], verbose=1)
        return history

    def evaluate_model(self, X_test, y_test):
        if self.model is None:
            print("Model not trained yet.")
            return None, None
        
        predictions_scaled = self.model.predict(X_test)
        predictions = self.scaler_y.inverse_transform(predictions_scaled)
        y_test_unscaled = self.scaler_y.inverse_transform(y_test.reshape(-1, 1))
        
        rmse = np.sqrt(np.mean((predictions - y_test_unscaled)**2))
        print(f"LSTM RMSE: {rmse:.2f}")
        return predictions, rmse

if __name__ == "__main__":
    # Dummy data for demonstration
    data = pd.DataFrame({
        'IV_zscore': np.random.rand(200),
        'oi_momentum': np.random.rand(200),
        'time_sin': np.sin(np.arange(200) * 0.1),
        'time_cos': np.cos(np.arange(200) * 0.1),
        'target_pnl': np.random.rand(200) * 100 - 50 # Dummy PnL
    })

    features = ['IV_zscore', 'oi_momentum', 'time_sin', 'time_cos']
    target = 'target_pnl'
    look_back = 30

    lstm_trainer = LSTMTrainer(data, features, target, look_back)
    lstm_trainer.build_model(lstm_units=50, dropout_rate=0.2)
    
    # Prepare data for training and evaluation split
    X_full, y_full = lstm_trainer._prepare_data()
    split_index = int(len(X_full) * 0.8)
    X_train, X_test = X_full[:split_index], X_full[split_index:]
    y_train, y_test = y_full[:split_index], y_full[split_index:]

    # Train the model using the training split
    lstm_trainer.model.fit(X_train, y_train, epochs=100, batch_size=32, validation_split=0.2, callbacks=[EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)], verbose=1)

    # Evaluate the model on the test split
    predictions, rmse = lstm_trainer.evaluate_model(X_test, y_test)
    if predictions is not None:
        print(f"Sample predictions: {predictions[:5].flatten()}")
        print(f"Actual values: {lstm_trainer.scaler_y.inverse_transform(y_test.reshape(-1, 1))[:5].flatten()}")