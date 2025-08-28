#!/usr/bin/env python3
"""
Immediate session fix for Breeze API
Use this to generate a new session token for live trading
"""

import os
import webbrowser
from dotenv import load_dotenv
import urllib.parse
from breeze_connect import BreezeConnect

def generate_new_session():
    """Generate new Breeze API session token"""
    load_dotenv()
    
    api_key = os.getenv("BREEZE_API_KEY")
    if api_key:
        api_key = api_key.strip('"')  # Remove any quotes
        
    api_secret = os.getenv("BREEZE_API_SECRET")
    if api_secret:
        api_secret = api_secret.strip('"')  # Remove any quotes
        
    client_code = os.getenv("ICICI_CLIENT_CODE")
    if client_code:
        client_code = client_code.strip('"')  # Remove any quotes
    
    if not all([api_key, api_secret, client_code]):
        print("❌ Missing credentials in .env file")
        missing = []
        if not api_key: missing.append("BREEZE_API_KEY")
        if not api_secret: missing.append("BREEZE_API_SECRET")
        if not client_code: missing.append("ICICI_CLIENT_CODE")
        print(f"Missing credentials: {', '.join(missing)}")
        print("Please update your .env file with the required credentials.")
        return False
    
    # Initialize BreezeConnect
    breeze = BreezeConnect(api_key=api_key)
    
    # Properly encode API key for URL (handle special characters)
    encoded_key = urllib.parse.quote_plus(api_key)
    session_url = f"https://api.icicidirect.com/apiuser/login?api_key={encoded_key}"
    
    print("🚨 URGENT: Session Token Required for Live Trading")
    print("=" * 50)
    print("\n📱 COMPLETE STEPS TO FIX:")
    print("\n🎯 STEP 1: Verify App Status")
    print("   - Go to https://api.icicidirect.com/apiuser/home")
    print("   - Click 'View Apps' tab")
    print("   - Ensure your app status is 'Active'")
    print("   - If inactive, activate it and wait 5-10 minutes")
    print("\n🎯 STEP 2: Use Developer Tools Method (Most Reliable)")
    print("   1. Open INCOGNITO/PRIVATE browser window")
    print("   2. Press F12 to open Developer Tools")
    print("   3. Go to 'Network' tab")
    print("   4. Open this URL:")
    print(f"      {session_url}")
    print("   5. Login with your ICICI Direct credentials")
    print("   6. Enter OTP when prompted")
    print("   7. After successful login, look in Network tab:")
    print("      - Payload → Form Data → 'API_Session' value")
    print("\n🎯 STEP 3: Alternative Token Locations")
    print("   - Check URL address bar: ends with '?apisession=XXXXX'")
    print("   - Check left sidebar of success page: 'API Session' value")
    print("\n⚠️  IMPORTANT:")
    print("   - Complete process within 5 minutes (OTP expiry)")
    print("   - Use Chrome/Firefox/Edge in incognito mode")
    print("   - Clear browser cache for api.icicidirect.com")
    print("   - Make sure your API key and secret are correct in .env file")
    print(f"   - Current API key being used: {api_key[:5]}...")
    print(f"   - Current client code: {client_code}")
    
    # Open browser automatically
    webbrowser.open(session_url)
    
    # Get the redirect URL or session token from user
    print("\n📋 How would you like to provide the session token?")
    print("1. Paste the complete redirected URL")
    print("2. Paste just the session token value")
    choice = input("Enter choice (1 or 2): ").strip()
    
    session_token = None
    
    if choice == "1":
        redirect_url = input("\n📋 Paste the redirected URL here: ").strip()
        
        if not redirect_url.startswith('http'):
            print("❌ Invalid URL format")
            return False
        
        # Extract session token from URL
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(redirect_url)
        query_params = parse_qs(parsed_url.query)
        
        session_token = query_params.get('apisession', [None])[0] or query_params.get('session_token', [None])[0] or query_params.get('API_Session', [None])[0]
        
        if not session_token:
            print("❌ Could not extract session token from URL")
            print("   URL should contain '?apisession=XXXXX' or similar")
            return False
            
    elif choice == "2":
        session_token = input("\n📋 Paste the session token value here: ").strip()
        
    else:
        print("❌ Invalid choice")
        return False
    
    print(f"Extracted session token: {session_token}")
    
    # Debugging: Print the type and value of session_token before use
    print(f"Debug: Type of session_token: {type(session_token)}")
    print(f"Debug: Value of session_token: '{session_token}'")

    if not session_token:
        return False
    
    # Comprehensive token testing
    print(f"\n🔍 Testing session token...")
    print(f"Token length: {len(session_token)}")
    print(f"Token preview: {session_token[:8]}...{session_token[-4:]}")
    
    # Test the new session with improved error handling
    try:
        breeze.user_id = client_code
        
        # Generate session with proper error handling
        session_result = breeze.generate_session(
            api_secret=api_secret, 
            session_token=session_token
        )
        
        print(f"Session generation result: {session_result}")
        
        # Test customer details with specific error handling
        customer = breeze.get_customer_details()
        print(f"Customer details response: {customer}")
        
        # Check for specific error messages
        customer_str = str(customer) if customer else ""
        
        if customer and 'Error' not in customer_str and 'Public Key does not exist' not in customer_str:
            print("✅ New session is working!")
            
            # Update .env file without quotes to avoid issues
            update_env_file(session_token)
            
            # Create verification script for future use
            create_verification_script(session_token)
            
            return True
        elif 'Public Key does not exist' in customer_str:
            print("❌ App not activated or API permissions missing")
            print("   Go to https://api.icicidirect.com/apiuser/home → View Apps → Activate your app")
            return False
        else:
            print("❌ New session failed validation")
            print(f"Response: {customer}")
            return False
            
    except Exception as e:
        print(f"❌ Session test failed: {e}")
        print("   Common causes:")
        print("   - App status not active")
        print("   - Token expired (5min limit)")
        print("   - API key encoding issues")
        return False

