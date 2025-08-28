#!/usr/bin/env python3
"""
Simple test script to verify Breeze API session generation
Without external dependencies
"""

import os
import sys
import json
from datetime import datetime

try:
    from breeze_connect import BreezeConnect
except ImportError:
    print("❌ breeze-connect library not installed")
    print("Install with: pip install breeze-connect")
    sys.exit(1)

def test_session():
    """Test basic session generation"""
    
    # Check if .env file exists
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
            print("✅ .env file found")
            
            # Parse key variables
            lines = env_content.strip().split('\n')
            api_key = None
            api_secret = None
            
            for line in lines:
                if line.startswith('BREEZE_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                elif line.startswith('BREEZE_API_SECRET='):
                    api_secret = line.split('=', 1)[1].strip()
            
            if not api_key or not api_secret:
                print("❌ Missing API credentials in .env")
                return False
                
            print(f"✅ API Key: {api_key[:10]}...")
            print(f"✅ API Secret: {api_secret[:10]}...")
            
    except FileNotFoundError:
        print("❌ .env file not found")
        return False
    
    # Step 1: Get API session from browser
    print("\n" + "="*50)
    print("STEP 1: Get API Session from Browser")
    print("="*50)
    print(f"🌐 Go to: https://api.icicidirect.com/apiuser/login?api_key={api_key}")
    print("📋 After login, copy the api_session value from the URL")
    
    try:
        api_session = input("\n🔍 Enter api_session: ").strip()
        
        if not api_session:
            print("❌ No session provided")
            return False
            
        # Step 2: Initialize and generate session
        print("\n" + "="*50)
        print("STEP 2: Generate Session")
        print("="*50)
        
        breeze = BreezeConnect(api_key=api_key)
        
        session_response = breeze.generate_session(
            api_secret=api_secret,
            session_token=api_session
        )
        
        print("✅ Session generated!")
        print(f"📊 Response: {json.dumps(session_response, indent=2)}")
        
        # Step 3: Test customer details
        print("\n" + "="*50)
        print("STEP 3: Test Customer Details")
        print("="*50)
        
        try:
            customer_details = breeze.get_customer_details()
            print("✅ Customer details retrieved!")
            print(f"📋 Details: {json.dumps(customer_details, indent=2)}")
            
            # Save session info
            session_info = {
                "timestamp": str(datetime.now()),
                "session_response": session_response,
                "customer_details": customer_details
            }
            
            with open("session_test_result.json", "w") as f:
                json.dump(session_info, f, indent=2)
            
            print("\n✅ Test completed successfully!")
            print("📁 Results saved to session_test_result.json")
            
            return True
            
        except Exception as e:
            print(f"❌ Customer details failed: {e}")
            return False
            
    except KeyboardInterrupt:
        print("\n❌ Test interrupted")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Simple Breeze API Session Test")
    print("="*50)
    
    success = test_session()
    
    if success:
        print("\n🎉 Session test passed!")
    else:
        print("\n❌ Session test failed")