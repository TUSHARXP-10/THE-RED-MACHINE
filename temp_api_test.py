import requests
import json

url = "http://localhost:8000/predict/"
headers = {
    "Authorization": "Bearer test_secure_token",
    "Content-Type": "application/json"
}

payload = {
    "data": [
        {
            "implied_volatility": 0.15,
            "open_interest": 1000.0,
            "last_traded_price": 100.0,
            "high": 105.0,
            "low": 99.0,
            "ask_price": 100.5,
            "bid_price": 99.5,
            "strike_price": 100.0,
            "volume": 10000.0,
            "VWAP": 102.0,
            "ATR": 2.0,
            "ADX": 30.0,
            "CCI": 50.0,
            "MACD": 1.0,
            "MACD_signal": 0.5,
            "OBV": 1000.0,
            "Stochastic_K": 70.0,
            "Stochastic_D": 65.0,
            "Ultimate_Oscillator": 60.0,
            "Williams_R": -20.0,
            "Bollinger_Bands_Upper": 104.0,
            "Bollinger_Bands_Lower": 100.0,
            "Donchian_Channel_Upper": 106.0,
            "Donchian_Channel_Lower": 98.0,
            "option_type_Put": 0.0, # Assuming 0 for Call, 1 for Put if one-hot encoded
            "IV_zscore": 0.5,
            "oi_change": 100.0,
            "rsi": 50.0,
            "sma_10": 150.0,
            "minute_of_day": 720.0, # Mid-day
            "minute_sin": 0.0,
            "minute_cos": -1.0,
            "price_spread": 1.0,
            "spread_pct": 0.01,
            "oi_momentum": 5.0,
            "directional_buy": 0.0,
            "gamma_buy": 0.0,
            "atr": 2.0,
            "risk_weight": 10.0,
            "position_size": 5.0
        }
    ]
}

try:
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    print("Response Status Code:", response.status_code)
    print("Response Body:", json.dumps(response.json(), indent=4))
except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
    print(f"Response Body: {response.text}")
except requests.exceptions.RequestException as err:
    print(f"Request failed: {err}")