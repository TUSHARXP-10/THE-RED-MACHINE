#!/usr/bin/env python3
"""
Complete Kite Connect Setup Guide with Client ID GSS065
Step-by-step authentication setup
"""

import os
from kiteconnect import KiteConnect
import webbrowser
from dotenv import load_dotenv

def show_current_config():
    """Display current configuration"""
    load_dotenv()
    
    print("📊 Current Configuration:")
    print(f"API Key: {os.getenv('KITE_API_KEY', 'Not set')}")
    print(f"Client ID: {os.getenv('ZERODHA_CLIENT_ID', 'Not set')}")
    print(f"API Secret: {'✅ Set' if os.getenv('KITE_API_SECRET') else '❌ Missing'}")
    print(f"Access Token: {'✅ Set' if os.getenv('KITE_ACCESS_TOKEN') else '❌ Missing'}")

def manual_setup_steps():
    """Provide manual setup steps"""
    print("\n🎯 Complete Manual Setup Guide")
    print("=" * 40)
    
    print("\n1️⃣ Verify API Credentials:")
    print("   • Login to https://developers.kite.trade")
    print("   • Check your app: 'q23715gf6tzjmyf5'")
    print("   • Verify API secret matches exactly")
    
    print("\n2️⃣ Generate New Access Token:")
    print("   • URL: https://kite.trade/connect/login?api_key=q23715gf6tzjmyf5&v=3")
    print("   • Login with: tusharchandane51@gmail.com")
    print("   • Ensure Client ID GSS065 appears")
    print("   • Copy request_token from redirect URL")
    
    print("\n3️⃣ Update .env File:")
    print("   KITE_API_KEY=q23715gf6tzjmyf5")
    print("   KITE_API_SECRET=your_actual_secret")
    print("   ZERODHA_CLIENT_ID=GSS065")
    print("   KITE_ACCESS_TOKEN=new_token_here")
    
    print("\n4️⃣ Test Connection:")
    print("   python -c \"from kiteconnect import KiteConnect; k=KiteConnect('q23715gf6tzjmyf5'); k.set_access_token('your_token'); print(k.profile())\"")

def create_quick_setup():
    """Create quick setup script"""
    script_content = '''#!/usr/bin/env python3
"""Quick Kite Connect Setup"""
import os
from kiteconnect import KiteConnect
import webbrowser

def setup():
    api_key = "q23715gf6tzjmyf5"
    client_id = "GSS065"
    
    kite = KiteConnect(api_key=api_key)
    
    print(f"🚀 Setup for Client ID: {client_id}")
    print(f"🔗 Login: {kite.login_url()}")
    
    webbrowser.open(kite.login_url())
    
    request_token = input("Enter request_token: ")
    api_secret = input("Enter API secret: ")
    
    try:
        data = kite.generate_session(request_token, api_secret)
        print(f"✅ Access Token: {data['access_token']}")
        print("💾 Save this to .env file as KITE_ACCESS_TOKEN")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    setup()
'''
    
    with open('quick_setup.py', 'w') as f:
        f.write(script_content)
    
    print("\n✅ Created quick_setup.py for manual authentication")

def main():
    print("🎯 Kite Connect Complete Setup")
    print("=" * 50)
    
    show_current_config()
    manual_setup_steps()
    create_quick_setup()
    
    print("\n🔄 Next Steps:")
    print("1. Run: python quick_setup.py")
    print("2. Or follow manual steps above")
    print("3. After getting access token, run: python START_LIVE_TRADING.py")

if __name__ == "__main__":
    main()