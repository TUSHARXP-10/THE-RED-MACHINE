#!/usr/bin/env python3
"""
🔧 ICICI Direct Credentials Setup Script
Helps users safely configure their API credentials for testing
"""

import os
import getpass
import json
from datetime import datetime

def setup_credentials():
    """Interactive setup for ICICI Direct credentials"""
    print("🔧 ICICI Direct Credentials Setup")
    print("=" * 50)
    print("This will help you set up your API credentials safely.")
    print("\n⚠️ IMPORTANT: Never share these credentials!")
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("\n📋 Found existing .env file")
        with open('.env', 'r') as f:
            print("Current configuration:")
            print(f.read())
        
        choice = input("\nOverwrite existing .env? (y/N): ").strip().lower()
        if choice != 'y':
            print("Setup cancelled. Using existing .env")
            return
    
    # Get credentials interactively
    print("\n📝 Enter your ICICI Direct API credentials:")
    print("(These will be saved to .env file)")
    
    api_key = getpass.getpass("BREEZE_API_KEY: ").strip()
    api_secret = getpass.getpass("BREEZE_API_SECRET: ").strip()
    session_token = getpass.getpass("BREEZE_SESSION_TOKEN: ").strip()
    
    if not all([api_key, api_secret, session_token]):
        print("❌ All credentials are required!")
        return
    
    # Create .env file
    env_content = f"""# ICICI Direct Breeze API Credentials
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

BREEZE_API_KEY={api_key}
BREEZE_API_SECRET={api_secret}
BREEZE_SESSION_TOKEN={session_token}

# Optional: Set to true for paper trading mode
PAPER_TRADING=true

# Optional: Set to false when ready for live trading
# PAPER_TRADING=false
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    # Create credentials backup
    backup_data = {
        "setup_date": datetime.now().isoformat(),
        "note": "Store this securely - you'll need these daily",
        "instructions": [
            "Session tokens expire daily - refresh via ICICI login",
            "Test credentials with: python comprehensive_icici_test.py",
            "Monitor logs: type comprehensive_icici_test.log"
        ]
    }
    
    with open('credentials_backup.json', 'w') as f:
        json.dump(backup_data, f, indent=2)
    
    print("\n✅ Credentials setup complete!")
    print("📁 Files created:")
    print("  - .env (your credentials)")
    print("  - credentials_backup.json (setup info)")
    print("\n🎯 Next steps:")
    print("1. Run: python comprehensive_icici_test.py")
    print("2. Check results in comprehensive_icici_test.log")
    print("3. Follow SAFETY_CHECKLIST.md before live trading")

def verify_setup():
    """Verify the setup is working"""
    if not os.path.exists('.env'):
        print("❌ .env file not found. Run setup first.")
        return False
    
    # Check if credentials are set
    required_vars = ['BREEZE_API_KEY', 'BREEZE_API_SECRET', 'BREEZE_SESSION_TOKEN']
    missing = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        return False
    
    print("✅ Setup verification passed!")
    return True

if __name__ == "__main__":
    print("ICICI Direct Setup Tool")
    print("=" * 30)
    
    while True:
        print("\nOptions:")
        print("1. Setup new credentials")
        print("2. Verify existing setup")
        print("3. Exit")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == '1':
            setup_credentials()
        elif choice == '2':
            verify_setup()
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")