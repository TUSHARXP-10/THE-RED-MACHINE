import json
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity
import logging
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

class PromptRetriever:
    def __init__(self, memory_index_path='memory_index.json'):
        self.memory_index_path = memory_index_path
        self.memory_index = self._load_memory_index()
        self.client = self._initialize_openai_client()

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
        logging.warning(f"Memory index file not found at {self.memory_index_path}")
        return {}

    def _get_embedding(self, text):
        try:
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        except Exception as e:
            logging.error(f"Error getting embedding: {e}")
            return None

    def retrieve_by_similarity(self, query_text, top_k=5):
        logging.info(f"Retrieving prompts similar to: {query_text}")
        try:
            query_embedding = self._get_embedding(query_text)
        except NotImplementedError as e:
            logging.error(e)
            return []

        if not query_embedding:
            return []

        similarities = []
        for log_id, data in self.memory_index.items():
            if 'prompt_embedding' in data and data['prompt_embedding']:
                embedding = np.array(data['prompt_embedding']).reshape(1, -1)
                q_embedding = np.array(query_embedding).reshape(1, -1)
                similarity = cosine_similarity(q_embedding, embedding)[0][0]
                similarities.append((similarity, data))

        similarities.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in similarities[:top_k]]

    def retrieve_by_metrics(self, metric_name, top_k=5, sort_order='desc'):
        logging.info(f"Retrieving prompts by metric: {metric_name} (order: {sort_order})")
        ranked_prompts = []
        for log_id, data in self.memory_index.items():
            metrics = data.get('associated_metrics', {})
            if metric_name in metrics:
                ranked_prompts.append((metrics[metric_name], data))

        if sort_order == 'desc':
            ranked_prompts.sort(key=lambda x: x[0], reverse=True)
        else:
            ranked_prompts.sort(key=lambda x: x[0])

        return [item[1] for item in ranked_prompts[:top_k]]

    def search_memory(self, query=None, metric_filter=None, min_metric_value=None, top_k=10):
        results = []
        # First, filter by metric if specified
        filtered_by_metric = []
        if metric_filter and min_metric_value is not None:
            for log_id, data in self.memory_index.items():
                metrics = data.get('associated_metrics', {})
                if metric_filter in metrics and metrics[metric_filter] >= min_metric_value:
                    filtered_by_metric.append(data)
        else:
            filtered_by_metric = list(self.memory_index.values())

        # Then, if a query is provided, retrieve by similarity within the filtered set
        if query:
            try:
                query_embedding = self._get_embedding(query)
            except NotImplementedError as e:
                logging.error(e)
                return []

            if not query_embedding:
                return []

            similarities = []
            for data in filtered_by_metric:
                if 'prompt_embedding' in data and data['prompt_embedding']:
                    embedding = np.array(data['prompt_embedding']).reshape(1, -1)
                    q_embedding = np.array(query_embedding).reshape(1, -1)
                    similarity = cosine_similarity(q_embedding, embedding)[0][0]
                    similarities.append((similarity, data))
            similarities.sort(key=lambda x: x[0], reverse=True)
            results = [item[1] for item in similarities[:top_k]]
        else:
            # If no query, just return top_k from metric-filtered results (or all if no metric filter)
            results = filtered_by_metric[:top_k]

        return results

if __name__ == '__main__':
    import os
    # Create a dummy memory_index.json for testing
    dummy_memory_data = {
        "log_1": {
            "timestamp": "2023-01-01T10:00:00",
            "prompt": "Create a strategy for RSI crossover.",
            "completion": "Strategy YAML for RSI.",
            "prompt_embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
            "completion_embedding": [0.5, 0.4, 0.3, 0.2, 0.1],
            "associated_metrics": {"sharpe_ratio": 1.5, "pnl": 1000, "win_rate": 0.6}
        },
        "log_2": {
            "timestamp": "2023-01-02T11:00:00",
            "prompt": "Develop a MACD divergence strategy.",
            "completion": "Strategy YAML for MACD.",
            "prompt_embedding": [0.1, 0.1, 0.1, 0.1, 0.1],
            "completion_embedding": [0.2, 0.2, 0.2, 0.2, 0.2],
            "associated_metrics": {"sharpe_ratio": 0.8, "pnl": 500, "win_rate": 0.55}
        },
        "log_3": {
            "timestamp": "2023-01-03T12:00:00",
            "prompt": "Scalping strategy with Bollinger Bands.",
            "completion": "Strategy YAML for Bollinger.",
            "prompt_embedding": [0.9, 0.8, 0.7, 0.6, 0.5],
            "completion_embedding": [0.5, 0.6, 0.7, 0.8, 0.9],
            "associated_metrics": {"sharpe_ratio": 2.1, "pnl": 1500, "win_rate": 0.7}
        }
    }
    with open('memory_index.json', 'w') as f:
        json.dump(dummy_memory_data, f, indent=2)

    retriever = PromptRetriever()

    print("\n--- Top 2 prompts by Sharpe Ratio ---")
    top_sharpe = retriever.retrieve_by_metrics('sharpe_ratio', top_k=2)
    for p in top_sharpe:
        print(f"Prompt: {p['prompt']} | Sharpe: {p['associated_metrics']['sharpe_ratio']}")

    print("\n--- Prompts similar to 'RSI based trading' ---")
    # Note: This will fail until _get_embedding is implemented to use OpenAI client
    # For testing, you might manually set a query_embedding or mock the method.
    # For now, this part is commented out to avoid NotImplementedError.
    # similar_prompts = retriever.retrieve_by_similarity('RSI based trading', top_k=1)
    # for p in similar_prompts:
    #     print(f"Prompt: {p['prompt']} | Similarity: (requires embedding)")

    print("\n--- Search for prompts with Win Rate >= 0.6 ---")
    filtered_prompts = retriever.search_memory(metric_filter='win_rate', min_metric_value=0.6)
    for p in filtered_prompts:
        print(f"Prompt: {p['prompt']} | Win Rate: {p['associated_metrics']['win_rate']}")

    # Clean up dummy file
    # os.remove('memory_index.json')