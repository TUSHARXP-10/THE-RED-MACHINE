import os
import webbrowser
from dotenv import load_dotenv, find_dotenv, set_key
from kiteconnect import KiteConnect

def quick_kite_session_fix():
    """Simplified script to fix Kite access token issues"""
    print("🔄 Quick Kite Session Fix Tool")
    print("="*50)
    
    # Find the .env file
    dotenv_path = find_dotenv()
    if not dotenv_path:
        print("❌ .env file not found")
        return False
    
    # Load the current environment variables
    load_dotenv(dotenv_path)
    
    # Get API credentials
    api_key = os.getenv("KITE_API_KEY")
    if api_key:
        api_key = api_key.strip('"')
    
    api_secret = os.getenv("KITE_API_SECRET")
    if api_secret:
        api_secret = api_secret.strip('"')
    
    client_id = os.getenv("ZERODHA_CLIENT_ID")
    if client_id:
        client_id = client_id.strip('"')
    
    redirect_url = os.getenv("KITE_REDIRECT_URL", "https://localhost")
    if redirect_url:
        redirect_url = redirect_url.strip('"')
    
    # Check if all credentials are present
    missing = []
    if not api_key: missing.append("KITE_API_KEY")
    if not api_secret: missing.append("KITE_API_SECRET")
    if not client_id: missing.append("ZERODHA_CLIENT_ID")
    
    if missing:
        print(f"❌ Missing credentials: {', '.join(missing)}")
        print("Please update your .env file with the required credentials.")
        return False
    
    print("✅ API credentials found")
    print(f"API Key: {api_key[:5]}...")
    
    # Initialize KiteConnect
    try:
        kite = KiteConnect(api_key=api_key)
        login_url = kite.login_url()
    except Exception as e:
        print(f"❌ Failed to initialize KiteConnect: {e}")
        return False
    
    print("\n🔍 Access Token Generation Steps:")
    print("1. Opening login URL in your default browser")
    print("2. Login with your Zerodha credentials")
    print("3. After successful login, you'll be redirected")
    print("4. Copy the entire redirect URL from your browser")
    
    # Open the login URL in the default browser
    try:
        webbrowser.open(login_url)
        print("\n✅ Opened login URL in browser")
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        print(f"Please manually open this URL: {login_url}")
    
    # Get the redirect URL from the user
    print("\nAfter logging in, please provide the redirect URL:")
    redirect_url_input = input("Redirect URL: ").strip()
    
    if not redirect_url_input:
        print("❌ No redirect URL provided")
        return False
    
    # Extract request token from redirect URL
    try:
        # The redirect URL format is typically: https://your_redirect_uri/?request_token=xxx&action=login&status=success
        if "request_token" not in redirect_url_input:
            print("❌ Error: Could not find request token in the URL")
            return False
        
        # Extract the request token parameter
        params = redirect_url_input.split('?')[1].split('&')
        request_token = None
        for param in params:
            if param.startswith('request_token='):
                request_token = param.split('=')[1]
                break
        
        if not request_token:
            print("❌ Could not extract request token from URL")
            return False
        
        print(f"✅ Extracted request token: {request_token[:5]}...")
    except Exception as e:
        print(f"❌ Error extracting request token: {e}")
        return False
    
    # Generate access token
    try:
        print("\n🔍 Generating access token...")
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]
        print(f"✅ Successfully generated access token: {access_token[:5]}...")
    except Exception as e:
        print(f"❌ Error generating access token: {e}")
        return False
    
    # Test the access token
    try:
        print("\n🔍 Testing access token...")
        kite.set_access_token(access_token)
        profile = kite.profile()
        print(f"✅ Access token verified! Logged in as: {profile['user_name']}")
        
        # Update the .env file
        set_key(dotenv_path, "KITE_ACCESS_TOKEN", access_token)
        print("✅ Updated .env file with new access token")
        
        return True
    except Exception as e:
        print(f"❌ Error testing access token: {e}")
        return False

if __name__ == "__main__":
    quick_kite_session_fix()