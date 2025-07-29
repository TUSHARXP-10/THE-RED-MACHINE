import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
from datetime import datetime

# Sample training data (replace with your actual data)
data = {
    "IV_zscore": [0.5],
    "oi_change": [100.0],
    # Add all 28 features from your model
    # ... (use the full list from sensex_trading_model.py line 40)
    "Donchian_Channel_Lower": [98.0]
}
df = pd.DataFrame(data)
y = [103.0]  # Target (e.g., close price)

# Train simple RF model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(df, y)

# Save with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
filename = f"automated-cashflow-pipeline/models/rf_model_{timestamp}.pkl"
joblib.dump(model, filename)
print(f"Model saved to {filename}")