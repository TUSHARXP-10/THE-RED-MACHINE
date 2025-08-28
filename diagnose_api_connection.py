import os
import sys
from dotenv import load_dotenv, find_dotenv, set_key
from breeze_connect import BreezeConnect

def diagnose_api_connection():
    """Diagnose API connection issues and provide solutions"""
    print("🔍 Starting API Connection Diagnostics")
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
    api_key = os.getenv("BREEZE_API_KEY")
    api_secret = os.getenv("BREEZE_API_SECRET")
    session_token = os.getenv("BREEZE_SESSION_TOKEN")
    client_code = os.getenv("ICICI_CLIENT_CODE")
    
    # Clean up any quotes
    if api_key:
        api_key = api_key.strip('"')
        set_key(dotenv_path, "BREEZE_API_KEY", api_key)
    
    if api_secret:
        api_secret = api_secret.strip('"')
        set_key(dotenv_path, "BREEZE_API_SECRET", api_secret)
    
    if session_token:
        session_token = session_token.strip('"')
        set_key(dotenv_path, "BREEZE_SESSION_TOKEN", session_token)
    
    if client_code:
        client_code = client_code.strip('"')
        set_key(dotenv_path, "ICICI_CLIENT_CODE", client_code)
    
    # Check if all credentials are present
    missing = []
    if not api_key: missing.append("BREEZE_API_KEY")
    if not api_secret: missing.append("BREEZE_API_SECRET")
    if not session_token: missing.append("BREEZE_SESSION_TOKEN")
    if not client_code: missing.append("ICICI_CLIENT_CODE")
    
    if missing:
        print(f"❌ Missing credentials: {', '.join(missing)}")
        print("Please update your .env file with the required credentials.")
        return False
    
    print("✅ All required credentials are present")
    print(f"API Key: {api_key[:5]}...")
    print(f"API Secret: {api_secret[:5]}...")
    print(f"Session Token: {session_token[:5]}...")
    print(f"Client Code: {client_code}")
    
    # Test BreezeConnect initialization
    try:
        print("\n🔍 Testing BreezeConnect initialization...")
        breeze = BreezeConnect(api_key=api_key)
        print("✅ BreezeConnect initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize BreezeConnect: {e}")
        print("Possible solutions:")
        print("1. Check if your API key is correct")
        print("2. Make sure you have the correct version of breeze_connect installed")
        print("3. Check your internet connection")
        return False
    
    # Test session generation
    try:
        print("\n🔍 Testing session generation...")
        result = breeze.generate_session(api_secret=api_secret, session_token=session_token)
        print(f"Session generation result: {result}")
    except Exception as e:
        print(f"❌ Failed to generate session: {e}")
        print("Possible solutions:")
        print("1. Your session token may be expired. Run fix_session_immediately.py to get a new one.")
        print("2. Check if your API secret is correct")
        print("3. Make sure your API key and session token match")
        return False
    
    # Test customer details
    try:
        print("\n🔍 Testing customer details retrieval...")
        customer = breeze.get_customer_details()
        print(f"Customer details response: {customer}")
        
        if 'Error' not in str(customer) and 'Public Key does not exist' not in str(customer):
            print("✅ Successfully retrieved customer details")
            print("\n🎉 All tests passed! Your API connection is working correctly.")
            return True
        else:
            print("❌ Failed to retrieve customer details")
            print("Possible solutions:")
            print("1. Your session token may be expired. Run fix_session_immediately.py to get a new one.")
            print("2. Check if your API credentials are correct")
            return False
    except Exception as e:
        print(f"❌ Failed to retrieve customer details: {e}")
        print("Possible solutions:")
        print("1. Your session token may be expired. Run fix_session_immediately.py to get a new one.")
        print("2. Check if your API credentials are correct")
        return False

def create_env_file():
    """Create a new .env file with placeholders"""
    env_content = """BREEZE_API_KEY=your_api_key_here
BREEZE_API_SECRET=your_api_secret_here
BREEZE_APP_ID=your_app_id_here
BREEZE_SESSION_TOKEN=your_session_token_here
ICICI_CLIENT_CODE=your_client_code_here
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ Created new .env file with placeholders")
    print("Please update the file with your actual credentials")

if __name__ == "__main__":
    diagnose_api_connection()