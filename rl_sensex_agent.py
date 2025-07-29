from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.monitor import Monitor
import numpy as np
import pandas as pd
import os
import json
from sensex_env import SensexTradingEnv
from breeze_connect import BreezeConnect

class TensorboardCallback(BaseCallback):
    """
    Custom callback for plotting additional values in tensorboard.
    """
    def __init__(self, verbose=0):
        super(TensorboardCallback, self).__init__(verbose)
        self.episode_rewards = []
        self.episode_lengths = []

    def _on_step(self) -> bool:
        # Log scalar value to tensorboard
        if 'episode' in self.locals:
            episode = self.locals['episode']
            self.episode_rewards.append(episode.r)
            self.episode_lengths.append(episode.l)
            self.logger.record('rollout/episode_reward', np.mean(self.episode_rewards[-100:]))
            self.logger.record('rollout/episode_length', np.mean(self.episode_lengths[-100:]))
        return True

class RLAgent:
    """
    Reinforcement Learning Agent for SENSEX Options Trading
    """
    def __init__(self, config_path='rl_config.json', regime=None):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize BreezeConnect (mock for now)
        self.breeze = BreezeConnect(api_key=self.config['api_key'])
        
        # Create environment
        self.regime = regime
        self.env = SensexTradingEnv(breeze_connect=self.breeze,
                                  initial_capital=self.config['initial_capital'],
                                  mode=self.config['mode'],
                                  regime=self.regime)
        
        # Wrap environment for monitoring and vectorization
        self.env = Monitor(self.env)
        self.env = DummyVecEnv([lambda: self.env])
        
        # Initialize model
        self.model = PPO('MlpPolicy', self.env,
                        verbose=1,
                        tensorboard_log='./logs/rl_tensorboard/',
                        **self.config['ppo_params'])
        
        # Create logs directory if not exists
        os.makedirs('./logs', exist_ok=True)
        
    def train(self, total_timesteps=10000):
        """
        Train the RL agent
        """
        callback = TensorboardCallback()
        self.model.learn(total_timesteps=total_timesteps,
                        callback=callback,
                        tb_log_name="ppo_sensex")
        
    def save_model(self, path='models/rl_sensex_agent'):
        """
        Save trained model
        """
        os.makedirs('models', exist_ok=True)
        self.model.save(path)
        print(f"Model saved to {path}")
        
    def load_model(self, path='models/rl_sensex_agent'):
        """
        Load trained model
        """
        self.model = PPO.load(path, env=self.env)
        print(f"Model loaded from {path}")
        
    def predict(self, obs=None, deterministic=False):
        """
        Get action prediction from the model
        """
        if obs is None:
            obs = self.env.reset()
        action, _states = self.model.predict(obs, deterministic=deterministic)
        return action
        
    def run_episode(self, render=False):
        """
        Run a single episode with the current model
        """
        obs = self.env.reset()
        done = False
        episode_reward = 0
        
        while not done:
            action = self.predict(obs)
            obs, reward, done, info = self.env.step(action)
            episode_reward += reward
            if render:
                self.env.render()
                
        return episode_reward, info

    def evaluate(self, num_episodes=50):
        """
        Evaluate the trained agent over multiple episodes.
        Logs Reward Mean, Std, and Percent Profitable.
        """
        from stable_baselines3.common.evaluation import evaluate_policy

        mean_reward, std_reward = evaluate_policy(self.model, self.env, n_eval_episodes=num_episodes, return_episode_rewards=True)
        
        episode_rewards = mean_reward # evaluate_policy returns a list of rewards when return_episode_rewards=True
        
        profitable_episodes = sum(1 for r in episode_rewards if r > 0)
        percent_profitable = (profitable_episodes / num_episodes) * 100

        print(f"\n--- Evaluation Results over {num_episodes} episodes ---")
        print(f"Mean Reward: {np.mean(episode_rewards):.2f}")
        print(f"Std Reward: {np.std(episode_rewards):.2f}")
        print(f"Percent Profitable: {percent_profitable:.2f}%")
        print("--------------------------------------------------")

        return np.mean(episode_rewards), np.std(episode_rewards), percent_profitable

# Example Usage
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train RL agent for SENSEX Options Trading.')
    parser.add_argument('--regime', type=str, default=None, help='Market regime for training (e.g., uptrend, rangebound, high_vol, crash).')
    parser.add_argument('--episodes', type=int, default=10000, help='Total timesteps for training.')
    args = parser.parse_args()

    # Create default config if not exists
    if not os.path.exists('rl_config.json'):
        default_config = {
            "api_key": "YOUR_API_KEY",
            "secret_key": "YOUR_SECRET_KEY",
            "session_token": "YOUR_SESSION_TOKEN",
            "initial_capital": 100000,
            "mode": "paper",
            "ppo_params": {
                "learning_rate": 3e-4,
                "n_steps": 2048,
                "batch_size": 64,
                "n_epochs": 10,
                "gamma": 0.99,
                "gae_lambda": 0.95,
                "clip_range": 0.2,
                "ent_coef": 0.0,
                "vf_coef": 0.5,
                "max_grad_norm": 0.5
            }
        }
        with open('rl_config.json', 'w') as f:
            json.dump(default_config, f, indent=4)
    
    # Initialize and train agent
    try:
        agent = RLAgent(regime=args.regime)
        print(f"Starting training for regime: {args.regime if args.regime else 'default'}...")
        agent.train(total_timesteps=args.episodes)
        
        model_path = f'models/ppo_agent_{args.regime}.zip' if args.regime else 'models/rl_sensex_agent.zip'
        agent.save_model(path=model_path)
        
        # Evaluate the trained agent
        agent.evaluate(num_episodes=50)

        # Test the trained agent
        print("Running test episode...")
        reward, info = agent.run_episode(render=True)
        print(f"Test episode reward: {reward:.2f}")
        print(f"Final capital: {info['current_capital']:.2f}")
        print(f"Number of trades: {info['trade_log_len']}")
    except Exception as e:
        import traceback
        print(f"An error occurred during training: {e}")
        traceback.print_exc()