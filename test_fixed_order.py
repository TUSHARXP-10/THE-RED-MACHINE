from breeze_connect import BreezeConnect 
import os 
from dotenv import load_dotenv 
 
load_dotenv() 
 
# Initialize Breeze 
breeze = BreezeConnect(api_key=os.getenv("BREEZE_API_KEY")) 
breeze.generate_session( 
    api_secret=os.getenv("BREEZE_API_SECRET"), 
    session_token=os.getenv("BREEZE_SESSION_TOKEN") 
) 
 
# Test 1: Verify session 
print("=== Testing Session ===") 
customer = breeze.get_customer_details() 
print(f"Session status: {customer.get('Status')}") 
 
# Test 2: Place order with CORRECT parameters 
print("\n=== Testing Order Placement ===") 
try: 
    order_response = breeze.place_order( 
        stock_code="RELIANCE", 
        exchange_code="NSE", 
        product="cash",           # ✅ Added missing parameter 
        action="buy",             # ✅ Fixed parameter name 
        order_type="limit", 
        quantity="1", 
        price="2000",             # Low price that won't execute 
        validity="day",           # ✅ Added missing parameter 
        stoploss="", 
        disclosed_quantity="0" 
    ) 
     
    print("Order response:", order_response) 
     
    # Cancel immediately if successful to avoid execution 
    if order_response.get('Status') == 200: 
        order_id = order_response['Success']['order_id'] 
        cancel_response = breeze.cancel_order( 
            exchange_code="NSE", 
            order_id=order_id 
        ) 
        print("Cancel response:", cancel_response) 
         
except Exception as e: 
    print(f"Order placement test failed: {e}")

print("\n=== Test Complete ===")