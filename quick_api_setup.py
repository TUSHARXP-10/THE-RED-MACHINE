#!/usr/bin/env python3
"""
Quick Kite API Setup - Skip package installation
Focuses on getting API secret and setting up access token
"""

import os
import webbrowser

def setup_env_file():
    """Create or update .env file with Kite API credentials"""
    print("\n🔑 Setting up API credentials...")
    
    # Check if .env file exists
    env_path = '.env'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_content = f.read()
    else:
        env_content = ""
    
    print("\n📋 Current API Key:", end=" ")
    if "KITE_API_KEY" in env_content:
        for line in env_content.split('\n'):
            if line.startswith('KITE_API_KEY='):
                print(line.split('=')[1])
    else:
        print("Not found")
    
    print("\n📝 Please provide the following information:")
    
    # Get API secret (from brother's account)
    api_secret = input("Enter your brother's Kite API Secret: ").strip()
    if not api_secret:
        print("❌ API Secret is required!")
        return False
    
    # Get client ID (your demat account)
    client_id = input("Enter your Demat Client ID (GSS065): ").strip()
    if not client_id:
        client_id = "GSS065"  # Default based on your account
    
    # Update .env file
    env_lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_lines = f.read().split('\n')
    
    # Remove empty lines and existing entries
    env_lines = [line for line in env_lines if line.strip() and not line.startswith(('KITE_API_SECRET=', 'ZERODHA_CLIENT_ID=', 'KITE_ACCESS_TOKEN='))]
    
    # Add new entries
    env_lines.append(f"KITE_API_SECRET={api_secret}")
    env_lines.append(f"ZERODHA_CLIENT_ID={client_id}")
    env_lines.append("KITE_ACCESS_TOKEN=")
    
    # Write updated content
    with open(env_path, 'w') as f:
        f.write('\n'.join(env_lines))
    
    print("✅ API credentials saved!")
    return True

def next_steps():
    """Show next steps for completing the setup"""
    print("\n🎯 Next Steps:")
    print("1. Run: python fix_kite_session.py")
    print("2. Login with YOUR demat account: tusharchandane51@gmail.com")
    print("3. Browser will open - complete the login process")
    print("4. Access token will be generated automatically")
    print("5. Run: python verify_api_linking.py to confirm")

def main():
    print("🚀 Quick API Setup - Skip Package Installation")
    print("=" * 50)
    print("\n📖 Instructions:")
    print("- Use your brother's API secret (from developers.kite.trade)")
    print("- Your demat account (tusharchandane51@gmail.com) will be used for trading")
    
    # Open browser to help get API secret
    print("\n🌐 Opening Kite Developer Portal...")
    webbrowser.open("https://developers.kite.trade/")
    
    # Setup credentials
    if setup_env_file():
        next_steps()
    else:
        print("❌ Setup failed. Please try again.")

if __name__ == "__main__":
    main()