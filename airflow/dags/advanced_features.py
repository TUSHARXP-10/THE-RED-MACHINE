import pandas as pd
import numpy as np
from textblob import TextBlob  # For sentiment

def add_advanced_features(df):
    """Add technical and sentiment features"""
    # Technical indicators
    df['rsi'] = compute_rsi(df['stock_price'], window=14)  # Implement RSI logic
    df['macd'] = compute_macd(df['stock_price'])  # Implement MACD

    # Simulated sentiment (replace with real news API)
    # Add dummy news_text if not present for sentiment analysis
    if 'news_text' not in df.columns:
        df['news_text'] = 'Neutral market sentiment for financial data'
    df['sentiment'] = df['news_text'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)

    return df

def compute_rsi(series, window):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def compute_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast).mean()
    ema_slow = series.ewm(span=slow).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal).mean()
    return macd - signal_line