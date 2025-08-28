#!/usr/bin/env python3
"""
Kite API Session Refresh Tool
Fixes authentication issues with comprehensive validation
"""

import os
import sys
import json
import time
from datetime import datetime
from kiteconnect import KiteConnect
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KiteSessionFix:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("KITE_API_KEY", "").strip('"')
        self.api_secret = os.getenv("KITE_API_SECRET", "").strip('"')
        self.access_token = os.getenv("KITE_ACCESS_TOKEN", "").strip('"')
        
    def check_env_file(self):
        """Check if .env file exists and has required credentials"""
        if not os.path.exists(".env"):
            print("❌ .env file not found")
            return False
            
        required_vars = ["KITE_API_KEY", "KITE_API_SECRET", "KITE_ACCESS_TOKEN"]
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing:
            print(f"❌ Missing variables: {', '.join(missing)}")
            return False
            
        print("✅ All required variables found")
        return True
    
    def validate_session(self):
        """Validate current Kite session"""
        try:
            if not all([self.api_key, self.access_token]):
                return False, "Missing API key or access token"
                
            kite = KiteConnect(api_key=self.api_key)
            kite.set_access_token(self.access_token)
            profile = kite.profile()
            
            return True, f"Valid session for {profile.get('user_name', 'Unknown')}"
            
        except Exception as e:
            return False, str(e)
    
    def generate_login_url(self):
        """Generate Kite Connect login URL"""
        if not self.api_key:
            return None, "API key not found"
            
        kite = KiteConnect(api_key=self.api_key)
        return kite.login_url(), None
    
    def refresh_access_token(self, request_token):
        """Refresh access token using request token"""
        try:
            if not all([self.api_key, self.api_secret]):
                return False, "API key or secret missing"
                
            kite = KiteConnect(api_key=self.api_key)
            data = kite.generate_session(request_token, api_secret=self.api_secret)
            
            # Update .env file manually
            with open('.env', 'r') as f:
                lines = f.readlines()
            
            with open('.env', 'w') as f:
                for line in lines:
                    if line.startswith('KITE_ACCESS_TOKEN='):
                        f.write(f'KITE_ACCESS_TOKEN="{data["access_token"]}"\n')
                    else:
                        f.write(line)
            
            return True, data["access_token"]
            
        except Exception as e:
            return False, str(e)

def main():
    """Interactive session fix"""
    print("🔄 Kite API Session Fix")
    print("=" * 40)
    
    fix = KiteSessionFix()
    
    # Check environment
    if not fix.check_env_file():
        print("\n📝 Please ensure your .env file contains:")
        print("KITE_API_KEY=your_api_key")
        print("KITE_API_SECRET=your_api_secret")
        print("KITE_ACCESS_TOKEN=your_access_token")
        return
    
    # Validate current session
    print("\n🔍 Validating current session...")
    valid, message = fix.validate_session()
    
    if valid:
        print(f"✅ {message}")
        return
    else:
        print(f"❌ {message}")
    
    # Generate login URL
    login_url, error = fix.generate_login_url()
    if error:
        print(f"❌ {error}")
        return
    
    print(f"\n🔗 Login URL: {login_url}")
    print("\n📋 Steps:")
    print("1. Open the URL above in your browser")
    print("2. Login with your Zerodha credentials")
    print("3. After login, you'll be redirected to localhost")
    print("4. Copy the 'request_token' parameter from the URL")
    
    request_token = input("\nEnter request_token: ").strip()
    
    if not request_token:
        print("❌ No token provided")
        return
    
    # Refresh token
    success, token = fix.refresh_access_token(request_token)
    
    if success:
        print(f"✅ Token refreshed successfully!")
        print(f"📝 New token: {token[:20]}...")
        
        # Revalidate
        valid, message = fix.validate_session()
        if valid:
            print("🎉 Session fixed!")
        else:
            print(f"⚠️ Validation failed: {message}")
    else:
        print(f"❌ Failed to refresh token: {token}")

if __name__ == "__main__":
    main()