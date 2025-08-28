# create_env_file.py - Script to create .env file with API credentials

import os
import getpass
from datetime import datetime

def create_env_file():
    """Create a .env file with API credentials"""
    print("\n===== .env File Creator =====\n")
    print("This script will help you create a .env file with your API credentials.")
    print("The .env file is required for the minimal trading system to work.")
    print("\nNOTE: Your credentials will be stored in a local .env file and will not be transmitted anywhere.")
    
    # Check if .env file already exists
    if os.path.exists(".env"):
        print("\nWARNING: A .env file already exists!")
        backup = input("Would you like to create a backup before proceeding? (y/n): ").lower()
        if backup == 'y':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f".env.backup_{timestamp}"
            try:
                with open(".env", "r") as src, open(backup_file, "w") as dst:
                    dst.write(src.read())
                print(f"Backup created: {backup_file}")
            except Exception as e:
                print(f"Error creating backup: {e}")
                return
        
        overwrite = input("Do you want to overwrite the existing .env file? (y/n): ").lower()
        if overwrite != 'y':
            print("Operation cancelled.")
            return
    
    # Collect credentials
    print("\nPlease enter your API credentials:")
    
    # Breeze API credentials
    breeze_api_key = input("Breeze API Key: ")
    breeze_api_secret = getpass.getpass("Breeze API Secret: ")
    breeze_session_token = getpass.getpass("Breeze Session Token: ")
    icici_client_code = input("ICICI Client Code: ")
    
    # Email configuration
    print("\nEmail configuration (for notifications):")
    email_host = input("Email SMTP Host (e.g., smtp.gmail.com): ")
    email_port = input("Email SMTP Port (e.g., 587): ")
    email_user = input("Email Username: ")
    email_pass = getpass.getpass("Email Password: ")
    email_recipient = input("Email Recipient (where to send alerts): ")
    
    # Additional API keys (optional)
    print("\nAdditional API keys (optional, press Enter to skip):")
    alpha_vantage_key = input("Alpha Vantage API Key: ")
    fred_api_key = input("FRED API Key: ")
    perplexity_api_key = input("Perplexity API Key: ")
    
    # Create .env file
    try:
        with open(".env", "w") as f:
            f.write(f"# Breeze API credentials\n")
            f.write(f"BREEZE_API_KEY={breeze_api_key}\n")
            f.write(f"BREEZE_API_SECRET={breeze_api_secret}\n")
            f.write(f"BREEZE_SESSION_TOKEN={breeze_session_token}\n")
            f.write(f"ICICI_CLIENT_CODE={icici_client_code}\n\n")
            
            f.write(f"# Email configuration\n")
            f.write(f"EMAIL_HOST={email_host}\n")
            f.write(f"EMAIL_PORT={email_port}\n")
            f.write(f"EMAIL_USER={email_user}\n")
            f.write(f"EMAIL_PASS={email_pass}\n")
            f.write(f"EMAIL_RECIPIENT={email_recipient}\n\n")
            
            f.write(f"# Additional API keys (optional)\n")
            if alpha_vantage_key:
                f.write(f"ALPHA_VANTAGE_KEY={alpha_vantage_key}\n")
            if fred_api_key:
                f.write(f"FRED_API_KEY={fred_api_key}\n")
            if perplexity_api_key:
                f.write(f"PERPLEXITY_API_KEY={perplexity_api_key}\n")
            
            f.write(f"\n# Created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print("\n✅ .env file created successfully!")
        print("Your API credentials have been saved to .env")
        print("\nYou can now run the minimal trading system.")
        
    except Exception as e:
        print(f"\n❌ Error creating .env file: {e}")

if __name__ == "__main__":
    create_env_file()