import pandas as pd
import os
import json
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from market_regime_labeler import MarketRegimeLabeler
from sensex_env import SensexTradingEnv # Import the environment for loading models
import csv

class RegimeRouterExecutor:
    def __init__(self, model_dir='models/', rl_config_path='rl_config.json'):
        self.market_regime_labeler = MarketRegimeLabeler()
        self.model_dir = model_dir
        self.rl_config = self._load_rl_config(rl_config_path)
        self.ppo_agents = {}
        self.active_agent_status_path = 'active_agent_status.json'

    def _load_rl_config(self, rl_config_path):
        try:
            with open(rl_config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {rl_config_path} not found.")
            return {}

    def _save_active_agent_status(self, regime, agent_name):
        status = {
            "active_regime": regime,
            "active_agent_name": agent_name
        }
        with open(self.active_agent_status_path, 'w') as f:
            json.dump(status, f, indent=4)

    def _log_agent_rotation(self, timestamp, regime, model_loaded, action, reward, position, pnl):
        log_entry = {
            "timestamp": timestamp,
            "regime": regime,
            "model_loaded": model_loaded,
            "action": action,
            "reward": reward,
            "position": position,
            "pnl": pnl
        }
        log_file_path = 'logs/agent_rotation_log.csv'
        # Check if file exists to write header
        file_exists = os.path.exists(log_file_path)
        with open(log_file_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=log_entry.keys())
            if not file_exists:
                writer.writeheader()  # file doesn't exist yet, write a header
            writer.writerow(log_entry)

    def load_ppo_agent(self, regime):
        # Placeholder for loading the specific PPO agent for the given regime
        # In a real scenario, this would load a trained model (e.g., from a .zip file)
        # based on the regime.
        if regime not in self.ppo_agents:
            model_path = os.path.join(self.model_dir, f"ppo_agent_{regime}.zip")
            if os.path.exists(model_path):
                print(f"Loading PPO agent for {regime} from {model_path}")
                # When loading a PPO model, it needs an environment. We'll create a dummy one.
                # The actual environment used for training might be different, but for prediction,
                # a compatible observation space is needed.
                # For simplicity, we'll use a mock BreezeConnect and default initial_capital/mode.
                # In a real scenario, you might want to pass the actual env or a dummy env with correct specs.
                from breeze_connect import BreezeConnect
                class MockBreezeConnect:
                     def __init__(self, api_key, secret_key):
                         pass
                     def get_quotes(self, stock_code, exchange_code, product_type, expiry_date, right, strike_price):
                         return {"Success": True, "last_price": 72000} # Mock price
                
                mock_breeze = MockBreezeConnect("", "")
                dummy_env = SensexTradingEnv(breeze_connect=mock_breeze, initial_capital=100000, mode='paper', regime=regime)
                dummy_env = DummyVecEnv([lambda: dummy_env])

                self.ppo_agents[regime] = PPO.load(model_path, env=dummy_env)
            else:
                print(f"No PPO agent found for {regime} at {model_path}")
                self.ppo_agents[regime] = None
        return self.ppo_agents[regime]

    def execute_strategy(self, live_data):
        # Ensure live_data has 'high', 'low', 'close' for regime labeling
        if not all(col in live_data.columns for col in ['high', 'low', 'close']):
            print("Error: live_data must contain 'high', 'low', and 'close' columns for regime labeling.")
            return "No_Action_Taken"

        # 1. Detect regime from live data
        # Use the latest data point for current regime labeling
        latest_high = live_data['high'].iloc[-1]
        latest_low = live_data['low'].iloc[-1]
        latest_close = live_data['close'].iloc[-1]

        current_regime = self.market_regime_labeler.label_current_regime(latest_high, latest_low, latest_close)
        print(f"Detected market regime: {current_regime}")

        if current_regime and current_regime != "initializing":
            # 2. Route decision control to correct PPO model
            agent = self.load_ppo_agent(current_regime)
            if agent:
                # 3. Prepare observation for the agent
                # The observation space of the environment is (current_price, position, capital, regime_numeric)
                # For prediction, we need to construct an observation array that matches this.
                # For now, we'll use a simplified observation based on the latest close price and dummy values.
                # In a real scenario, this observation should be carefully constructed from live_data.
                current_price = latest_close
                position = 0 # Assume flat for prediction
                capital = 100000 # Assume some capital
                regime_map = {"uptrend": 0, "downtrend": 1, "rangebound": 2, "high_volatility": 3, "crash": 4, "initializing": 5, "unknown": 6}
                regime_numeric = regime_map.get(current_regime, -1)
                
                obs = np.array([current_price, position, capital, regime_numeric], dtype=np.float32)
                obs = np.expand_dims(obs, axis=0) # Add batch dimension

                # Predict action
                action, _states = agent.predict(obs, deterministic=True)
                print(f"Agent for {current_regime} suggests action: {action[0]}")
                self._save_active_agent_status(current_regime, f"ppo_agent_{current_regime}")
                
                # Dummy values for reward, position, pnl for logging purposes
                # In a real scenario, these would come from the environment or trade execution
                dummy_reward = 0.0
                dummy_position = 0
                dummy_pnl = 0.0
                
                self._log_agent_rotation(
                    timestamp=pd.Timestamp.now().isoformat(),
                    regime=current_regime,
                    model_loaded=f"ppo_agent_{current_regime}",
                    action=action[0].item(), # .item() to get scalar from numpy array
                    reward=dummy_reward,
                    position=dummy_position,
                    pnl=dummy_pnl
                )
                return f"Action_from_{current_regime}_Agent_Action_{action[0]}"
            else:
                print(f"No active agent for regime: {current_regime}")
                return "No_Action_Taken"
        else:
            print("Could not determine current market regime or still initializing.")
            return "No_Action_Taken"

if __name__ == '__main__':
    # Example Usage:
    # Create a dummy rl_config.json if it doesn't exist
    if not os.path.exists('rl_config.json'):
        dummy_rl_config = {
            "regimes": ["uptrend", "downtrend", "rangebound", "high_vol"],
            "model_paths": {
                "uptrend": "models/ppo_agent_uptrend.zip",
                "downtrend": "models/ppo_agent_downtrend.zip",
                "rangebound": "models/ppo_agent_rangebound.zip",
                "high_vol": "models/ppo_agent_high_vol.zip"
            }
        }
        with open('rl_config.json', 'w') as f:
            json.dump(dummy_rl_config, f, indent=4)

    # Create dummy PPO agent files for testing
    if not os.path.exists('models'):
        os.makedirs('models')
    for regime in ["uptrend", "downtrend", "rangebound", "high_vol"]:
        dummy_model_path = os.path.join('models', f"ppo_agent_{regime}.zip")
        if not os.path.exists(dummy_model_path):
            with open(dummy_model_path, 'w') as f:
                f.write(f"This is a dummy PPO model for {regime}")

    router = RegimeRouterExecutor()

    # Simulate live data (replace with actual live data fetching in production)
    # The MarketRegimeLabeler would need actual data to label the regime.
    # For this example, we'll just pass a placeholder.
    print("\nSimulating execution with dummy live data...")
    dummy_live_data = pd.DataFrame({
        'close': [100, 101, 102, 103, 104],
        'volume': [1000, 1100, 1050, 1200, 1150]
    }) # This data needs to be meaningful for MarketRegimeLabeler

    # Note: MarketRegimeLabeler.label_current_regime needs to be implemented to use live_data
    # For now, it will likely return None or a default value if not properly configured.
    # You would need to ensure your MarketRegimeLabeler can process this `live_data` to return a valid regime.
    
    # For demonstration, we'll create a dummy DataFrame with 'high', 'low', 'close'
    # that can be processed by MarketRegimeLabeler. This data is designed to simulate an uptrend.
    dummy_live_data = pd.DataFrame({
        'high': np.linspace(70000, 70000 + 50 * 5, 50),
        'low': np.linspace(69900, 69900 + 50 * 5, 50),
        'close': np.linspace(69950, 69950 + 50 * 5, 50),
        'volume': np.random.rand(50) * 10000
    })

    # Simulate processing live data point by point
    for index, row in dummy_live_data.iterrows():
        # Create a DataFrame with just the current row to pass to execute_strategy
        current_live_data_point = pd.DataFrame([row])
        action = router.execute_strategy(current_live_data_point)
        print(f"Action taken: {action}")
        # Optional: Add a small delay to simulate real-time processing
        # import time
        # time.sleep(0.1)

    # Clean up dummy files (optional)
    # os.remove('rl_config.json')
    # for regime in ["uptrend", "downtrend", "rangebound", "high_vol"]:
    #     os.remove(os.path.join('models', f"ppo_agent_{regime}.zip"))
    # os.rmdir('models')