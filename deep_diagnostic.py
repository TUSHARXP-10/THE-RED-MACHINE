#!/usr/bin/env python3
"""
Deep diagnostic for ICICI Breeze API session issues
Tests every possible failure point systematically
"""

import os
import sys
import requests
from urllib.parse import quote, quote_plus
from dotenv import load_dotenv

def test_environment():
    """Test environment setup"""
    print("🔍 ENVIRONMENT DIAGNOSTIC")
    print("=" * 50)
    
    load_dotenv()
    
    # Check all required variables
    required_vars = [
        'BREEZE_API_KEY',
        'BREEZE_API_SECRET', 
        'ICICI_CLIENT_CODE',
        'BREEZE_SESSION_TOKEN'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            # Show actual values for debugging (with length)
            clean_value = value.strip().strip('"').strip("'")
            print(f"{var}: {clean_value[:8]}...{clean_value[-4:] if len(clean_value) > 12 else ''} (len: {len(clean_value)})")
    
    if missing_vars:
        print(f"❌ Missing variables: {missing_vars}")
        return False
    
    return True

def test_api_key_encoding():
    """Test API key encoding issues"""
    print("\n🔍 API KEY ENCODING TEST")
    print("=" * 50)
    
    api_key = os.getenv('BREEZE_API_KEY', '').strip().strip('"').strip("'")
    
    print(f"Original API key: {api_key}")
    print(f"URL encoded: {quote(api_key)}")
    print(f"URL encoded (+ as %2B): {quote_plus(api_key)}")
    
    # Test which encoding works
    test_url = f"https://api.icicidirect.com/apiuser/login?api_key={quote_plus(api_key)}"
    print(f"Login URL: {test_url}")
    
    try:
        response = requests.get(test_url, timeout=10)
        print(f"Login page response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Login URL accessible")
        else:
            print("❌ Login URL not accessible")
    except Exception as e:
        print(f"❌ Error accessing login URL: {e}")

def test_session_token_format():
    """Test if session token format is valid"""
    print("\n🔍 SESSION TOKEN FORMAT TEST")
    print("=" * 50)
    
    token = os.getenv('BREEZE_SESSION_TOKEN', '').strip().strip('"').strip("'")
    
    print(f"Current token: {token}")
    print(f"Token length: {len(token)}")
    
    # Valid ICICI session tokens are typically 20-50 characters
    if len(token) < 15:
        print("❌ Token too short - likely truncated or incorrect")
        print("   Expected: 20-50 characters")
        print("   Actual: {} characters".format(len(token)))
    elif len(token) > 100:
        print("❌ Token too long - may contain extra data")
    else:
        print("✅ Token length appears valid")
    
    # Check for common issues
    if not token.isalnum():
        print("⚠️  Token contains special characters - may need URL decoding")
    
    return len(token) >= 15

def test_breeze_connection():
    """Test actual Breeze API connection"""
    print("\n🔍 BREEZE API CONNECTION TEST")
    print("=" * 50)
    
    try:
        from breeze_connect import BreezeConnect
        
        api_key = os.getenv('BREEZE_API_KEY', '').strip().strip('"').strip("'")
        api_secret = os.getenv('BREEZE_API_SECRET', '').strip().strip('"').strip("'")
        client_code = os.getenv('ICICI_CLIENT_CODE', '').strip().strip('"').strip("'")
        session_token = os.getenv('BREEZE_SESSION_TOKEN', '').strip().strip('"').strip("'")
        
        print(f"Testing with:")
        print(f"  API Key: {api_key[:8]}...")
        print(f"  API Secret: {api_secret[:8]}...")
        print(f"  Client Code: {client_code}")
        print(f"  Session Token: {session_token[:8]}...")
        
        # Test connection
        breeze = BreezeConnect(api_key=api_key)
        breeze.user_id = client_code
        
        # Test session generation
        print("\nTesting session generation...")
        result = breeze.generate_session(api_secret=api_secret, session_token=session_token)
        print(f"Session generation result: {result}")
        
        # Test customer details
        print("\nTesting customer details...")
        customer = breeze.get_customer_details()
        print(f"Customer details: {customer}")
        
        # Check response
        if customer and 'Error' not in str(customer) and 'Public Key does not exist' not in str(customer):
            print("✅ Session is VALID!")
            return True
        else:
            print("❌ Session is INVALID!")
            
            # Check specific error
            customer_str = str(customer) if customer else ""
            if 'Public Key does not exist' in customer_str:
                print("   → App not activated or API permissions missing")
            elif 'API Session cannot be empty' in customer_str:
                print("   → Session token format issue or expired")
            
            return False
            
    except ImportError:
        print("❌ breeze_connect not installed - run: pip install breeze-connect")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_app_status():
    """Check app status via API"""
    print("\n🔍 APP STATUS CHECK")
    print("=" * 50)
    
    api_key = os.getenv('BREEZE_API_KEY', '').strip().strip('"').strip("'")
    
    # Try to access the app status page
    status_url = f"https://api.icicidirect.com/apiuser/apps"
    
    print(f"Check app status manually:")
    print(f"   1. Go to: https://api.icicidirect.com/apiuser/home")
    print(f"   2. Click 'View Apps' tab")
    print(f"   3. Look for app with API key: {api_key[:8]}...")
    print(f"   4. Ensure status shows 'Active'")

def main():
    """Run all diagnostics"""
    print("🚀 ICICI BREEZE API DEEP DIAGNOSTIC")
    print("=" * 60)
    
    # Run tests
    env_ok = test_environment()
    test_api_key_encoding()
    token_ok = test_session_token_format()
    test_app_status()
    
    if env_ok:
        test_breeze_connection()
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY & NEXT STEPS")
    print("=" * 60)
    
    if not env_ok:
        print("1. Fix missing environment variables in .env file")
    elif not token_ok:
        print("1. Get a proper session token (20-50 characters)")
        print("2. Use the comprehensive_session_fix.py script")
    else:
        print("1. Check app activation status on ICICI portal")
        print("2. Ensure API key has proper permissions")
        print("3. Verify client code matches your account")

if __name__ == "__main__":
    main()