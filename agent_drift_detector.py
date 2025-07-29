# agent_drift_detector.py

import pandas as pd
import numpy as np
import os
import subprocess
import datetime

class AgentDriftDetector:
    def __init__(self, log_path='logs/agent_rotation_log.csv', retrain_log_path='logs/retrain_log.csv', drift_threshold=0.75, rolling_window=7):
        self.log_path = log_path
        self.retrain_log_path = retrain_log_path
        self.drift_threshold = drift_threshold
        self.rolling_window = rolling_window

    def load_logs(self):
        if not os.path.exists(self.log_path):
            print(f"Error: Log file not found at {self.log_path}")
            return pd.DataFrame()
        df = pd.read_csv(self.log_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

    def analyze_drift(self, df):
        if df.empty:
            return {}

        drift_agents = {}
        agents = df['agent_name'].unique()

        for agent in agents:
            agent_df = df[df['agent_name'] == agent].sort_values(by='timestamp')
            if len(agent_df) < self.rolling_window:
                continue

            historical_mean_reward = agent_df['reward'].mean()
            
            # Calculate rolling average for the last N episodes
            # Assuming 'reward' is the column to monitor for performance
            # And each row represents an episode or a performance metric for a period
            # For simplicity, let's take the last 'rolling_window' entries as 'last N episodes'
            rolling_avg_reward = agent_df['reward'].tail(self.rolling_window).mean()

            if historical_mean_reward == 0:
                # Avoid division by zero, consider it drift if rolling_avg is also 0
                if rolling_avg_reward == 0:
                    continue # No change, no drift
                else:
                    # If historical mean is 0 but rolling avg is not, it's an improvement, not drift
                    pass
            elif rolling_avg_reward < self.drift_threshold * historical_mean_reward:
                drift_agents[agent] = {
                    'rolling_avg_reward': rolling_avg_reward,
                    'historical_mean_reward': historical_mean_reward,
                    'drift_percentage': (1 - (rolling_avg_reward / historical_mean_reward)) * 100
                }
        return drift_agents

    def trigger_retrain(self, agent_name, regime):
        print(f"🚨 Detected Drift in {agent_name}:")
        print(f"→ REMEDIAL ACTION: Retrain Triggered via rl_sensex_agent.py --regime={regime}")
        
        # Map agent_name to regime for retraining
        # This mapping should ideally be more robust, perhaps from a config file
        # For now, assuming agent_name directly implies regime (e.g., ppo_agent_rangebound -> rangebound)
        
        # Extract regime from agent_name
        # Example: ppo_agent_uptrend -> uptrend
        # This assumes a consistent naming convention
        regime_from_agent_name = agent_name.replace('ppo_agent_', '')

        try:
            # Construct the command to run rl_sensex_agent.py
            command = [
                'python',
                'rl_sensex_agent.py',
                '--regime',
                regime_from_agent_name,
                '--episodes', # Assuming a default number of episodes for retraining
                '100' # You might want to make this configurable
            ]
            
            # Execute the command in a non-blocking way
            # subprocess.Popen is suitable for this
            subprocess.Popen(command, cwd=os.getcwd())
            print(f"Retraining command issued for {agent_name} in regime {regime_from_agent_name}.")
            self.log_retrain_event(agent_name, regime_from_agent_name, 'triggered')
        except Exception as e:
            print(f"Error triggering retrain for {agent_name}: {e}")
            self.log_retrain_event(agent_name, regime_from_agent_name, 'failed', str(e))

    def log_retrain_event(self, agent_name, regime, status, error_message=""):
        timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'agent_name': agent_name,
            'regime': regime,
            'status': status,
            'error_message': error_message
        }
        
        log_df = pd.DataFrame([log_entry])
        
        if not os.path.exists(self.retrain_log_path):
            log_df.to_csv(self.retrain_log_path, index=False)
        else:
            log_df.to_csv(self.retrain_log_path, mode='a', header=False, index=False)
        print(f"Logged retrain event for {agent_name}: {status}")

    def run(self):
        df = self.load_logs()
        if df.empty:
            print("No agent rotation logs to analyze.")
            return

        drift_agents = self.analyze_drift(df)

        if drift_agents:
            print("\n--- Drift Detected! ---")
            for agent, data in drift_agents.items():
                print(f"Agent: {agent}")
                print(f"  Rolling Avg Reward (last {self.rolling_window} episodes): {data['rolling_avg_reward']:.2f}")
                print(f"  Historical Mean Reward: {data['historical_mean_reward']:.2f}")
                print(f"  Drift: {data['drift_percentage']:.2f}%")
                
                # Assuming regime can be inferred from agent name for now
                # A more robust solution would involve a mapping or a dedicated column in the log
                regime = agent.replace('ppo_agent_', '') # Simple inference
                self.trigger_retrain(agent, regime)
            print("-----------------------")
        else:
            print("No significant agent drift detected.")

if __name__ == '__main__':
    detector = AgentDriftDetector()
    detector.run()