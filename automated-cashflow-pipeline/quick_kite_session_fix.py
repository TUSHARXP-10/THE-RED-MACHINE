#!/usr/bin/env python3
"""
Quick Kite Session Fix Tool
Improved version with better error handling and user guidance
"""

import os
import webbrowser
import sys
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

def load_env():
    """Load environment variables"""
    load_dotenv()
    return {
        'api_key': os.getenv('KITE_API_KEY'),
        'api_secret': os.getenv('KITE_API_SECRET'),
        'redirect_url': os.getenv('KITE_REDIRECT_URL')
    }

def check_credentials(creds):
    """Check if all required credentials are present"""
    missing = []
    for key, value in creds.items():
        if not value:
            missing.append(key.upper())
    
    if missing:
        print(f"❌ Missing credentials: {', '.join(missing)}")
        print("Please add these to your .env file")
        return False
    return True

def extract_request_token(url):
    """Extract request token from redirect URL with improved error handling"""
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        if 'request_token' in params:
            return params['request_token'][0]
        else:
            print("❌ No request_token found in URL")
            print("\n💡 This usually happens when:")
            print("   1. You pasted the login page URL instead of the redirect URL")
            print("   2. The redirect didn't complete properly")
            print("   3. Your Kite app's redirect URI is not set correctly")
            return None
    except Exception as e:
        print(f"❌ Error parsing URL: {e}")
        return None

def generate_login_url(api_key):
    """Generate Kite login URL"""
    return f"https://kite.zerodha.com/connect/login?api_key={api_key}&v=3"

def generate_access_token(api_key, api_secret, request_token):
    """Generate access token using request token"""
    try:
        import requests
        
        url = "https://api.kite.trade/session/token"
        payload = {
            'api_key': api_key,
            'request_token': request_token,
            'api_secret': api_secret
        }
        
        response = requests.post(url, data=payload)
        
        if response.status_code == 200:
            data = response.json()
            return data['data']['access_token']
        else:
            print(f"❌ Failed to generate access token: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error generating access token: {e}")
        return None

def update_env_file(access_token):
    """Update .env file with new access token"""
    try:
        env_path = '.env'
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update or add KITE_ACCESS_TOKEN
        token_found = False
        for i, line in enumerate(lines):
            if line.startswith('KITE_ACCESS_TOKEN='):
                lines[i] = f'KITE_ACCESS_TOKEN={access_token}\n'
                token_found = True
                break
        
        if not token_found:
            lines.append(f'KITE_ACCESS_TOKEN={access_token}\n')
        
        with open(env_path, 'w') as f:
            f.writelines(lines)
        
        print("✅ Updated .env file with new access token")
        return True
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

def test_connection(api_key, access_token):
    """Test the connection to Kite API"""
    try:
        from kiteconnect import KiteConnect
        
        kite = KiteConnect(api_key=api_key)
        kite.set_access_token(access_token)
        
        # Test by getting user profile
        profile = kite.profile()
        print(f"✅ Connection successful! Welcome {profile['user_name']}")
        return True
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Quick Kite Session Fix Tool")
    print("=" * 50)
    
    # Load credentials
    creds = load_env()
    
    if not check_credentials(creds):
        sys.exit(1)
    
    print("✅ All credentials found")
    print(f"API Key: {creds['api_key'][:8]}...")
    print(f"Redirect URL: {creds['redirect_url']}")
    
    # Generate login URL
    login_url = generate_login_url(creds['api_key'])
    
    print("\n🔍 Access Token Generation Steps:")
    print("1. Opening login URL in your default browser")
    print("2. Login with your Zerodha credentials")
    print("3. After successful login, you'll be redirected")
    print("4. Copy the entire redirect URL from your browser")
    print("\n💡 The redirect URL should contain 'request_token='")
    
    # Open browser
    try:
        webbrowser.open(login_url)
        print("✅ Opened login URL in browser")
    except Exception as e:
        print(f"⚠️ Could not open browser automatically: {e}")
        print(f"Please manually visit: {login_url}")
    
    # Get redirect URL from user
    print("\n" + "=" * 50)
    redirect_url = input("After logging in, please provide the redirect URL: ").strip()
    
    # Extract request token
    request_token = extract_request_token(redirect_url)
    if not request_token:
        print("\n❌ Failed to extract request token. Please try again.")
        sys.exit(1)
    
    print(f"✅ Extracted request_token: {request_token[:8]}...")
    
    # Generate access token
    access_token = generate_access_token(
        creds['api_key'], 
        creds['api_secret'], 
        request_token
    )
    
    if not access_token:
        print("❌ Failed to generate access token")
        sys.exit(1)
    
    print(f"✅ Generated access token: {access_token[:8]}...")
    
    # Update .env file
    if update_env_file(access_token):
        # Test connection
        if test_connection(creds['api_key'], access_token):
            print("\n🎉 Success! Your Kite session is now active.")
            print("You can now run your trading system with Kite Connect.")
        else:
            print("\n⚠️ Access token saved but connection test failed.")
            print("Please check your credentials and try again.")
    else:
        print("\n❌ Failed to save access token to .env file")

if __name__ == '__main__':
    main()