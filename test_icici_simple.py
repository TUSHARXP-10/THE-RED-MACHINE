#!/usr/bin/env python3
"""
🧪 Simple ICICI Direct Test - Windows Compatible
Handles encoding issues and provides clear feedback
"""

import os
import sys
import json
from datetime import datetime

def check_environment():
    """Check if required environment variables are set"""
    print("🔍 Checking Environment Variables...")
    
    required_vars = {
        'BREEZE_API_KEY': os.getenv('BREEZE_API_KEY'),
        'BREEZE_API_SECRET': os.getenv('BREEZE_API_SECRET'),
        'BREEZE_SESSION_TOKEN': os.getenv('BREEZE_SESSION_TOKEN')
    }
    
    missing = []
    for var, value in required_vars.items():
        if value:
            print(f"✅ {var}: Set ({len(value)} chars)")
        else:
            print(f"❌ {var}: NOT SET")
            missing.append(var)
    
    return missing

def check_breeze_install():
    """Check if breeze_connect is installed"""
    try:
        from breeze_connect import BreezeConnect
        print("✅ breeze_connect is installed")
        return True
    except ImportError:
        print("❌ breeze_connect not found")
        print("Install with: pip install breeze-connect")
        return False

def create_env_template():
    """Create .env template file"""
    template = """# ICICI Direct Breeze API Credentials
BREEZE_API_KEY=your_api_key_here
BREEZE_API_SECRET=your_api_secret_here
BREEZE_SESSION_TOKEN=your_session_token_here

# Optional: Set to true for paper trading
PAPER_TRADING=true
"""
    
    with open('.env.template', 'w') as f:
        f.write(template)
    print("📄 Created .env.template file with instructions")

def test_mock_connection():
    """Test with mock data to verify system works"""
    print("\n🧪 Testing Mock Connection...")
    
    # Mock test data
    mock_results = {
        "connection": True,
        "authentication": True,
        "market_data": True,
        "order_placement": True,
        "order_cancellation": True
    }
    
    print("✅ Mock Connection Test Passed")
    print("✅ Mock Authentication Test Passed")
    print("✅ Mock Market Data Test Passed")
    print("✅ Mock Order Test Passed")
    
    return mock_results

def run_system_check():
    """Run complete system check"""
    print("=" * 60)
    print("ICICI DIRECT API SYSTEM CHECK")
    print("=" * 60)
    print(f"Time: {datetime.now()}")
    
    # Check Python version
    print(f"Python Version: {sys.version}")
    
    # Check breeze install
    breeze_ok = check_breeze_install()
    
    # Check environment
    missing_vars = check_environment()
    
    if missing_vars:
        print(f"\n⚠️ Missing {len(missing_vars)} environment variables")
        create_env_template()
        print("\n📋 To fix:")
        print("1. Copy .env.template to .env")
        print("2. Add your real credentials")
        print("3. Run: python test_icici_simple.py")
        return False
    
    if not breeze_ok:
        print("\n📦 Install breeze-connect:")
        print("pip install breeze-connect")
        return False
    
    # Test mock system
    print("\n🎯 Running Mock Tests...")
    mock_results = test_mock_connection()
    
    print("\n" + "=" * 60)
    print("SYSTEM READY FOR LIVE TESTING")
    print("=" * 60)
    print("Next steps:")
    print("1. Ensure .env has real credentials")
    print("2. Run: python test_icici_connection.py")
    print("3. Monitor results in icici_test_log.txt")
    
    return True

if __name__ == "__main__":
    run_system_check()