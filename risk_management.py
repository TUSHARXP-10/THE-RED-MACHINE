import pandas as pd
import numpy as np

import logging
from riskfolio import Portfolio  # For portfolio optimization

logger = logging.getLogger(__name__)

def apply_risk_controls(df, predictions):
    """Integrate pre-trade risk controls and position sizing"""
    # Volatility-based position sizing
    df['volatility'] = df['stock_price'].rolling(window=20).std()
    df['position_size'] = 1 / (df['volatility'] * 10 + 0.01)  # Avoid division by zero, scale inversely

    # Correlation limits to prevent overconcentration
    corr_matrix = df[['stock_price', 'interest_rate']].corr()
    if corr_matrix.iloc[0,1] > 0.8:
        logger.warning("High correlation detected - adjusting positions")
        df['position_size'] = df['position_size'] * 0.5  # Reduce exposure

    # Circuit breaker for high volatility
    df['risk_flag'] = np.where(df['volatility'] > 0.15, 'high_risk', 'normal')
    df['position_size'] = np.where(df['risk_flag'] == 'high_risk', 0, df['position_size'])

    # Log risk metrics to MLflow
    import mlflow
    with mlflow.start_run():
        mlflow.log_metric("avg_volatility", df['volatility'].mean())
        mlflow.log_metric("max_position_size", df['position_size'].max())

    logger.info("Risk controls applied with volatility-based sizing.")
    return df

def evaluate_risk_with_predictions(df, model_predictions):
    """Combine model predictions with risk controls"""
    df['predicted_cashflow'] = model_predictions  # Placeholder; adjust based on model output
    df = apply_risk_controls(df, model_predictions)
    df.to_csv('/opt/airflow/data/warehouse/risk_adjusted_data.csv', index=True)
    logger.info("Risk evaluation completed and data saved.")
    return df

