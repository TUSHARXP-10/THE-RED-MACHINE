#!/usr/bin/env python3
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
        print("
📝 UPDATE YOUR .ENV FILE:")
        print(f'KITE_ACCESS_TOKEN="{access_token}"')
        
        # Update .env file
        with open('.env', 'r') as file:
            lines = file.readlines()
        
        with open('.env', 'w') as file:
            for line in lines:
                if line.startswith('KITE_ACCESS_TOKEN='):
                    file.write(f'KITE_ACCESS_TOKEN="{access_token}"
')
                else:
                    file.write(line)
        
        print("
✅ .env file updated!")
        print("
🚀 NOW RUN: python START_LIVE_TRADING.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your request_token")
else:
    print("❌ No request_token provided")
