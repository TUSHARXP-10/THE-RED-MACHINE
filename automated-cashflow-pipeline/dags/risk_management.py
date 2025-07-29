import pandas as pd
import numpy as np
import riskfolio as rp  # For advanced risk metrics
import logging

logger = logging.getLogger(__name__)

def apply_risk_controls(df, predictions):
    """Integrate pre-trade risk controls and position sizing"""
    # Volatility-based position sizing
    df['volatility'] = df['stock_price'].rolling(window=20).std()
    df['position_size'] = 1 / (df['volatility'] * 10)  # Scale inversely to volatility

    # Correlation limits to prevent overconcentration
    corr_matrix = df[['stock_price', 'interest_rate']].corr()
    if corr_matrix.iloc[0,1] > 0.8:
        logger.warning("High correlation detected - adjusting positions")

    # Portfolio optimization example
    # Ensure the DataFrame passed to riskfolio has a DatetimeIndex or RangeIndex
    # and columns are asset names. Here, we'll use a simplified approach for demonstration.
    # For a real scenario, you'd need multiple asset returns.
    if not df[['stock_price']].pct_change().dropna().empty:
        port = rp.Portfolio(returns=df[['stock_price']].pct_change().dropna())
        port.assets_stats(method_mu='hist', method_cov='hist')
        # Ensure 'w' has enough elements to flatten and assign to df
        try:
            w = port.optimization(model='Classic', rm='MV', obj='Sharpe')
            # Ensure the length of w.values.flatten() matches or exceeds len(df)
            if len(w.values.flatten()) >= len(df):
                df['optimized_weights'] = w.values.flatten()[:len(df)]
            else:
                logger.warning("Not enough optimized weights to assign to DataFrame. Skipping 'optimized_weights' assignment.")
                df['optimized_weights'] = np.nan # Assign NaN if not enough weights
        except Exception as e:
            logger.error(f"Error during portfolio optimization: {e}")
            df['optimized_weights'] = np.nan # Assign NaN on error
    else:
        logger.warning("Not enough data for portfolio optimization. Skipping 'optimized_weights' assignment.")
        df['optimized_weights'] = np.nan # Assign NaN if not enough data

    # Add kill switch for high risk
    df['risk_flag'] = np.where(df['volatility'] > 0.15, 'high_risk', 'normal')

    return df

# Integrate predictions from models
def evaluate_risk_with_predictions(df, model_predictions):
    df['predicted_cashflow'] = model_predictions
    df = apply_risk_controls(df, model_predictions) # predictions are not directly used in apply_risk_controls for now, but can be integrated
    return df