def validate_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Clean dataset by removing NaNs, duplicates, and non-finite values."""
    try:
        # Drop NaNs and duplicates
        df_clean = df.dropna().drop_duplicates()
          
        # Validate numeric fields
        numeric_cols = ['VaR', 'exposure', 'correlation_threshold'] # Added 'correlation_threshold' based on common risk metrics
        for col in numeric_cols:
            if col in df_clean.columns:
                df_clean = df_clean[np.isfinite(df_clean[col])]
                  
        return df_clean
    except Exception as e:
        # Assuming log_ethical_decision is accessible or can be imported
        # If not, a simple print or standard logging would be used.
        # For this example, we'll assume it's accessible.
        log_ethical_decision(
            decision_context="DATA_VALIDATION_FAIL",
            decision_outcome=f"Validation error: {str(e)}",
            bias_detected=False
        )
        raise

class RiskManagement:
    def __init__(self, max_risk_per_trade_percent=2, max_daily_drawdown_percent=10):
        self.max_risk_per_trade_percent = max_risk_per_trade_percent
        self.max_daily_drawdown_percent = max_daily_drawdown_percent
        self.daily_pnl = 0.0
        self.initial_capital = 100000.0 # Placeholder, should be loaded from config or actual capital

    def set_initial_capital(self, capital):
        self.initial_capital = capital

    def check_position_sizing(self, entry_price, stop_loss_price, capital=None):
        if capital is None:
            capital = self.initial_capital

        if stop_loss_price >= entry_price:
            print("Warning: Stop loss price must be less than entry price for a long position, or greater for a short position.")
            return 0 # Cannot calculate position size if stop loss is not set correctly

        risk_per_share = abs(entry_price - stop_loss_price)
        if risk_per_share == 0:
            return 0 # Avoid division by zero

        max_dollar_risk = capital * (self.max_risk_per_trade_percent / 100)
        quantity = int(max_dollar_risk / risk_per_share)
        return quantity

    def check_stop_loss(self, current_price, entry_price, stop_loss_price, action):
        if action == "BUY": # Long position
            if current_price <= stop_loss_price:
                print(f"STOP LOSS HIT: Current Price {current_price} <= Stop Loss {stop_loss_price}")
                return True
        elif action == "SELL": # Short position
            if current_price >= stop_loss_price:
                print(f"STOP LOSS HIT: Current Price {current_price} >= Stop Loss {stop_loss_price}")
                return True
        return False

    def update_daily_pnl(self, pnl_change):
        self.daily_pnl += pnl_change

    def check_daily_drawdown(self):
        current_drawdown_percent = (self.daily_pnl / self.initial_capital) * 100
        if current_drawdown_percent < -(self.max_daily_drawdown_percent):
            print(f"DAILY DRAWDOWN LIMIT REACHED: Current Drawdown {current_drawdown_percent:.2f}% > {self.max_daily_drawdown_percent}%")
            return True
        return False

    def run_monte_carlo_simulation(self, historical_returns, num_simulations=1000, time_horizon=252):
        """
        Runs Monte Carlo simulations to estimate future portfolio values and VaR.
        historical_returns: pandas Series or numpy array of daily returns.
        num_simulations: Number of simulation paths.
        time_horizon: Number of trading days to simulate.
        """
        # Validate the input historical_returns DataFrame using the new function
        try:
            historical_returns = validate_dataset(pd.DataFrame({'returns': historical_returns}))['returns']
        except Exception as e:
            print(f"Error validating historical returns for Monte Carlo simulation: {e}")
            return None, None

        if len(historical_returns) == 0:
            print("Error: No historical returns provided for Monte Carlo simulation after validation.")
            return None, None

        mean_daily_return = historical_returns.mean()
        std_daily_return = historical_returns.std()

        # Simulate price paths
        simulated_price_paths = np.zeros((num_simulations, time_horizon))
        last_price = self.initial_capital # Starting point for simulation

        for i in range(num_simulations):
            daily_returns_simulated = np.random.normal(mean_daily_return, std_daily_return, time_horizon)
            price_path = last_price * (1 + daily_returns_simulated).cumprod()
            simulated_price_paths[i] = price_path

        # Calculate Value at Risk (VaR) at 95% confidence level
        # This assumes the simulated_price_paths represent portfolio values
        final_portfolio_values = simulated_price_paths[:, -1]
        var_95 = np.percentile(final_portfolio_values, 5) # 5th percentile for 95% VaR

        print(f"Monte Carlo Simulation Results (over {time_horizon} days, {num_simulations} simulations):")
        print(f"  Expected Final Portfolio Value: {np.mean(final_portfolio_values):.2f}")
        print(f"  95% VaR (Value at Risk): {self.initial_capital - var_95:.2f} (potential loss)")

        return simulated_price_paths, var_95

    def check_correlation_based_limits(self, asset_correlations, current_portfolio_exposure):
        """
        Placeholder for checking risk limits based on asset correlations.
        asset_correlations: A dictionary or DataFrame of asset correlations.
        current_portfolio_exposure: Current exposure to different assets.
        """
        print("Checking correlation-based limits...")
        # Logic to assess portfolio risk based on correlations
        # Example: If highly correlated assets exceed a certain combined exposure, flag it.
        # This would involve more complex portfolio optimization/risk models.
        if asset_correlations is None or current_portfolio_exposure is None:
            print("  No correlation or exposure data provided.")
            return False

        # Dummy logic: if any correlation is too high and exposure is also high
        # This needs actual implementation based on portfolio construction rules.
        high_correlation_threshold = 0.9
        high_exposure_threshold = 0.2 # e.g., 20% of portfolio

        # Example: Check if SENSEX and BANKNIFTY are highly correlated and both have high exposure
        # This is a simplified example. Real implementation would iterate through pairs.
        if 'SENSEX' in asset_correlations and 'BANKNIFTY' in asset_correlations:
            if asset_correlations.get(('SENSEX', 'BANKNIFTY'), 0) > high_correlation_threshold and \
               current_portfolio_exposure.get('SENSEX', 0) > high_exposure_threshold and \
               current_portfolio_exposure.get('BANKNIFTY', 0) > high_exposure_threshold:
                print("  WARNING: High correlation between SENSEX and BANKNIFTY with significant exposure. Consider rebalancing.")
                return True
        return False

    def log_ethical_decision(self, decision_context, decision_outcome, bias_detected=False, compliance_status="N/A"):
        """
        Logs decisions for ethical AI and compliance review.
        decision_context: Description of the decision being made (e.g., 'trade execution', 'prompt generation').
        decision_outcome: The result of the decision.
        bias_detected: Boolean indicating if any bias was detected in the process.
        compliance_status: Status regarding regulatory compliance (e.g., 'compliant', 'non-compliant', 'pending review').
        """
        log_entry = {
            "timestamp": pd.Timestamp.now(),
            "decision_context": decision_context,
            "decision_outcome": decision_outcome,
            "bias_detected": bias_detected,
            "compliance_status": compliance_status
        }
        print(f"Ethical Decision Log: {log_entry}")
        # In a real system, this would write to a dedicated log file or database
        return log_entry

    def get_risk_metrics(self):
        return {
            "max_risk_per_trade_percent": self.max_risk_per_trade_percent,
            "max_daily_drawdown_percent": self.max_daily_drawdown_percent,
            "current_daily_pnl": self.daily_pnl,
            "initial_capital": self.initial_capital
        }

if __name__ == "__main__":
    risk_manager = RiskManagement(max_risk_per_trade_percent=1, max_daily_drawdown_percent=5)
    risk_manager.set_initial_capital(100000)

    # Example: Position Sizing
    entry = 100
    stop = 99.5
    quantity = risk_manager.check_position_sizing(entry_price=entry, stop_loss_price=stop)
    print(f"Calculated quantity for trade: {quantity} shares")

    # Example: Stop Loss Check (Long Position)
    current_price_long = 99.4
    stop_loss_long = 99.5
    if risk_manager.check_stop_loss(current_price=current_price_long, entry_price=entry, stop_loss_price=stop_loss_long, action="BUY"):
        print("Initiate exit for long position due to stop loss.")
    else:
        print("Long position is safe.")

    # Example: Daily Drawdown Check
    risk_manager.update_daily_pnl(-2000) # Simulate a loss of 2000
    if risk_manager.check_daily_drawdown():
        print("Daily trading halted due to drawdown limit.")
    else:
        print(f"Current daily PnL: {risk_manager.daily_pnl}. Still within drawdown limits.")

    risk_manager.update_daily_pnl(-3500) # Simulate another loss of 3500 (total -5500)
    if risk_manager.check_daily_drawdown():
        print("Daily trading halted due to drawdown limit.")
    else:
        print(f"Current daily PnL: {risk_manager.daily_pnl}. Still within drawdown limits.")

    print("\nRisk Metrics:")
    print(risk_manager.get_risk_metrics())

    # Example: Monte Carlo Simulation
    # Generate some dummy historical returns for demonstration
    np.random.seed(42) # for reproducibility
    dummy_returns = np.random.normal(0.0005, 0.01, 252) # Mean 0.05%, Std Dev 1% daily returns
    sim_paths, var = risk_manager.run_monte_carlo_simulation(dummy_returns)

    # Example: Correlation-based limits
    dummy_correlations = {
        ('SENSEX', 'BANKNIFTY'): 0.95,
        ('GOLD', 'USDINR'): -0.30
    }
    dummy_exposure = {
        'SENSEX': 0.30,
        'BANKNIFTY': 0.25,
        'GOLD': 0.10
    }
    risk_manager.check_correlation_based_limits(dummy_correlations, dummy_exposure)

    # Example: Ethical AI Logging
    risk_manager.log_ethical_decision(
        decision_context="Trade Execution for NIFTY Option",
        decision_outcome="BUY 50 NIFTYCE",
        bias_detected=False,
        compliance_status="compliant"
    )

    risk_manager.log_ethical_decision(
        decision_context="Prompt Generation for Strategy Suggestion",
        decision_outcome="Generated 'Buy the Dip' strategy",
        bias_detected=True,
        compliance_status="pending review"
    )