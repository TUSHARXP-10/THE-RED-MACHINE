#!/usr/bin/env python3
"""
Complete Kite Authentication Fix
"""

import os
import webbrowser
from kiteconnect import KiteConnect

def verify_credentials():
    """Verify API credentials are correct"""
    api_key = os.getenv('KITE_API_KEY', 'q23715gf6tzjmyf5')
    api_secret = os.getenv('KITE_API_SECRET', '87ivk3royi2z30lhzprgovhrocp8yq1g')
    
    print("🔍 Verifying Kite API credentials...")
    print(f"API Key: {api_key}")
    print(f"API Secret: {len(api_secret) * '*'}")
    
    return api_key, api_secret

def generate_login_url():
    """Generate fresh login URL"""
    api_key = 'q23715gf6tzjmyf5'
    kite = KiteConnect(api_key=api_key)
    
    login_url = kite.login_url()
    print(f"\n🌐 Login URL: {login_url}")
    print("\n📋 Steps:")
    print("1. Click the link above or copy-paste in browser")
    print("2. Login with your Zerodha credentials")
    print("3. Authorize the app")
    print("4. Copy the request_token from the redirect URL")
    
    return login_url

def update_token_manually():
    """Interactive token update"""
    print("\n🔄 Manual Token Update")
    request_token = input("Enter the new request_token from redirect URL: ").strip()
    
    if not request_token:
        print("❌ No token provided")
        return False
    
    try:
        api_key = 'q23715gf6tzjmyf5'
        api_secret = '87ivk3royi2z30lhzprgovhrocp8yq1g'
        
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
        
        print(f"✅ Token updated successfully!")
        
        # Test
        kite.set_access_token(new_token)
        profile = kite.profile()
        print(f"✅ Connected as: {profile['user_name']}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🎯 Kite Authentication Fix")
    print("=" * 50)
    
    # Verify credentials
    verify_credentials()
    
    # Generate login URL
    login_url = generate_login_url()
    
    # Open browser
    print("\n🚀 Opening browser...")
    webbrowser.open(login_url)
    
    # Update token
    success = update_token_manually()
    
    if success:
        print("\n🎉 Authentication complete!")
        print("Next steps:")
        print("- Run: python quick_start_live.py")
        print("- Or: python live_dashboard.py")
    else:
        print("\n❌ Try again with a fresh request token")

if __name__ == "__main__":
    main()