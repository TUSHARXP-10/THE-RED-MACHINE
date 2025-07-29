import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any

class SensexOptionsEnv(gym.Env):
    """
    Custom OpenAI Gym environment for SENSEX options trading.
    
    State Space: Current option metrics, Greeks, market indicators
    Action Space: Buy/Sell/Hold decisions with position sizing
    Reward Function: Risk-adjusted returns with protective stop strategies
    """
    
    metadata = {'render.modes': ['human']}
    
    def __init__(self, df: pd.DataFrame):
        super(SensexOptionsEnv, self).__init__()
        
        self.df = df
        self.current_step = 0
        
        # Define action space: [action_type, position_size]
        # action_type: -1 (sell), 0 (hold), 1 (buy)
        # position_size: normalized between 0 and 1
        self.action_space = spaces.Box(
            low=np.array([-1, 0]), 
            high=np.array([1, 1]), 
            dtype=np.float32
        )
        
        # Define observation space (state)
        # Using all columns except 'timestamp' as features
        self.observation_space = spaces.Box(
            low=-np.inf, 
            high=np.inf, 
            shape=(len(df.columns) - 1,), 
            dtype=np.float32
        )
        
        # Initialize state
        self.state = None
        self.position = 0  # Current position (-1 to 1)
        self.cash = 100000  # Starting cash
        self.portfolio_value = self.cash
        self.max_drawdown = 0
        
    def _get_state(self) -> np.ndarray:
        """Get current state from dataframe."""
        # Exclude timestamp column if present
        if 'timestamp' in self.df.columns:
            return self.df.iloc[self.current_step, 1:].values
        return self.df.iloc[self.current_step].values
    
    def reset(self, **kwargs) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Reset the environment to initial state."""
        self.current_step = 0
        self.position = 0
        self.cash = 100000
        self.portfolio_value = self.cash
        self.max_drawdown = 0
        
        self.state = self._get_state()
        return self.state, {}
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """
        Execute one step in the environment.
        
        Args:
            action: Array containing [action_type, position_size]
        
        Returns:
            observation: Next state
            reward: Calculated reward
            terminated: Whether episode is terminated
            truncated: Whether episode is truncated
            info: Additional information
        """
        # Check if episode is done
        if self.current_step >= len(self.df) - 1:
            terminated = True
            truncated = False
            return self.state, 0, terminated, truncated, {}
        
        # Get current price (assuming 'price' column exists)
        current_price = self.df.iloc[self.current_step]['price']
        next_price = self.df.iloc[self.current_step + 1]['price']
        
        # Extract action components
        action_type, position_size = action
        
        # Calculate target position (-1 to 1)
        target_position = action_type * position_size
        
        # Execute trade (simplified - no transaction costs)
        position_change = target_position - self.position
        
        # Update cash based on position change
        self.cash -= position_change * current_price
        
        # Update position
        self.position = target_position
        
        # Calculate new portfolio value
        prev_portfolio_value = self.portfolio_value
        self.portfolio_value = self.cash + self.position * next_price
        
        # Calculate return
        daily_return = (self.portfolio_value - prev_portfolio_value) / prev_portfolio_value
        
        # Update max drawdown
        self.max_drawdown = min(self.max_drawdown, daily_return)
        
        # Calculate reward (risk-adjusted return)
        # Penalize large drawdowns and volatility
        reward = daily_return - 0.5 * abs(daily_return) - 2 * abs(self.max_drawdown)
        
        # Move to next step
        self.current_step += 1
        self.state = self._get_state()
        
        # Check termination conditions
        terminated = False
        truncated = False
        
        # Terminate if portfolio value drops below 20% of initial
        if self.portfolio_value < 20000:
            terminated = True
            reward = -10  # Large penalty for blowing up account
        
        # Terminate if we reach the end of data
        if self.current_step >= len(self.df) - 1:
            terminated = True
        
        info = {
            'portfolio_value': self.portfolio_value,
            'position': self.position,
            'cash': self.cash,
            'daily_return': daily_return,
            'max_drawdown': self.max_drawdown
        }
        
        return self.state, reward, terminated, truncated, info
    
    def render(self, mode='human'):
        """Render the current state of the environment."""
        if mode == 'human':
            print(f"Step: {self.current_step}")
            print(f"Portfolio Value: {self.portfolio_value:.2f}")
            print(f"Position: {self.position:.2f}")
            print(f"Cash: {self.cash:.2f}")
            print(f"Current State: {self.state}")
            print("-" * 40)
        
    def close(self):
        """Clean up any resources."""
        pass

# Example usage
if __name__ == "__main__":
    # Create dummy data for testing
    data = {
        'timestamp': pd.date_range(start='2023-01-01', periods=100),
        'price': np.random.normal(100, 5, 100).cumsum(),
        'iv': np.random.uniform(0.1, 0.5, 100),
        'delta': np.random.uniform(-1, 1, 100),
        'gamma': np.random.uniform(0, 0.1, 100),
        'theta': np.random.uniform(-0.1, 0, 100),
        'vega': np.random.uniform(0, 0.1, 100),
        'volume': np.random.randint(100, 1000, 100),
        'oi': np.random.randint(1000, 10000, 100)
    }
    df = pd.DataFrame(data)
    
    # Create and test the environment
    env = SensexOptionsEnv(df)
    observation, _ = env.reset()
    
    for _ in range(10):  # Run for 10 steps
        action = env.action_space.sample()  # Random action
        observation, reward, terminated, truncated, info = env.step(action)
        env.render()
        
        if terminated or truncated:
            observation, _ = env.reset()