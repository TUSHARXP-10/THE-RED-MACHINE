"""
Final Session Validator for ICICI Breeze API
Comprehensive validation with detailed debugging
"""

import os
import sys
from urllib.parse import quote_plus
from breeze_connect import BreezeConnect
from dotenv import load_dotenv

def validate_environment():
    """Validate all required environment variables"""
    load_dotenv()
    
    required_vars = {
        'BREEZE_API_KEY': os.getenv('BREEZE_API_KEY'),
        'BREEZE_API_SECRET': os.getenv('BREEZE_API_SECRET'),
        'ICICI_CLIENT_CODE': os.getenv('ICICI_CLIENT_CODE'),
        'BREEZE_SESSION_TOKEN': os.getenv('BREEZE_SESSION_TOKEN')
    }
    
    print("🔍 Environment Validation:")
    print("=" * 50)
    
    missing = []
    for key, value in required_vars.items():
        if value:
            masked_value = value[:5] + "..." + value[-3:] if len(value) > 8 else "***"
            print(f"✅ {key}: {masked_value}")
        else:
            print(f"❌ {key}: MISSING")
            missing.append(key)
    
    if missing:
        print(f"\n🚨 Missing variables: {', '.join(missing)}")
        return False
    
    return True

def test_session_with_debug(session_token):
    """Test session with comprehensive debugging"""
    load_dotenv()
    
    api_key = os.getenv('BREEZE_API_KEY')
    api_secret = os.getenv('BREEZE_API_SECRET')
    client_code = os.getenv('ICICI_CLIENT_CODE')
    
    print(f"\n🧪 Testing Session Token: {session_token}")
    print("=" * 50)
    
    try:
        # Initialize Breeze
        print("1. Initializing BreezeConnect...")
        breeze = BreezeConnect(api_key=api_key)
        print("   ✅ BreezeConnect initialized")
        
        # Set client code
        print("2. Setting client code...")
        breeze.user_id = client_code
        print(f"   ✅ Client code set: {client_code}")
        
        # Test session generation
        print("3. Testing session generation...")
        try:
            session_response = breeze.generate_session(
                api_secret=api_secret,
                session_token=session_token
            )
            print(f"   ✅ Session generation response: {session_response}")
        except Exception as e:
            print(f"   ❌ Session generation failed: {e}")
            return False
        
        # Test customer details
        print("4. Testing customer details...")
        customer_details = breeze.get_customer_details()
        print(f"   Customer details response: {customer_details}")
        
        # Check response structure
        if isinstance(customer_details, dict):
            if customer_details.get('Status') == 200:
                print("   ✅ Session validation successful!")
                if 'Success' in customer_details:
                    user_name = customer_details['Success'].get('idirect_user_name', 'Unknown')
                    print(f"   👤 User: {user_name}")
                return True
            else:
                error_msg = customer_details.get('Error', 'Unknown error')
                print(f"   ❌ Session validation failed: {error_msg}")
                return False
        else:
            print(f"   ❌ Unexpected response format: {type(customer_details)}")
            return False
            
    except Exception as e:
        print(f"   ❌ Critical error: {e}")
        return False

def generate_fresh_login_url():
    """Generate fresh login URL with proper encoding"""
    load_dotenv()
    api_key = os.getenv('BREEZE_API_KEY')
    
    if not api_key:
        print("❌ BREEZE_API_KEY not found")
        return None
    
    encoded_key = quote_plus(api_key)
    login_url = f"https://api.icicidirect.com/apiuser/login?api_key={encoded_key}"
    
    return login_url

def extract_and_validate_url():
    """Interactive URL extraction and validation"""
    print("\n🔗 URL Session Token Extraction")
    print("=" * 50)
    
    url = input("Paste your redirect URL: ").strip()
    
    if not url.startswith('http'):
        print("❌ Invalid URL format")
        return None
    
    # Extract session token
    from urllib.parse import urlparse, parse_qs
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    # Try multiple parameter names
    session_token = (
        query_params.get('apisession', [None])[0] or
        query_params.get('session_token', [None])[0] or
        query_params.get('api_session', [None])[0] or
        query_params.get('token', [None])[0]
    )
    
    if session_token:
        print(f"✅ Extracted: {session_token}")
        return session_token
    else:
        print("❌ No session token found")
        print("Available parameters:", list(query_params.keys()))
        return None

def main():
    """Main validation workflow"""
    print("🚀 ICICI Breeze Session Validator")
    print("=" * 60)
    
    # Step 1: Validate environment
    if not validate_environment():
        print("\n💡 Please check your .env file and restart")
        return
    
    # Step 2: Get current session token
    current_token = os.getenv('BREEZE_SESSION_TOKEN', '').strip('"')
    
    if current_token:
        print(f"\n📋 Current session token: {current_token}")
        test_result = test_session_with_debug(current_token)
        
        if test_result:
            print("\n🎉 SUCCESS: Session token is valid!")
            return
        else:
            print("\n🔄 Current token is invalid, need fresh token")
    
    # Step 3: Generate fresh login URL
    login_url = generate_fresh_login_url()
    if login_url:
        print(f"\n🌐 Fresh login URL:")
        print(login_url)
        print("\n📋 Steps:")
        print("1. Open this URL in browser")
        print("2. Login with ICICI credentials")
        print("3. Copy the redirect URL")
        print("4. Paste here to extract session token")
    
    # Step 4: Interactive extraction
    new_token = extract_and_validate_url()
    if new_token:
        # Test new token
        if test_session_with_debug(new_token):
            print("\n✅ New token is valid!")
            
            # Save to .env
            save = input("Save to .env file? (y/n): ").lower()
            if save == 'y':
                with open('.env', 'r') as f:
                    lines = f.readlines()
                
                with open('.env', 'w') as f:
                    updated = False
                    for line in lines:
                        if line.startswith('BREEZE_SESSION_TOKEN='):
                            f.write(f'BREEZE_SESSION_TOKEN="{new_token}"\n')
                            updated = True
                        else:
                            f.write(line)
                    
                    if not updated:
                        f.write(f'BREEZE_SESSION_TOKEN="{new_token}"\n')
                
                print("✅ .env file updated!")
                print("🔄 Restart your trading system")
        else:
            print("❌ New token is also invalid")

if __name__ == "__main__":
    main()