#!/usr/bin/env python3
"""
Comprehensive session fix for ICICI Breeze API
Implements all troubleshooting steps from the guide
"""

import os
import webbrowser
import time
from dotenv import load_dotenv
import urllib.parse
from breeze_connect import BreezeConnect

def check_app_status():
    """Guide user to check app status"""
    print("\n🎯 STEP 1: Verify App Status")
    print("=" * 40)
    print("1. Go to https://api.icicidirect.com/apiuser/home")
    print("2. Click 'View Apps' tab")
    print("3. Check if your app status shows 'Active'")
    print("4. If 'Inactive' or 'Deactivated', click to activate")
    print("5. Wait 5-10 minutes after activation")
    
    input("\nPress Enter after verifying app status is 'Active'...")
    return True

def generate_session_url():
    """Generate properly encoded session URL"""
    load_dotenv()
    
    api_key = os.getenv("BREEZE_API_KEY")
    if not api_key:
        print("❌ BREEZE_API_KEY not found in .env")
        return None
    
    # Handle special characters in API key
    encoded_key = urllib.parse.quote_plus(api_key)
    session_url = f"https://api.icicidirect.com/apiuser/login?api_key={encoded_key}"
    
    return session_url

def extract_session_token():
    """Multiple methods to extract session token"""
    print("\n🎯 STEP 2: Extract Session Token")
    print("=" * 40)
    print("Choose extraction method:")
    print("1. Developer Tools (Most Reliable)")
    print("2. URL Address Bar")
    print("3. Left Sidebar")
    
    method = input("Enter method (1-3): ").strip()
    
    if method == "1":
        print("\n📱 Developer Tools Method:")
        print("1. Open INCOGNITO browser window")
        print("2. Press F12 to open Developer Tools")
        print("3. Go to 'Network' tab")
        print("4. Login with your credentials")
        print("5. After OTP, look for:")
        print("   - Network tab → Payload → Form Data → 'API_Session'")
        
    elif method == "2":
        print("\n📱 URL Address Bar Method:")
        print("1. After successful login")
        print("2. Check URL for: localhost:8501/?apisession=XXXXX")
        
    elif method == "3":
        print("\n📱 Left Sidebar Method:")
        print("1. After successful login")
        print("2. Check left sidebar for 'API Session' value")
    
    # Get token
    token = input("\n📋 Enter the session token: ").strip()
    return token

def validate_token_format(token):
    """Validate token format"""
    if not token:
        print("❌ Empty token provided")
        return False
    
    if len(token) < 5:
        print("❌ Token too short")
        return False
    
    return True

def test_session_immediately(token):
    """Test session token immediately"""
    load_dotenv()
    
    api_key = os.getenv("BREEZE_API_KEY")
    api_secret = os.getenv("BREEZE_API_SECRET")
    client_code = os.getenv("ICICI_CLIENT_CODE")
    
    if not all([api_key, api_secret, client_code]):
        print("❌ Missing credentials in .env")
        return False
    
    try:
        breeze = BreezeConnect(api_key=api_key)
        breeze.user_id = client_code
        
        print(f"\n🔍 Testing token: {token[:8]}...{token[-4:]}")
        
        # Generate session
        result = breeze.generate_session(
            api_secret=api_secret,
            session_token=token
        )
        
        print(f"Session generation: {result}")
        
        # Test customer details
        customer = breeze.get_customer_details()
        
        # Check response
        customer_str = str(customer) if customer else ""
        
        if customer and 'Error' not in customer_str:
            if 'Public Key does not exist' in customer_str:
                print("❌ App not activated - Go to View Apps and activate")
                return False
            else:
                print("✅ Session token is VALID!")
                return True
        else:
            print("❌ Session token is INVALID!")
            print(f"Response: {customer}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing token: {e}")
        return False

def update_env_file(token):
    """Update .env file"""
    env_path = '.env'
    
    try:
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        with open(env_path, 'w') as f:
            updated = False
            for line in lines:
                if line.startswith('BREEZE_SESSION_TOKEN='):
                    f.write(f'BREEZE_SESSION_TOKEN={token}\n')
                    updated = True
                else:
                    f.write(line)
            
            if not updated:
                f.write(f'\nBREEZE_SESSION_TOKEN={token}\n')
        
        print("✅ .env file updated!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env: {e}")
        return False

def main():
    """Main function implementing all troubleshooting steps"""
    print("🚨 ICICI Breeze API Session Fix - Complete Guide")
    print("=" * 50)
    
    # Step 1: Check app status
    check_app_status()
    
    # Step 2: Generate session URL
    session_url = generate_session_url()
    if not session_url:
        return False
    
    print(f"\n🌐 Session URL: {session_url}")
    
    # Open browser
    open_browser = input("\nOpen browser automatically? (y/n): ").strip().lower()
    if open_browser == 'y':
        webbrowser.open(session_url)
    
    print("\n⏰ IMPORTANT: Complete within 5 minutes (OTP expiry)")
    
    # Step 3: Extract token
    token = extract_session_token()
    
    # Validate token
    if not validate_token_format(token):
        return False
    
    # Step 4: Test immediately
    if test_session_immediately(token):
        # Update .env
        if update_env_file(token):
            print("\n🎉 SUCCESS! Session token is working!")
            print("🔄 Restart your trading system to use the new session")
            return True
    else:
        print("\n❌ Failed to validate session token")
        print("Try again with a fresh browser session")
        return False

if __name__ == "__main__":
    main()