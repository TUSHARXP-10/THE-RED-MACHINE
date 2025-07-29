import yaml
import pandas as pd
from datetime import datetime
from typing import Dict, List
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yaml

class StrategyLab:
    def __init__(self, data_path: str):
        """Initialize Strategy Lab with historical data"""
        self.data = pd.read_csv(data_path)
        self.results = []
        self.all_trades = pd.DataFrame()

    def load_strategies(self, config_path: str) -> List[Dict]:
        """Load strategy configurations from YAML file, filtering out inactive ones"""
        with open(config_path, 'r') as f:
            all_strategies = yaml.safe_load(f)
        
        active_strategies = [s for s in all_strategies if s.get('status', 'active').lower() == 'active']
        return active_strategies

    def backtest_strategy(self, strategy: Dict) -> Dict:
        """Backtest a single strategy and return performance metrics"""
        strategy_name = strategy['name']
        triggers = strategy['triggers']

        # Define a mapping for trigger keys to actual column names in the CSV
        column_mapping = {
            'rsi': 'RSI',
            'iv_zscore': 'IV_ZScore',
            'oi_change': 'OI_Change'
        }

        # Filter data based on triggers
        triggered_data = self.data.copy()
        for trigger_key, trigger_value in triggers.items():
            base_key = trigger_key.replace('_below', '').replace('_above', '')
            column = column_mapping.get(base_key, base_key) # Use mapping, or fallback to base_key if not found

            if '_below' in trigger_key:
                triggered_data = triggered_data[triggered_data[column] < trigger_value]
            elif '_above' in trigger_key:
                triggered_data = triggered_data[triggered_data[column] > trigger_value]

        total_trades = len(triggered_data)
        if total_trades == 0:
            return {
                'Strategy Name': strategy_name,
                'Total Trades': 0,
                'Accuracy': 0.0,
                'Avg PnL': 0.0,
                'Win Rate': '0%',
                'Sharpe': 0.0,
                'Max Drawdown': '0.0%'
            }

        total_pnl = triggered_data['PnL'].sum()
        winning_trades = triggered_data[triggered_data['PnL'] > 0].shape[0]
        losing_trades = triggered_data[triggered_data['PnL'] <= 0].shape[0]

        accuracy = winning_trades / total_trades if total_trades > 0 else 0.0
        avg_pnl = total_pnl / total_trades if total_trades > 0 else 0.0
        win_rate = f"{(winning_trades / total_trades * 100):.0f}%" if total_trades > 0 else '0%'

        # Calculate Sharpe Ratio (simplified, assuming daily returns and risk-free rate = 0)
        returns = triggered_data['PnL']
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0.0

        # Calculate Max Drawdown
        cumulative_pnl = triggered_data['PnL'].cumsum()
        peak = cumulative_pnl.expanding(min_periods=1).max()
        drawdown = (cumulative_pnl - peak) / peak
        max_drawdown = drawdown.min() if not drawdown.empty else 0.0

        # Add strategy name to each row of triggered_data for detailed logging
        triggered_data['Strategy'] = strategy_name

        return {
            'summary': {
                'Strategy Name': strategy_name,
                'Total Trades': total_trades,
                'Accuracy': round(accuracy, 2),
                'Avg PnL': round(avg_pnl, 2),
                'Win Rate': win_rate,
                'Sharpe': round(sharpe, 2),
                'Max Drawdown': f"{(max_drawdown * 100):.1f}%"
            },
            'trades': triggered_data # Return the detailed trades
        }

    def backtest_all(self, config_path: str) -> pd.DataFrame:
        """Backtest all strategies in config and return results"""
        strategies = self.load_strategies(config_path)
        
        for strategy in strategies:
            result = self.backtest_strategy(strategy)
            if 'summary' in result:
                self.results.append(result['summary'])
                if result['summary']['Total Trades'] > 0:
                    self.all_trades = pd.concat([self.all_trades, result['trades']], ignore_index=True)
            else:
                self.results.append(result)
        
        return pd.DataFrame(self.results)

    def save_results(self, summary_output_path: str, trades_output_path: str = 'detailed_trades.csv'):
        """Save backtest results to CSV"""
        pd.DataFrame(self.results).to_csv(summary_output_path, index=False)
        if not self.all_trades.empty:
            self.all_trades.to_csv(trades_output_path, index=False)

    def plot_results(self):
        """Generate visualizations of backtest results"""
        if not self.results:
            print("No results to plot. Run backtest_all first.")
            return

        results_df = pd.DataFrame(self.results)

        # PnL Histograms (requires individual trade PnL, which is not stored in self.results yet)
        # For now, we'll plot Avg PnL
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Strategy Name', y='Avg PnL', data=results_df)
        plt.title('Average PnL per Strategy')
        plt.ylabel('Average PnL')
        plt.xlabel('Strategy Name')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('results/avg_pnl_per_strategy.png')


        # Accuracy and Win Rate
        results_df['Win Rate Num'] = results_df['Win Rate'].str.replace('%', '').astype(float)
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        sns.barplot(x='Strategy Name', y='Accuracy', data=results_df, ax=axes[0])
        axes[0].set_title('Accuracy per Strategy')
        axes[0].set_ylabel('Accuracy')
        axes[0].set_xlabel('Strategy Name')
        axes[0].tick_params(axis='x', rotation=45)

        sns.barplot(x='Strategy Name', y='Win Rate Num', data=results_df, ax=axes[1])
        axes[1].set_title('Win Rate per Strategy')
        axes[1].set_ylabel('Win Rate (%)')
        axes[1].set_xlabel('Strategy Name')
        axes[1].tick_params(axis='x', rotation=45)
        plt.tight_layout()
        plt.savefig('results/accuracy_win_rate_per_strategy.png')


        # Sharpe Ratio and Max Drawdown
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        sns.barplot(x='Strategy Name', y='Sharpe', data=results_df, ax=axes[0])
        axes[0].set_title('Sharpe Ratio per Strategy')
        axes[0].set_ylabel('Sharpe Ratio')
        axes[0].set_xlabel('Strategy Name')
        axes[0].tick_params(axis='x', rotation=45)

        results_df['Max Drawdown Num'] = results_df['Max Drawdown'].str.replace('%', '').astype(float)
        sns.barplot(x='Strategy Name', y='Max Drawdown Num', data=results_df, ax=axes[1])
        axes[1].set_title('Max Drawdown per Strategy')
        axes[1].set_ylabel('Max Drawdown (%)')
        axes[1].set_xlabel('Strategy Name')
        axes[1].tick_params(axis='x', rotation=45)
        plt.tight_layout()
        plt.savefig('results/sharpe_drawdown_per_strategy.png')


        print(results_df[['Strategy Name', 'Total Trades', 'Accuracy', 'Avg PnL', 'Win Rate', 'Sharpe', 'Max Drawdown']].to_markdown(index=False))

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Strategy Lab Backtesting Engine')
    parser.add_argument('backtest', type=str, help='Run backtest for all strategies')
    parser.add_argument('config', type=str, help='Path to strategies config YAML')
    parser.add_argument('--summary_output', type=str, default='backtest_results.csv', 
                       help='Output path for summary results CSV')
    parser.add_argument('--trades_output', type=str, default='detailed_trades.csv', 
                       help='Output path for detailed trades CSV')
    parser.add_argument('--plot', action='store_true', help='Generate plots of backtest results')
    
    args = parser.parse_args()
    
    lab = StrategyLab('sensex_options.csv')
    results = lab.backtest_all(args.config)
    lab.save_results(summary_output_path=args.summary_output, trades_output_path=args.trades_output)
    
    if args.plot:
        import os
        if not os.path.exists('results'):
            os.makedirs('results')
        lab.plot_results()