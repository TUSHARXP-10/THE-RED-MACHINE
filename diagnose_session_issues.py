#!/usr/bin/env python3
"""
Diagnostic script for ICICI Breeze API session issues
Quick checks for common problems
"""

import os
from dotenv import load_dotenv
from breeze_connect import BreezeConnect
import urllib.parse

def check_credentials():
    """Check if all required credentials are present"""
    load_dotenv()
    
    required_vars = [
        "BREEZE_API_KEY",
        "BREEZE_API_SECRET", 
        "ICICI_CLIENT_CODE",
        "BREEZE_SESSION_TOKEN"
    ]
    
    print("🔍 Checking credentials...")
    missing = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        else:
            masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else value
            print(f"✅ {var}: {masked_value}")
    
    if missing:
        print(f"❌ Missing: {', '.join(missing)}")
        return False
    
    return True

def test_api_key_encoding():
    """Test API key for special characters"""
    load_dotenv()
    api_key = os.getenv("BREEZE_API_KEY")
    
    if not api_key:
        print("❌ No API key found")
        return False
    
    special_chars = ['(', ')', '+', '!', '#', '=', '@', '$', '%', '^', '&', '*']
    found_chars = [char for char in special_chars if char in api_key]
    
    if found_chars:
        print(f"⚠️  API key contains special characters: {found_chars}")
        encoded = urllib.parse.quote_plus(api_key)
        print(f"   Encoded: {encoded}")
        return True
    else:
        print("✅ API key has no problematic special characters")
        return True

def test_basic_connection():
    """Test basic API connection"""
    load_dotenv()
    
    api_key = os.getenv("BREEZE_API_KEY")
    if not api_key:
        print("❌ No API key")
        return False
    
    try:
        breeze = BreezeConnect(api_key=api_key)
        print("✅ Basic connection successful")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_session_token():
    """Test current session token"""
    load_dotenv()
    
    api_key = os.getenv("BREEZE_API_KEY")
    api_secret = os.getenv("BREEZE_API_SECRET")
    client_code = os.getenv("ICICI_CLIENT_CODE")
    session_token = os.getenv("BREEZE_SESSION_TOKEN")
    
    if not all([api_key, api_secret, client_code, session_token]):
        print("❌ Missing credentials for session test")
        return False
    
    try:
        breeze = BreezeConnect(api_key=api_key)
        breeze.user_id = client_code
        
        result = breeze.generate_session(
            api_secret=api_secret,
            session_token=session_token
        )
        
        customer = breeze.get_customer_details()
        customer_str = str(customer) if customer else ""
        
        if 'Public Key does not exist' in customer_str:
            print("❌ App not activated or API permissions missing")
            return False
        elif 'Error' in customer_str:
            print(f"❌ Session error: {customer}")
            return False
        else:
            print("✅ Session token is working")
            return True
            
    except Exception as e:
        print(f"❌ Session test failed: {e}")
        return False

def check_market_hours():
    """Check if current time is within market hours"""
    from datetime import datetime
    import pytz
    
    # IST timezone
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    # Market hours: 9:15 AM to 3:30 PM IST, Monday-Friday
    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    
    is_weekday = now.weekday() < 5  # Monday=0, Friday=4
    is_market_hours = market_open <= now <= market_close
    
    print(f"📅 Current time (IST): {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Weekday: {'Yes' if is_weekday else 'No'}")
    print(f"   Market hours: {'Yes' if is_market_hours else 'No'}")
    
    return is_weekday and is_market_hours

def generate_debug_report():
    """Generate comprehensive debug report"""
    print("\n" + "="*50)
    print("🔍 ICICI Breeze API Diagnostic Report")
    print("="*50)
    
    # Check credentials
    credentials_ok = check_credentials()
    
    # Test API key encoding
    encoding_ok = test_api_key_encoding()
    
    # Test basic connection
    connection_ok = test_basic_connection()
    
    # Test session token
    session_ok = test_session_token()
    
    # Check market hours
    market_ok = check_market_hours()
    
    print("\n" + "="*50)
    print("📊 Summary")
    print("="*50)
    
    results = {
        "Credentials": "✅" if credentials_ok else "❌",
        "API Key Encoding": "✅" if encoding_ok else "⚠️",
        "Basic Connection": "✅" if connection_ok else "❌",
        "Session Token": "✅" if session_ok else "❌",
        "Market Hours": "✅" if market_ok else "⚠️"
    }
    
    for test, status in results.items():
        print(f"{test}: {status}")
    
    if not all([credentials_ok, connection_ok, session_ok]):
        print("\n🚨 Issues detected! Run comprehensive_session_fix.py")
    else:
        print("\n✅ All systems appear to be working!")

def main():
    """Main diagnostic function"""
    generate_debug_report()

if __name__ == "__main__":
    main()