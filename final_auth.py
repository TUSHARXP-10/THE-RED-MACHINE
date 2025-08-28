#!/usr/bin/env python3
"""
Final Kite Connect Authentication with Client ID GSS065
"""

import os
from kiteconnect import KiteConnect
import webbrowser
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    api_key = os.getenv('KITE_API_KEY', 'q23715gf6tzjmyf5')
    client_id = os.getenv('ZERODHA_CLIENT_ID', 'GSS065')
    
    print("Kite Connect Authentication")
    print("=" * 30)
    print(f"Client ID: {client_id}")
    print(f"API Key: {api_key}")
    
    kite = KiteConnect(api_key=api_key)
    login_url = kite.login_url()
    
    print(f"\nLogin URL: {login_url}")
    print("\nSteps:")
    print("1. Open the URL above")
    print("2. Login with your demat account")
    print("3. Copy request_token from redirect URL")
    
    webbrowser.open(login_url)
    
    request_token = input("\nEnter request_token: ").strip()
    api_secret = input("Enter API secret: ").strip()
    
    try:
        data = kite.generate_session(request_token, api_secret)
        print(f"\nSuccess! Access Token: {data['access_token']}")
        
        # Update .env file
        with open('.env', 'r') as f:
            content = f.read()
        
        new_content = content.replace(
            f"KITE_ACCESS_TOKEN={os.getenv('KITE_ACCESS_TOKEN')}",
            f"KITE_ACCESS_TOKEN={data['access_token']}"
        )
        
        with open('.env', 'w') as f:
            f.write(new_content)
        
        print("Access token saved to .env")
        print("Run: python START_LIVE_TRADING.py")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()