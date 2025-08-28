#!/usr/bin/env python3
"""
Live Trading Launcher
Ensures proper environment loading and starts real-time Kite Connect trading
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
def load_environment():
    """Load and verify all environment variables"""
    load_dotenv()
    
    api_key = os.getenv('KITE_API_KEY')
    api_secret = os.getenv('KITE_API_SECRET')
    access_token = os.getenv('KITE_ACCESS_TOKEN')
    client_id = os.getenv('ZERODHA_CLIENT_ID')
    
    if not all([api_key, api_secret, access_token, client_id]):
        print("❌ Missing Kite Connect credentials")
        print("Please check your .env file contains:")
        print("KITE_API_KEY, KITE_API_SECRET, KITE_ACCESS_TOKEN, ZERODHA_CLIENT_ID")
        return False
    
    print("✅ Environment variables loaded:")
    print(f"   API Key: {api_key[:8]}...")
    print(f"   Client ID: {client_id}")
    print(f"   Access Token: {'***' if access_token else 'MISSING'}")
    
    return True

def start_live_trading():
    """Start the live trading system"""
    print("🚀 Starting REAL-TIME Kite Connect Trading...")
    print("💰 Capital: ₹3,000")
    print("🎯 Target: 50-100 OTM SENSEX Options")
    print("⚡ Mode: LIVE TRADING via Kite Connect")
    
    try:
        # Import and start the live signal executor
        from live_signal_executor import LiveSignalExecutor
        
        executor = LiveSignalExecutor()
        executor.run()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed")
    except Exception as e:
        print(f"❌ Error starting trading: {e}")

if __name__ == "__main__":
    print("🔍 Verifying Kite Connect setup...")
    
    if load_environment():
        print("\n" + "="*50)
        start_live_trading()
    else:
        print("\nPlease fix the environment configuration and try again.")