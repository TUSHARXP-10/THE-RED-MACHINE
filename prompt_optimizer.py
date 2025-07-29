import json
import os
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

class PromptOptimizer:
    def __init__(self, memory_index_path='memory_index.json', score_tracker_path='prompt_score_tracker.json'):
        load_dotenv()
        self.memory_index_path = memory_index_path
        self.score_tracker_path = score_tracker_path
        self.openai_client = self._initialize_openai_client()
        self.memory_index = self._load_json(self.memory_index_path)
        self.score_tracker = self._load_json(self.score_tracker_path)

    def _initialize_openai_client(self):
        api_type = os.getenv("OPENAI_API_TYPE", "openai")
        if api_type == "perplexity":
            return OpenAI(api_key=os.getenv("PERPLEXITY_API_KEY"), base_url="https://api.perplexity.ai")
        else:
            return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _load_json(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}

    def _save_json(self, data, file_path):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def _get_embedding(self, text):
        try:
            model = "text-embedding-ada-002"
            if os.getenv("OPENAI_API_TYPE") == "perplexity":
                model = "llama-2-70b-chat"
            response = self.openai_client.embeddings.create(input=text, model=model)
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None

    def update_prompt_score(self, prompt_hash, metrics, themes=None, regime=None):
        score_data = {"metrics": metrics}
        if themes is not None:
            score_data["themes"] = themes
        if regime is not None:
            score_data["regime"] = regime
        self.score_tracker[prompt_hash] = score_data
        self._save_json(self.score_tracker, self.score_tracker_path)

    def get_top_prompts(self, num_prompts=10, metric='sharpe_ratio', filter_regime=None):
        # This method assumes that prompt_memory.py has already processed and linked metrics
        # We need to retrieve prompts from memory_index and their associated scores from score_tracker
        scored_prompts = []
        for prompt_id, data in self.memory_index.items():
            prompt_hash = data.get('prompt_hash')
            if prompt_hash and prompt_hash in self.score_tracker:
                score_data = self.score_tracker[prompt_hash]
                score = score_data.get('metrics', {}).get(metric)
                regime = score_data.get('regime')

                # Apply regime filter if specified
                if filter_regime and regime != filter_regime:
                    continue

                if score is not None:
                    scored_prompts.append({'prompt': data['prompt_text'], 'score': score, 'prompt_id': prompt_id, 'themes': score_data.get('themes'), 'regime': regime})
        
        # Sort by score in descending order
        scored_prompts.sort(key=lambda x: x['score'], reverse=True)
        return scored_prompts[:num_prompts]

    def suggest_next_generation(self, top_prompts):
        evolved_prompts = []
        for prompt_data in top_prompts:
            prompt_text = prompt_data['prompt']
            score = prompt_data['score']
            
            # Craft a prompt for GPT to evolve the current prompt
            system_message = (
                "You are an expert trading strategy designer. Your goal is to evolve existing successful trading prompts "
                "into new, potentially higher-performing variants. Focus on adjusting indicators, entry/exit logic, "
                "or risk management. The original prompt had a score of {score}."
            ).format(score=score)

            user_message = (
                f"Evolve the following trading strategy prompt into 3 new variants. "
                f"Each variant should explore a slightly different approach (e.g., different indicators, "
                f"timeframes, or entry/exit conditions). The original prompt is: "
                f"\n\n'{prompt_text}'\n\n" 
                f"Provide only the new prompt texts, one per line, without any additional commentary or numbering."
            )

            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",  # Or another suitable model like "gpt-3.5-turbo"
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7, # Adjust for creativity
                    n=1 # We ask for 3 variants in the prompt, GPT will provide them in one response
                )
                
                new_prompts_raw = response.choices[0].message.content.strip()
                new_prompts = [p.strip() for p in new_prompts_raw.split('\n') if p.strip()]
                evolved_prompts.extend(new_prompts)
                
            except Exception as e:
                print(f"Error evolving prompt '{prompt_text}': {e}")
                continue
        
        return evolved_prompts

    def create_prompt_audit_trail(self, original_prompt_id, evolved_prompts):
        audit_dir = 'prompt_evolution'
        os.makedirs(audit_dir, exist_ok=True)
        
        # Load original prompt details
        original_prompt_data = self.memory_index.get(original_prompt_id)
        if not original_prompt_data:
            print(f"Original prompt ID {original_prompt_id} not found in memory index.")
            return

        audit_file_path = os.path.join(audit_dir, f'audit_{original_prompt_id}.json')
        audit_log = {
            'original_prompt_id': original_prompt_id,
            'original_prompt_text': original_prompt_data.get('prompt_text'),
            'original_prompt_hash': original_prompt_data.get('prompt_hash'),
            'evolved_variants': []
        }

        for i, prompt_text in enumerate(evolved_prompts):
            audit_log['evolved_variants'].append({
                'variant_id': f'{original_prompt_id}_v{i+1}',
                'prompt_text': prompt_text,
                'timestamp': pd.Timestamp.now().isoformat() # Requires pandas
            })
        
        self._save_json(audit_log, audit_file_path)
        print(f"Audit trail for prompt {original_prompt_id} saved to {audit_file_path}")

