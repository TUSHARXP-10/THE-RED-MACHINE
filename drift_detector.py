import os
import json
import pandas as pd
from datetime import datetime

# Define paths
LEADERBOARD_PATH = 'leaderboard.csv'
DRIFT_METRICS_FILE = '.drift_metrics.json'
STRATEGIES_DIR = 'strategies/'
REFINED_STRATEGIES_DIR = 'refined_strategies/'

class DriftDetector:
    def __init__(self):
        self.drift_metrics = self._load_drift_metrics()

    def _load_drift_metrics(self):
        if os.path.exists(DRIFT_METRICS_FILE):
            with open(DRIFT_METRICS_FILE, 'r') as f:
                return json.load(f)
        return {}

    def _save_drift_metrics(self):
        with open(DRIFT_METRICS_FILE, 'w') as f:
            json.dump(self.drift_metrics, f, indent=4)

    def record_current_metrics(self):
        if not os.path.exists(LEADERBOARD_PATH):
            print(f"Leaderboard file not found at {LEADERBOARD_PATH}")
            return

        leaderboard_df = pd.read_csv(LEADERBOARD_PATH)
        current_timestamp = datetime.now().isoformat()

        for index, row in leaderboard_df.iterrows():
            strategy_name = row['Strategy Name']
            if strategy_name not in self.drift_metrics:
                self.drift_metrics[strategy_name] = []

            self.drift_metrics[strategy_name].append({
                'timestamp': current_timestamp,
                'sharpe_ratio': row['Sharpe Ratio'],
                'pnl': row['PnL'],
                'max_drawdown': row['Max Drawdown'],
                'win_rate': row['Win Rate']
            })
        self._save_drift_metrics()
        print(f"Recorded current metrics for {len(leaderboard_df)} strategies.")

    def detect_drift(self, threshold_percentage=0.10, min_history_points=5):
        drifted_strategies = []
        for strategy_name, history in self.drift_metrics.items():
            if len(history) < min_history_points:
                continue

            # Convert history to DataFrame for easier analysis
            history_df = pd.DataFrame(history)
            history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
            history_df = history_df.sort_values(by='timestamp')

            # Consider the last few points for current performance and overall average
            recent_performance = history_df.tail(min_history_points)
            
            # Metrics to monitor for degradation (lower is worse for Sharpe, PnL, Win Rate; higher is worse for Drawdown)
            metrics_to_monitor = {
                'sharpe_ratio': 'lower',
                'pnl': 'lower',
                'win_rate': 'lower',
                'max_drawdown': 'higher'
            }

            has_drift = False
            for metric, trend in metrics_to_monitor.items():
                if metric not in recent_performance.columns:
                    continue

                current_value = recent_performance[metric].iloc[-1]
                historical_average = history_df[metric].mean()

                if trend == 'lower':
                    if current_value < historical_average * (1 - threshold_percentage):
                        print(f"Drift detected for {strategy_name} in {metric}: Current {current_value:.2f} < Historical Avg {historical_average:.2f} by > {threshold_percentage*100}% (lower is worse)")
                        has_drift = True
                        break
                elif trend == 'higher':
                    if current_value > historical_average * (1 + threshold_percentage):
                        print(f"Drift detected for {strategy_name} in {metric}: Current {current_value:.2f} > Historical Avg {historical_average:.2f} by > {threshold_percentage*100}% (higher is worse)")
                        has_drift = True
                        break
            
            if has_drift:
                drifted_strategies.append(strategy_name)
        return drifted_strategies

    def update_strategy_status(self, strategy_name, status):
        # This method will update the YAML file for the strategy
        # It assumes strategies are in 'refined_strategies/' or 'strategies/'
        # and have a 'status' field.
        
        file_path = os.path.join(REFINED_STRATEGIES_DIR, f'{strategy_name}.yaml')
        if not os.path.exists(file_path):
            file_path = os.path.join(STRATEGIES_DIR, f'{strategy_name}.yaml')
            if not os.path.exists(file_path):
                print(f"Strategy YAML for {strategy_name} not found in either {REFINED_STRATEGIES_DIR} or {STRATEGIES_DIR}")
                return

        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()

            updated_lines = []
            status_found = False
            for line in lines:
                if line.strip().startswith('status:'):
                    updated_lines.append(f'status: {status}\n')
                    status_found = True
                else:
                    updated_lines.append(line)
            
            if not status_found:
                # Add status if not found, typically at the end or after a specific field
                # For simplicity, let's add it at the end if not found
                updated_lines.append(f'status: {status}\n')

            with open(file_path, 'w') as f:
                f.writelines(updated_lines)
            print(f"Updated status of {strategy_name} to '{status}' in {file_path}")
        except Exception as e:
            print(f"Error updating status for {strategy_name}: {e}")

    def auto_correct_drift(self, drifted_strategies):
        for strategy_name in drifted_strategies:
            print(f"Attempting to auto-correct drifted strategy: {strategy_name}")
            self.update_strategy_status(strategy_name, 'inactive')
            # Trigger a new GPT generation cycle for a replacement strategy
            print(f"Triggering new GPT strategy suggestion to replace {strategy_name}.")
            try:
                import subprocess
                import sys
                subprocess.run([sys.executable, 'gpt_strategy_suggestor.py'], check=True)
                print("New GPT strategy suggestion triggered successfully.")
            except Exception as e:
                print(f"Error triggering GPT strategy suggestion: {e}")

    def run_drift_detection_cycle(self):
        print("Running drift detection cycle...")
        self.record_current_metrics()
        drifted_strategies = self.detect_drift()
        if drifted_strategies:
            print(f"Detected drift in strategies: {', '.join(drifted_strategies)}")
            self.auto_correct_drift(drifted_strategies)
        else:
            print("No significant drift detected.")

if __name__ == '__main__':
    detector = DriftDetector()
    detector.run_drift_detection_cycle()

    # Example of how to manually update a strategy status
    # detector.update_strategy_status('example_strategy_name', 'active')
    # detector.update_strategy_status('example_strategy_name', 'inactive')

    # To test drift detection, you might manually edit leaderboard.csv
    # or .drift_metrics.json to simulate performance degradation.