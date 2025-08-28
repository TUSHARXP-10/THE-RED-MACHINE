import os
import webbrowser
from dotenv import load_dotenv, find_dotenv, set_key
from breeze_connect import BreezeConnect

def quick_session_fix():
    """Simplified script to fix session token issues"""
    print("🔄 Quick Session Fix Tool")
    print("="*50)
    
    # Find the .env file
    dotenv_path = find_dotenv()
    if not dotenv_path:
        print("❌ .env file not found")
        return False
    
    # Load the current environment variables
    load_dotenv(dotenv_path)
    
    # Get API credentials
    api_key = os.getenv("BREEZE_API_KEY")
    if api_key:
        api_key = api_key.strip('"')
    
    api_secret = os.getenv("BREEZE_API_SECRET")
    if api_secret:
        api_secret = api_secret.strip('"')
    
    client_code = os.getenv("ICICI_CLIENT_CODE")
    if client_code:
        client_code = client_code.strip('"')
    
    # Check if all credentials are present
    missing = []
    if not api_key: missing.append("BREEZE_API_KEY")
    if not api_secret: missing.append("BREEZE_API_SECRET")
    if not client_code: missing.append("ICICI_CLIENT_CODE")
    
    if missing:
        print(f"❌ Missing credentials: {', '.join(missing)}")
        print("Please update your .env file with the required credentials.")
        return False
    
    print("✅ API credentials found")
    print(f"API Key: {api_key[:5]}...")
    
    # Generate login URL
    login_url = f"https://api.icicidirect.com/apiuser/login?api_key={api_key}"
    
    print("\n🔍 Session Token Generation Steps:")
    print("1. Opening login URL in your default browser")
    print("2. Login with your ICICI Direct credentials")
    print("3. Enter OTP when prompted")
    print("4. After successful login, look for the session token")
    print("   - Check URL: ?apisession=XXXXX")
    print("   - Check Network tab in Developer Tools (F12)")
    print("   - Check left sidebar for 'API Session' value")
    
    # Open the login URL in the default browser
    try:
        webbrowser.open(login_url)
        print("\n✅ Opened login URL in browser")
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        print(f"Please manually open this URL: {login_url}")
    
    # Get the session token from the user
    print("\nAfter logging in, please provide the session token:")
    session_token = input("Session Token: ").strip()
    
    if not session_token:
        print("❌ No session token provided")
        return False
    
    # Test the session token
    print(f"\n🔍 Testing session token: {session_token[:5]}...")
    
    try:
        breeze = BreezeConnect(api_key=api_key)
        breeze.generate_session(api_secret=api_secret, session_token=session_token)
        customer = breeze.get_customer_details()
        
        if 'Error' not in str(customer) and 'Public Key does not exist' not in str(customer):
            print("✅ Session token is valid!")
            
            # Update the .env file
            set_key(dotenv_path, "BREEZE_SESSION_TOKEN", session_token)
            print("✅ Updated .env file with new session token")
            
            return True
        else:
            print("❌ Session token validation failed")
            print(f"Response: {customer}")
            return False
    except Exception as e:
        print(f"❌ Error testing session token: {e}")
        return False

if __name__ == "__main__":
    quick_session_fix()