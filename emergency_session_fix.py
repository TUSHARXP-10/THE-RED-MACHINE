"""
Emergency Session Fix for ICICI Breeze API
Implements official ICICI documentation methods
"""

import os
import webbrowser
import time
from urllib.parse import quote_plus, urlparse, parse_qs
from breeze_connect import BreezeConnect
from dotenv import load_dotenv

def get_fresh_session():
    """Get fresh session using official ICICI method"""
    load_dotenv()
    
    api_key = os.getenv('BREEZE_API_KEY')
    api_secret = os.getenv('BREEZE_API_SECRET')
    client_code = os.getenv('ICICI_CLIENT_CODE')
    
    if not all([api_key, api_secret, client_code]):
        print("Missing credentials in .env")
        return None
    
    # Generate login URL
    encoded_key = quote_plus(api_key)
    login_url = f"https://api.icicidirect.com/apiuser/login?api_key={encoded_key}"
    
    print("EMERGENCY SESSION FIX")
    print("=" * 60)
    print(f"Login URL: {login_url}")
    print("\nCRITICAL STEPS:")
    print("1. Open above URL in browser (incognito mode)")
    print("2. Login with ICICI credentials")
    print("3. After login, look for session token in TWO places:")
    print("   URL: http://localhost/?apisession=XXXXXXX")
    print("   Left panel: API Session value")
    
    # Create HTML redirect
    with open('emergency_login.html', 'w', encoding='utf-8') as f:
        f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Emergency Session Login</title>
    <style>
        body {{ font-family: Arial; margin: 40px; }}
        .url {{ background: #f0f0f0; padding: 10px; margin: 10px 0; }}
        .steps {{ background: #e8f4f8; padding: 20px; border-radius: 5px; }}
    </style>
    <meta http-equiv="refresh" content="0; url={login_url}">
</head>
<body>
    <h2>Emergency Session Fix</h2>
    <div class="url">
        <strong>Login URL:</strong><br>
        <a href="{login_url}" target="_blank">{login_url}</a>
    </div>
    <div class="steps">
        <h3>Steps to get session token:</h3>
        <ol>
            <li>Click the login URL above</li>
            <li>Enter ICICI credentials</li>
            <li>After successful login, look for:</li>
            <ul>
                <li><strong>URL:</strong> http://localhost/?apisession=XXXXXXX</li>
                <li><strong>Page:</strong> API Session value on left panel</li>
            </ul>
            <li>Copy the complete session token</li>
        </ol>
    </div>
</body>
</html>
""")
    
    print("\nemergency_login.html created")
    webbrowser.open('emergency_login.html')
    
    return login_url

def validate_extracted_token(session_token):
    """Validate extracted session token"""
    if not session_token:
        return False
    
    # Basic validation
    if len(session_token) < 5 or len(session_token) > 20:
        print(f"Invalid token length: {len(session_token)}")
        return False
    
    if not session_token.isalnum():
        print(f"Token contains invalid characters: {session_token}")
        return False
    
    print(f"Token format valid: {session_token}")
    return True

def test_session_comprehensive(session_token):
    """Comprehensive session testing"""
    load_dotenv()
    
    api_key = os.getenv('BREEZE_API_KEY')
    api_secret = os.getenv('BREEZE_API_SECRET')
    client_code = os.getenv('ICICI_CLIENT_CODE')
    
    print(f"\n🔍 Testing session: {session_token}")
    print("=" * 50)
    
    try:
        # Initialize
        breeze = BreezeConnect(api_key=api_key)
        breeze.user_id = client_code
        
        # Method 1: Standard session generation
        print("1. Standard session generation...")
        try:
            session_resp = breeze.generate_session(
                api_secret=api_secret,
                session_token=session_token
            )
            print(f"   Session response: {session_resp}")
        except Exception as e:
            print(f"   Session generation error: {e}")
        
        # Method 2: Direct session assignment
        print("2. Direct session assignment...")
        breeze.session_key = session_token
        
        # Method 3: Customer details test
        print("3. Testing customer details...")
        customer = breeze.get_customer_details()
        print(f"   Response: {customer}")
        
        if isinstance(customer, dict):
            status = customer.get('Status')
            if status == 200:
                print("   ✅ Session is VALID!")
                user_info = customer.get('Success', {})
                print(f"   👤 User: {user_info.get('idirect_user_name', 'Unknown')}")
                return True
            else:
                error = customer.get('Error', 'Unknown error')
                print(f"   ❌ Session error: {error}")
        
        return False
        
    except Exception as e:
        print(f"   ❌ Critical error: {e}")
        return False

def update_session_in_env(session_token):
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
    
    print("ENV file updated with new session token")

def interactive_fix():
    """Interactive emergency fix"""
    print("EMERGENCY SESSION FIX - Interactive Mode")
    print("=" * 60)
    
    # Step 1: Validate environment
    if not validate_environment():
        return
    
    # Step 2: Get fresh login URL
    login_url = get_fresh_session()
    
    # Step 3: Interactive extraction
    print("\n🔗 Extract session token:")
    redirect_url = input("Paste your redirect URL: ").strip()
    
    # Extract token
    parsed = urlparse(redirect_url)
    params = parse_qs(parsed.query)
    
    session_token = (
        params.get('apisession', [None])[0] or
        params.get('session_token', [None])[0] or
        params.get('api_session', [None])[0]
    )
    
    if not session_token:
        print("❌ No session token found in URL")
        manual_token = input("Enter session token manually: ").strip()
        session_token = manual_token
    
    # Validate token
    if not validate_extracted_token(session_token):
        return
    
    # Test token
    if test_session_comprehensive(session_token):
        # Save token
        update_session_in_env(session_token)
        print("SUCCESS! Session token is now valid")
        print("🔄 Restart your trading system")
    else:
        print("\n❌ Session token still invalid")
        print("💡 Try:")
        print("1. Clear browser cache")
        print("2. Use incognito mode")
        print("3. Generate fresh token")

def validate_environment():
    """Validate environment variables"""
    load_dotenv()
    
    required = ['BREEZE_API_KEY', 'BREEZE_API_SECRET', 'ICICI_CLIENT_CODE']
    missing = []
    
    for var in required:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing: {', '.join(missing)}")
        return False
    
    return True

def main():
    """Main emergency fix"""
    if not validate_environment():
        print("Please check your .env file")
        return
    
    print("ICICI Breeze Emergency Session Fix")
    print("=" * 60)
    print("\nOptions:")
    print("1. Get fresh login URL")
    print("2. Manual session extraction")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        get_fresh_session()
        print("\n📋 Complete the login process and copy the session token")
    elif choice == "2":
        interactive_fix()
    else:
        print("Exiting...")

if __name__ == "__main__":
    main()