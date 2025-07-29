import time
import json
import os
import yaml
from broker_interface import BrokerInterface
from telegram_signal_bot import TelegramSignalBot

class LiveSignalExecutor:
    def __init__(self, config_path='signal_config.json', leaderboard_path='leaderboard.csv', strategies_dir='refined_strategies/'):
        self.config = self._load_config(config_path)
        self.broker = BrokerInterface(config_path)
        self.leaderboard_path = leaderboard_path
        self.strategies_dir = strategies_dir
        self.active_strategy = None
        self.telegram_bot = TelegramSignalBot()

    def _load_config(self, config_path):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found at {config_path}")
        with open(config_path, 'r') as f:
            return json.load(f)

    def _get_top_strategy(self):
        print("Fetching top strategy from leaderboard.csv...")
        if not os.path.exists(self.leaderboard_path):
            print(f"Error: Leaderboard file not found at {self.leaderboard_path}")
            self.active_strategy = None
            return

        try:
            import pandas as pd
            leaderboard_df = pd.read_csv(self.leaderboard_path)
            if leaderboard_df.empty:
                print("Leaderboard is empty. No strategy to load.")
                self.active_strategy = None
                return

            # Assuming the top strategy is the first row after sorting by a performance metric
            # For now, let's just take the first one or assume a 'score' column exists
            # You might want to sort by 'composite_score' or 'sharpe_ratio' here
            top_strategy_id = leaderboard_df.iloc[0]['strategy_id'] # Assuming 'strategy_id' column
            strategy_file = os.path.join(self.strategies_dir, f'{top_strategy_id}.yaml')

            if os.path.exists(strategy_file):
                with open(strategy_file, 'r') as f:
                    self.active_strategy = yaml.safe_load(f)
                print(f"Loaded top strategy: {self.active_strategy.get('name', 'Unnamed Strategy')} from {strategy_file}")
            else:
                print(f"Warning: Strategy YAML not found for {top_strategy_id} at {strategy_file}. Live execution will not proceed.")
                self.active_strategy = None
        except Exception as e:
            print(f"Error loading top strategy: {e}")
            self.active_strategy = None

    def _evaluate_strategy_rules(self, market_data):
        if not self.active_strategy or 'rules' not in self.active_strategy:
            return False

        strategy_name = self.active_strategy.get('name', 'Unnamed Strategy')
        print(f"Evaluating rules for {strategy_name} with market data: {market_data}")

        # Ensure SENSEX-only filtering
        if self.config.get('symbol_filter') != 'SENSEX':
            print("Error: Symbol filter not set to SENSEX. Skipping strategy evaluation.")
            return False

        # Iterate through rules and evaluate them
        for rule in self.active_strategy['rules']:
            rule_type = rule.get('type')
            condition = rule.get('condition')
            action = rule.get('action')

            if rule_type == 'entry' and condition and action:
                # Simple evaluation: This needs to be expanded for complex conditions
                # For now, let's assume 'condition' is a string that can be evaluated
                # against market_data. This is a highly simplified example.
                try:
                    # Basic condition parsing for 'price > X' format
                    if 'price' in condition and '>' in condition:
                        parts = condition.split('>')
                        if len(parts) == 2:
                            try:
                                threshold_price = float(parts[1].strip())
                                if market_data.get('current_price', 0) > threshold_price:
                                    print(f"Rule met: {condition}. Generating {action} signal.")
                                    # The strike and price should be dynamically determined based on strategy and market data
                                    # For now, using dummy strike and current price
                                    return {"signal": action, "strike": "SENSEX_CALL_17000", "price": market_data['current_price']}
                            except ValueError:
                                print(f"Warning: Invalid price threshold in condition '{condition}'")
                    # Add more condition parsing logic here for other types of rules (e.g., '<', '==', 'AND', 'OR')
                    # For now, if no specific parsing, default to false

                except Exception as e:
                    print(f"Error evaluating rule '{condition}': {e}")
        return False

    def run(self):
        print("Starting live signal executor...")
        self._get_top_strategy()

        if not self.active_strategy:
            print("No active strategy loaded. Exiting.")
            return

        refresh_interval = self.config.get('refresh_interval_sec', 30)
        symbol_filter = self.config.get('symbol_filter', 'SENSEX')
        max_trades = self.config.get('max_trades_per_day', 3)
        trades_today = 0

        while trades_today < max_trades:
            print(f"Waiting for {refresh_interval} seconds...")
            time.sleep(refresh_interval)

            market_data = self.broker.get_market_data(symbol_filter)

            if market_data:
                signal = self._evaluate_strategy_rules(market_data)
                if signal and signal['signal'] == "BUY": # Assuming 'BUY' for now based on dummy strategy
                    print("Signal detected! Placing order...")
                    # Pass the strategy name as strategy_id
                    result = self.broker.place_order(signal['strike'], signal['signal'], signal['price'], self.active_strategy.get('name', 'UNKNOWN'))
                    if result and result['status'] == 'success':
                        trades_today += 1
                        print(f"Trade placed. Total trades today: {trades_today}")
                        self.telegram_bot.send_signal_alert(self.active_strategy.get('name', 'UNKNOWN'), signal['signal'], signal['price'], signal['strike'])
                    else:
                        print(f"Failed to place order: {result.get('message', 'Unknown error')}")
                else:
                    print("No signal generated.")
            else:
                print("Could not retrieve market data.")

        print(f"Max trades per day ({max_trades}) reached. Stopping execution.")

if __name__ == "__main__":
    # For testing, create a dummy strategy file if it doesn't exist
    dummy_strategy_path = 'refined_strategies/example_strategy.yaml'
    if not os.path.exists('refined_strategies'):
        os.makedirs('refined_strategies')
    if not os.path.exists(dummy_strategy_path):
        with open(dummy_strategy_path, 'w') as f:
            f.write("""
name: DummySENSEXStrategy
description: A simple dummy strategy for SENSEX options.
rules:
  - type: entry
    condition: price > 100
    action: BUY
""")
        print(f"Created dummy strategy file: {dummy_strategy_path}")

    executor = LiveSignalExecutor()
    executor.run()