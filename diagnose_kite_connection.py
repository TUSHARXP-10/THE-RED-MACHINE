import os
import sys
from dotenv import load_dotenv, find_dotenv, set_key
from kiteconnect import KiteConnect

def diagnose_kite_connection():
    """Diagnose Kite API connection issues and provide solutions"""
    print("🔍 Starting Kite API Connection Diagnostics")
    print("="*50)
    
    # Find the .env file
    dotenv_path = find_dotenv()
    if not dotenv_path:
        print("❌ .env file not found")
        create_env_file()
        return False
    
    print(f"✅ Found .env file at: {dotenv_path}")
    
    # Load the current environment variables
    load_dotenv(dotenv_path)
    
    # Check API credentials
    api_key = os.getenv("KITE_API_KEY")
    api_secret = os.getenv("KITE_API_SECRET")
    access_token = os.getenv("KITE_ACCESS_TOKEN")
    client_id = os.getenv("ZERODHA_CLIENT_ID")
    redirect_url = os.getenv("KITE_REDIRECT_URL")
    
    # Clean up any quotes
    if api_key:
        api_key = api_key.strip('"')
        set_key(dotenv_path, "KITE_API_KEY", api_key)
    
    if api_secret:
        api_secret = api_secret.strip('"')
        set_key(dotenv_path, "KITE_API_SECRET", api_secret)
    
    if access_token:
        access_token = access_token.strip('"')
        set_key(dotenv_path, "KITE_ACCESS_TOKEN", access_token)
    
    if client_id:
        client_id = client_id.strip('"')
        set_key(dotenv_path, "ZERODHA_CLIENT_ID", client_id)
    
    if redirect_url:
        redirect_url = redirect_url.strip('"')
        set_key(dotenv_path, "KITE_REDIRECT_URL", redirect_url)
    else:
        redirect_url = "https://localhost"
        set_key(dotenv_path, "KITE_REDIRECT_URL", redirect_url)
    
    # Check if all credentials are present
    missing = []
    if not api_key: missing.append("KITE_API_KEY")
    if not api_secret: missing.append("KITE_API_SECRET")
    if not access_token: missing.append("KITE_ACCESS_TOKEN")
    if not client_id: missing.append("ZERODHA_CLIENT_ID")
    
    if missing:
        print(f"❌ Missing credentials: {', '.join(missing)}")
        print("Please update your .env file with the required credentials.")
        return False
    
    print("✅ All required credentials are present")
    print(f"API Key: {api_key[:5]}...")
    print(f"API Secret: {api_secret[:5]}...")
    print(f"Access Token: {access_token[:5]}...")
    print(f"Client ID: {client_id}")
    print(f"Redirect URL: {redirect_url}")
    
    # Test KiteConnect initialization
    try:
        print("\n🔍 Testing KiteConnect initialization...")
        kite = KiteConnect(api_key=api_key)
        print("✅ KiteConnect initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize KiteConnect: {e}")
        print("Possible solutions:")
        print("1. Check if your API key is correct")
        print("2. Make sure you have the correct version of kiteconnect installed")
        print("3. Check your internet connection")
        return False
    
    # Test setting access token
    try:
        print("\n🔍 Testing access token...")
        kite.set_access_token(access_token)
        print("✅ Access token set successfully")
    except Exception as e:
        print(f"❌ Failed to set access token: {e}")
        print("Possible solutions:")
        print("1. Your access token may be expired. Run fix_kite_session.py to get a new one.")
        print("2. Check if your access token is correct")
        return False
    
    # Test user profile
    try:
        print("\n🔍 Testing user profile retrieval...")
        profile = kite.profile()
        print(f"User profile: {profile['user_name']} ({profile['user_id']})")
        print("✅ Successfully retrieved user profile")
    except Exception as e:
        print(f"❌ Failed to retrieve user profile: {e}")
        print("Possible solutions:")
        print("1. Your access token may be expired. Run fix_kite_session.py to get a new one.")
        print("2. Check if your API credentials are correct")
        return False
    
    # Test market data
    try:
        print("\n🔍 Testing market data retrieval...")
        instruments = kite.instruments("NSE")
        print(f"Retrieved {len(instruments)} instruments from NSE")
        print("✅ Successfully retrieved market data")
    except Exception as e:
        print(f"❌ Failed to retrieve market data: {e}")
        print("Possible solutions:")
        print("1. Your access token may be expired. Run fix_kite_session.py to get a new one.")
        print("2. Check if your API credentials are correct")
        print("3. Check your internet connection")
        return False
    
    print("\n🎉 All tests passed! Your Kite API connection is working correctly.")
    return True

def create_env_file():
    """Create a new .env file with placeholders"""
    env_content = """KITE_API_KEY=your_api_key_here
KITE_API_SECRET=your_api_secret_here
KITE_ACCESS_TOKEN=your_access_token_here
ZERODHA_CLIENT_ID=your_client_id_here
KITE_REDIRECT_URL=https://localhost
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ Created new .env file with placeholders")
    print("Please update the file with your actual credentials")

if __name__ == "__main__":
    diagnose_kite_connection()