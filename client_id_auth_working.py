#!/usr/bin/env python3
"""
Working Client ID Authentication for GSS065
Uses exact API credentials from .env file
"""

import os
from kiteconnect import KiteConnect
import webbrowser
from dotenv import load_dotenv

def setup_authentication():
    """Complete authentication setup"""
    load_dotenv()
    
    # Use exact credentials from .env
    api_key = os.getenv('KITE_API_KEY', 'q23715gf6tzjmyf5')
    api_secret = os.getenv('KITE_API_SECRET', '87ivk3royi2z30lhzprgovhrocp8yq1g')
    client_id = os.getenv('ZERODHA_CLIENT_ID', 'GSS065')
    
    print("Kite Connect Authentication Setup")
    print("=" * 35)
    print(f"Client ID: {client_id}")
    print(f"API Key: {api_key}")
    print(f"API Secret: {api_secret[:8]}...")
    
    kite = KiteConnect(api_key=api_key)
    
    # Generate login URL
    login_url = kite.login_url()
    print(f"\nLogin URL: {login_url}")
    
    print("\nInstructions:")
    print("1. Click the login URL above")
    print("2. Login with your Zerodha account")
    print("3. Ensure you see Client ID: GSS065")
    print("4. Complete authentication")
    print("5. Copy request_token from redirect URL")
    
    # Open browser
    webbrowser.open(login_url)
    
    # Get fresh request token
    request_token = input("\nEnter request_token: ").strip()
    
    if not request_token:
        print("No request token provided")
        return False
    
    try:
        # Generate session with exact API secret
        print("\nGenerating session...")
        session_data = kite.generate_session(request_token, api_secret)
        
        new_access_token = session_data['access_token']
        print(f"✅ Success! New access token: {new_access_token}")
        
        # Verify profile
        kite.set_access_token(new_access_token)
        profile = kite.profile()
        
        print(f"\nProfile verified:")
        print(f"Name: {profile.get('user_name')}")
        print(f"Email: {profile.get('email')}")
        print(f"Client ID: {profile.get('user_id')}")
        
        # Update .env file
        update_env_file(new_access_token)
        
        # Test SENSEX access
        test_market_data(kite)
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("Check your API secret and try again")
        return False

def update_env_file(new_token):
    """Update .env with new access token"""
    try:
        with open('.env', 'r') as f:
            content = f.read()
        
        # Replace existing access token
        old_token = os.getenv('KITE_ACCESS_TOKEN', '')
        new_content = content.replace(
            f"KITE_ACCESS_TOKEN='{old_token}'",
            f"KITE_ACCESS_TOKEN='{new_token}'"
        )
        
        with open('.env', 'w') as f:
            f.write(new_content)
        
        print("✅ .env file updated with new access token")
        
    except Exception as e:
        print(f"Could not update .env: {e}")

def test_market_data(kite):
    """Test SENSEX market data access"""
    try:
        # Test SENSEX quote
        quote = kite.quote(["NSE:SENSEX"])
        print("✅ SENSEX data access working!")
        print(f"Current SENSEX: {quote['NSE:SENSEX']['last_price']}")
        
        # Test positions
        positions = kite.positions()
        print("✅ Trading permissions confirmed!")
        
    except Exception as e:
        print(f"⚠️ Market data test: {e}")

if __name__ == "__main__":
    print("Starting Client ID Authentication...")
    
    success = setup_authentication()
    
    if success:
        print("\n🎉 Authentication complete!")
        print("Run: python START_LIVE_TRADING.py")
    else:
        print("\n❌ Authentication failed")
        print("Check your Kite Connect app settings")