def update_env_file(new_session_token):
    """Update .env file with new session token"""
    env_path = '.env'
    
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    with open(env_path, 'w') as f:
        updated = False
        for line in lines:
            if line.startswith('BREEZE_SESSION_TOKEN='):
                f.write(f'BREEZE_SESSION_TOKEN={new_session_token}\n')
                updated = True
            else:
                f.write(line)
        
        if not updated:
            f.write(f'\nBREEZE_SESSION_TOKEN={new_session_token}\n')
    
    print("✅ .env file updated with new session token")
    print("🔄 Restart your trading system to use the new session")

def create_verification_script(session_token):
    """Create a simple verification script for quick testing"""
    script_content = f'''
import os
import sys
from breeze_connect import BreezeConnect
from dotenv import load_dotenv

def test_token(token=None):
    load_dotenv()
    api_key = os.getenv("BREEZE_API_KEY")
    if api_key:
        api_key = api_key.strip('"')  # Remove any quotes
        
    api_secret = os.getenv("BREEZE_API_SECRET")
    if api_secret:
        api_secret = api_secret.strip('"')  # Remove any quotes
        
    client_code = os.getenv("ICICI_CLIENT_CODE")
    if client_code:
        client_code = client_code.strip('"')  # Remove any quotes
    
    # Get token from argument, parameter, or env file
    if not token:
        token = sys.argv[1] if len(sys.argv) > 1 else os.getenv("BREEZE_SESSION_TOKEN")
        
    session_token = token or "{session_token}"
    if not session_token:
        print("❌ Session token is empty")
        return False
        
    print(f"Testing with API Key: {{api_key[:5]}}... and Session Token: {{session_token[:5] if len(session_token) > 5 else session_token}}...")
    
    try:
        breeze = BreezeConnect(api_key=api_key)
        breeze.user_id = client_code
        print("✅ BreezeConnect initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize BreezeConnect: {{e}}")
        return False
        
    try:
        print("Attempting to generate session...")
        result = breeze.generate_session(api_secret=api_secret, session_token=session_token)
        print(f"Session generation result: {{result}}")
        
        print("Fetching customer details...")
        customer = breeze.get_customer_details()
        print(f"Customer details: {{customer}}")
        
        if customer and 'Error' not in str(customer) and 'Public Key does not exist' not in str(customer):
            print("✅ Session token is VALID!")
            return True
        else:
            print("❌ Session token is INVALID!")
            print("Response:", customer)
            return False
    except Exception as e:
        print(f"❌ Error: {{e}}")
        print("Please check if your API credentials are correct and try again.")
        return False

if __name__ == "__main__":
    test_token()
'''
    
    with open("verify_session.py", "w") as f:
        f.write(script_content)
    
    print("✅ Created verify_session.py for quick token testing")
    print("   Run: python verify_session.py [TOKEN]")
    return True

if __name__ == "__main__":
    generate_new_session()