"""
Manual Session Token Extractor for ICICI Breeze API
Provides multiple methods to extract valid session tokens
"""

import os
import webbrowser
from urllib.parse import urlparse, parse_qs, quote_plus
from dotenv import load_dotenv

def print_login_url():
    """Print the correct login URL for manual access"""
    load_dotenv()
    api_key = os.getenv("BREEZE_API_KEY")
    
    if not api_key:
        print("❌ BREEZE_API_KEY not found in .env file")
        return
    
    encoded_key = quote_plus(api_key)
    login_url = f"https://api.icicidirect.com/apiuser/login?api_key={encoded_key}"
    
    print("🌐 LOGIN URL:")
    print("=" * 50)
    print(login_url)
    print("=" * 50)
    print("\n📋 COPY THIS URL and open in your browser")
    
    # Also create a local HTML file for easy access
    with open('login_redirect.html', 'w') as f:
        f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <title>ICICI Breeze Login</title>
    <meta http-equiv="refresh" content="0; url={login_url}">
</head>
<body>
    <p>Redirecting to ICICI Breeze login...</p>
    <p>If not redirected, <a href="{login_url}">click here</a></p>
</body>
</html>
""")
    print("📄 login_redirect.html created - open this file in browser")

def extract_session_from_url(url):
    """Extract session token from redirect URL"""
    try:
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
            print(f"✅ Extracted session token: {session_token}")
            return session_token
        else:
            print("❌ No session token found in URL")
            print("Available parameters:", list(query_params.keys()))
            return None
    except Exception as e:
        print(f"❌ URL parsing error: {e}")
        return None

def validate_session_token(token):
    """Quick validation of session token format"""
    if not token:
        return False
    
    # Check if it's purely numeric or alphanumeric
    if token.isdigit() or token.isalnum():
        print(f"✅ Token format valid: {len(token)} characters")
        return True
    else:
        print("❌ Token contains invalid characters")
        return False

def manual_extraction_guide():
    """Print comprehensive extraction guide"""
    print("""
🎯 **COMPLETE SESSION TOKEN EXTRACTION GUIDE**

**METHOD 1: Developer Tools (Most Reliable)**
1. Press F12 to open Developer Tools
2. Go to Network tab
3. Navigate to login URL: https://api.icicidirect.com/apiuser/login?api_key=YOUR_KEY
4. Login with credentials
5. Look for "API_Session" in Form Data

**METHOD 2: URL Analysis**
After login, check the redirect URL for:
- ?apisession=TOKEN
- ?session_token=TOKEN  
- ?api_session=TOKEN

**METHOD 3: Page Source**
1. Right-click on success page
2. View page source
3. Search for "session" or "token"

**METHOD 4: Browser Console**
1. Press F12 → Console tab
2. Type: window.location.href
3. Copy the full URL

**METHOD 5: Network Headers**
1. In Developer Tools → Network
2. Click on any request after login
3. Check Request Headers for session info

**IMPORTANT:**
- Session tokens expire at midnight IST
- Always copy the COMPLETE URL
- Token should be 6-12 characters (numbers/letters)
""")

def interactive_extractor():
    """Interactive session token extractor"""
    print("🔍 ICICI Breeze Session Token Extractor")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Print login URL")
        print("2. Extract from redirect URL")
        print("3. Show extraction guide")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            print_login_url()
        elif choice == "2":
            url = input("Paste your redirect URL: ").strip()
            token = extract_session_from_url(url)
            if token:
                validate_session_token(token)
                save = input("Save to .env file? (y/n): ").lower()
                if save == 'y':
                    update_env_file(token)
        elif choice == "3":
            manual_extraction_guide()
        elif choice == "4":
            break
        else:
            print("Invalid choice")

def update_env_file(token):
    """Update .env file with new token"""
    env_path = '.env'
    
    try:
        with open(env_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []
    
    with open(env_path, 'w') as f:
        updated = False
        for line in lines:
            if line.startswith('BREEZE_SESSION_TOKEN='):
                f.write(f'BREEZE_SESSION_TOKEN="{token}"\n')
                updated = True
            else:
                f.write(line)
        
        if not updated:
            f.write(f'BREEZE_SESSION_TOKEN="{token}"\n')
    
    print("✅ .env file updated successfully!")

if __name__ == "__main__":
    interactive_extractor()