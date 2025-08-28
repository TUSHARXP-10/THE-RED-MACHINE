import os
import re
from dotenv import load_dotenv, find_dotenv, set_key

def check_and_fix_env_file():
    """Check the .env file for formatting issues and fix them"""
    # Find the .env file
    dotenv_path = find_dotenv()
    if not dotenv_path:
        print("❌ .env file not found")
        return False
    
    print(f"Found .env file at: {dotenv_path}")
    
    # Load the current environment variables
    load_dotenv(dotenv_path)
    
    # Keys to check
    keys_to_check = [
        "BREEZE_API_KEY",
        "BREEZE_API_SECRET",
        "BREEZE_SESSION_TOKEN",
        "ICICI_CLIENT_CODE",
        "BREEZE_APP_ID"
    ]
    
    fixed_count = 0
    
    # Check each key
    for key in keys_to_check:
        value = os.getenv(key)
        if value:
            # Check if the value has quotes
            if value.startswith('"') and value.endswith('"'):
                # Remove the quotes
                clean_value = value.strip('"')
                set_key(dotenv_path, key, clean_value)
                print(f"✅ Fixed {key}: Removed quotes")
                fixed_count += 1
            elif value.startswith('\'') and value.endswith('\''):
                # Remove the quotes
                clean_value = value.strip('\'') 
                set_key(dotenv_path, key, clean_value)
                print(f"✅ Fixed {key}: Removed single quotes")
                fixed_count += 1
            else:
                print(f"✓ {key} is properly formatted")
        else:
            print(f"⚠️ {key} not found in .env file")
    
    if fixed_count > 0:
        print(f"✅ Fixed {fixed_count} issues in .env file")
    else:
        print("✅ No issues found in .env file")
    
    return True

if __name__ == "__main__":
    check_and_fix_env_file()