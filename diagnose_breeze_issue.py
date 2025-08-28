#!/usr/bin/env python3
"""
Comprehensive Breeze API Diagnostics Script
Run this to identify the exact cause of "Resource not available" error
"""

import os
from dotenv import load_dotenv
from breeze_connect import BreezeConnect

def diagnose_breeze_connection():
    """Diagnose Breeze API connection and permissions"""
    load_dotenv()
    
    print("🔍 BREEZE API DIAGNOSTICS")
    print("=" * 50)
    
    # Check environment variables
    api_key = os.getenv("BREEZE_API_KEY")
    api_secret = os.getenv("BREEZE_API_SECRET")
    session_token = os.getenv("BREEZE_SESSION_TOKEN")
    client_code = os.getenv("ICICI_CLIENT_CODE")
    
    print("📋 Environment Check:")
    print(f"API Key: {'✅ Present' if api_key else '❌ Missing'}")
    print(f"API Secret: {'✅ Present' if api_secret else '❌ Missing'}")
    print(f"Session Token: {'✅ Present' if session_token else '❌ Missing'}")
    print(f"Client Code: {'✅ Present' if client_code else '❌ Missing'}")
    
    if not all([api_key, api_secret, session_token, client_code]):
        print("❌ Missing required credentials")
        return False
    
    # Clean session token
    session_token = session_token.strip('"').strip()
    
    try:
        # Initialize BreezeConnect
        breeze = BreezeConnect(api_key=api_key)
        
        # Test session generation
        print("\n🔗 Testing Session...")
        breeze.generate_session(api_secret=api_secret, session_token=session_token)
        print("✅ Session generated successfully")
        
        # Test customer details
        print("\n👤 Testing Customer Details...")
        customer = breeze.get_customer_details()
        if customer and 'Error' not in str(customer):
            print("✅ Customer details retrieved")
            print(f"Client ID: {customer.get('client_id', 'N/A')}")
            print(f"Email: {customer.get('email_id', 'N/A')}")
        else:
            print("❌ Failed to get customer details")
            print(f"Response: {customer}")
            return False
            
        # Test funds
        print("\n💰 Testing Funds...")
        funds = breeze.get_funds()
        if funds and 'Error' not in str(funds):
            print("✅ Funds retrieved")
            print(f"Available Cash: ₹{funds.get('available_cash', 0)}")
        else:
            print("❌ Failed to get funds")
            print(f"Response: {funds}")
            
        # Test holdings
        print("\n📊 Testing Holdings...")
        holdings = breeze.get_demat_holdings()
        if holdings and 'Error' not in str(holdings):
            print("✅ Holdings retrieved")
            print(f"Holdings count: {len(holdings) if isinstance(holdings, list) else 'N/A'}")
        else:
            print("❌ Failed to get holdings")
            print(f"Response: {holdings}")
            
        # Test stock symbols
        print("\n📈 Testing Stock Symbols...")
        test_symbols = ["RELIANCE", "TCS", "INFY", "HDFC", "ITC"]
        for symbol in test_symbols:
            try:
                quote = breeze.get_quotes(stock_code=symbol, exchange_code="NSE")
                if quote and 'Error' not in str(quote):
                    print(f"✅ {symbol}: ₹{quote.get('ltp', 'N/A')}")
                else:
                    print(f"❌ {symbol}: {quote}")
            except Exception as e:
                print(f"❌ {symbol}: Error - {e}")
                
        # Test order placement (dry run)
        print("\n📝 Testing Order Placement (Dry Run)...")
        try:
            # Try with very small quantity to avoid actual execution
            test_order = breeze.place_order(
                stock_code="RELIANCE",
                exchange_code="NSE",
                product="cash",
                action="buy",
                order_type="limit",
                quantity="1",
                price="100",  # Very low price to prevent execution
                validity="day"
            )
            
            if test_order and 'Error' not in str(test_order):
                print("✅ Order placement test successful")
                print(f"Order Response: {test_order}")
                
                # Cancel the test order immediately
                if 'order_id' in test_order:
                    cancel = breeze.cancel_order(order_id=test_order['order_id'])
                    print(f"✅ Test order cancelled: {cancel}")
            else:
                print("❌ Order placement failed")
                print(f"Response: {test_order}")
                
        except Exception as e:
            print(f"❌ Order placement error: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    diagnose_breeze_connection()