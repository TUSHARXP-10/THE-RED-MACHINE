import json
import pandas as pd

class PromptSeeder:
    def __init__(self, prompt_score_index_path='prompt_score_index.json', prompt_memory_path='prompt_memory.json'):
        self.prompt_score_index_path = prompt_score_index_path
        self.prompt_memory_path = prompt_memory_path
        self.prompt_scores = self._load_json(self.prompt_score_index_path)
        self.prompt_memory = self._load_json(self.prompt_memory_path)

    def _load_json(self, file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {file_path} not found.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {file_path}.")
            return {}

    def get_top_prompts(self, num_prompts=5, sort_by='avg_sharpe', min_strategies=1,
                        include_themes=None, exclude_themes=None, filter_regime=None):
        if not self.prompt_scores:
            print("Prompt scores not loaded or empty.")
            return []

        # Filter out prompts with insufficient strategy count
        filtered_prompts = {hash: data for hash, data in self.prompt_scores.items() if data.get('total_strategy_count', 0) >= min_strategies}

        if not filtered_prompts:
            print("No prompts meet the minimum strategy count criteria.")
            return []

        # Convert to a list of dictionaries for easier sorting
        prompts_list = []
        for prompt_hash, metrics in filtered_prompts.items():
            prompt_data = self.prompt_memory.get(prompt_hash, {})
            prompt_text = prompt_data.get('prompt_text', 'N/A')
            prompt_themes = prompt_data.get('themes', [])
            
            # Retrieve regime from prompt_scores (which comes from prompt_score_index.json)
            prompt_regime = self.prompt_scores.get(prompt_hash, {}).get('regime')

            # Apply filter_regime
            if filter_regime and prompt_regime != filter_regime:
                continue

            # Apply include_themes filter
            if include_themes and not any(theme in prompt_themes for theme in include_themes):
                continue

            # Apply exclude_themes filter
            if exclude_themes and any(theme in prompt_themes for theme in exclude_themes):
                continue

            prompts_list.append({
                'prompt_hash': prompt_hash,
                'prompt_text': prompt_text,
                'avg_sharpe': metrics.get('average_sharpe_ratio', 0),
                'cumulative_pnl': metrics.get('cumulative_net_pnl', 0),
                'victory_rate': metrics.get('victory_rate', 0),
                'total_strategy_count': metrics.get('total_strategy_count', 0),
                'themes': prompt_themes # Add themes to the returned dictionary
            })

        # Sort based on the specified metric
        if sort_by == 'avg_sharpe':
            prompts_list.sort(key=lambda x: x['avg_sharpe'], reverse=True)
        elif sort_by == 'cumulative_pnl':
            prompts_list.sort(key=lambda x: x['cumulative_pnl'], reverse=True)
        elif sort_by == 'victory_rate':
            prompts_list.sort(key=lambda x: x['victory_rate'], reverse=True)
        else:
            print(f"Warning: Unknown sort_by metric '{sort_by}'. Sorting by average Sharpe.")
            prompts_list.sort(key=lambda x: x['avg_sharpe'], reverse=True)

        return prompts_list[:num_prompts]

    def format_seed_context(self, top_prompts):
        if not top_prompts:
            return ""

        context = "Here are examples of high-performing prompts:\n\n"
        for i, prompt in enumerate(top_prompts):
            context += f"- Prompt {i+1} (Hash: {prompt['prompt_hash']}): {prompt['prompt_text']}\n"
            context += f"  Themes: {', '.join(prompt['themes'])}\n" # Include themes in the context
        context += "\nApply a similar tone and structure."
        return context

if __name__ == '__main__':
    seeder = PromptSeeder()
    
    print("\n--- Testing with no filters ---")
    top_prompts_no_filter = seeder.get_top_prompts(num_prompts=3, sort_by='avg_sharpe')
    if top_prompts_no_filter:
        print("Top Prompts (no filter):")
        for prompt in top_prompts_no_filter:
            print(f"  Hash: {prompt['prompt_hash']}, Sharpe: {prompt['avg_sharpe']:.2f}, PnL: {prompt['cumulative_pnl']:.2f}, Victory Rate: {prompt['victory_rate']:.2f}, Themes: {prompt['themes']}")
        seed_context_no_filter = seeder.format_seed_context(top_prompts_no_filter)
        print("\nFormatted Seed Context (no filter):\n", seed_context_no_filter)
    else:
        print("No top prompts found (no filter).")

    print("\n--- Testing with include_themes (sensex) ---")
    top_prompts_sensex = seeder.get_top_prompts(num_prompts=3, sort_by='avg_sharpe', include_themes=['sensex'])
    if top_prompts_sensex:
        print("Top Prompts (sensex only):")
        for prompt in top_prompts_sensex:
            print(f"  Hash: {prompt['prompt_hash']}, Sharpe: {prompt['avg_sharpe']:.2f}, PnL: {prompt['cumulative_pnl']:.2f}, Victory Rate: {prompt['victory_rate']:.2f}, Themes: {prompt['themes']}")
        seed_context_sensex = seeder.format_seed_context(top_prompts_sensex)
        print("\nFormatted Seed Context (sensex only):\n", seed_context_sensex)
    else:
        print("No top prompts found (sensex only).")

    print("\n--- Testing with exclude_themes (nifty) ---")
    top_prompts_no_nifty = seeder.get_top_prompts(num_prompts=3, sort_by='avg_sharpe', exclude_themes=['nifty'])
    if top_prompts_no_nifty:
        print("Top Prompts (excluding nifty):")
        for prompt in top_prompts_no_nifty:
            print(f"  Hash: {prompt['prompt_hash']}, Sharpe: {prompt['avg_sharpe']:.2f}, PnL: {prompt['cumulative_pnl']:.2f}, Victory Rate: {prompt['victory_rate']:.2f}, Themes: {prompt['themes']}")
        seed_context_no_nifty = seeder.format_seed_context(top_prompts_no_nifty)
        print("\nFormatted Seed Context (excluding nifty):\n", seed_context_no_nifty)
    else:
        print("No top prompts found (excluding nifty).")

    print("\n--- Testing with filter_regime (uptrend) ---")
    top_prompts_uptrend = seeder.get_top_prompts(num_prompts=3, sort_by='avg_sharpe', filter_regime='uptrend')
    if top_prompts_uptrend:
        print("Top Prompts (uptrend only):")
        for prompt in top_prompts_uptrend:
            print(f"  Hash: {prompt['prompt_hash']}, Sharpe: {prompt['avg_sharpe']:.2f}, PnL: {prompt['cumulative_pnl']:.2f}, Victory Rate: {prompt['victory_rate']:.2f}, Themes: {prompt['themes']}, Regime: {prompt.get('regime', 'N/A')}")
        seed_context_uptrend = seeder.format_seed_context(top_prompts_uptrend)
        print("\nFormatted Seed Context (uptrend only):\n", seed_context_uptrend)
    else:
        print("No top prompts found (uptrend only).")