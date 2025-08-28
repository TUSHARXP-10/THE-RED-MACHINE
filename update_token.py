#!/usr/bin/env python3
"""
Update Kite access token with provided request token
"""

from kiteconnect import KiteConnect
import os

# Configuration
request_token = 'GM8BCPtLhtqBCpf20qaDgT2yFxl8oWWc'
api_key = 'q23715gf6tzjmyf5'
api_secret = '87ivk3royi2z30lhzprgovhrocp8yq1g'

print("🔄 Updating Kite access token...")

try:
    # Generate new access token
    kite = KiteConnect(api_key=api_key)
    data = kite.generate_session(request_token, api_secret=api_secret)
    new_token = data['access_token']
    
    print(f"✅ New token generated: {new_token[:20]}...")
    
    # Update .env file
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    with open('.env', 'w') as f:
        for line in lines:
            if line.startswith('KITE_ACCESS_TOKEN='):
                f.write(f'KITE_ACCESS_TOKEN="{new_token}"\n')
            else:
                f.write(line)
    
    print("✅ .env file updated successfully")
    
    # Test connection
    print("🧪 Testing new connection...")
    kite.set_access_token(new_token)
    profile = kite.profile()
    
    print(f"🎉 Success! Connected as: {profile['user_name']}")
    print(f"🆔 User ID: {profile['user_id']}")
    print(f"📧 Email: {profile['email']}")
    
    print("\n✅ Authentication complete! You can now:")
    print("- Run: python quick_start_live.py")
    print("- Access live trading dashboard")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("Please ensure:")
    print("1. The request token is fresh (expires quickly)")
    print("2. API key and secret are correct")
    print("3. You have proper permissions on Kite Connect")

if __name__ == "__main__":
    pass  # Script runs directly