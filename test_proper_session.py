#!/usr/bin/env python3
"""
Test script to verify proper Breeze API session generation
Based on official documentation analysis
"""

import os
from breeze_connect import BreezeConnect
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

def test_session_generation():
    """Test proper session generation as per documentation"""
    
    # Get API credentials from environment
    api_key = os.getenv("BREEZE_API_KEY")
    api_secret = os.getenv("BREEZE_API_SECRET")
    
    if not api_key or not api_secret:
        print("❌ Missing API credentials in .env file")
        print("Required: BREEZE_API_KEY, BREEZE_API_SECRET")
        return False
    
    print("🔑 API Key found in environment")
    print(f"📋 API Key: {api_key[:10]}...")
    
    # Step 1: Get fresh API session from browser
    print("\n" + "="*50)
    print("STEP 1: Get API Session from Browser")
    print("="*50)
    print(f"🌐 Go to this URL and login:")
    print(f"https://api.icicidirect.com/apiuser/login?api_key={api_key}")
    print("📋 Copy the api_session value from URL after login")
    
    try:
        api_session = input("\n🔍 Enter api_session from browser: ").strip()
        
        if not api_session:
            print("❌ No API session provided")
            return False
            
        print(f"✅ API Session received: {api_session[:20]}...")
        
        # Step 2: Initialize BreezeConnect and generate proper session
        print("\n" + "="*50)
        print("STEP 2: Generate Proper Session Token")
        print("="*50)
        
        breeze = BreezeConnect(api_key=api_key)
        
        # Generate session using browser session
        session_response = breeze.generate_session(
            api_secret=api_secret,
            session_token=api_session
        )
        
        print("✅ Session generated successfully!")
        print(f"📊 Session Response: {json.dumps(session_response, indent=2)}")
        
        # Step 3: Test customer details API
        print("\n" + "="*50)
        print("STEP 3: Test Customer Details API")
        print("="*50)
        
        customer_details = breeze.get_customer_details()
        print("✅ Customer details retrieved!")
        print(f"📋 Customer Details: {json.dumps(customer_details, indent=2)}")
        
        # Step 4: Test order placement with documentation format
        print("\n" + "="*50)
        print("STEP 4: Test Order Placement")
        print("="*50)
        
        # Test with ITC as suggested in documentation
        test_order = breeze.place_order(
            stock_code="ITC",
            exchange_code="NSE",
            product="cash",
            action="buy",
            order_type="limit",
            quantity="1",
            price="400",
            validity="day"
        )
        
        print("✅ Order placement attempted!")
        print(f"📊 Order Response: {json.dumps(test_order, indent=2)}")
        
        # Save working session details
        session_info = {
            "api_key": api_key,
            "session_token": api_session,
            "customer_details": customer_details,
            "test_order_response": test_order,
            "timestamp": str(pd.Timestamp.now())
        }
        
        with open("working_session.json", "w") as f:
            json.dump(session_info, f, indent=2)
        
        print("\n" + "="*50)
        print("✅ SUCCESS: All tests completed!")
        print("="*50)
        print("📁 Session details saved to working_session.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        return False

def verify_env_file():
    """Verify .env file has required variables"""
    
    required_vars = [
        "BREEZE_API_KEY",
        "BREEZE_API_SECRET",
        "BREEZE_SESSION_TOKEN"
    ]
    
    print("\n" + "="*50)
    print("ENVIRONMENT VARIABLES CHECK")
    print("="*50)
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Found")
        else:
            print(f"❌ {var}: Missing")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing variables: {', '.join(missing_vars)}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Breeze API Session Test")
    print("Based on official documentation analysis")
    print("="*50)
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("❌ .env file not found in current directory")
        print("Please create .env file with:")
        print("BREEZE_API_KEY=your_api_key")
        print("BREEZE_API_SECRET=your_secret_key")
        print("BREEZE_SESSION_TOKEN=your_session_token")
        exit(1)
    
    # Verify environment variables
    if not verify_env_file():
        print("\n❌ Please fix missing environment variables first")
        exit(1)
    
    # Run session test
    success = test_session_generation()
    
    if success:
        print("\n🎉 Session test completed successfully!")
        print("You can now use the session details for trading")
    else:
        print("\n❌ Session test failed. Please check the error messages above")