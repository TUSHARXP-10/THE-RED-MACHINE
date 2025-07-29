import pandas as pd
import json

class ThemeRegimeAnalyzer:
    def __init__(self, prompt_score_index_path='prompt_score_index.json',
                 prompt_memory_path='prompt_memory.json',
                 backtest_results_path='backtest_results.csv'):
        self.prompt_score_index_path = prompt_score_index_path
        self.prompt_memory_path = prompt_memory_path
        self.backtest_results_path = backtest_results_path

        self.prompt_scores = self._load_json(self.prompt_score_index_path)
        self.prompt_memory = self._load_json(self.prompt_memory_path)
        self.backtest_results = self._load_csv(self.backtest_results_path)

    def _load_json(self, file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {file_path} not found.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {file_path}.")
            return {}

    def _load_csv(self, file_path):
        try:
            return pd.read_csv(file_path)
        except FileNotFoundError:
            print(f"Error: {file_path} not found.")
            return pd.DataFrame()

    def _get_prompt_themes(self, prompt_hash):
        return self.prompt_memory.get(prompt_hash, {}).get('themes', [])

    def analyze_theme_regime_correlation(self):
        if self.backtest_results.empty or not self.prompt_scores:
            print("Backtest results or prompt scores not loaded.")
            return pd.DataFrame()

        # Ensure 'strategy_hash' and 'regime' columns exist
        if 'strategy_hash' not in self.backtest_results.columns:
            print("Error: 'strategy_hash' column not found in backtest_results.csv")
            return pd.DataFrame()
        if 'regime' not in self.backtest_results.columns:
            print("Error: 'regime' column not found in backtest_results.csv. Please label market regimes first.")
            return pd.DataFrame()

        # Map strategy_hash to prompt_hash and then to themes
        # First, create a mapping from strategy_hash to prompt_hash from prompt_score_index
        strategy_to_prompt_map = {}
        for prompt_hash, data in self.prompt_scores.items():
            for strategy_info in data.get('strategies', []):
                strategy_to_prompt_map[strategy_info['strategy_hash']] = prompt_hash

        # Add prompt_hash and themes to backtest_results
        self.backtest_results['prompt_hash'] = self.backtest_results['strategy_hash'].map(strategy_to_prompt_map)
        self.backtest_results['themes'] = self.backtest_results['prompt_hash'].apply(self._get_prompt_themes)

        # Explode themes to have one row per theme for analysis
        df_exploded = self.backtest_results.explode('themes')

        # Group by theme and regime to calculate performance metrics
        # Assuming 'net_pnl' and 'sharpe_ratio' are available in backtest_results or can be derived
        # For simplicity, let's assume 'net_pnl' is directly available for aggregation
        # In a real scenario, you might need to calculate Sharpe per strategy per regime if daily PnL is available

        # For this example, let's aggregate average net_pnl per theme per regime
        # You might want to use more sophisticated metrics like average Sharpe Ratio for strategies within that theme/regime
        # This requires daily PnL data for each strategy, which is not directly in backtest_results.csv usually.
        # For now, we'll use cumulative_net_pnl from prompt_scores, mapped to strategies.

        # Let's join with prompt_scores to get performance metrics
        prompt_performance_df = pd.DataFrame.from_dict(self.prompt_scores, orient='index')
        prompt_performance_df.index.name = 'prompt_hash'
        prompt_performance_df = prompt_performance_df[['avg_sharpe_ratio', 'cumulative_net_pnl']]
        prompt_performance_df['prompt_hash'] = prompt_performance_df.index.astype(str)

        df_exploded['prompt_hash'] = df_exploded['prompt_hash'].astype(str)

        df_merged = df_exploded.merge(prompt_performance_df, on='prompt_hash', how='left')

        # Aggregate by theme and regime
        theme_regime_summary = df_merged.groupby(['themes', 'regime']).agg(
            avg_sharpe=('avg_sharpe_ratio', 'mean'),
            total_pnl=('cumulative_net_pnl', 'sum'),
            strategy_count=('strategy_hash', 'nunique')
        ).reset_index()

        return theme_regime_summary

if __name__ == '__main__':
    # Example Usage (requires dummy data for prompt_score_index.json, prompt_memory.json, backtest_results.csv)
    # Create dummy prompt_score_index.json
    dummy_prompt_scores = {
        "hash1": {"average_sharpe_ratio": 1.2, "cumulative_net_pnl": 1000, "strategies": [{"strategy_hash": "strat1"}, {"strategy_hash": "strat2"}]},
        "hash2": {"average_sharpe_ratio": 0.8, "cumulative_net_pnl": 500, "strategies": [{"strategy_hash": "strat3"}]},
        "hash3": {"average_sharpe_ratio": 1.5, "cumulative_net_pnl": 1500, "strategies": [{"strategy_hash": "strat4"}, {"strategy_hash": "strat5"}]},
    }
    with open('prompt_score_index.json', 'w') as f:
        json.dump(dummy_prompt_scores, f, indent=4)

    # Create dummy prompt_memory.json
    dummy_prompt_memory = {
        "hash1": {"prompt_text": "Trend following strategy for Nifty", "themes": ["nifty", "trend_following"]},
        "hash2": {"prompt_text": "Mean reversion strategy for Sensex", "themes": ["sensex", "mean_reversion"]},
        "hash3": {"prompt_text": "Scalping strategy for BankNifty", "themes": ["banknifty", "scalping"]},
    }
    with open('prompt_memory.json', 'w') as f:
        json.dump(dummy_prompt_memory, f, indent=4)

    # Create dummy backtest_results.csv
    dummy_backtest_results = pd.DataFrame({
        'strategy_hash': ['strat1', 'strat2', 'strat3', 'strat4', 'strat5'],
        'regime': ['uptrend', 'rangebound', 'uptrend', 'downtrend', 'rangebound'],
        'net_pnl': [100, 50, 200, -30, 80] # Example PnL, not used for Sharpe here directly
    })
    dummy_backtest_results.to_csv('backtest_results.csv', index=False)

    analyzer = ThemeRegimeAnalyzer()
    correlation_matrix = analyzer.analyze_theme_regime_correlation()

    if not correlation_matrix.empty:
        print("\nTheme-Regime Correlation Matrix:")
        print(correlation_matrix)
    else:
        print("No correlation matrix generated.")

    # Clean up dummy files
    # import os
    # os.remove('prompt_score_index.json')
    # os.remove('prompt_memory.json')
    # os.remove('backtest_results.csv')