#!/usr/bin/env python3
"""
Configuration file for High Confidence SENSEX Scalper
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Strategy Configuration
STRATEGY_CONFIG = {
    # Core Parameters
    "PROFIT_POINTS": 25,           # +25 points profit target
    "STOP_POINTS": 25,             # -25 points stop loss
    "MIN_CONFIDENCE": 0.90,        # 90% minimum confidence
    "MIN_OI_PERCENTILE": 90,       # Top 10% open interest
    "POSITION_SIZE": 200,          # ₹200 per trade
    "MAX_CAPITAL": 1000,           # ₹1000 maximum capital
    
    # Trading Hours
    "START_TIME": "09:15",         # Market open
    "END_TIME": "15:30",           # Market close
    "AFTERNOON_START": "13:00",   # Afternoon session (as requested)
    
    # Risk Management
    "MAX_DAILY_LOSS": 100,         # ₹100 daily loss limit
    "MAX_CONSECUTIVE_LOSSES": 3,   # Stop after 3 losses
    
    # Signal Filters
    "MIN_VOLUME_THRESHOLD": 1000,  # Minimum volume for entry
    "MOMENTUM_THRESHOLD": 0.5,      # Minimum momentum for signal
    
    # Technical Parameters
    "LOOKBACK_PERIOD": 10,         # Bars for momentum calculation
    "VOLATILITY_FILTER": 2.0,      # Max volatility for entry
}

# Instrument Tokens
INSTRUMENTS = {
    "SENSEX": 260617,              # BSE SENSEX
    "NIFTY": 256265,               # NSE NIFTY 50
    "BANKNIFTY": 260105,           # NSE Bank Nifty
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "handlers": [
        "file",
        "console"
    ],
    "filename": "sensex_scalper.log",
    "max_size": "10MB",
    "backup_count": 5
}

# Kite Connect Configuration
KITE_CONFIG = {
    "api_key": os.getenv('KITE_API_KEY'),
    "access_token": os.getenv('KITE_ACCESS_TOKEN'),
    "client_id": os.getenv('KITE_CLIENT_ID'),
    "redirect_url": os.getenv('KITE_REDIRECT_URL'),
}

# Paper Trading Mode
PAPER_TRADING = True  # Set to False for live trading

# Notification Settings
NOTIFICATIONS = {
    "telegram_bot_token": os.getenv('TELEGRAM_BOT_TOKEN'),
    "telegram_chat_id": os.getenv('TELEGRAM_CHAT_ID'),
    "enable_notifications": False  # Set to True for Telegram alerts
}