#!/usr/bin/env python3
"""
Diagnostic script to identify why orders are failing
Tests both equity and FNO order placement
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from breeze_connect import BreezeConnect
    from dotenv import load_dotenv
    
    load_dotenv()
    
    print("🔍 Order Placement Diagnostic")
    print("="*50)
    
    # Get credentials
    api_key = os.getenv("BREEZE_API_KEY")
    api_secret = os.getenv("BREEZE_API_SECRET")
    session_token = os.getenv("BREEZE_SESSION_TOKEN")
    
    if not all([api_key, api_secret, session_token]):
        print("❌ Missing credentials in .env file")
        sys.exit(1)
    
    print("✅ Credentials loaded")
    
    # Initialize BreezeConnect
    breeze = BreezeConnect(api_key=api_key)
    breeze.generate_session(api_secret=api_secret, session_token=session_token)
    
    print("✅ Session generated")
    
    # Test customer details first
    try:
        customer_details = breeze.get_customer_details()
        print("\n📊 Customer Details:")
        success = customer_details.get('Success', {})
        print(f"Trading: {success.get('segments_allowed', {}).get('Trading', 'N/A')}")
        print(f"Equity: {success.get('segments_allowed', {}).get('Equity', 'N/A')}")
        print(f"Derivatives: {success.get('segments_allowed', {}).get('Derivatives', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Customer details failed: {e}")
    
    # Test 1: Equity Order (Current approach)
    print("\n" + "="*50)
    print("TEST 1: Equity Order (RELIANCE)")
    print("="*50)
    
    try:
        equity_order = breeze.place_order(
            stock_code="RELIANCE",
            exchange_code="NSE",
            product="cash",
            action="buy",
            order_type="limit",
            quantity="1",
            price="150.00",
            validity="day"
        )
        print("✅ Equity order response:")
        print(json.dumps(equity_order, indent=2))
    except Exception as e:
        print(f"❌ Equity order failed: {e}")
    
    # Test 2: NIFTY Options Order (FNO approach)
    print("\n" + "="*50)
    print("TEST 2: NIFTY Options Order")
    print("="*50)
    
    try:
        nifty_order = breeze.place_order(
            stock_code="NIFTY",
            exchange_code="NFO",
            product="options",
            action="buy",
            order_type="limit",
            quantity="1",
            price="50.00",
            validity="day",
            strike_price="24000",
            right="CE",
            expiry_date="2024-12-26T06:00:00.000Z"
        )
        print("✅ NIFTY options order response:")
        print(json.dumps(nifty_order, indent=2))
    except Exception as e:
        print(f"❌ NIFTY options order failed: {e}")
    
    # Test 3: Get available funds
    print("\n" + "="*50)
    print("TEST 3: Available Funds")
    print("="*50)
    
    try:
        funds = breeze.get_funds()
        print("✅ Funds response:")
        print(json.dumps(funds, indent=2))
    except Exception as e:
        print(f"❌ Funds query failed: {e}")
    
    print("\n" + "="*50)
    print("Diagnostic complete!")
    
except Exception as e:
    print(f"❌ Setup error: {e}")