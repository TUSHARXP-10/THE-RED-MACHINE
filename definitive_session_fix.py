"""
Definitive Session Fix for ICICI Breeze API
Based on official ICICI documentation and comprehensive analysis
"""

import os
import webbrowser
import requests
from urllib.parse import quote_plus, urlparse, parse_qs
from breeze_connect import BreezeConnect
from dotenv import load_dotenv
import json

def validate_credentials():
    """Validate all credentials are present"""
    load_dotenv()
    
    api_key = os.getenv('BREEZE_API_KEY')
    api_secret = os.getenv('BREEZE_API_SECRET')
    client_code = os.getenv('ICICI_CLIENT_CODE')
    
    missing = []
    if not api_key:
        missing.append('BREEZE_API_KEY')
    elif len(api_key) != 32: # Assuming API keys are 32 characters long, adjust if needed
        print("Warning: BREEZE_API_KEY does not appear to be a valid length (expected 32 characters).")

    if not api_secret:
        missing.append('BREEZE_API_SECRET')
    if not client_code:
        missing.append('ICICI_CLIENT_CODE')
    
    if missing:
        print(f"Missing credentials: {', '.join(missing)}")
        return False
    
    print("All credentials present")
    print(f"API Key: {api_key[:10]}...")
    print(f"Client Code: {client_code}")
    return True

def generate_login_url():
    """Generate proper login URL with encoding"""
    load_dotenv()
    api_key = os.getenv('BREEZE_API_KEY')
    
    if not api_key:
        return None
    
    # Proper encoding for special characters
    encoded_key = quote_plus(api_key)
    login_url = f"https://api.icicidirect.com/apiuser/login?api_key={encoded_key}"
    print(f"Generated login URL: {login_url}")
    return login_url

def extract_session_from_url(redirect_url):
    """Extract session token from redirect URL"""
    if not redirect_url:
        return None
    
    try:
        parsed = urlparse(redirect_url)
        params = parse_qs(parsed.query)
        
        # Try multiple parameter names
        session_token = (
            params.get('apisession', [None])[0] or
            params.get('session_token', [None])[0] or
            params.get('api_session', [None])[0] or
            params.get('session', [None])[0]
        )
        
        return session_token
    except Exception as e:
        print(f"Error extracting from URL: {e}")
        return None

def test_session_comprehensive(session_token):
    """Comprehensive session testing with all methods"""
    load_dotenv()
    
    api_key = os.getenv('BREEZE_API_KEY')
    api_secret = os.getenv('BREEZE_API_SECRET')
    client_code = os.getenv('ICICI_CLIENT_CODE')
    
    print(f"\nTesting session: {session_token}")
    print("=" * 60)
    
    results = {}
    
    try:
        # Method 1: Standard BreezeConnect
        print("\n1. Testing BreezeConnect.generate_session...")
        breeze = BreezeConnect(api_key=api_key)
        
        try:
            session_resp = breeze.generate_session(
                api_secret=api_secret,
                session_token=session_token
            )
            results['breeze_generate'] = {
                'success': True,
                'response': str(session_resp)
            }
            print(f"   ✅ Session generation: {session_resp}")
        except Exception as e:
            results['breeze_generate'] = {
                'success': False,
                'error': str(e)
            }
            print(f"   ❌ Session generation: {e}")
        
        # Method 2: Direct API call
        print("\n2. Testing direct API call...")
        try:
            url = "https://api.icicidirect.com/breezeapi/api/v1/customerdetails"
            headers = {
                'Content-Type': 'application/json',
                'api-key': api_key,
                'session-key': session_token
            }
            print(f"   Direct API URL: {url}")
            print(f"   Direct API Headers: {headers}")
            
            response = requests.get(url, headers=headers)
            results['direct_api'] = {
                'status_code': response.status_code,
                'response': response.text
            }
            
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('Status') == 200:
                    print("   ✅ Direct API success!")
                    return True
                else:
                    print(f"   ❌ API error: {data.get('Error', 'Unknown')}")
            
        except Exception as e:
            results['direct_api'] = {
                'error': str(e)
            }
            print(f"   ❌ Direct API error: {e}")
        
        # Method 3: Customer details via Breeze
        print("\n3. Testing customer details...")
        try:
            breeze.session_key = session_token
            breeze.user_id = client_code
            
            details = breeze.get_customer_details()
            results['customer_details'] = {
                'response': str(details)
            }
            
            print(f"   Details: {details}")
            
            if isinstance(details, dict) and details.get('Status') == 200:
                print("   ✅ Customer details successful!")
                return True
            else:
                print(f"   ❌ Customer details failed: {details}")
        
        except Exception as e:
            results['customer_details'] = {
                'error': str(e)
            }
            print(f"   ❌ Customer details error: {e}")
        
    except Exception as e:
        print(f"Critical error: {e}")
        results['critical_error'] = str(e)
    
    return False

