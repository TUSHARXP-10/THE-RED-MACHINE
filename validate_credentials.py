#!/usr/bin/env python3
"""
ICICI Direct Credentials Validator
==================================
Simple script to validate API credentials format and provide guidance.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def validate_credentials():
    """Validate ICICI Direct API credentials format"""
    
    print("🔍 ICICI Direct Credentials Validator")
    print("=" * 40)
    
    # Check required variables
    required_vars = {
        "BREEZE_API_KEY": "Your API key from ICICI Direct",
        "BREEZE_API_SECRET": "Your API secret from ICICI Direct", 
        "BREEZE_SESSION_TOKEN": "Session token from ICICI Direct portal"
    }
    
    all_valid = True
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        
        if not value:
            print(f"❌ {var}: MISSING")
            print(f"   Description: {description}")
            all_valid = False
            continue
            
        # Basic format validation
        if var == "BREEZE_API_KEY":
            if len(value) < 20:
                print(f"⚠️  {var}: SUSPICIOUS (length: {len(value)})")
                print(f"   Expected: Usually 30+ characters")
                all_valid = False
            else:
                print(f"✅ {var}: OK (length: {len(value)})")
                
        elif var == "BREEZE_API_SECRET":
            if len(value) < 20:
                print(f"⚠️  {var}: SUSPICIOUS (length: {len(value)})")
                print(f"   Expected: Usually 30+ characters")
                all_valid = False
            else:
                print(f"✅ {var}: OK (length: {len(value)})")
                
        elif var == "BREEZE_SESSION_TOKEN":
            if len(value) < 5:
                print(f"⚠️  {var}: SUSPICIOUS (length: {len(value)})")
                print(f"   Expected: Usually 6-10 digits")
                all_valid = False
            else:
                print(f"✅ {var}: OK (length: {len(value)})")
    
    print("\n" + "=" * 40)
    
    if all_valid:
        print("🎉 All credentials appear properly formatted!")
        print("\nNext Steps:")
        print("1. Verify credentials are correct from ICICI Direct portal")
        print("2. Ensure session token is current (expires every 24 hours)")
        print("3. Check if API key is activated for trading")
        print("4. Run: python test_icici_connection.py")
    else:
        print("❌ Credential issues detected!")
        print("\nTo fix:")
        print("1. Login to ICICI Direct Breeze API portal")
        print("2. Generate new API credentials")
        print("3. Update your .env file with correct values")
        print("4. Generate new session token (expires daily)")
        print("5. Run this validator again")
    
    return all_valid

if __name__ == "__main__":
    validate_credentials()