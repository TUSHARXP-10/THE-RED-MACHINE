#!/usr/bin/env python3
"""
Complete verification and fix for Kite Connect authentication
Addresses the checksum error by ensuring correct API credentials
"""

import os
from kiteconnect import KiteConnect
import webbrowser
from dotenv import load_dotenv

def verify_kite_app():
    """Verify Kite Connect app configuration"""
    print("🔍 KITE CONNECT VERIFICATION")
    print("=" * 40)
    
    print("\n1. Check your Kite Connect app:")
    print("   🔗 https://developers.kite.trade/apps")
    
    print("\n2. Find app with these details:")
    print("   📱 App Name: Should match your trading system")
    print("   🔑 API Key: q23715gf6tzjmyf5")
    print("   🔐 API Secret: VERIFY THIS IS CORRECT")
    print("   🌐 Redirect URL: https://localhost")
    
    print("\n3. If API Secret doesn't match:")
    print("   - Copy the EXACT API Secret from Kite dashboard")
    print("   - Update .env file")
    
    input("\nPress Enter after verifying API Secret...")

def update_api_secret():
    """Update API secret with correct value"""
    load_dotenv()
    
    print("\n📝 UPDATE API SECRET")
    print("=" * 25)
    
    new_secret = input("Enter correct API Secret: ").strip()
    if not new_secret:
        print("❌ No secret provided")
        return False
    
    try:
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            if line.startswith('KITE_API_SECRET='):
                new_lines.append(f"KITE_API_SECRET='{new_secret}'\n")
            else:
                new_lines.append(line)
        
        with open('.env', 'w') as f:
            f.writelines(new_lines)
        
        print("✅ API Secret updated!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env: {e}")
        return False

def authenticate_with_correct_secret():
    """Authenticate with verified credentials"""
    load_dotenv()
    
    print("\n🔐 AUTHENTICATE WITH CORRECT CREDENTIALS")
    print("=" * 45)
    
    api_key = os.getenv('KITE_API_KEY', 'q23715gf6tzjmyf5')
    api_secret = os.getenv('KITE_API_SECRET')
    client_id = os.getenv('ZERODHA_CLIENT_ID', 'GSS065')
    
    if not api_secret or len(api_secret) < 10:
        print("❌ API Secret not set correctly")
        return False
    
    kite = KiteConnect(api_key=api_key)
    
    # Generate login URL
    login_url = kite.login_url()
    print(f"\n🌐 Login URL: {login_url}")
    print(f"   Client ID: {client_id}")
    
    webbrowser.open(login_url)
    
    print("\n📋 Steps:")
    print("1. Open login URL")
    print("2. Login with Zerodha DEMAT account")
    print("3. Ensure you see Client ID: GSS065")
    print("4. Complete authentication")
    print("5. Copy request_token from redirect URL")
    
    request_token = input("\nEnter request_token: ").strip()
    
    if not request_token:
        print("❌ No request token provided")
        return False
    
    try:
        print("\n🔄 Generating session...")
        session_data = kite.generate_session(request_token, api_secret)
        
        new_access_token = session_data['access_token']
        print(f"✅ SUCCESS! New access token: {new_access_token}")
        
        # Update .env
        update_access_token(new_access_token)
        
        # Test connection
        kite.set_access_token(new_access_token)
        profile = kite.profile()
        
        print(f"\n👤 Profile verified:")
        print(f"   Name: {profile.get('user_name')}")
        print(f"   Email: {profile.get('email')}")
        print(f"   Client ID: {profile.get('user_id')}")
        
        # Test market data
        quote = kite.quote(["NSE:SENSEX"])
        print(f"📊 SENSEX: {quote['NSE:SENSEX']['last_price']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("   - Check API Secret is correct")
        print("   - Ensure request_token is fresh")
        print("   - Verify Kite app permissions")
        return False

def update_access_token(new_token):
    """Update access token in .env"""
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
        
        print("✅ Access token updated in .env")
        
    except Exception as e:
        print(f"⚠️ Could not update .env: {e}")

def main():
    """Main verification and fix process"""
    print("KITE CONNECT AUTHENTICATION FIX")
    print("=" * 50)
    print("This will resolve the checksum error")
    
    # Step 1: Verify app
    verify_kite_app()
    
    # Step 2: Update API secret if needed
    update_api_secret()
    
    # Step 3: Authenticate
    success = authenticate_with_correct_secret()
    
    if success:
        print("\n🎉 AUTHENTICATION COMPLETE!")
        print("\nNext steps:")
        print("1. Run: python START_LIVE_TRADING.py")
        print("2. System will start with Client ID GSS065")
        print("3. Live trading will be ready for 9:15 AM")
    else:
        print("\n❌ Still having issues?")
        print("1. Create new Kite Connect app")
        print("2. Use fresh API Key and Secret")
        print("3. Ensure GSS065 is linked to app")

if __name__ == "__main__":
    main()