def update_env_file(session_token):
    """Update session token in .env file"""
    env_path = '.env'
    
    try:
        with open(env_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []
    
    updated = False
    new_lines = []
    
    for line in lines:
        if line.startswith('BREEZE_SESSION_TOKEN='):
            new_lines.append(f'BREEZE_SESSION_TOKEN="{session_token}"\n')
            updated = True
        else:
            new_lines.append(line)
    
    if not updated:
        new_lines.append(f'BREEZE_SESSION_TOKEN="{session_token}"\n')
    
    with open(env_path, 'w') as f:
        f.writelines(new_lines)
    
    print(f"Updated .env with session token: {session_token}")

def interactive_session_fix():
    """Interactive session fix with all methods"""
    print("ICICI Breeze Definitive Session Fix")
    print("=" * 60)
    
    # Validate credentials
    if not validate_credentials():
        return False
    
    # Generate login URL
    login_url = generate_login_url()
    if not login_url:
        print("Could not generate login URL")
        return False
    
    print(f"\nLogin URL: {login_url}")
    print("\nSTEPS:")
    print("1. Open this URL in incognito browser")
    print("2. Login with ICICI credentials")
    print("3. Complete OTP if required")
    print("4. After successful login, look for:")
    print("   - URL: http://localhost/?apisession=XXXXXXX")
    print("   - Left panel: 'API Session' value")
    
    # Create HTML helper
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>ICICI Session Fix</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .url {{ background: #f0f0f0; padding: 10px; margin: 10px 0; word-break: break-all; }}
        .steps {{ background: #e8f4f8; padding: 15px; border-radius: 5px; }}
        .warning {{ background: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>ICICI Breeze Session Fix</h2>
        
        <div class="warning">
            <strong>Important:</strong> Use incognito/private browser mode to avoid cache issues
        </div>
        
        <div class="url">
            <strong>Login URL:</strong><br>
            <a href="{login_url}" target="_blank">{login_url}</a>
        </div>
        
        <div class="steps">
            <h3>Step-by-Step Process:</h3>
            <ol>
                <li><strong>Open Developer Tools:</strong> Press F12 or Ctrl+Shift+I</li>
                <li><strong>Go to Network tab</strong></li>
                <li><strong>Click the login URL above</strong></li>
                <li><strong>Login with your ICICI credentials</strong></li>
                <li><strong>Complete OTP if required</strong></li>
                <li><strong>After successful login:</strong>
                    <ul>
                        <li>Check Network tab for "API_Session" in Form Data</li>
                        <li>OR check left panel for "API Session" value</li>
                        <li>OR check URL for apisession parameter</li>
                    </ul>
                </li>
            </ol>
        </div>
    </div>
</body>
</html>
"""
    
    with open('session_fix_guide.html', 'w') as f:
        f.write(html_content)
    
    print("\nCreated session_fix_guide.html")
    webbrowser.open('session_fix_guide.html')
    
    # Get session token from user
    print("\nAfter completing login, paste your session token below:")
    session_token = input("Session token: ").strip()
    
    if not session_token:
        print("No session token provided")
        return False
    
    # Validate token format
    if not session_token.isalnum() or len(session_token) < 5:
        print("Invalid token format")
        return False
    
    # Test session
    print(f"\nTesting session token: {session_token}")
    success = test_session_comprehensive(session_token)
    
    if success:
        update_env_file(session_token)
        print("\n✅ SUCCESS! Session token is now valid")
        print("You can now restart your trading system")
        return True
    else:
        print("\n❌ Session token still invalid")
        print("Try:")
        print("1. Clear browser cache and try again")
        print("2. Use different browser")
        print("3. Check app status at api.icicidirect.com")
        return False

def main():
    """Main function"""
    while True:
        print("\nICICI Breeze Session Fix")
        print("=" * 60)
        print("1. Interactive session fix")
        print("2. Test existing session token")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            interactive_session_fix()
        elif choice == "2":
            token = input("Enter session token to test: ").strip()
            if token:
                test_session_comprehensive(token)
        elif choice == "3":
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()