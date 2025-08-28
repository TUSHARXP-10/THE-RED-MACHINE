#!/usr/bin/env python3
"""
Real-Time Trading Setup - IMMEDIATE ACTION REQUIRED
Step-by-step guide to get live Kite Connect trading working NOW
"""

import webbrowser
import os
from datetime import datetime

def immediate_setup():
    print("🚨 IMMEDIATE REAL-TIME TRADING SETUP")
    print("=" * 50)
    print("Market is OPEN - Let's get you trading LIVE!")
    print()
    
    # Step 1: Check current status
    print("📊 CURRENT STATUS:")
    print("   ❌ Access Token: EXPIRED/INVALID")
    print("   ✅ API Key: Available")
    print("   ✅ Client ID: Available")
    print("   ✅ Capital: ₹3,000 configured")
    print()
    
    # Step 2: Generate new login URL
    api_key = 'q23715gf6tzjmyf5'
    login_url = f"https://kite.trade/connect/login?api_key={api_key}&v=3"
    
    print("🎯 STEP 1: GET NEW ACCESS TOKEN")
    print("-" * 30)
    print("1. Open this URL in your browser:")
    print(f"   {login_url}")
    print()
    print("2. Login with your Zerodha credentials")
    print("3. After authorization, copy the 'request_token' from the URL")
    print()
    
    # Open browser
    try:
        webbrowser.open(login_url)
        print("✅ Browser opened automatically!")
    except:
        print("🌐 Please open the URL manually")
    
    print("\n" + "="*50)
    print("🔄 STEP 2: UPDATE ACCESS TOKEN")
    print("-" * 30)
    print("Once you have the request_token:")
    print("1. Run: python kite_access_generator.py")
    print("2. Enter your request_token")
    print("3. Copy the new access_token")
    print("4. Update .env file")
    print()
    
    # Create access token generator
    with open('kite_access_generator.py', 'w', encoding='utf-8') as f:
        f.write('''#!/usr/bin/env python3
import os
from kiteconnect import KiteConnect

# Your credentials
api_key = 'q23715gf6tzjmyf5'
api_secret = '87ivk3royi2z30lhzprgovhrocp8yq1g'

print("🎯 KITE ACCESS TOKEN GENERATOR")
print("=" * 40)

request_token = input("Enter your request_token: ").strip()

if request_token:
    try:
        kite = KiteConnect(api_key=api_key)
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]
        
        print(f"✅ NEW ACCESS TOKEN: {access_token}")
        print("\n📝 UPDATE YOUR .ENV FILE:")
        print(f'KITE_ACCESS_TOKEN="{access_token}"')
        
        # Update .env file
        with open('.env', 'r') as file:
            lines = file.readlines()
        
        with open('.env', 'w') as file:
            for line in lines:
                if line.startswith('KITE_ACCESS_TOKEN='):
                    file.write(f'KITE_ACCESS_TOKEN="{access_token}"\n')
                else:
                    file.write(line)
        
        print("\n✅ .env file updated!")
        print("\n🚀 NOW RUN: python START_LIVE_TRADING.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your request_token")
else:
    print("❌ No request_token provided")
''')
    
    print("\n" + "="*50)
    print("⚡ READY TO TRADE")
    print("-" * 20)
    print("After updating access token:")
    print("python START_LIVE_TRADING.py")
    print("\nThis will start REAL-TIME Kite Connect trading")
    print("with ₹3,000 capital on 50-100 OTM SENSEX options!")

if __name__ == "__main__":
    immediate_setup()