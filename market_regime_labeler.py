import pandas as pd
import numpy as np

class MarketRegimeLabeler:
    def __init__(self, volatility_window=20, trend_window=50, adx_threshold=25, history_length=100):
        self.volatility_window = volatility_window
        self.trend_window = trend_window
        self.adx_threshold = adx_threshold
        self.history_length = history_length # Length of historical data to keep for current regime labeling
        self.history_df = pd.DataFrame(columns=['high', 'low', 'close']) # To store recent market data

    def _update_history(self, high, low, close):
        # Add new data point to history
        new_data = pd.DataFrame([{'high': high, 'low': low, 'close': close}])
        self.history_df = pd.concat([self.history_df, new_data], ignore_index=True)
        # Keep only the most recent `history_length` data points
        if len(self.history_df) > self.history_length:
            self.history_df = self.history_df.iloc[-self.history_length:].reset_index(drop=True)

    def _calculate_atr(self, high, low, close, window=14):
        # Calculate True Range (TR)
        tr1 = high - low
        tr2 = np.abs(high - close.shift(1))
        tr3 = np.abs(low - close.shift(1))
        tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)

        # Calculate Average True Range (ATR)
        atr = tr.ewm(span=window, adjust=False).mean()
        return atr

    def _calculate_adx(self, high, low, close, window=14):
        # Calculate Directional Movement
        plus_dm = high.diff()
        minus_dm = low.diff() * -1

        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0

        # Correct for cases where both are positive or negative
        true_plus_dm = pd.Series(np.where(plus_dm > minus_dm, plus_dm, 0), index=high.index)
        true_minus_dm = pd.Series(np.where(minus_dm > plus_dm, minus_dm, 0), index=high.index)

        # Calculate ATR
        atr = self._calculate_atr(high, low, close, window)

        # Calculate Smoothed Directional Movement
        plus_di = (true_plus_dm.ewm(span=window, adjust=False).mean() / atr) * 100
        minus_di = (true_minus_dm.ewm(span=window, adjust=False).mean() / atr) * 100

        # Calculate DX and ADX
        dx = (np.abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
        adx = dx.ewm(span=window, adjust=False).mean()
        return adx

    def label_regimes(self, df):
        # Ensure DataFrame has required columns
        if not all(col in df.columns for col in ['high', 'low', 'close']):
            raise ValueError("DataFrame must contain 'high', 'low', and 'close' columns.")

        df = df.copy()

        # Calculate volatility (e.g., using rolling standard deviation of returns)
        df['returns'] = df['close'].pct_change()
        df['volatility'] = df['returns'].rolling(window=self.volatility_window).std()

        # Calculate trend (e.g., using moving average crossover or ADX)
        df['sma_short'] = df['close'].rolling(window=self.trend_window // 2).mean()
        df['sma_long'] = df['close'].rolling(window=self.trend_window).mean()
        df['adx'] = self._calculate_adx(df['high'], df['low'], df['close'], window=self.trend_window)

        # Define regime based on indicators
        df['regime'] = 'unknown'

        # Trend regime
        df.loc[(df['sma_short'] > df['sma_long']) & (df['adx'] > self.adx_threshold), 'regime'] = 'uptrend'
        df.loc[(df['sma_short'] < df['sma_long']) & (df['adx'] > self.adx_threshold), 'regime'] = 'downtrend'

        # Rangebound regime (low ADX)
        df.loc[df['adx'] <= self.adx_threshold, 'regime'] = 'rangebound'

        # High volatility regime (e.g., top quartile of volatility)
        volatility_threshold = df['volatility'].quantile(0.75)
        df.loc[df['volatility'] > volatility_threshold, 'regime'] = 'high_volatility'

        # Crash regime (significant negative returns over a short period)
        df['crash_indicator'] = df['close'].pct_change(periods=5).rolling(window=5).min()
        df.loc[df['crash_indicator'] < -0.05, 'regime'] = 'crash' # Example: 5% drop in 5 days

        return df

    def label_current_regime(self, high, low, close):
        self._update_history(high, low, close)

        if len(self.history_df) < max(self.volatility_window, self.trend_window, 14): # Ensure enough data for calculations
            return "initializing"

        # Use the last few data points to determine current regime
        current_df = self.label_regimes(self.history_df.copy())
        return current_df['regime'].iloc[-1]

if __name__ == '__main__':
    # Example Usage:
    # Create a dummy DataFrame for demonstration
    data = {
        'open': np.random.rand(100) * 100 + 100,
        'high': np.random.rand(100) * 100 + 105,
        'low': np.random.rand(100) * 100 + 95,
        'close': np.random.rand(100) * 100 + 100,
        'volume': np.random.rand(100) * 10000
    }
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(pd.date_range(start='2023-01-01', periods=100))
    df = df.set_index('date')

    labeler = MarketRegimeLabeler()
    df_labeled = labeler.label_regimes(df)

    print(df_labeled[['close', 'volatility', 'sma_short', 'sma_long', 'adx', 'regime']].tail(20))
    print("\nRegime Distribution:")
    print(df_labeled['regime'].value_counts())