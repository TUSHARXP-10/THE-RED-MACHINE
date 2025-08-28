#!/usr/bin/env python3
"""
Diagnose Kite API Setup Issues
"""

import os
import webbrowser

def check_kite_connect_app():
    """Guide user to verify Kite Connect app settings"""
    print("🔍 Kite API Setup Diagnosis")
    print("=" * 50)
    
    print("\n❌ Persistent 'Invalid checksum' error detected")
    print("\n📋 This usually means:")
    print("1. API key/secret mismatch")
    print("2. Wrong API key in .env")
    print("3. App not properly configured")
    
    print("\n🎯 Let's verify your setup:")
    
    # Show current .env values
    try:
        with open('.env', 'r') as f:
            content = f.read()
        
        print("\n📁 Current .env file:")
        for line in content.split('\n'):
            if 'KITE_API' in line and '=' in line:
                print(f"  {line}")
    except:
        print("❌ Could not read .env file")
    
    print("\n🌐 Please check your Kite Connect app:")
    print("1. Go to: https://developers.kite.trade/apps")
    print("2. Find your app")
    print("3. Verify the API key matches: q23715gf6tzjmyf5")
    print("4. Verify the API secret matches your .env")
    print("5. Check redirect URL is: https://localhost")
    
    print("\n🔧 To fix this:")
    print("1. Copy the correct API key from your Kite Connect app")
    print("2. Copy the correct API secret")
    print("3. Update your .env file")
    
    # Open Kite Connect apps page
    webbrowser.open("https://developers.kite.trade/apps")
    
    print("\n📝 After updating credentials, run:")
    print("python verify_kite_setup.py")

def create_env_template():
    """Create a template for correct .env setup"""
    template = """# Kite Connect API Configuration
# Get these from https://developers.kite.trade/apps
KITE_API_KEY='your_actual_api_key_here'
KITE_API_SECRET='your_actual_api_secret_here'
KITE_ACCESS_TOKEN='will_be_updated_automatically'
ZERODHA_CLIENT_ID='your_client_id'
KITE_REDIRECT_URL='https://localhost'
"""
    
    with open('.env_template', 'w') as f:
        f.write(template)
    
    print("✅ Created .env_template with correct format")

if __name__ == "__main__":
    diagnose_kite_setup()
    create_env_template()