#!/usr/bin/env python3
"""
Emergency Kite Session Fix Utility
================================
This script provides a quick way to fix Kite API session issues.
It will guide you through the process of generating a new access token.
"""

import os
import sys
import webbrowser
import time
from kiteconnect import KiteConnect
from dotenv import load_dotenv, set_key

def update_env_file(key, value):
    """Update a specific key in the .env file"""
    dotenv_path = os.path.join(os.getcwd(), '.env')
    set_key(dotenv_path, key, value)
    print(f"✅ Updated {key} in .env file")

def get_kite_credentials():
    """Load Kite API credentials from .env file"""
    load_dotenv()
    api_key = os.getenv("KITE_API_KEY")
    api_secret = os.getenv("KITE_API_SECRET")
    client_id = os.getenv("ZERODHA_CLIENT_ID")
    redirect_url = os.getenv("KITE_REDIRECT_URL", "https://localhost")
    
    # Strip quotes if present
    if api_key:
        api_key = api_key.strip('"')
    if api_secret:
        api_secret = api_secret.strip('"')
    if client_id:
        client_id = client_id.strip('"')
    if redirect_url:
        redirect_url = redirect_url.strip('"')
    
    return api_key, api_secret, client_id, redirect_url

def generate_login_url():
    """Generate Kite login URL and open in browser"""
    api_key, api_secret, client_id, redirect_url = get_kite_credentials()
    
    if not all([api_key, api_secret, client_id]):
        print("❌ Error: Missing Kite API credentials in .env file")
        print("Please ensure the following variables are set in your .env file:")
        print("KITE_API_KEY, KITE_API_SECRET, ZERODHA_CLIENT_ID")
        return None, None
    
    try:
        kite = KiteConnect(api_key=api_key)
        login_url = kite.login_url()
        print("\n🔑 Please follow these steps to get your access token:")
        print("1. A browser window will open with the Kite login page")
        print("2. Log in with your Zerodha credentials")
        print(f"3. After successful login, you'll be redirected to {redirect_url} with a request token in the URL")
        print("4. Copy the entire URL from your browser and paste it back here")
        print("\nOpening browser...")
        
        # Open the login URL in the default browser
        webbrowser.open(login_url)
        
        return kite, api_secret
    except Exception as e:
        print(f"❌ Error generating login URL: {e}")
        return None, None

def extract_request_token(redirect_url):
    """Extract request token from the redirect URL"""
    try:
        # The redirect URL format is typically: https://your_redirect_uri/?request_token=xxx&action=login&status=success
        if "request_token" not in redirect_url:
            print("❌ Error: Could not find request token in the URL")
            return None
        
        # Extract the request token parameter
        params = redirect_url.split('?')[1].split('&')
        for param in params:
            if param.startswith('request_token='):
                return param.split('=')[1]
        
        return None
    except Exception as e:
        print(f"❌ Error extracting request token: {e}")
        return None

def generate_access_token(kite, api_secret, request_token):
    """Generate access token using request token and API secret"""
    try:
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]
        print(f"✅ Successfully generated access token: {access_token[:5]}...")
        return access_token
    except Exception as e:
        print(f"❌ Error generating access token: {e}")
        return None

def test_access_token(api_key, access_token):
    """Test the access token by fetching user profile"""
    try:
        kite = KiteConnect(api_key=api_key)
        kite.set_access_token(access_token)
        profile = kite.profile()
        print(f"✅ Access token verified! Logged in as: {profile['user_name']}")
        return True
    except Exception as e:
        print(f"❌ Error verifying access token: {e}")
        return False

def main():
    print("\n🚨 EMERGENCY KITE SESSION FIX 🚨")
    print("================================\n")
    print("This utility will help you quickly fix Kite API session issues.")
    print("It will guide you through generating a new access token.\n")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ Error: .env file not found")
        print("Creating a template .env file...")
        with open('.env', 'w') as f:
            f.write("KITE_API_KEY=\n")
            f.write("KITE_API_SECRET=\n")
            f.write("KITE_ACCESS_TOKEN=\n")
            f.write("ZERODHA_CLIENT_ID=\n")
            f.write("KITE_REDIRECT_URL=https://localhost\n")
        print("✅ Created template .env file. Please fill in your Kite API credentials and run this script again.")
        return
    
    # Load existing credentials
    api_key, api_secret, client_id, redirect_url = get_kite_credentials()
    
    # Check if credentials are missing
    if not api_key or not api_secret or not client_id:
        print("❌ Error: Missing Kite API credentials in .env file")
        
        # Prompt for missing credentials
        if not api_key:
            api_key = input("Enter your Kite API Key: ")
            update_env_file("KITE_API_KEY", api_key)
        
        if not api_secret:
            api_secret = input("Enter your Kite API Secret: ")
            update_env_file("KITE_API_SECRET", api_secret)
        
        if not client_id:
            client_id = input("Enter your Zerodha Client ID: ")
            update_env_file("ZERODHA_CLIENT_ID", client_id)
        
        if not redirect_url:
            redirect_url = input("Enter your Kite Redirect URL (default: https://localhost): ") or "https://localhost"
            update_env_file("KITE_REDIRECT_URL", redirect_url)
    
    # Generate login URL and open browser
    kite, api_secret = generate_login_url()
    if not kite:
        return
    
    # Wait for user to log in and get the redirect URL
    print("\nWaiting for you to log in...")
    redirect_url = input("\nPaste the redirect URL here: ")
    
    # Extract request token from redirect URL
    request_token = extract_request_token(redirect_url)
    if not request_token:
        return
    
    # Generate access token
    access_token = generate_access_token(kite, api_secret, request_token)
    if not access_token:
        return
    
    # Update .env file with new access token
    update_env_file("KITE_ACCESS_TOKEN", access_token)
    
    # Test the access token
    if test_access_token(api_key, access_token):
        print("\n✅ Session fix completed successfully!")
        print("You can now use the Kite API with your updated access token.")
        print("\n⚠️ IMPORTANT: This access token will expire at the end of the day.")
        print("You will need to run this script again tomorrow to generate a new token.")
    else:
        print("\n❌ Session fix failed. Please try again.")

if __name__ == "__main__":
    main()