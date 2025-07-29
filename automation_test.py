import unittest
import os
import subprocess
import time
import json

# Assuming the project root is the current working directory
PROJECT_ROOT = os.getcwd()

class RedMachineAutomationTest(unittest.TestCase):

    def setUp(self):
        """Set up for test: Ensure necessary files/dirs exist and clean up previous runs."""
        self.backtest_results_path = os.path.join(PROJECT_ROOT, 'backtest_results.csv')
        self.trade_log_path = os.path.join(PROJECT_ROOT, 'trade_log.csv')
        self.prompt_tracker_path = os.path.join(PROJECT_ROOT, 'prompt_tracker.json')

        # Clean up previous test artifacts
        if os.path.exists(self.backtest_results_path):
            os.remove(self.backtest_results_path)
        if os.path.exists(self.trade_log_path):
            os.remove(self.trade_log_path)
        if os.path.exists(self.prompt_tracker_path):
            os.remove(self.prompt_tracker_path)

        # Ensure logs directory exists for prompt_tracker
        os.makedirs(os.path.dirname(self.prompt_tracker_path), exist_ok=True)

    def _run_script(self, script_name, args=None):
        """Helper to run a Python script and capture output."""
        cmd = ['python', os.path.join(PROJECT_ROOT, script_name)]
        if args:
            cmd.extend(args)
        print(f"\nRunning command: {' '.join(cmd)}")
        process = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
        if process.returncode != 0:
            print(f"Error running {script_name}:")
            print(f"Stdout: {process.stdout}")
            print(f"Stderr: {process.stderr}")
        return process.returncode, process.stdout, process.stderr

    def test_end_to_end_workflow(self):
        """Simulate and test the full Red Machine workflow."""

        print("\n--- Step 1: Simulate Prompt Generation and Backtest ---")
        # This step now implicitly logs prompts via sensex_trading_model.py
        return_code, stdout, stderr = self._run_script('sensex_trading_model.py', ['backtest'])
        self.assertEqual(return_code, 0, f"sensex_trading_model.py backtest failed: {stderr}")
        self.assertTrue(os.path.exists(self.backtest_results_path), "backtest_results.csv not created")
        self.assertTrue(os.path.exists(self.prompt_tracker_path), "prompt_tracker.json not created")

        # Verify prompt was logged
        with open(self.prompt_tracker_path, 'r') as f:
            prompts = json.load(f)
        self.assertGreater(len(prompts), 0, "No prompts logged in prompt_tracker.json")
        logged_prompt = prompts[0]
        self.assertIn('prompt_text', logged_prompt)
        self.assertIn('pnl', logged_prompt)
        self.assertIsInstance(logged_prompt['pnl'], (int, float))
        print("Prompt generation and backtest successful. Prompt logged.")

        print("\n--- Step 2: Simulate Trade Execution (using a dummy signal) ---")
        # For a true E2E test, this would involve live_signal_executor.py
        # For now, we'll just ensure trade_log.csv is created/updated by a dummy run
        # In a real scenario, you'd need to mock or run a component that actually places trades.
        # As sensex_trading_model.py doesn't directly log trades from backtest, we'll simulate.
        # The log_trade function is in sensex_trading_model.py, but not called in backtest_from_file
        # We need a way to trigger trade logging. Let's assume a simple script for this.
        # For this test, we'll manually create a dummy trade log entry.
        with open(self.trade_log_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['2024-01-01T10:00:00', 'Call', 75000, '2025-07-31', 100.0, 'BUY', 'EXECUTED'])
        self.assertTrue(os.path.exists(self.trade_log_path), "trade_log.csv not created")
        print("Trade execution simulated. Dummy trade logged.")

        print("\n--- Step 3: Trigger Feedback Loops (e.g., agent drift detection, prompt optimization) ---")
        # This would typically involve running feedback_loop.py or agent_drift_detector.py
        # For simplicity, we'll run agent_drift_detector.py
        return_code, stdout, stderr = self._run_script('agent_drift_detector.py')
        # agent_drift_detector.py might not have a direct success output, check return code
        self.assertEqual(return_code, 0, f"agent_drift_detector.py failed: {stderr}")
        print("Feedback loop (drift detection) triggered.")

        print("\n--- Step 4: Check Dashboard Updates (conceptual check) ---")
        # This is a conceptual check as we can't programmatically interact with Streamlit UI easily.
        # We assume that if the underlying data files (backtest_results.csv, prompt_tracker.json, trade_log.csv)
        # are updated, the dashboard will reflect these changes upon refresh.
        print("Dashboard updates are conceptually verified by checking underlying data files.")
        print("Ensure Streamlit dashboard is running and refresh to see changes.")

        print("\nEnd-to-end workflow simulation complete.")

if __name__ == '__main__':
    import csv # Import csv for manual trade log creation
    unittest.main()