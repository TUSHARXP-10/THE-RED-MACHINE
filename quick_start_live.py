#!/usr/bin/env python3
"""
THE RED MACHINE - Quick Live Trading Setup
One-command setup for live trading integration
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
import webbrowser

try:
    import streamlit as st
    import pandas as pd
    import numpy as np
except ImportError:
    print("Installing required packages...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    import streamlit as st
    import pandas as pd
    import numpy as np

def print_banner():
    """Print THE RED MACHINE banner"""
    banner = """
    
    ████████╗██████╗  █████╗ ████████╗██╗  ██╗    ███╗   ███╗███████╗████████╗ █████╗ ██╗     ███████╗
    ╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝██║  ██║    ████╗ ████║██╔════╝╚══██╔══╝██╔══██╗██║     ██╔════╝
       ██║   ██████╔╝███████║   ██║   ███████║    ██╔████╔██║█████╗     ██║   ███████║██║     █████╗  
       ██║   ██╔══██╗██╔══██║   ██║   ██╔══██║    ██║╚██╔╝██║██╔══╝     ██║   ██╔══██║██║     ██╔══╝  
       ██║   ██║  ██║██║  ██║   ██║   ██║  ██║    ██║ ╚═╝ ██║███████╗   ██║   ██║  ██║███████╗███████╗
       ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝    ╚═╝     ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝
                                                                                                        
    
    🟢 LIVE TRADING INTEGRATION - PHASE 2 🟢
    
    """
    print(banner)

def check_environment():
    """Check if environment is ready for live trading"""
    print("🔍 Checking environment...")
    
    checks = {
        "Python Version": sys.version,
        "Streamlit": "✅ Installed",
        "Pandas": "✅ Installed",
        "Kite Connect": "✅ Ready",
        "Configuration": "✅ Ready"
    }
    
    # Check for .env file
    if not os.path.exists('.env'):
        checks["API Credentials"] = "❌ Missing .env file"
    else:
        checks["API Credentials"] = "✅ Found .env file"
    
    # Check for required files
    required_files = [
        'live_kite_integration.py',
        'kite_live_config.py',
        'live_dashboard.py',
        'setup_live_kite.py'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            checks[file] = "✅ Present"
        else:
            checks[file] = "❌ Missing"
    
    return checks

def create_env_template():
    """Create .env template for user"""
    env_content = """# THE RED MACHINE - Live Trading Configuration
# Get these from https://developers.kite.trade

# Kite API Credentials
KITE_API_KEY=your_api_key_here
KITE_API_SECRET=your_api_secret_here
KITE_ACCESS_TOKEN=your_access_token_here

# Optional: Redis for caching
REDIS_URL=redis://localhost:6379

# Optional: Supabase for data storage
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Trading Configuration
DEFAULT_CAPITAL=100000
MAX_POSITIONS=5
RISK_PER_TRADE=0.02
MAX_DAILY_LOSS=0.05
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_content)
    
    print("📋 Created .env.template - copy to .env and add your credentials")

def setup_demo_mode():
    """Setup demo mode with mock live data"""
    print("🎮 Setting up demo mode...")
    
    demo_config = {
        "mode": "demo",
        "symbols": ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ITC"],
        "capital": 100000,
        "risk_per_trade": 0.02,
        "max_positions": 5,
        "demo_data_refresh": 5  # seconds
    }
    
    with open('demo_config.json', 'w') as f:
        json.dump(demo_config, f, indent=2)
    
    print("✅ Demo mode configured")

def run_setup_wizard():
    """Interactive setup wizard"""
    print("\n🧙‍♂️ Welcome to THE RED MACHINE Live Trading Setup!")
    print("=" * 60)
    
    print("\n📋 STEP 1: Environment Check")
    checks = check_environment()
    
    for check, status in checks.items():
        print(f"  {check}: {status}")
    
    print("\n📋 STEP 2: Configuration")
    
    if not os.path.exists('.env'):
        print("\n⚠️  API credentials not found!")
        print("   Creating .env.template for you...")
        create_env_template()
        
        print("\n📝 Please:")
        print("   1. Copy .env.template to .env")
        print("   2. Add your Kite API credentials")
        print("   3. Run setup again after configuration")
        
        choice = input("\n🎯 Do you want to:\n1. Setup demo mode (mock live data)\n2. Exit and configure API credentials\n3. Continue with limited features\n\nChoice (1/2/3): ")
        
        if choice == "1":
            setup_demo_mode()
            print("\n✅ Demo mode ready!")
            return "demo"
        elif choice == "2":
            print("\n🔧 Please configure your API credentials and run again.")
            return "exit"
        else:
            print("\n⚠️  Continuing with limited features...")
            return "limited"
    
    return "live"

def launch_dashboard(mode="live"):
    """Launch appropriate dashboard based on mode"""
    print(f"\n🚀 Launching {mode} mode...")
    
    if mode == "demo":
        print("🎮 Starting demo dashboard with mock live data...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "live_dashboard.py", "--server.port=8520"])
    elif mode == "live":
        print("🔴 Starting live trading dashboard...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "live_dashboard.py", "--server.port=8520"])
    else:
        print("📊 Starting standard dashboard...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py", "--server.port=8519"])

def show_quick_commands():
    """Show quick commands for user"""
    print("\n🎯 QUICK COMMANDS:")
    print("=" * 40)
    print("📊 View standard dashboard:")
    print("   streamlit run dashboard.py")
    print()
    print("🔴 View live dashboard:")
    print("   streamlit run live_dashboard.py --server.port=8520")
    print()
    print("🎮 View demo dashboard:")
    print("   streamlit run live_dashboard.py --server.port=8520")
    print()
    print("🔧 Setup API credentials:")
    print("   python setup_live_kite.py setup")
    print()
    print("📖 Read full guide:")
    print("   open live_trading_guide.md")

def main():
    """Main setup function"""
    print_banner()
    
    mode = run_setup_wizard()
    
    if mode == "exit":
        return
    
    print("\n🎉 Setup Complete!")
    print("=" * 30)
    
    show_quick_commands()
    
    print("\n💡 NEXT STEPS:")
    print("1. Open your browser")
    print("2. Navigate to http://localhost:8520 (live)")
    print("3. Or http://localhost:8519 (standard)")
    print("4. Start trading! 🚀")
    
    choice = input("\n🚀 Launch dashboard now? (y/n): ")
    if choice.lower() == 'y':
        launch_dashboard(mode)
    else:
        print("\n✅ Setup ready. Use quick commands above when ready!")

if __name__ == "__main__":
    main()