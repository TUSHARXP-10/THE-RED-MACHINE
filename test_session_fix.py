from breeze_connect import BreezeConnect
import os
from dotenv import load_dotenv

def test_session_token(session_token=None):
    """Test if the session token is valid"""
    load_dotenv()  # Load environment variables from .env file
    api_key = os.getenv("BREEZE_API_KEY")
    if api_key:
        api_key = api_key.strip('"')  # Remove any quotes
    
    api_secret = os.getenv("BREEZE_API_SECRET")
    if api_secret:
        api_secret = api_secret.strip('"')  # Remove any quotes
    
    if not api_key or not api_secret:
        print("❌ API key or secret not found in .env file")
        missing = []
        if not api_key: missing.append("BREEZE_API_KEY")
        if not api_secret: missing.append("BREEZE_API_SECRET")
        print(f"Missing credentials: {', '.join(missing)}")
        return False
    
    # Use provided token or get from .env
    if session_token is None:
        session_token = os.getenv("BREEZE_SESSION_TOKEN")
        if session_token:
            # Remove any quotes that might be in the token
            session_token = session_token.strip('"')
    
    if not session_token:
        print("❌ No session token provided or found in .env file")
        return False
    
    print(f"Testing session token: {session_token[:5] if len(session_token) > 5 else session_token}...")
    print(f"Using API key: {api_key[:5]}...")
    
    # Initialize BreezeConnect
    try:
        breeze = BreezeConnect(api_key=api_key)
    except Exception as e:
        print(f"❌ Failed to initialize BreezeConnect: {e}")
        return False
    
    try:
        # Generate session
        session_response = breeze.generate_session(
            api_secret=api_secret,
            session_token=session_token
        )
        
        print("✅ Session generation successful!")
        print(f"Response: {session_response}")
        
        # Validate session by getting customer details
        customer_details = breeze.get_customer_details()
        if customer_details and isinstance(customer_details, dict) and customer_details.get('Status') == 200:
            print("✅ Session validation successful!")
            print(f"User: {customer_details['Success']['idirect_user_name']}")
            return True
        else:
            print("❌ Session validation failed")
            print(f"Response: {customer_details}")
            return False
    except Exception as e:
        print(f"❌ Session test failed: Unexpected error: {e}")
        return False

if __name__ == "__main__":
    # Test the current token from .env
    test_session_token()