"""
Final Diagnostic for ICICI Breeze API Session Issue
Based on official ICICI documentation and common troubleshooting steps
"""

import os
import requests
from urllib.parse import quote_plus
from breeze_connect import BreezeConnect
from dotenv import load_dotenv
import json

def check_app_status():
    """Check if app is active in ICICI system"""
    load_dotenv()
    api_key = os.getenv('BREEZE_API_KEY')
    
    if not api_key:
        print("No API key found")
        return False
    
    # Test API key validity
    test_url = f"https://api.icicidirect.com/breezeapi/api/v1/customerdetails"
    
    try:
        response = requests.get(test_url, headers={'api-key': api_key}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('Status') == 200:
                print("API key is valid and app is active")
                return True
            else:
                print(f"API key issue: {data.get('Error', 'Unknown')}")
        else:
            print(f"API endpoint error: {response.status_code}")
    except Exception as e:
        print(f"Connection error: {e}")
    
    return False

def manual_session_generation():
    """Manual session generation using official method"""
    load_dotenv()
    
    api_key = os.getenv('BREEZE_API_KEY')
    api_secret = os.getenv('BREEZE_API_SECRET')
    client_code = os.getenv('ICICI_CLIENT_CODE')
    
    if not all([api_key, api_secret, client_code]):
        print("Missing credentials in .env file")
        return None
    
    # Generate proper login URL
    encoded_key = quote_plus(api_key)
    login_url = f"https://api.icicidirect.com/apiuser/login?api_key={encoded_key}"
    
    print("MANUAL SESSION GENERATION")
    print("=" * 50)
    print(f"Login URL: {login_url}")
    print("\nSTEPS:")
    print("1. Open this URL in incognito browser")
    print("2. Login with your ICICI credentials")
    print("3. After successful login, you'll see:")
    print("   - Redirect URL: http://localhost/?apisession=XXXXXXX")
    print("   - OR session token displayed on the page")
    
    return login_url

def test_session_with_debug(session_token):
    """Test session with detailed debugging"""
    load_dotenv()
    
    api_key = os.getenv('BREEZE_API_KEY')
    api_secret = os.getenv('BREEZE_API_SECRET')
    client_code = os.getenv('ICICI_CLIENT_CODE')
    
    print(f"\nTesting session: {session_token}")
    print("=" * 50)
    
    try:
        # Initialize Breeze
        breeze = BreezeConnect(api_key=api_key)
        
        print("1. BreezeConnect initialized")
        print(f"   API Key: {api_key[:10]}...")
        print(f"   Client Code: {client_code}")
        
        # Method 1: Standard generate_session
        print("\n2. Testing standard generate_session...")
        try:
            response = breeze.generate_session(
                api_secret=api_secret,
                session_token=session_token
            )
            print(f"   Response: {response}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Method 2: Try direct API call
        print("\n3. Testing direct API call...")
        try:
            url = "https://api.icicidirect.com/breezeapi/api/v1/customerdetails"
            headers = {
                'Content-Type': 'application/json',
                'api-key': api_key,
                'session-key': session_token
            }
            
            response = requests.get(url, headers=headers)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('Status') == 200:
                    print("   Session is VALID!")
                    return True
                else:
                    print(f"   Session error: {data.get('Error', 'Unknown')}")
            
        except Exception as e:
            print(f"   API error: {e}")
        
        # Method 3: Try with customer details
        print("\n4. Testing customer details...")
        try:
            breeze.session_key = session_token
            breeze.user_id = client_code
            
            details = breeze.get_customer_details()
            print(f"   Details: {details}")
            
            if isinstance(details, dict) and details.get('Status') == 200:
                print("   Session working!")
                return True
                
        except Exception as e:
            print(f"   Details error: {e}")
        
    except Exception as e:
        print(f"Critical error: {e}")
    
    return False

def create_env_template():
    """Create .env template if missing"""
    template = """# ICICI Breeze API Credentials
BREEZE_API_KEY=your_api_key_here
BREEZE_API_SECRET=your_api_secret_here
ICICI_CLIENT_CODE=your_client_code_here
BREEZE_SESSION_TOKEN=your_session_token_here
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(template)
        print("Created .env template file")
    else:
        print("Found existing .env file")

def main():
    """Main diagnostic"""
    print("ICICI Breeze Final Diagnostic")
    print("=" * 50)
    
    # Check environment
    create_env_template()
    
    # Check app status
    print("\n1. Checking app status...")
    check_app_status()
    
    # Get session token
    session_token = input("\nEnter session token: ").strip()
    
    if session_token:
        # Test with debug
        test_session_with_debug(session_token)
    else:
        # Manual generation
        manual_session_generation()

if __name__ == "__main__":
    main()