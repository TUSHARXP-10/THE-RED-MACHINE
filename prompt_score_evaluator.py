import json
import pandas as pd                                                                                                                                                                                                                
import os
from collections import defaultdict

class PromptScoreEvaluator:
    def __init__(self, base_path='.'):
        self.base_path = base_path
        self.prompt_memory_path = os.path.join(base_path, 'prompt_memory.json')
        self.leaderboard_path = os.path.join(base_path, 'leaderboard.csv')
        self.audit_log_dir = os.path.join(base_path, 'gpt_logs') # Assuming audit logs are here
        self.prompt_score_index_path = os.path.join(base_path, 'prompt_score_index.json')
        self.prompt_to_strategy_map = self._load_prompt_to_strategy_map()

    def _load_json(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}

    def _load_csv(self, filepath):
        if os.path.exists(filepath):
            return pd.read_csv(filepath)
        return pd.DataFrame()

    def _load_prompt_to_strategy_map(self):
        # This function will parse audit logs to create a mapping from prompt_hash to strategy_name
        # This is a placeholder and needs to be refined based on actual audit log structure
        prompt_strategy_map = defaultdict(list)
        for filename in os.listdir(self.audit_log_dir):
            if filename.startswith('audit_') and filename.endswith('.json'):
                filepath = os.path.join(self.audit_log_dir, filename)
                audit_data = self._load_json(filepath)
                # Assuming audit_data has a structure that links prompt_id/hash to strategy generation
                # This part needs to be customized based on the actual audit log format
                # For now, let's assume a simple structure where 'prompt_hash' and 'strategy_name' are present
                if 'prompt_hash' in audit_data and 'strategy_name' in audit_data:
                    prompt_strategy_map[audit_data['prompt_hash']].append(audit_data['strategy_name'])
        return prompt_strategy_map

    def evaluate_prompts(self):
        prompt_memory = self._load_json(self.prompt_memory_path)
        leaderboard = self._load_csv(self.leaderboard_path)

        prompt_scores = {}

        for prompt_hash, prompt_data in prompt_memory.items():
            derived_strategies = self.prompt_to_strategy_map.get(prompt_hash, [])
            
            if not derived_strategies:
                prompt_scores[prompt_hash] = {
                    "total_strategy_count": 0,
                    "avg_net_pnl": 0,
                    "cumulative_net_pnl": 0,
                    "avg_sharpe_ratio": 0,
                    "victory_rate": 0,
                    "strategies": []
                }
                continue

            # Filter leaderboard for strategies derived from this prompt
            relevant_strategies = leaderboard[leaderboard['strategy_name'].isin(derived_strategies)]

            if relevant_strategies.empty:
                prompt_scores[prompt_hash] = {
                    "total_strategy_count": len(derived_strategies),
                    "avg_net_pnl": 0,
                    "cumulative_net_pnl": 0,
                    "avg_sharpe_ratio": 0,
                    "victory_rate": 0,
                    "strategies": derived_strategies
                }
                continue

            # Calculate metrics
            total_strategy_count = len(relevant_strategies)
            avg_net_pnl = relevant_strategies['net_pnl'].mean() if 'net_pnl' in relevant_strategies.columns else 0
            cumulative_net_pnl = relevant_strategies['net_pnl'].sum() if 'net_pnl' in relevant_strategies.columns else 0
            avg_sharpe_ratio = relevant_strategies['sharpe_ratio'].mean() if 'sharpe_ratio' in relevant_strategies.columns else 0
            victory_rate = (relevant_strategies['net_pnl'] > 0).mean() * 100 if 'net_pnl' in relevant_strategies.columns else 0

            prompt_scores[prompt_hash] = {
                "total_strategy_count": total_strategy_count,
                "avg_net_pnl": avg_net_pnl,
                "cumulative_net_pnl": cumulative_net_pnl,
                "avg_sharpe_ratio": avg_sharpe_ratio,
                "victory_rate": victory_rate,
                "strategies": derived_strategies
            }
        
        self._save_prompt_scores(prompt_scores)
        return prompt_scores

    def _save_prompt_scores(self, scores):
        with open(self.prompt_score_index_path, 'w') as f:
            json.dump(scores, f, indent=4)

if __name__ == '__main__':
    evaluator = PromptScoreEvaluator()
    print("Evaluating prompts and generating scores...")
    scores = evaluator.evaluate_prompts()
    print(f"Scores saved to {evaluator.prompt_score_index_path}")
    # print(json.dumps(scores, indent=4)) # For debugging