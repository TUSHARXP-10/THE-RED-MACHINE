import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Dict, Any, List
from datetime import datetime
from prompt_seeder import PromptSeeder

load_dotenv()

# Default to Perplexity API
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

USE_PERPLEXITY = os.getenv("USE_PERPLEXITY", "True").lower() == "true"

if USE_PERPLEXITY and PERPLEXITY_API_KEY:
    client = OpenAI(
        api_key=PERPLEXITY_API_KEY,
        base_url="https://api.perplexity.ai"
    )
elif OPENAI_API_KEY:
    client = OpenAI(
        api_key=OPENAI_API_KEY
    )
else:
    raise ValueError("No API key found for OpenAI or Perplexity. Please set OPENAI_API_KEY or PERPLEXITY_API_KEY in your .env file.")

import argparse

class GPTStrategySuggestor:
    def __init__(self, prompt_seeder: PromptSeeder = None):
        self.prompt_seeder = prompt_seeder
        self.top_prompts_context = ""
        if self.prompt_seeder:
            top_prompts = self.prompt_seeder.get_top_prompts(num_prompts=5, sort_by='avg_sharpe')
            self.top_prompts_context = self.prompt_seeder.format_seed_context(top_prompts)


    def _log_interaction(self, prompt: str, completion: str):
        log_dir = "gpt_logs"
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_path = os.path.join(log_dir, f"log_{timestamp}.txt")
        with open(log_file_path, "w", encoding="utf-8") as f:
            f.write(f"Prompt:\n{prompt}\n\nCompletion:\n{completion}\n")

    def generate_strategy_suggestion(self, prompt: str, model: str = "sonar", max_tokens: int = 500, temperature: float = 0.7,
                                     num_seed_prompts: int = 5, seed_sort_by: str = 'avg_sharpe',
                                     min_seed_strategies: int = 1, include_themes: List[str] = None,
                                     exclude_themes: List[str] = None, filter_regime: str = None) -> Dict[str, Any]:
        system_prompt = "You are a trading strategy advisor. "

        if self.prompt_seeder:
            top_prompts = self.prompt_seeder.get_top_prompts(
                num_prompts=num_seed_prompts,
                sort_by=seed_sort_by,
                min_strategies=min_seed_strategies,
                include_themes=include_themes,
                exclude_themes=exclude_themes,
                filter_regime=filter_regime
            )
            if top_prompts:
                seed_context = self.prompt_seeder.format_seed_context(top_prompts)
                system_prompt = seed_context + "\n\n" + system_prompt

        messages = [
            {"role": "system", "content": system_prompt, "name": "system"},
            {"role": "user", "content": prompt, "name": "user"}
        ]

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            suggestion_text = response.choices[0].message.content
            self._log_interaction(prompt, suggestion_text) # Log the interaction
            parsed_suggestion = self._parse_suggestion(suggestion_text)
            return {"raw_suggestion": suggestion_text, "parsed_suggestion": parsed_suggestion}
        except Exception as e:
            print(f"Error generating strategy suggestion: {e}")
            return {"raw_suggestion": None, "parsed_suggestion": None}

    def _parse_suggestion(self, suggestion_text: str) -> Dict[str, str]:
        """
        Parses the generated strategy text into a dictionary.
        """
        parsed_strategy = {}
        lines = suggestion_text.split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                parsed_strategy[key.strip()] = value.strip()
        return parsed_strategy

# Example Usage:
if __name__ == "__main__":
    # Initialize PromptSeeder
    prompt_seeder = PromptSeeder()
    suggestor = GPTStrategySuggestor(prompt_seeder=prompt_seeder)

    print("\n--- Generating Strategy Suggestion (No Theme Filter) ---")
    prompt_no_filter = "Propose a simple intraday options scalping strategy using RSI and MACD for Nifty options."
    suggestion_no_filter = suggestor.generate_strategy_suggestion(prompt_no_filter)
    print("Raw Suggestion (No Filter):", suggestion_no_filter["raw_suggestion"])
    print("Parsed Suggestion (No Filter):", suggestion_no_filter["parsed_suggestion"])

    print("\n--- Generating Strategy Suggestion (Include 'sensex' theme) ---")
    prompt_sensex = "Propose a bullish strategy for SENSEX options, focusing on trend following."
    suggestion_sensex = suggestor.generate_strategy_suggestion(prompt_sensex, include_themes=['sensex'])
    print("Raw Suggestion (Sensex Theme):", suggestion_sensex["raw_suggestion"])
    print("Parsed Suggestion (Sensex Theme):", suggestion_sensex["parsed_suggestion"])

    print("\n--- Generating Strategy Suggestion (Exclude 'nifty' theme) ---")
    prompt_no_nifty = "Propose a mean-reversion strategy for Indian equities, but not Nifty."
    suggestion_no_nifty = suggestor.generate_strategy_suggestion(prompt_no_nifty, exclude_themes=['nifty'])
    print("Raw Suggestion (Exclude Nifty):", suggestion_no_nifty["raw_suggestion"])
    print("Parsed Suggestion (Exclude Nifty):", suggestion_no_nifty["parsed_suggestion"])

    print("\n--- Generating Strategy Suggestion (Filter by 'uptrend' regime) ---")
    prompt_uptrend = "Propose a strategy suitable for an uptrending market in Nifty."
    suggestion_uptrend = suggestor.generate_strategy_suggestion(prompt_uptrend, filter_regime='uptrend')
    print("Raw Suggestion (Uptrend Regime):", suggestion_uptrend["raw_suggestion"])
    print("Parsed Suggestion (Uptrend Regime):", suggestion_uptrend["parsed_suggestion"])