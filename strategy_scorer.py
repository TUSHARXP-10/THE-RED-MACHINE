import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tabulate import tabulate
from prompt_optimizer import PromptOptimizer
from market_regime_labeler import MarketRegimeLabeler

REFINED_STRATEGIES_DIR = 'refined_strategies/'

class StrategyScorer:
    def __init__(self, backtest_results_path='gpt_backtest_results.csv', leaderboard_path='leaderboard.csv', market_data_path='market_data.csv'):
        self.prompt_optimizer = PromptOptimizer() # Initialize PromptOptimizer
        self.backtest_results_path = backtest_results_path
        self.leaderboard_path = leaderboard_path
        self.market_regime_labeler = MarketRegimeLabeler(market_data_path) # Initialize MarketRegimeLabeler
        self.scoring_metrics = {
            'sharpe_ratio': {'weight': 0.4, 'direction': 'higher'},
            'total_pnl': {'weight': 0.3, 'direction': 'higher'},
            'max_drawdown': {'weight': 0.2, 'direction': 'lower'},
            'win_rate': {'weight': 0.1, 'direction': 'higher'}
        }

    def load_backtest_results(self):
        try:
            df = pd.read_csv(self.backtest_results_path)
            # Ensure 'strategy_name' is the key for merging/joining
            if 'strategy_name' not in df.columns:
                print("Error: 'strategy_name' column not found in backtest results.")
                return pd.DataFrame()

            # Label regimes for the backtest results based on their dates
            # Assuming backtest_results.csv has a 'date' column for each strategy's backtest period
            # For now, we'll use a placeholder or assume a single regime for simplicity
            # In a real scenario, you'd need to map each strategy's backtest period to a regime.
            # For the purpose of this integration, we'll add a dummy 'regime' column if not present
            # and then use the label_regimes method if a date column is available.

            # If 'regime' column is not present, add a placeholder. It should have been added by patch_backtest_results.py
            if 'regime' not in df.columns:
                df['regime'] = 'unknown' # Placeholder, should be filled by patch_backtest_results.py
            
            # If 'themes' column is not present, add a placeholder. It should have been added by patch_backtest_results.py
            if 'themes' not in df.columns:
                df['themes'] = '[]' # Placeholder, should be filled by patch_backtest_results.py

            return df
        except FileNotFoundError:
            print(f"Error: Backtest results file not found at {self.backtest_results_path}")
            return pd.DataFrame()

    def calculate_scores(self, df):
        if df.empty:
            return pd.DataFrame()

        # Normalize metrics
        scaler = MinMaxScaler()
        for metric, params in self.scoring_metrics.items():
            if metric in df.columns:
                # Handle potential non-numeric values or NaNs
                df[metric] = pd.to_numeric(df[metric], errors='coerce')
                df.dropna(subset=[metric], inplace=True)

                if not df.empty:
                    if params['direction'] == 'higher':
                        df[f'{metric}_normalized'] = scaler.fit_transform(df[[metric]])
                    else:  # 'lower'
                        df[f'{metric}_normalized'] = 1 - scaler.fit_transform(df[[metric]])
                else:
                    print(f"Warning: No data to normalize for metric {metric} after dropping NaNs.")
                    df[f'{metric}_normalized'] = 0 # Assign 0 if no data
            else:
                print(f"Warning: Metric '{metric}' not found in backtest results.")
                df[f'{metric}_normalized'] = 0 # Assign 0 if metric column is missing

        # Calculate composite score
        df['composite_score'] = 0
        for metric, params in self.scoring_metrics.items():
            normalized_col = f'{metric}_normalized'
            if normalized_col in df.columns:
                df['composite_score'] += df[normalized_col] * params['weight']

        return df.sort_values(by='composite_score', ascending=False)

    def update_leaderboard(self, new_results_df):
        if new_results_df.empty:
            print("No new results to add to the leaderboard.")
            return

        try:
            existing_leaderboard = pd.read_csv(self.leaderboard_path)
        except FileNotFoundError:
            existing_leaderboard = pd.DataFrame()

        # Combine new and existing results, remove duplicates (e.g., if a strategy was re-run)
        combined_df = pd.concat([existing_leaderboard, new_results_df]).drop_duplicates(subset=['strategy_name'], keep='last')

        # Recalculate scores for the combined dataframe to ensure consistent normalization
        final_leaderboard = self.calculate_scores(combined_df.copy())

        final_leaderboard.to_csv(self.leaderboard_path, index=False)
        print(f"Leaderboard updated and saved to {self.leaderboard_path}")

        # Update prompt scores in the PromptOptimizer
        for index, row in new_results_df.iterrows():
            prompt_hash = row.get('prompt_hash') # Assuming 'prompt_hash' column exists
            if prompt_hash:
                metrics = {
                    'sharpe_ratio': row.get('sharpe_ratio'),
                    'total_pnl': row.get('total_pnl'),
                    'max_drawdown': row.get('max_drawdown'),
                    'win_rate': row.get('win_rate'),
                    'composite_score': row.get('composite_score')
                }
                # Also pass themes and regime to the prompt optimizer
                themes = row.get('themes')
                regime = row.get('regime')
                self.prompt_optimizer.update_prompt_score(prompt_hash, metrics, themes=themes, regime=regime)
                print(f"Updated score for prompt {prompt_hash}")
        return final_leaderboard

    def display_leaderboard(self, top_n=10):
        try:
            leaderboard_df = pd.read_csv(self.leaderboard_path)
            if leaderboard_df.empty:
                print("Leaderboard is empty.")
                return

            print(f"\n--- Top {top_n} Strategies Leaderboard ---")
            display_df = leaderboard_df[['strategy_name', 'composite_score'] + [col for col in self.scoring_metrics if col in leaderboard_df.columns]].head(top_n)
            print(tabulate(display_df, headers='keys', tablefmt='pretty'))
        except FileNotFoundError:
            print("Leaderboard file not found. Run scoring first.")

if __name__ == '__main__':
    scorer = StrategyScorer()
    results_df = scorer.load_backtest_results()
    if not results_df.empty:
        scored_df = scorer.calculate_scores(results_df.copy())
        if not scored_df.empty:
            scorer.update_leaderboard(scored_df)
            scorer.display_leaderboard()
        else:
            print("No strategies could be scored.")
    else:
        print("No backtest results to score.")