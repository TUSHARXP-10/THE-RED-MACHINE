#!/usr/bin/env python3
"""
Kite Connect Demat Setup Guide and Quick Configuration
"""

import os
import json
from datetime import datetime

def setup_kite_connect():
    """Setup Kite Connect for demat integration"""
    
    print("🎯 KITE CONNECT DEMAT SETUP GUIDE")
    print("=" * 50)
    
    # Check current configuration
    print("\n📋 Current Configuration:")
    
    env_vars = {
        'KITE_API_KEY': os.getenv('KITE_API_KEY', 'NOT_SET'),
        'KITE_API_SECRET': os.getenv('KITE_API_SECRET', 'NOT_SET'),
        'KITE_ACCESS_TOKEN': os.getenv('KITE_ACCESS_TOKEN', 'NOT_SET'),
        'ZERODHA_CLIENT_ID': os.getenv('ZERODHA_CLIENT_ID', 'NOT_SET')
    }
    
    for key, value in env_vars.items():
        status = "✅" if value != 'NOT_SET' and len(value) > 5 else "❌"
        masked_value = value[:8] + "..." if len(value) > 8 else value
        print(f"   {status} {key}: {masked_value}")
    
    # Quick setup steps
    print("\n🔧 QUICK SETUP STEPS:")
    print("1. Get API credentials from https://kite.trade")
    print("2. Update .env file with your credentials")
    print("3. Generate access token using login flow")
    print("4. Test connection")
    
    # Create sample config
    sample_config = {
        "kite_api": {
            "api_key": "your_api_key_here",
            "api_secret": "your_api_secret_here",
            "redirect_url": "https://localhost",
            "client_id": "your_client_id"
        },
        "trading_parameters": {
            "initial_capital": 3000,
            "max_position_size": 0.15,
            "risk_per_trade": 0.02
        },
        "demat_settings": {
            "enable_live_trading": False,
            "enable_paper_trading": True,
            "order_type": "MARKET",
            "product_type": "MIS"
        }
    }
    
    # Save sample config
    with open('kite_setup_config.json', 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    print(f"\n✅ Sample config saved to: kite_setup_config.json")
    print("\n🚀 TO START TRADING:")
    print("1. Run: python test_kite_connection.py")
    print("2. Check dashboard: http://localhost:8501")
    print("3. Verify system: python verify_system_ready.py")

def generate_login_url():
    """Generate Kite Connect login URL"""
    api_key = os.getenv('KITE_API_KEY', '')
    if api_key:
        login_url = f"https://kite.trade/connect/login?api_key={api_key}&v=3"
        print(f"\n🔗 LOGIN URL:")
        print(f"   {login_url}")
        print("   Use this URL to get request token")
    else:
        print("\n❌ API key not set. Update .env file first.")

if __name__ == "__main__":
    setup_kite_connect()
    generate_login_url()