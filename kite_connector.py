import os
from datetime import datetime
import requests
from kiteconnect import KiteConnect
from dotenv import load_dotenv

class KiteConnector:
    def __init__(self):
        load_dotenv() # Load environment variables from .env file
        self.api_key = os.getenv("KITE_API_KEY")
        if self.api_key:
            self.api_key = self.api_key.strip('"')  # Remove any quotes
            
        self.api_secret = os.getenv("KITE_API_SECRET")
        if self.api_secret:
            self.api_secret = self.api_secret.strip('"')  # Remove any quotes
            
        self.access_token = os.getenv("KITE_ACCESS_TOKEN")
        if self.access_token:
            self.access_token = self.access_token.strip('"')  # Remove any quotes
            
        self.client_id = os.getenv("ZERODHA_CLIENT_ID")
        if self.client_id:
            self.client_id = self.client_id.strip('"')  # Remove any quotes
            
        self.kite = None

        if not all([self.api_key, self.api_secret, self.client_id]):
            print("Warning: Kite API credentials not fully set in .env. Live trading may fail.")
            missing = []
            if not self.api_key: missing.append("KITE_API_KEY")
            if not self.api_secret: missing.append("KITE_API_SECRET")
            if not self.client_id: missing.append("ZERODHA_CLIENT_ID")
            print(f"Missing credentials: {', '.join(missing)}")
        
        # Initialize KiteConnect
        try:
            self.kite = KiteConnect(api_key=self.api_key)
            if self.access_token:
                self.kite.set_access_token(self.access_token)
        except Exception as e:
            print(f"Error initializing KiteConnect: {e}")
            self.kite = None

    def connect(self):
        """Connect to Kite API and validate access token"""
        if not self.kite:
            print("KiteConnect not initialized. Check API credentials.")
            return False

        try:
            load_dotenv() # Reload environment variables to get the latest access token
            self.access_token = os.getenv("KITE_ACCESS_TOKEN").strip('"') if os.getenv("KITE_ACCESS_TOKEN") else None
            
            if not self.access_token:
                print("🚨 CRITICAL: KITE_ACCESS_TOKEN is empty or missing!")
                print("   Run: python fix_kite_session.py")
                return False

            # Set the access token
            print(f"Attempting to connect with API Key: {self.api_key[:5]}... and Access Token: {self.access_token[:5]}...")
            self.kite.set_access_token(self.access_token)
            
            # Verify session by testing profile
            profile = self.kite.profile()
            if profile and 'user_id' in profile:
                print(f"✅ Successfully connected to KiteConnect as {profile['user_name']}")
                return True
            else:
                print(f"⚠️  Connection issue: {profile}")
                print("🚨 CRITICAL: Access token may be expired or invalid!")
                print("Check your .env file for correct API credentials.")
                return False
                
        except Exception as e:
            print(f"❌ Error connecting to KiteConnect: {e}")
            print("🚨 CRITICAL: Access token may be expired or invalid!")
            print("   Run: python fix_kite_session.py to fix session issues")
            return False

    def get_market_data(self, stock_code, exchange_code="NSE", product_type="cash", expiry_date=None, strike_price=None, right=None):
        if not self.kite:
            print("KiteConnect not connected. Cannot fetch market data.")
            return None
        try:
            # For SENSEX, use BSE:SENSEX
            if stock_code.upper() == "SENSEX":
                instrument_token = self.get_instrument_token("BSE", "SENSEX")
                if not instrument_token:
                    print("Could not find instrument token for SENSEX")
                    return None
                
                # Get quote for SENSEX
                data = self.kite.quote(f"BSE:SENSEX")
                
                if data and "BSE:SENSEX" in data:
                    quote_data = data["BSE:SENSEX"]
                    current_price = float(quote_data.get('last_price', 81000.0))  # Default to realistic SENSEX level
                    volume = int(quote_data.get('volume', 0))
                    
                    return {
                        'symbol': 'SENSEX',
                        'current_price': current_price,
                        'volume': volume,
                        'timestamp': datetime.now().isoformat(),
                        'raw_data': quote_data
                    }
            else:
                # For other instruments
                instrument_token = self.get_instrument_token(exchange_code, stock_code)
                if not instrument_token:
                    print(f"Could not find instrument token for {stock_code} on {exchange_code}")
                    return None
                
                # Get quote
                data = self.kite.quote(f"{exchange_code}:{stock_code}")
                
                if data and f"{exchange_code}:{stock_code}" in data:
                    quote_data = data[f"{exchange_code}:{stock_code}"]
                    current_price = float(quote_data.get('last_price', 0.0))
                    volume = int(quote_data.get('volume', 0))
                    
                    return {
                        'symbol': stock_code,
                        'current_price': current_price,
                        'volume': volume,
                        'timestamp': datetime.now().isoformat(),
                        'raw_data': quote_data
                    }
            
            # Fallback to web API for SENSEX if Kite data is not available
            if stock_code.upper() == "SENSEX":
                try:
                    response = requests.get("https://api.bseindia.com/BseIndiaAPI/api/ComHeader/w")
                    if response.status_code == 200:
                        api_data = response.json()
                        current_price = float(api_data.get('Value', 81000.0))
                        return {
                            'symbol': 'SENSEX',
                            'current_price': current_price,
                            'volume': 0,  # No volume data from this API
                            'timestamp': datetime.now().isoformat(),
                            'raw_data': api_data
                        }
                except Exception as e:
                    print(f"Error fetching SENSEX data from web API: {e}")
            
            return None
                
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return None
    
    def get_instrument_token(self, exchange, symbol):
        """Get instrument token for a given exchange and symbol"""
        try:
            instruments = self.kite.instruments(exchange)
            for instrument in instruments:
                if instrument['tradingsymbol'] == symbol:
                    return instrument['instrument_token']
            return None
        except Exception as e:
            print(f"Error fetching instrument token: {e}")
            return None

    def place_order(self, stock_code, exchange_code, buy_sell, quantity, price, order_type="LIMIT", expiry_date=None, strike_price=None, right=None):
        if not self.kite:
            print("KiteConnect not connected. Cannot place order.")
            return None
        try:
            # Map parameters to KiteConnect API format
            transaction_type = "BUY" if buy_sell.upper() == "BUY" else "SELL"
            
            # For SENSEX trading - use RELIANCE as SENSEX proxy (major SENSEX constituent)
            if stock_code.upper() == "SENSEX":
                # Use RELIANCE as proxy for SENSEX trading - liquid and correlated
                order_params = {
                    "tradingsymbol": "RELIANCE",
                    "exchange": "NSE",
                    "transaction_type": transaction_type,
                    "quantity": quantity,
                    "order_type": order_type,
                    "product": "CNC",  # Cash and Carry (delivery)
                    "validity": "DAY"
                }
                
                # Add price for limit orders
                if order_type.upper() == "LIMIT":
                    order_params["price"] = price
                
                order_id = self.kite.place_order(variety="regular", **order_params)
                return {"order_id": order_id, "status": "success"}
                
            elif stock_code.upper() in ["RELIANCE", "INFY", "TCS", "HDFC", "ITC"]:
                # Direct stock trading
                order_params = {
                    "tradingsymbol": stock_code.upper(),
                    "exchange": "NSE",
                    "transaction_type": transaction_type,
                    "quantity": quantity,
                    "order_type": order_type,
                    "product": "CNC",  # Cash and Carry (delivery)
                    "validity": "DAY"
                }
                
                # Add price for limit orders
                if order_type.upper() == "LIMIT":
                    order_params["price"] = price
                
                order_id = self.kite.place_order(variety="regular", **order_params)
                return {"order_id": order_id, "status": "success"}
                
            else:
                # For options trading
                if right and strike_price and expiry_date:
                    # Format the trading symbol for options
                    # Example: NIFTY22D0817000CE
                    from datetime import datetime
                    expiry_obj = datetime.strptime(expiry_date.split('T')[0], '%Y-%m-%d')
                    expiry_str = expiry_obj.strftime('%y%b').upper()
                    
                    # Construct option symbol
                    option_symbol = f"{stock_code}{expiry_str}{strike_price}{right.upper()}"
                    
                    order_params = {
                        "tradingsymbol": option_symbol,
                        "exchange": exchange_code,
                        "transaction_type": transaction_type,
                        "quantity": quantity,
                        "order_type": order_type,
                        "product": "NRML",  # Normal for F&O
                        "validity": "DAY"
                    }
                    
                    # Add price for limit orders
                    if order_type.upper() == "LIMIT":
                        order_params["price"] = price
                    
                    order_id = self.kite.place_order(variety="regular", **order_params)
                    return {"order_id": order_id, "status": "success"}
                else:
                    # For equity/cash trades
                    order_params = {
                        "tradingsymbol": stock_code,
                        "exchange": exchange_code,
                        "transaction_type": transaction_type,
                        "quantity": quantity,
                        "order_type": order_type,
                        "product": "CNC",  # Cash and Carry (delivery)
                        "validity": "DAY"
                    }
                    
                    # Add price for limit orders
                    if order_type.upper() == "LIMIT":
                        order_params["price"] = price
                    
                    order_id = self.kite.place_order(variety="regular", **order_params)
                    return {"order_id": order_id, "status": "success"}
                    
        except Exception as e:
            print(f"Error placing order: {e}")
            return {"status": "error", "message": str(e)}

    def get_order_status(self, order_id):
        """Get status of an order"""
        if not self.kite:
            print("KiteConnect not connected. Cannot fetch order status.")
            return None
        try:
            orders = self.kite.orders()
            for order in orders:
                if order['order_id'] == order_id:
                    return order
            return None
        except Exception as e:
            print(f"Error fetching order status: {e}")
            return None

    def get_positions(self):
        """Get current positions"""
        if not self.kite:
            print("KiteConnect not connected. Cannot fetch positions.")
            return None
        try:
            return self.kite.positions()
        except Exception as e:
            print(f"Error fetching positions: {e}")
            return None

    def get_holdings(self):
        """Get current holdings"""
        if not self.kite:
            print("KiteConnect not connected. Cannot fetch holdings.")
            return None
        try:
            return self.kite.holdings()
        except Exception as e:
            print(f"Error fetching holdings: {e}")
            return None

    def get_margins(self):
        """Get account margins with enhanced error handling"""
        if not self.kite:
            print("KiteConnect not connected. Cannot fetch margins.")
            return None
        try:
            # Try direct margins endpoint
            margins = self.kite.margins()
            if margins and 'equity' in margins:
                return margins
        except Exception as e:
            print(f"⚠️  Standard margins endpoint failed: {e}")
            
        # Fallback strategies
        try:
            # Fallback 1: Get user profile funds
            profile = self.kite.profile()
            if profile and 'funds' in profile:
                # Create synthetic margins structure
                funds = profile['funds']
                return {
                    'equity': {
                        'available': {
                            'cash': funds.get('available', {}).get('cash', 3000.0),
                            'intraday_payin': 0.0
                        },
                        'utilised': {
                            'debits': 0.0,
                            'span': 0.0,
                            'exposure': 0.0
                        }
                    }
                }
        except Exception as e:
            print(f"⚠️  Profile funds fallback failed: {e}")
            
        # Fallback 2: Use default ₹3000 system
        print("ℹ️  Using ₹3000 system default margins")
        return {
            'equity': {
                'available': {
                    'cash': 3000.0,
                    'intraday_payin': 0.0
                },
                'utilised': {
                    'debits': 0.0,
                    'span': 0.0,
                    'exposure': 0.0
                }
            }
        }

    def get_available_balance(self):
        """Get simplified available balance for ₹3000 capital system"""
        margins = self.get_margins()
        if margins and 'equity' in margins:
            equity = margins['equity']
            available = equity.get('available', {})
            cash = available.get('cash', 0.0)
            intraday_payin = available.get('intraday_payin', 0.0)
            return cash + intraday_payin
        return 3000.0  # Default for ₹3000 system

    def get_nifty_spot_price(self):
        """Get NIFTY spot price"""
        return self.get_market_data("NIFTY 50", "NSE").get('current_price', 22000.0)

# Example usage (for testing purposes)
if __name__ == "__main__":
    import sys

    # Create a dummy .env file for testing if it doesn't exist
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write("KITE_API_KEY=YOUR_API_KEY\n")
            f.write("KITE_API_SECRET=YOUR_API_SECRET\n")
            f.write("KITE_ACCESS_TOKEN=YOUR_ACCESS_TOKEN\n")
            f.write("ZERODHA_CLIENT_ID=YOUR_CLIENT_ID\n")
        print("Created a dummy .env file. Please fill in your actual Kite API credentials.")

    connector = KiteConnector()
    if connector.connect():
        # Example: Fetching market data
        market_data = connector.get_market_data(stock_code="SENSEX")
        print(f"Market Data: {market_data}")

        # Example: Fetching positions
        positions = connector.get_positions()
        print(f"Positions: {positions}")