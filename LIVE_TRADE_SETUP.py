#!/usr/bin/env python3
"""
Live Trading Setup and Token Generator
Fixes Kite Connect authentication for real-time trading
"""

import os
import webbrowser
from datetime import datetime
from kiteconnect import KiteConnect

def generate_login_url():
    """Generate Kite Connect login URL for new access token"""
    
    # API credentials from environment
    api_key = 'q23715gf6tzjmyf5'
    
    if not api_key:
        print("❌ KITE_API_KEY not found in environment")
        return
    
    kite = KiteConnect(api_key=api_key)
    
    # Generate login URL
    login_url = kite.login_url()
    
    print("🎯 KITE CONNECT LOGIN SETUP")
    print("=" * 50)
    print("1. Click this URL to login:")
    print(f"   {login_url}")
    print("\n2. After login, you'll get a request_token in the URL")
    print("3. Copy the request_token parameter from the redirect URL")
    print("4. Update your .env file with the new access token")
    
    # Open browser automatically
    try:
        webbrowser.open(login_url)
        print("\n✅ Browser opened automatically!")
    except:
        print("\n⚠️  Please open the URL manually in your browser")
    
    return login_url

def show_current_config():
    """Display current configuration"""
    print("\n📋 CURRENT CONFIGURATION:")
    print("=" * 30)
    print(f"API Key: q23715gf6tzjmyf5")
    print(f"Client ID: GSS065")
    print(f"Access Token: *** (needs verification)")
    print(f"Mode: LIVE TRADING")
    print(f"Capital: ₹3,000")
    print(f"Target: 50-100 OTM SENSEX Options")

def quick_fix_guide():
    """Quick fix for access token issues"""
    print("\n🔧 QUICK FIX GUIDE:")
    print("=" * 25)
    print("1. Go to: https://kite.zerodha.com/connect/login?api_key=q23715gf6tzjmyf5")
    print("2. Login with your Zerodha credentials")
    print("3. After authorization, copy the 'request_token' from URL")
    print("4. Run: python kite_connect_setup.py")
    print("5. Enter the request_token to generate new access token")
    print("6. Restart the live trading system")

if __name__ == "__main__":
    show_current_config()
    
    print("\n" + "="*60)
    print("🚨 REAL-TIME TRADING READY BUT NEEDS ACCESS TOKEN")
    print("="*60)
    
    generate_login_url()
    quick_fix_guide()
    
    print("\n" + "="*60)
    print("⚡ AFTER SETUP, RUN:")
    print("python START_LIVE_TRADING.py")
    print("="*60)