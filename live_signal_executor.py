import time
import json
import os
import yaml
from broker_interface import KiteBrokerInterface
from telegram_signal_bot import TelegramSignalBot

# SENSEX-specific configuration
UNDERLYING_INDEX = "SENSEX"
EXCHANGE_CODE = "BSE"
STOCK_CODE = "BSESEN"
BASE_PRICE_LEVEL = 81000

class LiveSignalExecutor:
    def __init__(self, config_path='signal_config.json', leaderboard_path='leaderboard.csv', strategies_dir='refined_strategies/'):
        self.config = self._load_config(config_path)
        self.broker = KiteBrokerInterface()
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
        current_price = market_data.get('current_price', 81000)
        volume = market_data.get('volume', 0)
        
        # Track price history for calculations
        if not hasattr(self, 'price_history'):
            self.price_history = []
            self.previous_price = None
            
        # Add current price to history
        self.price_history.append(current_price)
        if len(self.price_history) > 20:
            self.price_history.pop(0)
            
        # Calculate metrics
        price_change = 0
        price_change_percent = 0
        volatility = 0
        
        if self.previous_price is not None:
            price_change = current_price - self.previous_price
            price_change_percent = (price_change / self.previous_price) * 100
            
        if len(self.price_history) >= 5:
            import numpy as np
            price_std = np.std(self.price_history)
            mean_price = np.mean(self.price_history)
            if mean_price > 0:
                volatility = (price_std / mean_price) * 100

        print(f"📊 {strategy_name} Analysis:")
        print(f"   Price: ₹{current_price:,.2f}")
        print(f"   Change: {price_change_percent:+.2f}%")
        print(f"   Volume: {volume:,}")
        print(f"   Volatility: {volatility:.2f}%")

        # Ensure SENSEX-only filtering
        if self.config.get('symbol_filter') != 'SENSEX':
            print("Error: Symbol filter not set to SENSEX. Skipping strategy evaluation.")
            return False

        # Ultra-fast scalping rule evaluation
        for rule in self.active_strategy['rules']:
            rule_type = rule.get('type')
            action = rule.get('action')
            confidence = rule.get('confidence', 0.9)
            
            rule_triggered = False
            
            # Aggressive scalping conditions
            if rule_type == 'entry':
                # Ultra-tight BUY_CALL: price up > 0.1% with volume > 1M
                if action == 'BUY_CALL' and price_change_percent > 0.1 and volume > 1000000:
                    rule_triggered = True
                    
                # Ultra-tight BUY_PUT: price down > 0.1% with volume > 1M  
                elif action == 'BUY_PUT' and price_change_percent < -0.1 and volume > 1000000:
                    rule_triggered = True
                    
            elif rule_type == 'exit':
                # Quick SQUARE_OFF: small profit/loss triggers exit
                if abs(price_change_percent) > 0.3:
                    rule_triggered = True
                    
            elif rule_type == 'no_trade':
                # Only avoid extreme volatility
                if volatility > 5.0:
                    rule_triggered = True

            if rule_triggered:
                print(f"✅ Rule triggered: {action} (confidence: {confidence})")
                
                # Determine strike based on current price
                strike = self._determine_strike(current_price, action)
                
                self.previous_price = current_price
                return {
                    "signal": action, 
                    "strike": strike, 
                    "price": current_price,
                    "confidence": confidence,
                    "change_pct": price_change_percent
                }

        self.previous_price = current_price
        return False
        
    def _determine_strike(self, current_price, action):
        """Determine appropriate strike price based on current SENSEX level"""
        # Round to nearest 100 for SENSEX options
        base_strike = round(current_price / 100) * 100
        
        if action in ['BUY_CALL', 'SELL_CALL']:
            # Slightly OTM call
            return f"SENSEX_{base_strike + 200}_CE"
        elif action in ['BUY_PUT', 'SELL_PUT']:
            # Slightly OTM put  
            return f"SENSEX_{base_strike - 200}_PE"
        else:
            return f"SENSEX_{base_strike}_ATM"

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

            market_data = self.broker.get_sensex_data()

            if market_data:
                signal = self._evaluate_strategy_rules(market_data)
                if signal and signal['signal'] in ["BUY_CALL", "BUY_PUT", "SELL_CALL", "SELL_PUT", "SQUARE_OFF"]:
                    print(f"🚀 SCALPING SIGNAL: {signal['signal']} at ₹{signal['price']:.2f}")
                    # Pass the strategy name as strategy_id
                    result = self.broker.place_order(signal['strike'], signal['signal'], signal['price'], self.active_strategy.get('name', 'UNKNOWN'))
                    if result and result['status'] == 'success':
                        trades_today += 1
                        print(f"✅ SCALP TRADE EXECUTED! Total trades today: {trades_today}")
                        self.telegram_bot.send_signal_alert(self.active_strategy.get('name', 'UNKNOWN'), signal['signal'], signal['price'], signal['strike'])
                    else:
                        print(f"❌ Failed to place order: {result.get('message', 'Unknown error')}")
                else:
                    print("⚡ No scalping signal yet...")
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