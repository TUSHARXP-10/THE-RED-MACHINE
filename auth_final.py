#!/usr/bin/env python3
"""
Final Client ID Authentication with Kite Connect
Uses Client ID GSS065 for authentication
"""

import os
from kiteconnect import KiteConnect
import webbrowser
from dotenv import load_dotenv

def load_credentials():
    """Load credentials from .env"""
    load_dotenv()
    return {
        'api_key': os.getenv('KITE_API_KEY'),
        'api_secret': os.getenv('KITE_API_SECRET'),
        'client_id': os.getenv('ZERODHA_CLIENT_ID')
    }

def authenticate():
    """Complete authentication flow"""
    creds = load_credentials()
    
    print("🚀 Kite Connect Authentication")
    print(f"Client ID: {creds['client_id']}")
    print(f"API Key: {creds['api_key']}")
    
    kite = KiteConnect(api_key=creds['api_key'])
    login_url = kite.login_url()
    
    print(f"\n🔗 Login URL: {login_url}")
    print("\n1. Open URL in browser")
    print("2. Login with demat account")
    print("3. Copy request_token from redirect")
    
    webbrowser.open(login_url)
    
    request_token = input("\n📝 Enter request_token: ").strip()
    
    try:
        data = kite.generate_session(request_token, creds['api_secret'])
        kite.set_access_token(data['access_token'])
        
        profile = kite.profile()
        print(f"\n✅ Success!")
        print(f"Name: {profile['user_name']}")
        print(f"Email: {profile['email']}")
        print(f"Client ID: {profile['user_id']}")
        
        # Save token
        with open('.env', 'r') as f:
            content = f.read()
        
        new_content = content.replace(
            f"KITE_ACCESS_TOKEN={os.getenv('KITE_ACCESS_TOKEN')}",
            f"KITE_ACCESS_TOKEN={data['access_token']}"
        )
        
        with open('.env', 'w') as f:
            f.write(new_content)
        
        print("✅ Access token saved")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    authenticate()