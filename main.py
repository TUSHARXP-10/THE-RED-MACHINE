import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Run Red Machine in various modes.")
    parser.add_argument('--mode', type=str, default='local', help='Mode to run the script: local, colab.')
    args = parser.parse_args()

    if args.mode == 'colab':
        print("Running in Google Colab mode...")
        # Placeholder for Colab-specific initialization if needed
        # For now, we'll just run the dashboard as suggested
        subprocess.run(["streamlit", "run", "dashboard.py", "--server.port", "8501", "--server.address", "0.0.0.0"])
    else:
        print("Running in local mode (default)...")
        # Add logic for local mode if different from colab
        subprocess.run(["streamlit", "run", "dashboard.py"])

if __name__ == "__main__":
    main()