#!/usr/bin/env python3
"""
Complete Client ID Authentication with Kite Connect
This script provides a comprehensive authentication flow using Client ID GSS065
"""

import os
from kiteconnect import KiteConnect
import webbrowser
from dotenv import load_dotenv
import time

def load_env_credentials():
    """Load and verify all credentials"""
    load_dotenv()
    
    return {
        'api_key': os.getenv('KITE_API_KEY'),
        'api_secret': os.getenv('KITE_API_SECRET'),
        'client_id': os.getenv('ZERODHA_CLIENT_ID'),
        'redirect_url': os.getenv('KITE_REDIRECT_URL', 'https://localhost')
    }

def verify_credentials(creds):
    """Verify all required credentials are present"""
    missing = []
    for key, value in creds.items():
        if not value:
            missing.append(key)
    
    if missing:
        print(f"❌ Missing credentials: {', '.join(missing)}")
        return False
    
    print("✅ All credentials verified")
    return True

def generate_new_session():
    """Generate a new session with proper Client ID integration"""
    creds = load_env_credentials()
    
    if not verify_credentials(creds):
        return False
    
    print(f"\n🎯 Client ID Authentication Setup")
    print(f"Client ID: {creds['client_id']}")
    print(f"API Key: {creds['api_key']}")
    print(f"Redirect URL: {creds['redirect_url']}")
    
    # Initialize Kite Connect
    kite = KiteConnect(api_key=creds['api_key'])
    
    # Generate login URL with enhanced parameters
    login_url = kite.login_url()
    enhanced_url = f"{login_url}&client_id={creds['client_id']}"
    
    print(f"\n🔗 Enhanced Login URL: {enhanced_url}")
    print("\n📋 Step-by-step Instructions:")
    print("1. Open the login URL above in your browser")
    print("2. Login with your Zerodha demat account")
    print("3. Ensure Client ID GSS065 is displayed during login")
    print("4. Complete the authentication process")
    print("5. Copy the 'request_token' from the redirect URL")
    
    # Open browser automatically
    print("\n🌐 Opening browser...")
    webbrowser.open(enhanced_url)
    
    # Get fresh request token
    print("\n⏳ Waiting for request token...")
    request_token = input("📝 Paste request_token: ").strip()
    
    if not request_token:
        print("❌ No request token provided")
        return False
    
    try:
        # Generate session with proper API secret
        print("\n🔐 Generating new session...")
        session_data = kite.generate_session(
            request_token=request_token,
            api_secret=creds['api_secret']
        )
        
        # Extract new access token
        new_access_token = session_data['access_token']
        
        print(f"✅ Session generated successfully!")
        print(f"📊 Session Details:")
        print(f"   Access Token: {new_access_token[:10]}...")
        print(f"   Public Token: {session_data.get('public_token', 'N/A')}")
        print(f"   Refresh Token: {session_data.get('refresh_token', 'N/A')}")
        
        # Verify client ID in profile
        kite.set_access_token(new_access_token)
        profile = kite.profile()
        
        print(f"\n👤 Profile Verification:")
        print(f"   Name: {profile.get('user_name')}")
        print(f"   Email: {profile.get('email')}")
        print(f"   Client ID: {profile.get('user_id')}")
        print(f"   User Type: {profile.get('user_type')}")
        
        # Verify client ID matches
        if profile.get('user_id') == creds['client_id']:
            print(f"✅ Client ID {creds['client_id']} verified successfully!")
            
            # Test trading permissions
            try:
                positions = kite.positions()
                print("✅ Trading permissions confirmed!")
                
                # Test SENSEX data access
                try:
                    sensex_data = kite.quote(["NSE:SENSEX"])
                    print("✅ SENSEX data access working!")
                    
                    # Save new access token
                    if save_new_access_token(new_access_token):
                        print("✅ Access token saved to .env")
                        return True
                        
                except Exception as e:
                    print(f"⚠️ SENSEX data test: {e}")
                    
            except Exception as e:
                print(f"⚠️ Trading permissions: {e}")
                
        else:
            print(f"❌ Client ID mismatch!")
            print(f"Expected: {creds['client_id']}")
            print(f"Got: {profile.get('user_id')}")
            
    except Exception as e:
        print(f"❌ Session generation failed: {e}")
        print(f"Error details: {str(e)}")
        
    return False

def save_new_access_token(new_token):
    """Save new access token to .env file"""
    try:
        env_path = '.env'
        
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        updated = False
        new_lines = []
        
        for line in lines:
            if line.startswith('KITE_ACCESS_TOKEN='):
                new_lines.append(f'KITE_ACCESS_TOKEN={new_token}\n')
                updated = True
            else:
                new_lines.append(line)
        
        if not updated:
            new_lines.append(f'KITE_ACCESS_TOKEN={new_token}\n')
        
        with open(env_path, 'w') as f:
            f.writelines(new_lines)
            
        print("✅ .env file updated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update .env: {e}")
        return False

def quick_test_connection():
    """Quick test of current connection"""
    creds = load_env_credentials()
    
    if not creds['access_token']:
        print("❌ No access token found - need to generate new session")
        return False
    
    try:
        kite = KiteConnect(api_key=creds['api_key'])
        kite.set_access_token(creds['access_token'])
        
        profile = kite.profile()
        print(f"✅ Current connection active!")
        print(f"   Client ID: {profile.get('user_id')}")
        print(f"   Name: {profile.get('user_name')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Current connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Complete Client ID Authentication")
    print("=" * 50)
    
    # Test current connection first
    print("\n1. Testing current connection...")
    current_working = quick_test_connection()
    
    if not current_working:
        print("\n2. Generating new session...")
        success = generate_new_session()
        
        if success:
            print("\n🎉 Authentication complete!")
            print("🔄 Ready to start live trading")
            print("\nNext steps:")
            print("   python START_LIVE_TRADING.py")
        else:
            print("\n❌ Authentication incomplete")
            print("   Check your API credentials and try again")
    else:
        print("\n✅ Already authenticated - ready for live trading!")