# Example Usage (for testing/demonstration)
if __name__ == "__main__":
    optimizer = PromptOptimizer()

    # Simulate updating scores (this would happen after backtesting)
    # For demonstration, let's assume some prompts exist and have been scored
    # In a real scenario, prompt_memory.py would process logs and link scores
    # For now, manually add some dummy scores to prompt_score_tracker.json
    # Ensure memory_index.json has some entries with 'prompt_hash'

    # Dummy data for demonstration if files are empty
    if not optimizer.memory_index:
        print("memory_index.json is empty. Populating with dummy data.")
        dummy_prompts = [
            {"prompt_id": "p1", "prompt_text": "Buy when RSI is oversold, sell when overbought.", "prompt_hash": "hash1"},
            {"prompt_id": "p2", "prompt_text": "Use MACD crossover for entry, exit on divergence.", "prompt_hash": "hash2"},
            {"prompt_id": "p3", "prompt_text": "Long when 50-day MA crosses above 200-day MA, short otherwise.", "prompt_hash": "hash3"},
        ]
        for p in dummy_prompts:
            optimizer.memory_index[p['prompt_id']] = p
        optimizer._save_json(optimizer.memory_index, optimizer.memory_index_path)

    if not optimizer.score_tracker:
        print("prompt_score_tracker.json is empty. Populating with dummy data.")
        optimizer.update_prompt_score("hash1", {"sharpe_ratio": 1.5, "pnl": 1000}, themes=["mean_reversion"], regime="rangebound")
        optimizer.update_prompt_score("hash2", {"sharpe_ratio": 2.1, "pnl": 1500}, themes=["trend_following"], regime="uptrend")
        optimizer.update_prompt_score("hash3", {"sharpe_ratio": 0.8, "pnl": 500}, themes=["scalping"], regime="high_volatility")

    print("\n--- Top Prompts ---")
    top_prompts = optimizer.get_top_prompts(num_prompts=2)
    for p in top_prompts:
        print(f"Prompt: {p['prompt']}, Score: {p['score']}")

    if top_prompts:
        print("\n--- Suggesting Next Generation ---")
        # We need to pass the full prompt_data including prompt_id for audit trail
        evolved_prompts = optimizer.suggest_next_generation(top_prompts)
        print("Evolved Prompts:")
        for ep in evolved_prompts:
            print(f"- {ep}")
        
        # Create audit trail for the first top prompt
        if evolved_prompts:
            optimizer.create_prompt_audit_trail(top_prompts[0]['prompt_id'], evolved_prompts)

    else:
        print("No top prompts found to evolve.")