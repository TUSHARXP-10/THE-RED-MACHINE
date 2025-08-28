#!/usr/bin/env python3
"""
Comprehensive Kite API Setup Verification
"""

import os
import re
import webbrowser
from kiteconnect import KiteConnect

def check_env_file():
    """Check .env file for correct formatting"""
    print("🔍 Checking .env file...")
    
    try:
        with open('.env', 'r') as f:
            content = f.read()
        
        # Check for proper API key format
        key_match = re.search(r'KITE_API_KEY=["\']?([^"\'\s]+)["\']?', content)
        secret_match = re.search(r'KITE_API_SECRET=["\']?([^"\'\s]+)["\']?', content)
        
        if key_match and secret_match:
            key = key_match.group(1).strip("'\"")
            secret = secret_match.group(1).strip("'\"")
            
            print(f"✅ API Key found: {key}")
            print(f"✅ API Secret found: {len(secret) * '*'}")
            
            # Validate format
            if len(key) == 20 and len(secret) == 32:
                print("✅ API credentials format appears correct")
                return key, secret
            else:
                print("⚠️  API credentials format seems unusual")
                return key, secret
        else:
            print("❌ API credentials not found in .env")
            return None, None
            
    except Exception as e:
        print(f"❌ Error reading .env: {e}")
        return None, None

def test_api_credentials(api_key, api_secret):
    """Test API credentials directly"""
    print("\n🧪 Testing API credentials...")
    
    try:
        kite = KiteConnect(api_key=api_key)
        login_url = kite.login_url()
        print(f"✅ Login URL generated: {login_url}")
        return login_url
    except Exception as e:
        print(f"❌ API credential error: {e}")
        return None

def get_fresh_token():
    """Interactive fresh token generation"""
    print("\n🎯 Getting fresh request token...")
    
    # Get credentials
    api_key, api_secret = check_env_file()
    if not api_key or not api_secret:
        print("❌ Cannot proceed without valid API credentials")
        return False
    
    # Test credentials
    login_url = test_api_credentials(api_key, api_secret)
    if not login_url:
        return False
    
    # Open browser
    print(f"\n🌐 Opening: {login_url}")
    webbrowser.open(login_url)
    
    print("\n📋 Please:")
    print("1. Login with your Zerodha account")
    print("2. Authorize the app")
    print("3. After redirect, copy the full URL")
    
    redirect_url = input("\nPaste the redirect URL here: ").strip()
    
    # Extract request token
    token_match = re.search(r'request_token=([^&\s]+)', redirect_url)
    if not token_match:
        print("❌ Could not find request token in URL")
        return False
    
    request_token = token_match.group(1)
    print(f"✅ Request token: {request_token}")
    
    # Generate access token
    try:
        kite = KiteConnect(api_key=api_key)
        data = kite.generate_session(request_token, api_secret=api_secret)
        new_token = data['access_token']
        
        # Update .env
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        with open('.env', 'w') as f:
            for line in lines:
                if line.startswith('KITE_ACCESS_TOKEN='):
                    f.write(f'KITE_ACCESS_TOKEN="{new_token}"\n')
                else:
                    f.write(line)
        
        print(f"✅ Access token updated successfully!")
        
        # Test connection
        kite.set_access_token(new_token)
        profile = kite.profile()
        print(f"🎉 Success! Connected as: {profile['user_name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Token generation failed: {e}")
        return False

def main():
    print("🔧 Kite API Setup Verification")
    print("=" * 50)
    
    # Check current setup
    key, secret = check_env_file()
    if key and secret:
        test_api_credentials(key, secret)
    
    # Get fresh token
    print("\n" + "=" * 50)
    success = get_fresh_token()
    
    if success:
        print("\n🚀 Ready for live trading!")
        print("Next: python quick_start_live.py")
    else:
        print("\n❌ Please check your Kite Connect app settings")

if __name__ == "__main__":
    main()