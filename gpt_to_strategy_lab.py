import os
import re
import yaml
import subprocess
from datetime import datetime
from research_refiner import ResearchRefiner

class GPTToStrategyLab:
    def __init__(self, gpt_logs_dir='gpt_logs/', gpt_outputs_dir='gpt_outputs/', refined_strategies_dir='refined_strategies/', strategy_lab_path='strategy_lab.py'):
        self.gpt_logs_dir = gpt_logs_dir
        self.gpt_outputs_dir = gpt_outputs_dir
        self.refined_strategies_dir = refined_strategies_dir
        self.strategy_lab_path = strategy_lab_path
        os.makedirs(self.gpt_outputs_dir, exist_ok=True)

    def _extract_yaml_from_log(self, log_content):
        # This regex looks for a YAML block, optionally preceded by '```yaml' and followed by '```'
        match = re.search(r'```(?:yaml)?\s*\n(.*?)\n```', log_content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def process_gpt_logs(self):
        processed_count = 0
        for filename in os.listdir(self.gpt_logs_dir):
            if filename.endswith('.log'):
                log_filepath = os.path.join(self.gpt_logs_dir, filename)
                with open(log_filepath, 'r', encoding='utf-8') as f:
                    log_content = f.read()

                yaml_content = self._extract_yaml_from_log(log_content)
                if yaml_content:
                    # Save raw extracted YAML to gpt_outputs_dir
                    raw_output_filename = f"gpt_strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
                    raw_output_filepath = os.path.join(self.gpt_outputs_dir, raw_output_filename)
                    with open(raw_output_filepath, 'w', encoding='utf-8') as f:
                        f.write(yaml_content)
                    print(f"Extracted YAML from {filename} and saved to {raw_output_filepath}")

                    # Refine the extracted YAML
                    refiner = ResearchRefiner(gpt_outputs_dir=self.gpt_outputs_dir, refined_strategies_dir=self.refined_strategies_dir)
                    # Temporarily save the raw YAML to gpt_outputs_dir for refiner to pick up
                    # Then refiner will move it to refined_strategies_dir
                    refined_count_for_this_log = refiner.refine_gpt_outputs_from_single_file(raw_output_filepath)

                    if refined_count_for_this_log > 0:
                        processed_count += 1
                    else:
                        print(f"Warning: No refined strategy generated for {filename}.")
        return processed_count

    def run_backtest_for_gpt_strategies(self):
        backtested_count = 0
        for filename in os.listdir(self.refined_strategies_dir):
            if filename.endswith('.yaml'):
                strategy_filepath = os.path.join(self.refined_strategies_dir, filename)
                print(f"Running backtest for {strategy_filepath}...")
                try:
                    # Assuming strategy_lab.py can take a YAML file as an argument for backtesting
                    # You might need to adjust this command based on your actual strategy_lab.py CLI
                    command = ['python', self.strategy_lab_path, 'backtest', strategy_filepath, '--output', 'gpt_backtest_results.csv']
                    result = subprocess.run(command, capture_output=True, text=True, check=True)
                    print(f"Backtest for {filename} completed successfully.\nOutput:\n{result.stdout}")
                    backtested_count += 1
                except subprocess.CalledProcessError as e:
                    print(f"Error running backtest for {filename}:\n{e.stderr}")
                except FileNotFoundError:
                    print(f"Error: {self.strategy_lab_path} not found. Make sure it's in the correct path.")
        return backtested_count

if __name__ == '__main__':
    gpt_processor = GPTToStrategyLab()
    print("\n--- Processing GPT Logs ---")
    processed_strategies = gpt_processor.process_gpt_logs()
    print(f"Processed {processed_strategies} new GPT strategy logs.")

    if processed_strategies > 0:
        print("\n--- Running Backtests for GPT Strategies ---")
        backtested_strategies = gpt_processor.run_backtest_for_gpt_strategies()
        print(f"Successfully backtested {backtested_strategies} GPT strategies.")
    else:
        print("No new strategies to backtest.")