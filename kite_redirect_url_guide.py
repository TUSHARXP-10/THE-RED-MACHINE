import os
import webbrowser
from kiteconnect import KiteConnect
from dotenv import load_dotenv

def get_kite_credentials():
    """Load Kite API credentials from .env file"""
    load_dotenv()
    api_key = os.getenv("KITE_API_KEY")
    api_secret = os.getenv("KITE_API_SECRET")
    redirect_url = os.getenv("KITE_REDIRECT_URL", "https://localhost")
    
    # Strip quotes if present
    if api_key:
        api_key = api_key.strip('"')
    if api_secret:
        api_secret = api_secret.strip('"')
    if redirect_url:
        redirect_url = redirect_url.strip('"')
    
    return api_key, api_secret, redirect_url

def main():
    # Get credentials
    api_key, api_secret, redirect_url = get_kite_credentials()
    
    if not all([api_key, api_secret]):
        print("❌ Error: Missing Kite API credentials in .env file")
        print("Please ensure KITE_API_KEY and KITE_API_SECRET are set in your .env file")
        return
    
    # Initialize KiteConnect
    kite = KiteConnect(api_key=api_key)
    login_url = kite.login_url()
    
    print("\n===== KITE REDIRECT URL GUIDE =====\n")
    print("This guide will help you understand the correct redirect URL format")
    print("\n🔑 STEP 1: A browser window will open with the Kite login page")
    print("🔑 STEP 2: Log in with your Zerodha credentials")
    print(f"🔑 STEP 3: After successful login, you'll be redirected to {redirect_url}")
    print("\n⚠️ IMPORTANT: The redirect URL should look like this:")
    print(f"   {redirect_url}/?request_token=XXXXXX&action=login&status=success")
    print("\n⚠️ DO NOT copy the login page URL, which looks like:")
    print("   https://kite.zerodha.com/connect/login?api_key=XXXXX&v=3")
    print("\nOpening browser now...")
    
    # Open the login URL in the default browser
    webbrowser.open(login_url)
    
    print("\n===== AFTER LOGGING IN =====\n")
    print("1. Copy the ENTIRE URL from your browser's address bar AFTER you log in")
    print("2. The URL must contain 'request_token=' in it")
    print("3. Use this URL when prompted in fix_kite_session.py or quick_kite_session_fix.py")
    
    print("\n===== EXAMPLE =====\n")
    print("Correct URL format to copy:")
    print(f"✅ {redirect_url}/?request_token=abc123xyz&action=login&status=success")
    print("\nIncorrect URL format (login page):")
    print("❌ https://kite.zerodha.com/connect/login?api_key=d2371g2f412eyfs&v=3")

if __name__ == "__main__":
    main()