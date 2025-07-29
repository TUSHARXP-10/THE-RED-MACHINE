import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
from breeze_connect import BreezeConnect
import json
import time
from market_regime_labeler import MarketRegimeLabeler # Import for regime-aware logic

class SensexTradingEnv(gym.Env):
    """Custom Gym Environment for SENSEX Options Trading."""
    metadata = {'render_modes': ['human'], 'render_fps': 30}

    def __init__(self, breeze_connect: BreezeConnect, initial_capital=100000, mode='paper', regime=None):
        super(SensexTradingEnv, self).__init__()

        self.regime = regime # Store the regime for regime-aware logic
        self.market_regime_labeler = MarketRegimeLabeler() # Initialize regime labeler

        # Placeholder for regime-specific data or logic
        if self.regime:
            print(f"Environment initialized for regime: {self.regime}")
            # TODO: Load regime-specific data or adjust environment parameters
            # based on the specified regime.
            # This might involve loading different historical data subsets,
            # adjusting reward functions, or modifying observation space.

        self.breeze = breeze_connect
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.mode = mode # 'paper' or 'live'
        self.position = 0 # -1 for short, 0 for flat, 1 for long
        self.avg_entry_price = 0
        self.trade_log = []

        # Define action space: Buy, Sell, Hold (for simplicity, discrete actions)
        # More complex actions (e.g., specific strike, quantity) can be added later
        self.action_space = spaces.Discrete(3) # 0: Hold, 1: Buy, 2: Sell

        # Define observation space: Example - current price, position, capital
        # This needs to be expanded significantly with real market data (OHLC, Greeks, IV, etc.)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(4,), dtype=np.float32) # Added space for regime

    def _get_obs(self):
        # This is a placeholder. Real observation should come from BreezeConnect
        # and include relevant market data, Greeks, IV, etc.
        current_prices = self._get_current_sensex_price() # Mock function, now returns dict
        current_price = current_prices['close']
        current_regime = self.market_regime_labeler.label_current_regime(current_prices['high'], current_prices['low'], current_prices['close'])
        # Map regime string to a numerical value for observation space
        regime_map = {"uptrend": 0, "downtrend": 1, "rangebound": 2, "high_volatility": 3, "crash": 4, "initializing": 5, "unknown": 6}
        regime_numeric = regime_map.get(current_regime, -1) # -1 for unmapped/error

        return np.array([current_price, self.position, self.current_capital, regime_numeric], dtype=np.float32)

    def _get_info(self):
        current_prices = self._get_current_sensex_price()
        current_regime = self.market_regime_labeler.label_current_regime(current_prices['high'], current_prices['low'], current_prices['close'])
        return {
            "current_capital": self.current_capital,
            "position": self.position,
            "avg_entry_price": self.avg_entry_price,
            "trade_log_len": len(self.trade_log),
            "current_regime": current_regime
        }
        super(SensexTradingEnv, self).__init__()

        self.breeze = breeze_connect
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.mode = mode # 'paper' or 'live'
        self.position = 0 # -1 for short, 0 for flat, 1 for long
        self.avg_entry_price = 0
        self.trade_log = []

        # Define action space: Buy, Sell, Hold (for simplicity, discrete actions)
        # More complex actions (e.g., specific strike, quantity) can be added later
        self.action_space = spaces.Discrete(3) # 0: Hold, 1: Buy, 2: Sell

        # Define observation space: Example - current price, position, capital
        # This needs to be expanded significantly with real market data (OHLC, Greeks, IV, etc.)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(3,), dtype=np.float32)



    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_capital = self.initial_capital
        self.position = 0
        self.avg_entry_price = 0
        self.trade_log = []

        observation = self._get_obs()
        info = self._get_info()
        return observation, info

    def step(self, action):
        current_prices = self._get_current_sensex_price() # Get current prices for action execution
        current_price = current_prices['close']
        reward = 0
        terminated = False
        truncated = False

        if action == 1: # Buy
            if self.position == 0: # Only buy if flat
                self.position = 1
                self.avg_entry_price = current_price
                print(f"Bought at {current_price}")
            # else: penalize for trying to buy when already in position or short
        elif action == 2: # Sell
            if self.position == 1: # Only sell if long
                pnl = (current_price - self.avg_entry_price) * 100 # Assuming 100 units per trade
                self.current_capital += pnl
                reward = pnl # Reward is PnL
                self.trade_log.append({'entry': self.avg_entry_price, 'exit': current_price, 'pnl': pnl})
                self.position = 0
                self.avg_entry_price = 0
                print(f"Sold at {current_price}, PnL: {pnl}")
            # else: penalize for trying to sell when flat or short
        # Action 0: Hold - no change in position, no immediate reward/penalty

        # Example termination condition: capital depletion or episode end
        # Example termination condition: capital depletion or episode end
        if self.current_capital <= self.initial_capital * 0.5:
            terminated = True
            reward -= 1000 # Large penalty for significant drawdown

        # Regime-aware reward shaping (placeholder)
        # You can add more sophisticated reward shaping here based on self.regime
        # For example, penalize long-holds in downtrend, reward volatility plays in high_volatility
        # if self.regime == 'downtrend' and self.position == 1: # Example: penalize long in downtrend
        #     reward -= 50
        # elif self.regime == 'uptrend' and self.position == 1: # Example: reward long in uptrend
        #     reward += 50

        observation = self._get_obs()
        info = self._get_info()

        return observation, reward, terminated, truncated, info

    def render(self):
        print(f"Capital: {self.current_capital:.2f}, Position: {self.position}, Price: {self._get_current_sensex_price():.2f}")

    def close(self):
        pass # Clean up resources if any

    def _get_current_sensex_price(self):
        # Mock function to simulate SENSEX price movement
        # In a real scenario, this would fetch live data from BreezeConnect
        # For now, return a dictionary with high, low, close
        close_price = np.random.uniform(70000, 75000)
        high_price = close_price + np.random.uniform(0, 100)
        low_price = close_price - np.random.uniform(0, 100)
        return {'high': high_price, 'low': low_price, 'close': close_price}

# Example Usage (for testing purposes)
if __name__ == '__main__':
    # Mock BreezeConnect for testing the environment
    class MockBreezeConnect:
        def __init__(self, api_key, secret_key, session_token):
            self.api_key = api_key
            self.secret_key = secret_key
            self.session_token = session_token

        def get_quotes(self, stock_code, exchange_code, product_type, expiry_date, right, strike_price):
            # Simulate fetching quotes
            print(f"Mock Breeze: Getting quotes for {stock_code}")
            return {"Success": True, "last_price": np.random.uniform(100, 500)}

    # Replace with your actual BreezeConnect credentials
    mock_breeze = MockBreezeConnect("YOUR_API_KEY", "YOUR_SECRET_KEY", "YOUR_SESSION_TOKEN")

    env = SensexTradingEnv(mock_breeze)

    obs, info = env.reset()
    print("Initial Observation:", obs, "Info:", info)

    for _ in range(10):
        action = env.action_space.sample() # Take a random action
        obs, reward, terminated, truncated, info = env.step(action)
        env.render()
        print(f"Action: {action}, Reward: {reward:.2f}, Terminated: {terminated}, Capital: {info['current_capital']:.2f}")
        if terminated or truncated:
            break

    print("Episode finished.")
    print("Total Trades:", len(env.trade_log))
    if env.trade_log:
        total_pnl = sum([t['pnl'] for t in env.trade_log])
        print(f"Total PnL: {total_pnl:.2f}")
    env.close()