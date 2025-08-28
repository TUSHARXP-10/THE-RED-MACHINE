#!/usr/bin/env python3
"""
One-Command Kite Authentication Fix
Resolves authentication issues with step-by-step guidance
"""

import os
import sys
import webbrowser
from kiteconnect import KiteConnect
from dotenv import load_dotenv
import time

def fix_kite_auth():
    """Complete authentication fix in one command"""
    load_dotenv()
    
    print("🔄 Kite API Authentication Fix")
    print("=" * 50)
    
    # Get credentials
    api_key = os.getenv("KITE_API_KEY", "").strip('"')
    api_secret = os.getenv("KITE_API_SECRET", "").strip('"')
    
    if not api_key or not api_secret:
        print("❌ Missing API credentials in .env file")
        print("Please ensure .env contains:")
        print("KITE_API_KEY=your_key")
        print("KITE_API_SECRET=your_secret")
        return
    
    print(f"✅ API Key: {api_key[:8]}...")
    print(f"✅ API Secret: {api_secret[:8]}...")
    
    # Generate login URL
    kite = KiteConnect(api_key=api_key)
    login_url = kite.login_url()
    
    print(f"\n🔗 Login URL ready: {login_url}")
    print("\n📋 Follow these steps:")
    print("1. Opening browser for Kite login...")
    
    # Open browser
    try:
        webbrowser.open(login_url)
        print("🌐 Browser opened! Please login...")
    except:
        print("📝 Please manually open this URL:")
        print(login_url)
    
    print("\n2. After successful login, you'll see a localhost URL")
    print("3. Copy the request_token parameter from the URL")
    print("\nExample: https://localhost/?request_token=ABC123XYZ")
    
    # Get request token
    request_token = input("\n🔑 Enter request_token: ").strip()
    
    if not request_token:
        print("❌ No token provided")
        return
    
    # Extract just the token if full URL provided
    if "request_token=" in request_token:
        request_token = request_token.split("request_token=")[1].split("&")[0]
    
    try:
        # Generate new access token
        print("\n🔄 Generating new access token...")
        data = kite.generate_session(request_token, api_secret=api_secret)
        new_token = data["access_token"]
        
        # Update .env file
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        with open('.env', 'w') as f:
            for line in lines:
                if line.startswith('KITE_ACCESS_TOKEN='):
                    f.write(f'KITE_ACCESS_TOKEN="{new_token}"\n')
                else:
                    f.write(line)
        
        print(f"✅ Access token updated!")
        print(f"📝 New token: {new_token[:20]}...")
        
        # Test connection
        print("\n🧪 Testing new connection...")
        kite.set_access_token(new_token)
        profile = kite.profile()
        print(f"✅ Success! Connected as: {profile['user_name']}")
        print(f"✅ Public ID: {profile['user_id']}")
        
        print("\n🎉 Authentication fixed!")
        print("\nNext steps:")
        print("1. Run: python quick_start_live.py")
        print("2. Or restart your dashboard")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("- Ensure API key/secret are correct")
        print("- Use a fresh request token (expires quickly)")
        print("- Check Kite Connect app permissions")

if __name__ == "__main__":
    fix_kite_auth()