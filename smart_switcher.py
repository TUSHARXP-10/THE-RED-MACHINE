import pandas as pd
import json
from typing import Dict, Any, Optional

class SmartSwitcher:
    def __init__(self, backtest_results_path: str = 'backtest_results.csv',
                 model_metrics_path: str = 'model_metrics.json'):
        self.backtest_results_path = backtest_results_path
        self.model_metrics_path = model_metrics_path
        self.backtest_results = self._load_backtest_results()
        self.model_metrics = self._load_model_metrics()

    def _load_backtest_results(self) -> Optional[pd.DataFrame]:
        try:
            return pd.read_csv(self.backtest_results_path)
        except FileNotFoundError:
            print(f"Warning: {self.backtest_results_path} not found. SmartSwitcher will rely on model_metrics.json.")
            return None

    def _load_model_metrics(self) -> Dict[str, Any]:
        try:
            with open(self.model_metrics_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {self.model_metrics_path} not found. SmartSwitcher cannot operate without model metrics.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {self.model_metrics_path}. Check file format.")
            return {}

    def get_best_model(self, metric: str = 'sharpe_ratio', ascending: bool = False) -> Optional[str]:
        """
        Analyzes model metrics and returns the ID of the best model.
        Prioritizes model_metrics.json if available and comprehensive.
        """
        if self.model_metrics:
            # Assuming model_metrics.json contains a dictionary where keys are model_ids
            # and values are dictionaries of metrics.
            # Example: {"model_A": {"sharpe_ratio": 1.5, "accuracy": 0.8}, ...}
            
            best_model_id = None
            best_metric_value = None

            for model_id, metrics in self.model_metrics.items():
                if metric in metrics:
                    current_metric_value = metrics[metric]
                    if best_model_id is None or \
                       (not ascending and current_metric_value > best_metric_value) or \
                       (ascending and current_metric_value < best_metric_value):
                        best_metric_value = current_metric_value
                        best_model_id = model_id
            
            if best_model_id:
                print(f"Best model identified from model_metrics.json: {best_model_id} with {metric} = {best_metric_value}")
                return best_model_id
            else:
                print(f"Warning: Metric '{metric}' not found in model_metrics.json for any model.")

        if self.backtest_results is not None and not self.backtest_results.empty:
            # Assuming backtest_results.csv has columns like 'strategy_id' and various metrics
            if metric in self.backtest_results.columns:
                best_model_row = self.backtest_results.sort_values(by=metric, ascending=ascending).iloc[0]
                best_model_id = best_model_row['strategy_id']
                best_metric_value = best_model_row[metric]
                print(f"Best model identified from backtest_results.csv: {best_model_id} with {metric} = {best_metric_value}")
                return str(best_model_id)
            else:
                print(f"Warning: Metric '{metric}' not found in backtest_results.csv.")
        
        print("No suitable model found based on available data and metric.")
        return None

    def get_model_details(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves details for a specific model ID.
        """
        if self.model_metrics and model_id in self.model_metrics:
            return self.model_metrics[model_id]
        
        if self.backtest_results is not None and not self.backtest_results.empty:
            details = self.backtest_results[self.backtest_results['strategy_id'] == model_id]
            if not details.empty:
                return details.iloc[0].to_dict()
        
        print(f"Model details not found for ID: {model_id}")
        return None

    def check_model_health(self, model_id: str, accuracy_threshold: float = 0.7) -> bool:
        """
        Checks if a model meets a minimum accuracy threshold.
        """
        details = self.get_model_details(model_id)
        if details and 'accuracy' in details:
            if details['accuracy'] >= accuracy_threshold:
                print(f"Model {model_id} is healthy (accuracy: {details['accuracy']:.2f} >= {accuracy_threshold:.2f}).")
                return True
            else:
                print(f"Model {model_id} is unhealthy (accuracy: {details['accuracy']:.2f} < {accuracy_threshold:.2f}).")
                return False
        print(f"Accuracy metric not available for model {model_id}. Assuming healthy for now.")
        return True # Assume healthy if accuracy not available

# Example Usage:
if __name__ == "__main__":
    # Create dummy backtest_results.csv for testing
    dummy_backtest_data = {
        'strategy_id': ['XGBoost_v1', 'LSTM_v1', 'RandomForest_v1', 'SVR_v1'],
        'sharpe_ratio': [1.2, 1.8, 1.5, 0.9],
        'accuracy': [0.75, 0.82, 0.78, 0.65],
        'win_rate': [0.60, 0.70, 0.65, 0.55]
    }
    dummy_df = pd.DataFrame(dummy_backtest_data)
    dummy_df.to_csv('backtest_results.csv', index=False)

    # Create dummy model_metrics.json for testing
    dummy_model_metrics = {
        "XGBoost_v1": {"sharpe_ratio": 1.25, "accuracy": 0.76, "f1_score": 0.70},
        "LSTM_v1": {"sharpe_ratio": 1.85, "accuracy": 0.83, "f1_score": 0.78},
        "RandomForest_v1": {"sharpe_ratio": 1.55, "accuracy": 0.79, "f1_score": 0.73},
        "SVR_v1": {"sharpe_ratio": 0.95, "accuracy": 0.68, "f1_score": 0.62}
    }
    with open('model_metrics.json', 'w') as f:
        json.dump(dummy_model_metrics, f, indent=4)

    switcher = SmartSwitcher()

    # Get best model by Sharpe Ratio
    best_model_sharpe = switcher.get_best_model(metric='sharpe_ratio')
    print(f"Daily recommended model (Sharpe): {best_model_sharpe}")

    # Get best model by Accuracy
    best_model_accuracy = switcher.get_best_model(metric='accuracy')
    print(f"Daily recommended model (Accuracy): {best_model_accuracy}")

    # Check health of a specific model
    is_healthy = switcher.check_model_health('LSTM_v1', accuracy_threshold=0.8)
    print(f"Is LSTM_v1 healthy? {is_healthy}")

    is_healthy_low = switcher.check_model_health('SVR_v1', accuracy_threshold=0.8)
    print(f"Is SVR_v1 healthy? {is_healthy_low}")

    # Clean up dummy files
    import os
    os.remove('backtest_results.csv')
    os.remove('model_metrics.json')