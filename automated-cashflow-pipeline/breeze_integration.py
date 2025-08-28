from breeze_connect import BreezeConnect
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def setup_breeze_connection():
    """Connect your enhanced system to Breeze API"""
    
    # Your credentials (generate tonight)
    # It's recommended to store these in environment variables or a secure config management system
    api_key = os.getenv("BREEZE_API_KEY")
    api_secret = os.getenv("BREEZE_API_SECRET")
    session_token = os.getenv("BREEZE_SESSION_TOKEN")
    
    if not api_key or not api_secret or not session_token:
        print("WARNING: Breeze API credentials are not set. Please set BREEZE_API_KEY, BREEZE_API_SECRET, and BREEZE_SESSION_TOKEN environment variables.")
        return None

    try:
        breeze = BreezeConnect(api_key=api_key)
        breeze.generate_session(api_secret=api_secret, session_token=session_token)
        
        # Enable ₹30K paper trading (if supported)
        try:
            breeze.set_paper_trading(True)
            print("✅ Paper trading enabled")
        except AttributeError:
            print("ℹ️  Paper trading method not available - using regular mode")
        
        # Test connection 
        funds = breeze.get_funds()
        print("✅ Breeze connected! Paper trading enabled with ₹30K virtual capital")
        print(f"Available funds: {funds}")
        
        return breeze
        
    except Exception as e:
        print(f"❌ Breeze connection failed: {e}")
        return None

class EnhancedBreezeTrading:
    """Enhanced Breeze Trading class for automated trading system"""
    
    def __init__(self, paper_trading=True):
        self.api_key = os.getenv("BREEZE_API_KEY")
        self.api_secret = os.getenv("BREEZE_API_SECRET")
        self.session_token = os.getenv("BREEZE_SESSION_TOKEN")
        self.paper_trading = paper_trading
        self.breeze = None
        
        if not all([self.api_key, self.api_secret, self.session_token]):
            print("❌ Error: Missing Breeze API credentials in .env file.")
            print("Please ensure BREEZE_API_KEY, BREEZE_API_SECRET, and BREEZE_SESSION_TOKEN are set.")
    
    def connect_breeze(self):
        """Connect to Breeze API"""
        try:
            self.breeze = BreezeConnect(api_key=self.api_key)
            self.breeze.generate_session(api_secret=self.api_secret, session_token=self.session_token)
            
            # Enable paper trading if specified
            if self.paper_trading:
                try:
                    self.breeze.set_paper_trading(True)
                    print("✅ Paper trading enabled with ₹30K virtual capital")
                except AttributeError:
                    print("ℹ️ Paper trading method not available - using regular mode")
            
            # Test connection
            self.get_available_funds()
            print("✅ BREEZE READY! Connection successful")
            return True
            
        except Exception as e:
            print(f"❌ Breeze connection failed: {e}")
            return False
    
    def get_available_funds(self):
        """Get available funds from Breeze API"""
        try:
            if not self.breeze:
                print("❌ Breeze not connected. Call connect_breeze() first.")
                return None
                
            funds = self.breeze.get_funds()
            available_funds = funds.get("Success", {}).get("available_margin", 0)
            print(f"💰 Available funds: ₹{available_funds}")
            return available_funds
            
        except Exception as e:
            print(f"❌ Error getting funds: {e}")
            return None
    
    def get_holdings(self):
        """Get holdings from Breeze API"""
        try:
            if not self.breeze:
                print("❌ Breeze not connected. Call connect_breeze() first.")
                return None
                
            holdings = self.breeze.get_holdings()
            return holdings.get("Success", [])
            
        except Exception as e:
            print(f"❌ Error getting holdings: {e}")
            return None
    
    def place_order(self, stock_code, exchange_code, product_type, buy_sell, quantity, price=0, order_type="MARKET"):
        """Place an order via Breeze API"""
        try:
            if not self.breeze:
                print("❌ Breeze not connected. Call connect_breeze() first.")
                return None
                
            order_params = {
                "stock_code": stock_code,
                "exchange_code": exchange_code,
                "product_type": product_type,
                "action": buy_sell,
                "quantity": quantity,
                "price": price,
                "order_type": order_type
            }
            
            print(f"🚀 Placing {buy_sell} order for {quantity} {stock_code} at {'MARKET' if order_type == 'MARKET' else price}")
            
            if self.paper_trading:
                print("📝 PAPER TRADING MODE: Order simulated (not actually placed)")
                return {"Status": 200, "Success": [{"order_id": f"PAPER_{stock_code}_{datetime.now().strftime('%Y%m%d%H%M%S')}"}]}
            
            response = self.breeze.place_order(**order_params)
            return response
            
        except Exception as e:
            print(f"❌ Error placing order: {e}")
            return None

if __name__ == "__main__":
    print("Testing Breeze API connection...")
    trader = EnhancedBreezeTrading(paper_trading=True)
    if trader.connect_breeze():
        print("Breeze connection test successful.")
        funds = trader.get_available_funds()
        print(f"Available funds: ₹{funds}")
    else:
        print("Breeze connection test failed.")