import os
import re
import yaml
from datetime import datetime

class ResearchRefiner:
    def __init__(self, gpt_outputs_dir='gpt_outputs/', refined_strategies_dir='refined_strategies/'):
        self.gpt_outputs_dir = gpt_outputs_dir
        self.refined_strategies_dir = refined_strategies_dir
        os.makedirs(self.refined_strategies_dir, exist_ok=True)

    def _load_yaml_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(f"Error parsing YAML in {filepath}: {e}")
                return None

    def _save_yaml_file(self, data, filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, indent=2, sort_keys=False)

    def _refine_strategy_yaml(self, strategy_data):
        # Example refinement: Ensure 'name' and 'description' exist
        if 'name' not in strategy_data or not strategy_data['name']:
            strategy_data['name'] = 'Unnamed_GPT_Strategy'
        if 'description' not in strategy_data or not strategy_data['description']:
            strategy_data['description'] = 'GPT-generated strategy without a specific description.'

        # Example refinement: Ensure 'parameters' section exists for a strategy
        if 'parameters' not in strategy_data:
            strategy_data['parameters'] = {}

        # Example refinement: Ensure 'rules' section exists and is a list
        if 'rules' not in strategy_data or not isinstance(strategy_data['rules'], list):
            strategy_data['rules'] = []

        # Add more sophisticated refinement logic here based on common GPT errors or desired structure
        # For instance, checking for valid indicator names, timeframes, etc.

        # Add a default status of 'active' to the strategy
        strategy_data['status'] = 'active'

        return strategy_data

    def refine_gpt_outputs(self):
        # This method can be used to refine all files in gpt_outputs_dir
        # It's kept for backward compatibility or batch processing if needed.
        refined_count = 0
        for filename in os.listdir(self.gpt_outputs_dir):
            if filename.endswith('.yaml'):
                filepath = os.path.join(self.gpt_outputs_dir, filename)
                refined_count += self.refine_gpt_outputs_from_single_file(filepath)
        return refined_count

    def refine_gpt_outputs_from_single_file(self, filepath):
        refined_count = 0
        filename = os.path.basename(filepath)
        strategy_data = self._load_yaml_file(filepath)

        if strategy_data:
            refined_data = self._refine_strategy_yaml(strategy_data)
            output_filename = f"refined_{filename}"
            output_filepath = os.path.join(self.refined_strategies_dir, output_filename)
            self._save_yaml_file(refined_data, output_filepath)
            print(f"Refined {filename} and saved to {output_filepath}")
            refined_count += 1
        else:
            print(f"Skipping {filename} due to YAML parsing error.")
        return refined_count

    def meta_analyze_strategies(self):
        # This is a placeholder for more advanced meta-analysis.
        # In a real scenario, this would involve analyzing backtest results
        # of refined strategies to identify patterns in successful prompts/structures.
        print("\n--- Performing Meta-Analysis (Placeholder) ---")
        print("Analyze refined strategies and their backtest results to identify effective patterns.")
        print("This would involve correlating strategy characteristics with performance metrics.")

if __name__ == '__main__':
    refiner = ResearchRefiner()
    print("\n--- Refining GPT-Generated Strategy YAMLs ---")
    # Example usage: refine all files in gpt_outputs_dir
    refined_strategies_count = refiner.refine_gpt_outputs()
    print(f"Refined {refined_strategies_count} strategy YAMLs.")

    if refined_strategies_count > 0:
        refiner.meta_analyze_strategies()
    else:
        print("No strategies to refine.")

    # Example of refining a single file (for testing or specific use cases)
    # You would replace 'path/to/your/gpt_strategy_file.yaml' with an actual path
    # print("\n--- Refining a single strategy YAML (Example) ---")
    # single_file_path = 'gpt_outputs/gpt_strategy_20231027_123456.yaml' # Replace with a real file
    # if os.path.exists(single_file_path):
    #     refined_single_count = refiner.refine_gpt_outputs_from_single_file(single_file_path)
    #     print(f"Refined {refined_single_count} single strategy YAML.")
    # else:
    #     print(f"Example file {single_file_path} not found.")