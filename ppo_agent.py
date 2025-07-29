import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import EvalCallback, StopTrainingOnRewardThreshold
import pandas as pd
import numpy as np

# Assuming SensexOptionsEnv is in sensex_options_env.py
from sensex_options_env import SensexOptionsEnv

class PPOAgent:
    def __init__(self, env_df: pd.DataFrame, log_dir: str = "./ppo_logs"):
        self.env_df = env_df
        self.log_dir = log_dir
        self.model = None
        self.env = None

    def create_env(self):
        # Create a vectorized environment
        # Lambda function needed to pass df to the environment constructor
        self.env = make_vec_env(lambda: SensexOptionsEnv(self.env_df), n_envs=1)

    def train_agent(self, total_timesteps: int = 100000, eval_freq: int = 10000, n_eval_episodes: int = 10):
        if self.env is None:
            self.create_env()

        # Define callbacks for evaluation and early stopping
        stop_callback = StopTrainingOnRewardThreshold(reward_threshold=1000, verbose=1)
        eval_callback = EvalCallback(self.env, 
                                     best_model_save_path=f"{self.log_dir}/best_model", 
                                     log_path=self.log_dir, 
                                     eval_freq=eval_freq, 
                                     n_eval_episodes=n_eval_episodes,
                                     callback_on_new_best=stop_callback,
                                     verbose=1)

        self.model = PPO("MlpPolicy", self.env, verbose=1, tensorboard_log=self.log_dir)
        self.model.learn(total_timesteps=total_timesteps, callback=eval_callback)
        print("Training finished.")

    def save_agent(self, path: str = "ppo_sensex_agent"):
        if self.model:
            self.model.save(path)
            print(f"Agent saved to {path}.zip")
        else:
            print("No model to save. Train the agent first.")

    def load_agent(self, path: str = "ppo_sensex_agent"):
        self.model = PPO.load(path, env=self.env)
        print(f"Agent loaded from {path}.zip")

    def evaluate_agent(self, n_episodes: int = 10):
        if self.model is None:
            print("No model loaded or trained. Please train or load an agent first.")
            return

        if self.env is None:
            self.create_env()

        print(f"Evaluating agent for {n_episodes} episodes...")
        episode_rewards = []
        for i in range(n_episodes):
            obs, _ = self.env.reset()
            done = False
            total_reward = 0
            while not done:
                action, _states = self.model.predict(obs, deterministic=True)
                obs, reward, done, info = self.env.step(action)
                total_reward += reward[0] # Assuming single environment
            episode_rewards.append(total_reward)
            print(f"Episode {i+1}: Total Reward = {total_reward:.2f}")
        
        print(f"\nAverage reward over {n_episodes} episodes: {np.mean(episode_rewards):.2f}")
        print(f"Standard deviation of rewards: {np.std(episode_rewards):.2f}")

# Example Usage:
if __name__ == "__main__":
    # Create dummy data for testing the environment and agent
    data = {
        'timestamp': pd.date_range(start='2023-01-01', periods=1000),
        'price': np.random.normal(100, 5, 1000).cumsum(),
        'iv': np.random.uniform(0.1, 0.5, 1000),
        'delta': np.random.uniform(-1, 1, 1000),
        'gamma': np.random.uniform(0, 0.1, 1000),
        'theta': np.random.uniform(-0.1, 0, 1000),
        'vega': np.random.uniform(0, 0.1, 1000),
        'volume': np.random.randint(100, 1000, 1000),
        'oi': np.random.randint(1000, 10000, 1000)
    }
    dummy_df = pd.DataFrame(data)

    agent = PPOAgent(env_df=dummy_df)
    agent.create_env()
    agent.train_agent(total_timesteps=10000, eval_freq=1000, n_eval_episodes=5)
    agent.save_agent()
    # agent.load_agent()
    agent.evaluate_agent(n_episodes=3)

    # Close the environment after use
    if agent.env:
        agent.env.close()