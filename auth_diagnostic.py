#!/usr/bin/env python3
"""
Kite Connect Authentication Diagnostic
Comprehensive credential verification and troubleshooting
"""

import os
from kiteconnect import KiteConnect
import webbrowser
from dotenv import load_dotenv
import hashlib
import hmac
import base64

def diagnostic_check():
    """Complete diagnostic of authentication setup"""
    load_dotenv()
    
    print("🔍 Kite Connect Diagnostic Report")
    print("=" * 40)
    
    # Check environment variables
    api_key = os.getenv('KITE_API_KEY')
    api_secret = os.getenv('KITE_API_SECRET')
    client_id = os.getenv('ZERODHA_CLIENT_ID')
    
    print(f"API Key: {api_key}")
    print(f"API Secret: {api_secret}")
    print(f"Client ID: {client_id}")
    
    # Validate credentials
    issues = []
    
    if not api_key or len(api_key) < 10:
        issues.append("❌ Invalid API Key")
    
    if not api_secret or len(api_secret) < 10:
        issues.append("❌ Invalid API Secret")
    
    if not client_id or client_id != 'GSS065':
        issues.append("❌ Client ID mismatch")
    
    if issues:
        print("\nIssues found:")
        for issue in issues:
            print(issue)
        return False
    
    print("✅ Credentials format valid")
    
    # Test API key
    try:
        kite = KiteConnect(api_key=api_key)
        print("✅ API key accepted by Kite Connect")
        
        # Generate login URL
        login_url = kite.login_url()
        print(f"\nLogin URL: {login_url}")
        
        # Manual verification steps
        print("\n🔧 Manual Verification Steps:")
        print("1. Check Kite Connect App:")
        print("   - Go to https://developers.kite.trade/apps")
        print("   - Verify API Key: q23715gf6tzjmyf5")
        print("   - Verify API Secret matches: 87ivk3royi2z30lhzprgovhrocp8yq1g")
        print("   - Verify Redirect URL: https://localhost")
        
        print("\n2. Test with fresh request token:")
        print("   - Open login URL")
        print("   - Login with Zerodha")
        print("   - Ensure you see Client ID: GSS065")
        print("   - Copy request_token from redirect")
        
        return True
        
    except Exception as e:
        print(f"❌ API key validation failed: {e}")
        return False

def create_new_app_guide():
    """Guide to create new Kite Connect app"""
    print("\n🆕 Creating New Kite Connect App")
    print("=" * 35)
    print("1. Visit: https://developers.kite.trade/apps")
    print("2. Click 'Create App'")
    print("3. App Name: RED-MACHINE-TRADING")
    print("4. Description: Real-time scalping system")
    print("5. Redirect URL: https://localhost")
    print("6. Save the new API Key and Secret")
    print("7. Update .env file")

def emergency_token_generator():
    """Emergency token generation with manual verification"""
    load_dotenv()
    
    api_key = 'q23715gf6tzjmyf5'  # Current key
    api_secret = '87ivk3royi2z30lhzprgovhrocp8yq1g'  # Current secret
    
    print("\n🚨 Emergency Token Generation")
    print("=" * 30)
    
    kite = KiteConnect(api_key=api_key)
    login_url = kite.login_url()
    
    print(f"Login URL: {login_url}")
    print("\nSteps:")
    print("1. Open URL in browser")
    print("2. Login with Zerodha")
    print("3. Copy full redirect URL")
    print("4. Extract request_token parameter")
    
    redirect_url = input("\nEnter full redirect URL: ").strip()
    
    try:
        # Extract request_token
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(redirect_url)
        request_token = parse_qs(parsed.query)['request_token'][0]
        
        print(f"Request Token: {request_token}")
        
        # Generate session
        session_data = kite.generate_session(request_token, api_secret)
        new_token = session_data['access_token']
        
        print(f"✅ New Access Token: {new_token}")
        
        # Update .env
        update_env_token(new_token)
        
        return new_token
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def update_env_token(new_token):
    """Update .env with new token"""
    try:
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            if line.startswith('KITE_ACCESS_TOKEN='):
                new_lines.append(f"KITE_ACCESS_TOKEN='{new_token}'\n")
            else:
                new_lines.append(line)
        
        with open('.env', 'w') as f:
            f.writelines(new_lines)
        
        print("✅ .env updated successfully")
        
    except Exception as e:
        print(f"Could not update .env: {e}")

if __name__ == "__main__":
    print("Kite Connect Authentication Diagnostic")
    
    # Run diagnostic
    diagnostic_check()
    
    print("\nOptions:")
    print("1. Run emergency token generator")
    print("2. Create new Kite Connect app")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        emergency_token_generator()
    elif choice == "2":
        create_new_app_guide()
    else:
        print("Exiting diagnostic")