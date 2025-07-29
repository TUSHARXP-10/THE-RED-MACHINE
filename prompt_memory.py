import os
import json
import logging
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

class PromptMemory:
    def __init__(self, gpt_logs_dir='gpt_logs/', memory_index_path='memory_index.json',
                 leaderboard_path='leaderboard.csv'):
        self.gpt_logs_dir = gpt_logs_dir
        self.memory_index_path = memory_index_path
        self.leaderboard_path = leaderboard_path
        self.client = self._initialize_openai_client()
        self.memory_index = self._load_memory_index()

    def _initialize_openai_client(self):
        PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        USE_PERPLEXITY = os.getenv("USE_PERPLEXITY", "True").lower() == "true"

        if USE_PERPLEXITY and PERPLEXITY_API_KEY:
            return OpenAI(
                api_key=PERPLEXITY_API_KEY,
                base_url="https://api.perplexity.ai"
            )
        elif OPENAI_API_KEY:
            return OpenAI(
                api_key=OPENAI_API_KEY
            )
        else:
            raise ValueError("No API key found for OpenAI or Perplexity. Please set OPENAI_API_KEY or PERPLEXITY_API_KEY in your .env file.")

    def _load_memory_index(self):
        if os.path.exists(self.memory_index_path):
            with open(self.memory_index_path, 'r') as f:
                return json.load(f)
        return {}

    def _save_memory_index(self):
        with open(self.memory_index_path, 'w') as f:
            json.dump(self.memory_index, f, indent=2)

    def _get_embedding(self, text):
        try:
            # Using a common embedding model, adjust as needed
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        except Exception as e:
            logging.error(f"Error getting embedding: {e}")
            return None

    def _get_strategy_metrics(self, strategy_name):
        # This is a placeholder. In a real scenario, you'd parse leaderboard.csv
        # or a more detailed backtest results file to get metrics for a specific strategy.
        # For now, we'll return dummy data or look for a simple match.
        # A more robust solution would involve linking the prompt log to the refined strategy YAML
        # and then to its backtest results.
        return {"sharpe_ratio": 0.0, "pnl": 0.0, "win_rate": 0.0}

    def process_gpt_logs(self):
        logging.info("Processing GPT logs for memory indexing...")
        for filename in os.listdir(self.gpt_logs_dir):
            if filename.startswith('log_') and filename.endswith('.txt'):
                log_filepath = os.path.join(self.gpt_logs_dir, filename)
                log_id = os.path.splitext(filename)[0] # e.g., log_20231027_123456

                if log_id in self.memory_index:
                    logging.info(f"Log {log_id} already processed. Skipping.")
                    continue

                with open(log_filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract prompt and completion
                prompt_match = content.split("\n\nCompletion:\n", 1)
                if len(prompt_match) == 2:
                    prompt = prompt_match[0].replace("Prompt:\n", "").strip()
                    completion = prompt_match[1].strip()
                else:
                    logging.warning(f"Could not parse prompt/completion from {filename}. Skipping.")
                    continue

                prompt_embedding = self._get_embedding(prompt)
                completion_embedding = self._get_embedding(completion)

                if prompt_embedding and completion_embedding:
                    # Attempt to link to strategy metrics. This is the most challenging part
                    # as there's no direct link from gpt_log to a specific strategy name/metrics.
                    # A robust solution would require adding a unique ID to the GPT output
                    # that persists through refinement and backtesting.
                    # For now, we'll use a dummy strategy name or try to infer from completion.
                    strategy_name = f"strategy_{log_id}" # Placeholder
                    metrics = self._get_strategy_metrics(strategy_name)

                    self.memory_index[log_id] = {
                        "timestamp": datetime.now().isoformat(),
                        "prompt": prompt,
                        "completion": completion,
                        "prompt_embedding": prompt_embedding,
                        "completion_embedding": completion_embedding,
                        "associated_metrics": metrics # Link to performance metrics
                    }
                    logging.info(f"Indexed log {log_id}.")
                else:
                    logging.error(f"Failed to generate embeddings for {filename}. Skipping.")

        self._save_memory_index()
        logging.info("Finished processing GPT logs.")

if __name__ == '__main__':
    memory = PromptMemory()
    memory.process_gpt_logs()