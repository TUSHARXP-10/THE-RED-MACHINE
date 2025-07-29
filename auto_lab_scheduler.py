import os
import sys
import subprocess
import datetime
import logging
from dotenv import load_dotenv
from runbook_generator import RunbookGenerator
from prompt_memory import PromptMemory
from prompt_optimizer import PromptOptimizer
from runbook_email_sender import RunbookEmailSender
from prompt_retriever import PromptRetriever

# Load environment variables from .env file
load_dotenv()

# --- Configuration --- #
LOG_DIR = 'scheduler_logs/'
LOG_FILE = os.path.join(LOG_DIR, 'auto_lab_scheduler.log')

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

# --- Paths to other modules (relative to this script) ---
GPT_STRATEGY_SUGGESTOR_PATH = 'gpt_strategy_suggestor.py'
GPT_TO_STRATEGY_LAB_PATH = 'gpt_to_strategy_lab.py'
STRATEGY_SCORER_PATH = 'strategy_scorer.py'
DAILY_DIGEST_PATH = 'daily_digest.py' # Assuming this exists for notifications
TELEGRAM_BOT_PATH = 'telegram_bot.py' # Assuming this exists for notifications

class AutoLabScheduler:
    def __init__(self):
        self.auto_backtest_gpt = os.getenv('AUTO_BACKTEST_GPT', 'False').lower() == 'true'
        self.runbook_generator = RunbookGenerator()
        self.prompt_memory = PromptMemory() # Initialize PromptMemory
        self.prompt_optimizer = PromptOptimizer() # Initialize PromptOptimizer
        self.email_sender = RunbookEmailSender() # Initialize RunbookEmailSender
        self.prompt_retriever = PromptRetriever() # Initialize PromptRetriever
        logging.info(f"AutoLabScheduler initialized. AUTO_BACKTEST_GPT: {self.auto_backtest_gpt}")

    def _run_command(self, command, cwd=None):
        """Helper to run a shell command and log its output."""
        logging.info(f"Running command: {' '.join(command)}")
        try:
            result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=True)
            logging.info(f"Command stdout:\n{result.stdout}")
            if result.stderr:
                logging.warning(f"Command stderr:\n{result.stderr}")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Command failed with exit code {e.returncode}: {e.cmd}")
            logging.error(f"Stdout: {e.stdout}")
            logging.error(f"Stderr: {e.stderr}")
            return False
        except FileNotFoundError:
            logging.error(f"Command not found. Make sure it's in your PATH: {command[0]}")
            return False

    def run_gpt_suggestion(self):
        """Runs the GPT strategy suggestion module."""
        logging.info("--- Starting GPT Strategy Suggestion ---")
        top_prompts = self.prompt_retriever.retrieve_by_metrics('sharpe_ratio', top_k=3)
        top_prompts_content = [p['prompt'] for p in top_prompts]

        command = [sys.executable, GPT_STRATEGY_SUGGESTOR_PATH]
        if top_prompts_content:
            command.append('--top_prompts')
            command.extend(top_prompts_content)

        if self._run_command(command):
            logging.info("GPT Strategy Suggestion completed successfully.")
            return True
        else:
            logging.error("GPT Strategy Suggestion failed.")
            return False

    def process_and_backtest_gpt_strategies(self):
        """Processes GPT logs, refines, and backtests strategies."""
        logging.info("--- Starting GPT Strategy Processing and Backtesting ---")
        if not self.auto_backtest_gpt:
            logging.info("AUTO_BACKTEST_GPT is set to False. Skipping backtesting.")
            return True

        if self._run_command([sys.executable, GPT_TO_STRATEGY_LAB_PATH]):
            logging.info("GPT Strategy Processing and Backtesting completed successfully.")
            return True
        else:
            logging.error("GPT Strategy Processing and Backtesting failed.")
            return False

    def score_strategies(self):
        """Scores the backtested strategies and updates the leaderboard."""
        logging.info("--- Starting Strategy Scoring ---")
        if self._run_command([sys.executable, STRATEGY_SCORER_PATH]):
            logging.info("Strategy Scoring completed successfully.")
            return True
        else:
            logging.error("Strategy Scoring failed.")
            return False

    def run_drift_detection(self):
        """Runs the drift detection module."""
        logging.info("--- Starting Drift Detection ---")
        if self._run_command([sys.executable, 'drift_detector.py']):
            logging.info("Drift Detection completed successfully.")
            return True
        else:
            logging.error("Drift Detection failed.")
            return False

    def send_notifications(self):
        """Sends daily updates via daily_digest or telegram_bot."""
        logging.info("--- Sending Notifications ---")
        # Example: Trigger daily digest (assuming it generates and sends a report)
        if os.path.exists(DAILY_DIGEST_PATH):
            if self._run_command([sys.executable, DAILY_DIGEST_PATH]):
                logging.info("Daily Digest sent successfully.")
            else:
                logging.warning("Daily Digest failed to send.")
        else:
            logging.info(f"Daily Digest script not found at {DAILY_DIGEST_PATH}. Skipping.")

        # Example: Trigger Telegram bot (assuming it has a command for updates)
        if os.path.exists(TELEGRAM_BOT_PATH):
            # This might require a specific command or interaction, adjust as needed
            logging.info(f"Telegram bot script found at {TELEGRAM_BOT_PATH}. Manual trigger might be needed.")
        else:
            logging.info(f"Telegram Bot script not found at {TELEGRAM_BOT_PATH}. Skipping.")

    def clean_old_logs(self, days_to_retain=7):
        """Cleans up old scheduler logs."""
        logging.info(f"--- Cleaning old logs (retaining {days_to_retain} days) ---")
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_to_retain)
        for filename in os.listdir(LOG_DIR):
            filepath = os.path.join(LOG_DIR, filename)
            if os.path.isfile(filepath):
                file_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_mod_time < cutoff_date:
                    os.remove(filepath)
                    logging.info(f"Removed old log file: {filename}")

    def run_full_cycle(self):
        """Runs the complete autonomous lab cycle."""
        logging.info("\n--- Starting Full Autonomous Lab Cycle ---")

        if self.run_gpt_suggestion():
            logging.info("--- Processing GPT Logs for Prompt Memory ---")
            try:
                self.prompt_memory.process_gpt_logs()
                logging.info("GPT Logs processed and indexed successfully.")

                logging.info("--- Optimizing Prompts ---")
                try:
                    top_prompts = self.prompt_optimizer.get_top_prompts(num_prompts=10)
                    if top_prompts:
                        logging.info(f"Identified {len(top_prompts)} top prompts for optimization.")
                        evolved_prompts = self.prompt_optimizer.suggest_next_generation(top_prompts)
                        logging.info(f"Generated {len(evolved_prompts)} evolved prompts.")
                        # Here you would typically save these evolved prompts or feed them back into the system
                        # For now, we'll just log them.
                        for i, prompt in enumerate(evolved_prompts):
                            logging.info(f"Evolved Prompt {i+1}: {prompt}")
                        
                        # Create audit trail for the first top prompt that was evolved
                        if evolved_prompts and top_prompts:
                            self.prompt_optimizer.create_prompt_audit_trail(top_prompts[0]['prompt_id'], evolved_prompts)

                    else:
                        logging.info("No top prompts found for optimization.")
                except Exception as e:
                    logging.error(f"Failed to optimize prompts: {e}")

            except Exception as e:
                logging.error(f"Failed to process GPT logs for prompt memory: {e}")

            if self.process_and_backtest_gpt_strategies():
                if self.score_strategies():
                    if self.run_drift_detection():
                        logging.info("Full cycle: GPT suggestion, processing, backtesting, scoring, and drift detection completed.")
                        # Generate daily runbook
                        logging.info("--- Generating Daily Runbook ---")
                        try:
                            latest_runbook_path = self.runbook_generator.generate_html_report()
                            logging.info("Daily Runbook generated successfully.")
                            self.runbook_generator.clean_old_reports() # Clean old reports after generating a new one
                            if latest_runbook_path:
                                self.email_sender.send_runbook_email(latest_runbook_path)
                        except Exception as e:
                            logging.error(f"Failed to generate daily runbook: {e}")
                    else:
                        logging.error("Full cycle failed at drift detection stage.")
                else:
                    logging.error("Full cycle failed at strategy scoring stage.")
            else:
                logging.error("Full cycle failed at processing/backtesting stage.")
        else:
            logging.error("Full cycle failed at GPT suggestion stage.")

        self.send_notifications()
        self.clean_old_logs()

        logging.info("--- Autonomous Lab Cycle Finished ---\n")

if __name__ == '__main__':
    scheduler = AutoLabScheduler()
    scheduler.run_full_cycle()

    # Example of how this might be run via cron:
    # 0 6 * * * /usr/bin/python3 /path/to/your/auto_lab_scheduler.py
    # For Windows Task Scheduler, you'd configure a task to run this Python script daily.