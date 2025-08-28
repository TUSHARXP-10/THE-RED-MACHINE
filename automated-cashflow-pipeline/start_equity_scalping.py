#!/usr/bin/env python3
"""
🚀 Quick Start Script for ₹5,000 Equity Scalping Strategy
Run this script to get started immediately!
"""

import os
import json
import sys
from pathlib import Path
import subprocess
import time

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")

def check_prerequisites():
    """Check if all required files exist"""
    print_header("Checking Prerequisites")
    
    required_files = [
        'equity_scalping_config.json',
        'equity_scalping_strategy.py',
        'api.py',
        'requirements.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files present")
    return True

def setup_breeze_credentials():
    """Interactive setup for Breeze API credentials"""
    print_header("Setting up Breeze API Credentials")
    
    print("📋 Let's set up your ICICI Direct Breeze API credentials")
    print("1. Login to ICICI Direct at: https://www.icicidirect.com")
    print("2. Go to: My Account → API Access")
    print("3. Generate your credentials")
    print()
    
    # Check if .env exists
    env_file = Path('.env')
    if env_file.exists():
        print("⚠️  .env file already exists. Do you want to update it? (y/n)")
        choice = input().lower()
        if choice != 'y':
            return
    
    print("\n🔐 Enter your Breeze API credentials:")
    api_key = input("BREEZE_API_KEY: ").strip()
    api_secret = input("BREEZE_API_SECRET: ").strip()
    session_token = input("BREEZE_SESSION_TOKEN: ").strip()
    client_code = input("ICICI_CLIENT_CODE: ").strip()
    
    env_content = f"""# Breeze API Credentials for ICICI Direct
BREEZE_API_KEY={api_key}
BREEZE_API_SECRET={api_secret}
BREEZE_SESSION_TOKEN={session_token}
ICICI_CLIENT_CODE={client_code}

# Trading Configuration
MODE=paper
MAX_POSITION_SIZE=1500
MAX_DAILY_LOSS=200
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Breeze credentials saved to .env file")
    print("📁 You can edit .env anytime to update credentials")

def test_api_endpoints():
    """Test the API endpoints"""
    print_header("Testing API Endpoints")
    
    try:
        import requests
        
        # Test if server is running
        try:
            response = requests.get('http://localhost:8002/health', timeout=5)
            if response.status_code == 200:
                print("✅ API server is running")
                return True
        except:
            pass
        
        print("❌ API server not running. Starting now...")
        return False
        
    except ImportError:
        print("📦 Installing requests for testing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests'])
        return False

def start_server():
    """Start the FastAPI server"""
    print_header("Starting API Server")
    
    print("🚀 Starting FastAPI server...")
    print("Server will be available at: http://localhost:8002")
    print()
    print("📋 Available endpoints:")
    print("  • GET  /equity-scalping/plan?week=1")
    print("  • POST /equity-scalping/trade")
    print("  • GET  /equity-scalping/performance")
    print("  • GET  /setup/breeze-credentials")
    print()
    
    try:
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 
            'api:app', 
            '--host', '0.0.0.0', 
            '--port', '8002', 
            '--reload'
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

def show_quick_commands():
    """Show useful commands"""
    print_header("Quick Commands")
    
    commands = [
        ("Start server", "uvicorn api:app --host 0.0.0.0 --port 8002 --reload"),
        ("Test Week 1 plan", "curl 'http://localhost:8002/equity-scalping/plan?week=1'"),
        ("Test trade", "curl -X POST 'http://localhost:8002/equity-scalping/trade' -H 'Content-Type: application/json' -d '{\"symbol\":\"RELIANCE\",\"current_price\":2800.50,\"model_score\":0.95,\"confidence\":0.85,\"week_number\":1}'"),
        ("Check performance", "curl 'http://localhost:8002/equity-scalping/performance'"),
        ("Setup guide", "curl 'http://localhost:8002/setup/breeze-credentials'")
    ]
    
    for desc, cmd in commands:
        print(f"{desc:20} : {cmd}")

def main():
    """Main setup flow"""
    print_header("🚀 ₹5,000 Equity Scalping Strategy Setup")
    
    print("Welcome to your systematic equity scalping implementation!")
    print("This script will guide you through the setup process.")
    
    # Check prerequisites
    if not check_prerequisites():
        print("❌ Please ensure all required files are present")
        return
    
    # Setup credentials
    print("\n1️⃣ Setup Breeze API credentials? (y/n)")
    if input().lower() == 'y':
        setup_breeze_credentials()
    
    # Show quick commands
    show_quick_commands()
    
    # Ask to start server
    print("\n2️⃣ Start the API server now? (y/n)")
    if input().lower() == 'y':
        start_server()
    else:
        print("\n✅ Setup complete!")
        print("📖 Read EQUITY_SCALPING_GUIDE.md for detailed instructions")
        print("🎯 Start with Week 1: Pure equity focus")
        print("📈 Target: ₹5,000 → ₹5,300 (6% gain)")

if __name__ == "__main__":
    main()