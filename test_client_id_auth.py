#!/usr/bin/env python3
"""
Enhanced Kite Connect Authentication Test with Client ID Integration
This script tests the authentication flow using Client ID GSS065 to resolve email mismatch issues.
"""

import os
from kiteconnect import KiteConnect
import webbrowser
from dotenv import load_dotenv

def load_credentials():
    """Load API credentials from .env file"""
    load_dotenv()
    
    return {
        'api_key': os.getenv('KITE_API_KEY', 'q23715gf6tzjmyf5'),
        'api_secret': os.getenv('KITE_API_SECRET'),
        'client_id': os.getenv('ZERODHA_CLIENT_ID', 'GSS065')
    }

def test_client_id_auth():
    """Test authentication with Client ID integration"""
    creds = load_credentials()
    
    print("🔧 Testing Client ID Authentication...")
    print(f"📋 Client ID: {creds['client_id']}")
    print(f"🔑 API Key: {creds['api_key']}")
    
    # Initialize Kite Connect
    kite = KiteConnect(api_key=creds['api_key'])
    
    # Enhanced login URL with client_id parameter
    login_url = f"{kite.login_url()}&client_id={creds['client_id']}"
    
    print(f"\n🔗 Enhanced Login URL: {login_url}")
    print("\n📋 Instructions:")
    print("1. Open the login URL above")
    print("2. Login with your demat account email: tusharchandane51@gmail.com")
    print("3. Verify that Client ID GSS065 is displayed during login")
    print("4. Complete authentication")
    print("5. Copy the 'request_token' from the redirect URL")
    
    # Open browser
    webbrowser.open(login_url)
    
    # Get request token
    request_token = input("\n📝 Enter request_token: ").strip()
    
    if not request_token:
        print("❌ No request token provided")
        return False
    
    try:
        # Generate session
        print("\n🔐 Generating session...")
        data = kite.generate_session(request_token, api_secret=creds['api_secret'])
        
        # Set access token
        kite.set_access_token(data["access_token"])
        
        # Verify profile and client ID
        profile = kite.profile()
        
        print(f"\n✅ Authentication Successful!")
        print(f"👤 User: {profile.get('user_name')}")
        print(f"📧 Email: {profile.get('email')}")
        print(f"🏢 Client ID: {profile.get('user_id')}")
        
        # Verify client ID matches
        if profile.get('user_id') == creds['client_id']:
            print(f"✅ Client ID {creds['client_id']} verified successfully!")
            
            # Test trading permissions
            try:
                positions = kite.positions()
                print("✅ Trading permissions confirmed!")
                
                # Test SENSEX data access
                try:
                    sensex_quote = kite.quote(["NSE:BANKNIFTY"])
                    print("✅ Market data access working!")
                    
                    # Save new access token
                    update_env_file(data["access_token"])
                    
                    return True
                    
                except Exception as e:
                    print(f"⚠️ Market data test: {e}")
                    
            except Exception as e:
                print(f"⚠️ Trading permissions test: {e}")
                
        else:
            print(f"⚠️ Client ID mismatch - Expected: {creds['client_id']}, Got: {profile.get('user_id')}")
            
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        
    return False

def update_env_file(new_access_token):
    """Update .env file with new access token"""
    try:
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            if line.startswith('KITE_ACCESS_TOKEN='):
                new_lines.append(f'KITE_ACCESS_TOKEN={new_access_token}\n')
            else:
                new_lines.append(line)
        
        with open('.env', 'w') as f:
            f.writelines(new_lines)
            
        print("✅ .env file updated with new access token")
        
    except Exception as e:
        print(f"⚠️ Could not update .env file: {e}")

def quick_verification():
    """Quick verification of current setup"""
    creds = load_credentials()
    
    print("\n📊 Current Setup Verification:")
    print(f"API Key: {'✅ Set' if creds['api_key'] else '❌ Missing'}")
    print(f"Client ID: {'✅ Set' if creds['client_id'] else '❌ Missing'}")
    print(f"API Secret: {'✅ Set' if creds['api_secret'] else '❌ Missing'}")
    
    return creds

if __name__ == "__main__":
    print("🚀 Client ID Authentication Test")
    print("=" * 50)
    
    # Quick verification
    creds = quick_verification()
    
    # Run authentication test
    success = test_client_id_auth()
    
    if success:
        print("\n🎉 Client ID authentication successful!")
        print("🔄 You can now start live trading with START_LIVE_TRADING.py")
    else:
        print("\n❌ Client ID authentication failed")
        print("🔍 Check your credentials and try again")