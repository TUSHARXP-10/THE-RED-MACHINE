import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_dummy_data(num_rows=1000):
    data = {
        'Date': [datetime(2023, 1, 1) + timedelta(days=i) for i in range(num_rows)],
        'implied_volatility': np.random.uniform(10, 30, num_rows),
        'open_interest': np.random.randint(50000, 200000, num_rows),
        'last_traded_price': np.random.uniform(100, 110, num_rows),
        'high': np.random.uniform(105, 115, num_rows),
        'low': np.random.uniform(95, 105, num_rows),
        'ask_price': np.random.uniform(100.5, 110.5, num_rows),
        'bid_price': np.random.uniform(99.5, 109.5, num_rows),
        'option_type': np.random.choice(['Call', 'Put'], num_rows),
        'strike_price': np.random.choice([75000, 75500, 76000], num_rows),
        'expiry_date': [datetime(2025, 7, 31) for _ in range(num_rows)],
        'volume': np.random.randint(1000, 10000, num_rows),
        'VWAP': np.random.uniform(100, 110, num_rows),
        'ATR': np.random.uniform(1, 5, num_rows),
        'ADX': np.random.uniform(10, 50, num_rows),
        'CCI': np.random.uniform(-100, 100, num_rows),
        'MACD': np.random.uniform(-5, 5, num_rows),
        'MACD_signal': np.random.uniform(-5, 5, num_rows),
        'OBV': np.random.randint(-100000, 100000, num_rows),
        'Stochastic_K': np.random.uniform(0, 100, num_rows),
        'Stochastic_D': np.random.uniform(0, 100, num_rows),
        'Ultimate_Oscillator': np.random.uniform(0, 100, num_rows),
        'Williams_R': np.random.uniform(-100, 0, num_rows),
        'Bollinger_Bands_Upper': np.random.uniform(105, 115, num_rows),
        'Bollinger_Bands_Lower': np.random.uniform(95, 105, num_rows),
        'Donchian_Channel_Upper': np.random.uniform(106, 116, num_rows),
        'Donchian_Channel_Lower': np.random.uniform(94, 104, num_rows)
    }
    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    dummy_df = generate_dummy_data(num_rows=1000)
    dummy_df.to_csv("sensex_options.csv", index=False)
    print("Generated sensex_options.csv with 1000 rows of dummy data.")