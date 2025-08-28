import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key
from breeze_connect import BreezeConnect

def refresh_session():
    """
    Refreshes the Breeze API session token by prompting the user to visit a URL and paste the redirect URL.
    Updates the .env file with the new session token.
    """
    print("\n🔄 Starting Breeze API session refresh...")
    
    # Load environment variables
    env_path = Path('.env')
    load_dotenv(env_path)
    
    # Get API credentials from environment variables
    api_key = os.getenv('BREEZE_API_KEY')
    api_secret = os.getenv('BREEZE_API_SECRET')
    app_id = os.getenv('BREEZE_APP_ID')
    
    if not all([api_key, api_secret, app_id]):
        print("❌ Error: Missing Breeze API credentials in .env file.")
        print("Please ensure BREEZE_API_KEY, BREEZE_API_SECRET, and BREEZE_APP_ID are set.")
        sys.exit(1)
    
    try:
        # Initialize Breeze Connect
        breeze = BreezeConnect(api_key=api_key)
        
        # Generate session URL
        session_url = breeze.generate_session(api_secret=api_secret, session_token=None)
        
        # Prompt user to visit URL and get redirect URL
        print("\n✅ Please follow these steps to refresh your Breeze API session:")
        print(f"\n1. Visit this URL in your browser: {session_url}")
        print("2. Log in with your Breeze credentials")
        print("3. After successful login, you will be redirected to a URL")
        print("4. Copy the ENTIRE redirect URL and paste it below\n")
        
        redirect_url = input("Paste the redirect URL here: ")
        
        # Extract session token from redirect URL
        match = re.search(r'token=([^&]+)', redirect_url)
        if not match:
            print("❌ Error: Could not extract session token from redirect URL.")
            sys.exit(1)
        
        session_token = match.group(1)
        
        # Update .env file with new session token
        set_key(env_path, 'BREEZE_SESSION_TOKEN', session_token)
        
        print("\n✅ Session token successfully updated in .env file!")
        print("Your Breeze API session has been refreshed.")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Error refreshing Breeze API session: {str(e)}")
        return False

if __name__ == "__main__":
    refresh_session()