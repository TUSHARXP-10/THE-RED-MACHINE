import os
from dotenv import load_dotenv, set_key

def update_env_file(key, value):
    """Update a specific key in the .env file"""
    dotenv_path = os.path.join(os.getcwd(), '.env')
    set_key(dotenv_path, key, value)
    print(f"✅ Updated {key} in .env file")

def fix_api_key_format():
    """Fix the API key format by removing quotes"""
    load_dotenv()
    
    # Get current values
    api_key = os.getenv("KITE_API_KEY", "")
    api_secret = os.getenv("KITE_API_SECRET", "")
    redirect_url = os.getenv("KITE_REDIRECT_URL", "")
    
    # Strip quotes if present
    if api_key:
        api_key = api_key.strip("'\"")
    if api_secret:
        api_secret = api_secret.strip("'\"")
    if redirect_url:
        redirect_url = redirect_url.strip("'\"")
    
    print("Current API credentials:")
    print(f"KITE_API_KEY: {api_key}")
    print(f"KITE_API_SECRET: {api_secret}")
    print(f"KITE_REDIRECT_URL: {redirect_url}")
    
    # Update with correct format (no quotes)
    update_env_file("KITE_API_KEY", api_key)
    update_env_file("KITE_API_SECRET", api_secret)
    update_env_file("KITE_REDIRECT_URL", redirect_url)
    
    print("\n✅ API credentials updated with correct format")
    print("Please try running the Kite session fix script again")

if __name__ == "__main__":
    print("🔧 Fixing Kite API key format in .env file...\n")
    fix_api_key_format()