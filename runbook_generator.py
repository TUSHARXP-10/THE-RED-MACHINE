import pandas as pd
from datetime import datetime
import os
import json
from datetime import datetime, timedelta
import logging
import yaml

# Configure logging for the runbook generator
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

class RunbookGenerator:
    def __init__(self, reports_dir='reports/', leaderboard_path='leaderboard.csv',
                 drift_metrics_path='.drift_metrics.json', scheduler_logs_dir='scheduler_logs/',
                 gpt_logs_dir='gpt_logs/', refined_strategies_dir='refined_strategies/',
                 strategies_yaml_path='strategies.yaml'): # Assuming strategies.yaml is the main file for all strategies
        self.reports_dir = reports_dir
        self.leaderboard_path = leaderboard_path
        self.drift_metrics_path = drift_metrics_path
        self.scheduler_logs_dir = scheduler_logs_dir
        self.gpt_logs_dir = gpt_logs_dir
        self.refined_strategies_dir = refined_strategies_dir
        self.strategies_yaml_path = strategies_yaml_path
        os.makedirs(self.reports_dir, exist_ok=True)
        self.reports_dir = reports_dir
        self.leaderboard_path = leaderboard_path
        self.drift_metrics_path = drift_metrics_path
        self.scheduler_logs_dir = scheduler_logs_dir
        os.makedirs(self.reports_dir, exist_ok=True)

    def _load_leaderboard(self):
        if os.path.exists(self.leaderboard_path):
            return pd.read_csv(self.leaderboard_path)
        logging.warning(f"Leaderboard file not found at {self.leaderboard_path}")
        return pd.DataFrame()

    def _load_drift_metrics(self):
        if os.path.exists(self.drift_metrics_path):
            with open(self.drift_metrics_path, 'r') as f:
                return json.load(f)
        logging.warning(f"Drift metrics file not found at {self.drift_metrics_path}")
        return {}

    def _get_scheduler_logs(self):
        logs = []
        for filename in sorted(os.listdir(self.scheduler_logs_dir)):
            if filename.endswith('.log'):
                filepath = os.path.join(self.scheduler_logs_dir, filename)
                with open(filepath, 'r') as f:
                    logs.append(f.read())
        return "\n".join(logs)

    def clean_old_reports(self, days_to_retain=30):
        """Cleans up old reports from the reports directory."""
        logging.info(f"--- Cleaning old reports (retaining {days_to_retain} days) ---")
        cutoff_date = datetime.now() - timedelta(days=days_to_retain)
        for filename in os.listdir(self.reports_dir):
            filepath = os.path.join(self.reports_dir, filename)
            if os.path.isfile(filepath) and (filename.endswith('.html') or filename.endswith('.pdf')):
                file_mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_mod_time < cutoff_date:
                    os.remove(filepath)
                    logging.info(f"Removed old report file: {filename}")

    def _get_gpt_logs(self):
        gpt_logs_content = []
        for filename in sorted(os.listdir(self.gpt_logs_dir)):
            if filename.startswith('log_') and filename.endswith('.txt'):
                filepath = os.path.join(self.gpt_logs_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    gpt_logs_content.append(f"<h3>File: {filename}</h3><pre class=\"log-pre\">{f.read()}</pre>")
        return "\n".join(gpt_logs_content)

    def _get_strategy_changelog(self):
        new_strategies = []
        refined_strategies = []
        deactivated_strategies = []

        # Get all strategies from strategies.yaml
        all_strategies = []
        if os.path.exists(self.strategies_yaml_path):
            try:
                with open(self.strategies_yaml_path, 'r', encoding='utf-8') as f:
                    all_strategies = yaml.safe_load(f)
                    if not isinstance(all_strategies, list):
                        all_strategies = [] # Ensure it's a list
            except Exception as e:
                logging.warning(f"Could not read strategies.yaml: {e}")

        # Track new/refined strategies from refined_strategies_dir
        # This assumes that files in refined_strategies are newly generated/refined and not yet merged into strategies.yaml
        for filename in os.listdir(self.refined_strategies_dir):
            if filename.endswith('.yaml'):
                refined_strategies.append(filename)

        # Track deactivated strategies from strategies.yaml
        for strategy in all_strategies:
            if isinstance(strategy, dict) and strategy.get('status') == 'inactive':
                deactivated_strategies.append(strategy.get('name', 'Unnamed Inactive Strategy'))
            elif isinstance(strategy, dict) and strategy.get('status') == 'active':
                # To identify truly 'new' strategies, we'd need to compare with a historical record
                # or check if they were just added to strategies.yaml. For now, we'll rely on refined_strategies_dir
                # for new/refined and strategies.yaml for deactivated.
                pass

        changelog_html = ""
        if new_strategies:
            changelog_html += "<h4>Newly Created Strategies:</h4><ul>" + "".join([f"<li>{s}</li>" for s in new_strategies]) + "</ul>"
        if refined_strategies:
            changelog_html += "<h4>Refined Strategies:</h4><ul>" + "".join([f"<li>{s}</li>" for s in refined_strategies]) + "</ul>"
        if deactivated_strategies:
            changelog_html += "<h4>Deactivated Strategies:</h4><ul>" + "".join([f"<li>{s}</li>" for s in deactivated_strategies]) + "</ul>"

        if not changelog_html:
            changelog_html = "<p>No significant strategy changes detected today.</p>"

        return changelog_html

    def generate_html_report(self):
        report_date = datetime.now().strftime('%Y-%m-%d')
        report_filename = os.path.join(self.reports_dir, f'runbook_{report_date}.html')

        leaderboard_df = self._load_leaderboard()
        drift_metrics = self._load_drift_metrics()
        scheduler_logs = self._get_scheduler_logs()
        gpt_logs = self._get_gpt_logs()
        strategy_changelog = self._get_strategy_changelog()

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>The Red Machine - Daily Runbook {report_date}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; background-color: #f4f4f4; }}
                .container {{ max-width: 1000px; margin: auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1, h2, h3 {{ color: #0056b3; }}
                h1 {{ text-align: center; color: #d32f2f; margin-bottom: 30px; }}
                .section {{ margin-bottom: 30px; padding: 20px; background-color: #e9f7ff; border-left: 5px solid #007bff; border-radius: 5px; }}
                .section h2 {{ color: #007bff; margin-top: 0; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
                th {{ background-color: #007bff; color: white; }}
                .log-pre {{ background-color: #eee; padding: 15px; border-radius: 5px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; font-family: 'Consolas', 'Monaco', monospace; font-size: 0.9em; }}
                .footer {{ text-align: center; margin-top: 40px; font-size: 0.8em; color: #777; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>The Red Machine - Daily Runbook</h1>
                <p style="text-align: center; font-size: 1.1em; color: #555;">Report Date: {report_date}</p>

                <div class="section">
                    <h2>📊 Strategy Leaderboard Summary</h2>
                    {leaderboard_df.to_html(index=False) if not leaderboard_df.empty else '<p>No leaderboard data available.</p>'}
                </div>

                <div class="section">
                    <h2>📈 Strategy Changelog</h2>
                    {strategy_changelog}
                </div>

                <div class="section">
                    <h2>📉 Drift Detection Insights</h2>
                    <p>This section summarizes strategies that have shown performance drift and actions taken.</p>
                    <pre class="log-pre">{json.dumps(drift_metrics, indent=2)}</pre>
                </div>

                <div class="section">
                    <h2>🧠 GPT Prompt Insights</h2>
                    <p>Recent prompts and completions from the GPT strategy suggestor.</p>
                    {gpt_logs if gpt_logs else '<p>No GPT logs available.</p>'}
                </div>

                <div class="section">
                    <h2>📜 Scheduler Activity Logs</h2>
                    <p>Comprehensive logs from the autonomous lab scheduler.</p>
                    <pre class="log-pre">{scheduler_logs if scheduler_logs else 'No scheduler logs available.'}</pre>
                </div>

                <div class="footer">
                    <p>Generated by The Red Machine - Autonomous Quant Platform</p>
                    <p>&copy; {datetime.now().year}</p>
                </div>
            </div>
        </body>
        </html>
        """

        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logging.info(f"Daily runbook generated: {report_filename}")
        return report_filename

if __name__ == '__main__':
    generator = RunbookGenerator()
    generator.generate_html_report()

    # Example of how to integrate this into auto_lab_scheduler.py:
    # In auto_lab_scheduler.py, after scoring strategies:
    # from runbook_generator import RunbookGenerator
    # ...
    # self.runbook_generator = RunbookGenerator()
    # self.runbook_generator.generate_html_report()

    # To convert to PDF, you would typically use a library like WeasyPrint or wkhtmltopdf
    # which would need to be installed separately and called via subprocess.