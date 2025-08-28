import os
import sys
import subprocess
import webbrowser

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        return False
    return True

def install_requirements():
    """Install required packages from requirements.txt"""
    print("\n📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def setup_env_file():
    """Create or update .env file with Kite API credentials"""
    print("\n🔑 Setting up environment variables...")
    
    # Check if .env file exists
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
    else:
        env_content = ""
    
    # Check if Kite API credentials already exist
    kite_api_key = None
    kite_api_secret = None
    zerodha_client_id = None
    
    if "KITE_API_KEY" in env_content:
        kite_api_key = input("KITE_API_KEY already exists. Enter new value or press Enter to keep existing: ")
    else:
        kite_api_key = input("Enter your Kite API Key: ")
    
    if "KITE_API_SECRET" in env_content:
        kite_api_secret = input("KITE_API_SECRET already exists. Enter new value or press Enter to keep existing: ")
    else:
        kite_api_secret = input("Enter your Kite API Secret: ")
    
    if "ZERODHA_CLIENT_ID" in env_content:
        zerodha_client_id = input("ZERODHA_CLIENT_ID already exists. Enter new value or press Enter to keep existing: ")
    else:
        zerodha_client_id = input("Enter your Zerodha Client ID: ")
    
    # Update .env file
    env_lines = env_content.split('\n')
    updated_lines = []
    
    # Update existing variables
    kite_api_key_updated = False
    kite_api_secret_updated = False
    zerodha_client_id_updated = False
    
    for line in env_lines:
        if line.startswith("KITE_API_KEY=") and kite_api_key:
            updated_lines.append(f"KITE_API_KEY={kite_api_key}")
            kite_api_key_updated = True
        elif line.startswith("KITE_API_SECRET=") and kite_api_secret:
            updated_lines.append(f"KITE_API_SECRET={kite_api_secret}")
            kite_api_secret_updated = True
        elif line.startswith("ZERODHA_CLIENT_ID=") and zerodha_client_id:
            updated_lines.append(f"ZERODHA_CLIENT_ID={zerodha_client_id}")
            zerodha_client_id_updated = True
        else:
            updated_lines.append(line)
    
    # Add new variables if they don't exist
    if not kite_api_key_updated and kite_api_key:
        updated_lines.append(f"KITE_API_KEY={kite_api_key}")
    
    if not kite_api_secret_updated and kite_api_secret:
        updated_lines.append(f"KITE_API_SECRET={kite_api_secret}")
    
    if not zerodha_client_id_updated and zerodha_client_id:
        updated_lines.append(f"ZERODHA_CLIENT_ID={zerodha_client_id}")
    
    # Add KITE_ACCESS_TOKEN if it doesn't exist
    if "KITE_ACCESS_TOKEN" not in env_content:
        updated_lines.append("KITE_ACCESS_TOKEN=")
    
    # Write updated content to .env file
    with open('.env', 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print("✅ Environment variables set up successfully")
    return True

def open_kite_developer_portal():
    """Open Kite Developer Portal in browser"""
    print("\n🌐 Opening Kite Developer Portal...")
    webbrowser.open("https://developers.kite.trade/")

def main():
    print("\n🚀 Kite API Setup Utility")
    print("========================\n")
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install requirements
    if not install_requirements():
        return
    
    # Open Kite Developer Portal
    open_kite_developer_portal()
    
    # Set up environment variables
    if not setup_env_file():
        return
    
    print("\n✅ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run 'python fix_kite_session.py' to generate an access token")
    print("2. Run 'python test_kite_connector.py' to test the connection")

if __name__ == "__main__":
    main()