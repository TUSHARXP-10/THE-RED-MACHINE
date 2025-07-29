# portfolio_engine.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

class PortfolioEngine:
    def __init__(self, detailed_trades_path='detailed_trades.csv', output_dir='results'):
        self.detailed_trades_path = detailed_trades_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.trades_df = self._load_detailed_trades()

    def _load_detailed_trades(self):
        """Loads detailed trade logs from the CSV file."""
        try:
            df = pd.read_csv(self.detailed_trades_path)
            # Ensure 'Date' column is datetime type for potential time-series analysis
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
            return df
        except FileNotFoundError:
            print(f"Error: {self.detailed_trades_path} not found. Please run Strategy Lab first to generate it.")
            return pd.DataFrame()

    def aggregate_trades(self):
        """Aggregates trades across strategies and calculates key metrics."""
        if self.trades_df.empty:
            print("No trade data to aggregate.")
            return None

        # Aggregate P&L by strategy
        pnl_by_strategy = self.trades_df.groupby('Strategy')['PnL'].sum().reset_index()
        pnl_by_strategy.rename(columns={'PnL': 'Total PnL'}, inplace=True)

        # Aggregate exposure by strategy
        exposure_by_strategy = self.trades_df.groupby('Strategy')['Exposure'].sum().reset_index()
        exposure_by_strategy.rename(columns={'Exposure': 'Total Exposure'}, inplace=True)

        # Combine aggregated data
        portfolio_snapshot = pd.merge(pnl_by_strategy, exposure_by_strategy, on='Strategy', how='outer')

        # Add overall metrics
        portfolio_snapshot['Net PnL'] = portfolio_snapshot['Total PnL'].sum()
        portfolio_snapshot['Net Exposure'] = portfolio_snapshot['Total Exposure'].sum()

        return portfolio_snapshot

    def track_pnl_by_expiry(self):
        """Tracks P&L by expiry."""
        if self.trades_df.empty:
            return None
        pnl_expiry = self.trades_df.groupby('Expiry')['PnL'].sum().reset_index()
        return pnl_expiry

    def track_exposure_by_type(self):
        """Tracks exposure by sector and signal type."""
        if self.trades_df.empty:
            return None
        exposure_sector = self.trades_df.groupby('Sector')['Exposure'].sum().reset_index()
        exposure_signal = self.trades_df.groupby('SignalType')['Exposure'].sum().reset_index()
        return exposure_sector, exposure_signal

    def assign_capital_risk(self, strategy_capital_allocation):
        """Assigns capital and risk per strategy (placeholder for more complex logic)."""
        # This method would typically involve more sophisticated risk models.
        # For now, it's a simple assignment based on a dictionary.
        if self.trades_df.empty:
            return None

        df_with_allocation = self.trades_df.copy()
        df_with_allocation['AllocatedCapital'] = df_with_allocation['Strategy'].map(strategy_capital_allocation)
        df_with_allocation['RiskPerTrade'] = df_with_allocation['AllocatedCapital'] * 0.01 # Example: 1% risk per trade
        return df_with_allocation

    def prevent_over_exposure(self, max_exposure_per_strategy=0.3, max_exposure_total=0.8):
        """Checks and flags potential over-exposure."""
        if self.trades_df.empty:
            return None, "No trades to check for over-exposure."

        total_portfolio_exposure = self.trades_df['Exposure'].sum()
        over_exposure_flags = {}

        for strategy, group in self.trades_df.groupby('Strategy'):
            strategy_exposure = group['Exposure'].sum()
            if strategy_exposure / total_portfolio_exposure > max_exposure_per_strategy:
                over_exposure_flags[strategy] = f"Exceeds {max_exposure_per_strategy*100}% of total portfolio exposure."

        if total_portfolio_exposure / self.trades_df['Exposure'].sum() > max_exposure_total: # This logic needs total capital base
             # For now, let's just check if total exposure is too high relative to itself (dummy)
            if total_portfolio_exposure > 10000: # Arbitrary threshold
                over_exposure_flags['Total Portfolio'] = f"Total portfolio exposure ({total_portfolio_exposure}) is high."

        if over_exposure_flags:
            return True, over_exposure_flags
        else:
            return False, "No over-exposure detected."

    def save_portfolio_snapshot(self, snapshot_df, filename='portfolio_snapshot.csv'):
        """Saves the portfolio snapshot to a CSV file."""
        if snapshot_df is not None:
            filepath = os.path.join(self.output_dir, filename)
            snapshot_df.to_csv(filepath, index=False)
            print(f"Portfolio snapshot saved to {filepath}")

    def plot_portfolio_metrics(self, portfolio_snapshot, pnl_expiry, exposure_sector, exposure_signal):
        """Generates and saves plots for portfolio metrics."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Plot 1: P&L by Strategy
        if portfolio_snapshot is not None and not portfolio_snapshot.empty:
            plt.figure(figsize=(10, 6))
            sns.barplot(x='Strategy', y='Total PnL', data=portfolio_snapshot)
            plt.title('Total PnL by Strategy')
            plt.xlabel('Strategy')
            plt.ylabel('Total PnL')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_dir, 'pnl_by_strategy.png'))
            plt.close()

        # Plot 2: P&L by Expiry
        if pnl_expiry is not None and not pnl_expiry.empty:
            plt.figure(figsize=(10, 6))
            sns.barplot(x='Expiry', y='PnL', data=pnl_expiry)
            plt.title('PnL by Expiry')
            plt.xlabel('Expiry')
            plt.ylabel('PnL')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_dir, 'pnl_by_expiry.png'))
            plt.close()

        # Plot 3: Exposure by Sector
        if exposure_sector is not None and not exposure_sector.empty:
            plt.figure(figsize=(10, 6))
            sns.barplot(x='Sector', y='Exposure', data=exposure_sector)
            plt.title('Exposure by Sector')
            plt.xlabel('Sector')
            plt.ylabel('Exposure')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_dir, 'exposure_by_sector.png'))
            plt.close()

        # Plot 4: Exposure by Signal Type
        if exposure_signal is not None and not exposure_signal.empty:
            plt.figure(figsize=(10, 6))
            sns.barplot(x='SignalType', y='Exposure', data=exposure_signal)
            plt.title('Exposure by Signal Type')
            plt.xlabel('Signal Type')
            plt.ylabel('Exposure')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_dir, 'exposure_by_signal_type.png'))
            plt.close()


if __name__ == "__main__":
    # Example Usage:
    # Ensure backtest_results.csv exists and has some data (even summary data for initial testing)
    # For a more robust solution, strategy_lab.py should output a detailed trade log.

    # Ensure detailed_trades.csv exists and has some data
    # This part is for testing the portfolio engine independently. In a real flow,
    # strategy_lab.py would generate detailed_trades.csv first.
    if not os.path.exists('detailed_trades.csv') or os.path.getsize('detailed_trades.csv') == 0:
        print("Creating dummy detailed_trades.csv for Portfolio Engine testing with more diverse data...")
        dummy_trades = {
            'Strategy': ['RSI_Drop_IV_Surge', 'IV_Reversion', 'OI_Build_Up', 'RSI_Drop_IV_Surge', 'IV_Reversion', 'OI_Build_Up', 'RSI_Drop_IV_Surge', 'IV_Reversion', 'OI_Build_Up', 'RSI_Drop_IV_Surge', 'IV_Reversion', 'OI_Build_Up'],
            'Date': pd.to_datetime([f'2023-{month:02d}-{day:02d}' for month in range(1, 13) for day in range(1, 29)]),

            'PnL': [10, -5, 20, 15, -12, 8, 25, -7, 30, -10, 5, -18, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6, 7, -7, 8, -8, 9, -9, 10, -10, 11, -11, 12, -12],
            'Exposure': [1000, 1500, 1200, 1100, 1300, 900, 1400, 1600, 1150, 1450, 1050, 1350],
            'Expiry': ['2023-12-31', '2023-12-31', '2024-01-31', '2023-12-31', '2024-01-31', '2023-12-31', '2024-01-31', '2023-12-31', '2024-01-31', '2023-12-31', '2024-01-31', '2023-12-31'],
            'Sector': ['Tech', 'Finance', 'Healthcare', 'Tech', 'Finance', 'Healthcare', 'Tech', 'Finance', 'Healthcare', 'Tech', 'Finance', 'Healthcare'],
            'SignalType': ['Trend', 'Reversion', 'Momentum', 'Trend', 'Reversion', 'Momentum', 'Trend', 'Reversion', 'Momentum', 'Trend', 'Reversion', 'Momentum']
        }
        pd.DataFrame(dummy_trades).to_csv('detailed_trades.csv', index=False)

    engine = PortfolioEngine()

    # 1. Aggregate all trades across strategies
    portfolio_snapshot = engine.aggregate_trades()
    if portfolio_snapshot is not None:
        print("\nPortfolio Snapshot:")
        print(portfolio_snapshot)
        engine.save_portfolio_snapshot(portfolio_snapshot)

    # 2. Track P&L by expiry
    pnl_expiry = engine.track_pnl_by_expiry()
    if pnl_expiry is not None:
        print("\nPnL by Expiry:")
        print(pnl_expiry)

    # 3. Track exposure by sector and signal type
    exposure_sector, exposure_signal = engine.track_exposure_by_type()
    if exposure_sector is not None:
        print("\nExposure by Sector:")
        print(exposure_sector)
    if exposure_signal is not None:
        print("\nExposure by Signal Type:")
        print(exposure_signal)

    # 4. Assign capital/risk per strategy (example allocation)
    strategy_capital_allocation = {
        'RSI_Drop_IV_Surge': 100000,
        'IV_Reversion': 150000,
        'OI_Build_Up': 80000
    }
    df_with_allocation = engine.assign_capital_risk(strategy_capital_allocation)
    if df_with_allocation is not None:
        print("\nTrades with Capital Allocation and Risk:")
        print(df_with_allocation.head())

    # 5. Prevent over-exposure to one type
    is_over_exposed, over_exposure_details = engine.prevent_over_exposure()
    print(f"\nOver-exposure detected: {is_over_exposed}")
    if is_over_exposed:
        print("Over-exposure details:", over_exposure_details)

    # Generate and save plots
    engine.plot_portfolio_metrics(portfolio_snapshot, pnl_expiry, exposure_sector, exposure_signal)
    print(f"\nPortfolio plots saved to the '{engine.output_dir}' directory.")