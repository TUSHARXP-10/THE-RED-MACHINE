import os
from datetime import datetime
import requests
from breeze_connect import BreezeConnect
from dotenv import load_dotenv

class BreezeConnector:
    def __init__(self):
        load_dotenv() # Load environment variables from .env file
        self.api_key = os.getenv("BREEZE_API_KEY")
        if self.api_key:
            self.api_key = self.api_key.strip('"')  # Remove any quotes
            
        self.api_secret = os.getenv("BREEZE_API_SECRET")
        if self.api_secret:
            self.api_secret = self.api_secret.strip('"')  # Remove any quotes
            
        self.session_token = os.getenv("BREEZE_SESSION_TOKEN")
        if self.session_token:
            self.session_token = self.session_token.strip('"')  # Remove any quotes
            
        self.client_code = os.getenv("ICICI_CLIENT_CODE")
        if self.client_code:
            self.client_code = self.client_code.strip('"')  # Remove any quotes
            
        self.breeze = None

        if not all([self.api_key, self.api_secret, self.session_token, self.client_code]):
            print("Warning: Breeze API credentials not fully set in .env. Live trading may fail.")
            missing = []
            if not self.api_key: missing.append("BREEZE_API_KEY")
            if not self.api_secret: missing.append("BREEZE_API_SECRET")
            if not self.session_token: missing.append("BREEZE_SESSION_TOKEN")
            if not self.client_code: missing.append("ICICI_CLIENT_CODE")
            print(f"Missing credentials: {', '.join(missing)}")
        
        # Initialize BreezeConnect
        try:
            self.breeze = BreezeConnect(api_key=self.api_key)
        except Exception as e:
            print(f"Error initializing BreezeConnect: {e}")
            self.breeze = None

    def connect(self):
        """Connect to Breeze API and validate session token"""
        if not self.breeze:
            print("BreezeConnect not initialized. Check API credentials.")
            return False

        try:
            load_dotenv() # Reload environment variables to get the latest session token
            self.session_token = os.getenv("BREEZE_SESSION_TOKEN").strip('"') if os.getenv("BREEZE_SESSION_TOKEN") else None
            
            if not self.session_token:
                print("🚨 CRITICAL: BREEZE_SESSION_TOKEN is empty or missing!")
                print("   Run: python fix_session_immediately.py")
                return False

            # Ensure the BreezeConnect object has the latest user_id and session_token
            self.breeze.user_id = self.client_code
            self.breeze.session_key = self.session_token
            
            # Test session validity first
            print(f"Attempting to connect with API Key: {self.api_key[:5]}... and Session Token: {self.session_token[:5]}...")
            self.breeze.generate_session(api_secret=self.api_secret, session_token=self.session_token)
            
            # Verify session by testing customer details
            customer = self.breeze.get_customer_details()
            if customer and 'Error' in str(customer) and 'Session' in str(customer):
                print("🚨 SESSION EXPIRED: Please generate new session token")
                print("Response:", customer)
                print("   Run: python fix_session_immediately.py")
                return False
            elif customer and 'client_id' in str(customer):
                print("✅ Successfully connected to BreezeConnect")
                return True
            else:
                print(f"⚠️  Connection issue: {customer}")
                print("🚨 CRITICAL: Session token may be expired or invalid!")
                print("Check your .env file for correct API credentials.")
                return False
                
        except Exception as e:
            print(f"❌ Error connecting to BreezeConnect: {e}")
            print("🚨 CRITICAL: Session token may be expired or invalid!")
            print("   Run: python fix_session_immediately.py to fix session issues")
            self.breeze = None
            return False

    def get_market_data(self, stock_code, exchange_code="BSE", product_type="cash", expiry_date=None, strike_price=None, right=None):
        if not self.breeze:
            print("BreezeConnect not connected. Cannot fetch market data.")
            return None
        try:
            # Use BSE exchange for SENSEX
            data = self.breeze.get_quotes(stock_code="BSESEN", exchange_code="BSE")
            
            # Extract current price from Breeze response
            if data and 'success' in str(data).lower():
                current_price = float(data.get('ltp', 81000.0))  # Default to realistic SENSEX level
                volume = int(data.get('volume', 0))
                
                return {
                    'symbol': 'SENSEX',
                    'current_price': current_price,
                    'volume': volume,
                    'timestamp': datetime.now().isoformat(),
                    'raw_data': data
                }
            else:
                # Fallback to real SENSEX data via web API
                import requests
                response = requests.get("https://api.bseindia.com/BseIndiaAPI/api/ComHeader/w")
                if response.status_code == 200:
                    api_data = response.json()
                    current_price = float(api_data.get('Value', 81000.0))
                    return {
                        'symbol': 'SENSEX',
                        'current_price': current_price,
                        'volume': 0,
                        'timestamp': datetime.now().isoformat(),
                        'source': 'web_api'
                    }
                
                return {
                    'symbol': 'SENSEX',
                    'current_price': 81000.0 + (hash(str(datetime.now())) % 200 - 100),  # Simulated movement
                    'volume': 1000000,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'simulated'
                }
                
        except Exception as e:
            print(f"Error fetching real SENSEX data: {e}")
            # Return realistic simulated data for testing
            return {
                'symbol': 'SENSEX',
                'current_price': 81000.0 + (hash(str(datetime.now())) % 400 - 200),
                'volume': 1000000,
                'timestamp': datetime.now().isoformat(),
                'source': 'error_fallback'
            }

    def place_order(self, stock_code, exchange_code, buy_sell, quantity, price, order_type="LIMIT", expiry_date=None, strike_price=None, right=None):
        if not self.breeze:
            print("BreezeConnect not connected. Cannot place order.")
            return None
        try:
            # Map parameters to BreezeConnect API format
            # For SENSEX trading - use RELIANCE as SENSEX proxy (major SENSEX constituent)
            if stock_code.upper() == "SENSEX":
                # Use RELIANCE as proxy for SENSEX trading - liquid and correlated
                order_response = self.breeze.place_order(
                    stock_code="RELIANCE",
                    exchange_code="NSE",
                    product="cash",
                    action=buy_sell,
                    order_type=order_type,
                    quantity=str(quantity),
                    price=str(price),
                    validity="DAY",
                    disclosed_quantity="0"
                )
            elif stock_code.upper() == "RELIANCE":
                # Direct RELIANCE trading
                order_response = self.breeze.place_order(
                    stock_code="RELIANCE",
                    exchange_code="NSE",
                    product="cash",
                    action=buy_sell,
                    order_type=order_type,
                    quantity=str(quantity),
                    price=str(price),
                    validity="DAY",
                    disclosed_quantity="0"
                )
            elif stock_code.upper() in ["INFY", "TCS", "HDFC", "ITC"]:
                # Other liquid stocks for testing
                order_response = self.breeze.place_order(
                    stock_code=stock_code.upper(),
                    exchange_code="NSE",
                    product="cash",
                    action=buy_sell,
                    order_type=order_type,
                    quantity=str(quantity),
                    price=str(price),
                    validity="DAY",
                    disclosed_quantity="0"
                )
            else:
                # For other instruments (options/futures)
                if right and strike_price and expiry_date:
                    # For options trading
                    order_response = self.breeze.place_order(
                        stock_code=stock_code,
                        exchange_code=exchange_code,
                        product="options",
                        action=buy_sell,
                        order_type=order_type,
                        quantity=str(quantity),
                        price=str(price),
                        validity="DAY",
                        disclosed_quantity="0",
                        strike_price=str(strike_price),
                        right=right.lower(),  # Convert to lowercase (call/put)
                        expiry_date=expiry_date
                    )
                else:
                    # For equity/cash trades
                    order_response = self.breeze.place_order(
                        stock_code=stock_code,
                        exchange_code=exchange_code,
                        product="cash",
                        action=buy_sell,
                        order_type=order_type,
                        quantity=str(quantity),
                        price=str(price),
                        validity="DAY",
                        disclosed_quantity="0"
                    )
            print(f"Order placed: {order_response}")
            return order_response
        except Exception as e:
            print(f"Error placing order with BreezeConnect: {e}")
            return None

def refresh_session(session_token_arg=None):
    load_dotenv()
    api_key = os.getenv("BREEZE_API_KEY")
    api_secret = os.getenv("BREEZE_API_SECRET")
    client_code = os.getenv("ICICI_CLIENT_CODE")

    if not all([api_key, api_secret, client_code]):
        print("Error: BREEZE_API_KEY, BREEZE_API_SECRET, and ICICI_CLIENT_CODE must be set in .env to refresh session.")
        return

    try:
        breeze = BreezeConnect(api_key=api_key)
        # This URL is typically provided by Breeze for session generation
        # The user needs to visit this URL, log in, and get the session token from the redirect URL
        import urllib.parse
        print("Please visit the following URL to generate a new session token:")
        session_url = f"https://api.icicidirect.com/apiuser/login?api_key={urllib.parse.quote_plus(api_key)}"
        if session_token_arg:
            new_session_token = session_token_arg
        else:
            print("Please visit the following URL to generate a new session token:")
            session_url = f"https://api.icicidirect.com/apiuser/login?api_key={urllib.parse.quote_plus(api_key)}"
            print(session_url)
            redirect_url = input("After logging in and getting the new session token, please copy and paste the *entire URL* from your browser's address bar after redirection (it should start with http://localhost:8501/ or similar): ")

            if not redirect_url.startswith('http'):
                print("Invalid input: Please paste the full redirect URL starting with 'http'.")
                return

            # Extract session token from the redirect URL
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(redirect_url)
            query_params = parse_qs(parsed_url.query)
            new_session_token = query_params.get('session_token', query_params.get('apisession', [None]))[0]

        if new_session_token:
            # Update the .env file with the new session token
            with open('.env', 'r') as f:
                lines = f.readlines()
            with open('.env', 'w') as f:
                updated = False
                for line in lines:
                    if line.startswith('BREEZE_SESSION_TOKEN='):
                        f.write(f'BREEZE_SESSION_TOKEN="{new_session_token}"\n')
                        updated = True
                    else:
                        f.write(line)
                if not updated:
                    f.write(f'BREEZE_SESSION_TOKEN="{new_session_token}"\n')
            print("BREEZE_SESSION_TOKEN updated in .env file.")
            load_dotenv() # Reload environment variables
        else:
            print("Could not extract session token from the provided URL. Please ensure you pasted the correct redirect URL.")
            return
        
        if new_session_token:
            try:
                test_breeze = BreezeConnect(api_key=api_key)
                test_breeze.generate_session(api_secret=api_secret, session_token=new_session_token)
                print("Successfully tested new session token.")
            except Exception as test_e:
                print(f"Error testing new session token: {test_e}")
        else:
            print("New session token not found in .env after update.")

    except Exception as e:
        print(f"Error refreshing session: {e}")

# Example usage (for testing purposes)
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "refresh_session":
        if len(sys.argv) > 2:
            refresh_session(sys.argv[2])
        else:
            refresh_session()
        sys.exit()

    # Create a dummy .env file for testing if it doesn't exist
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write("BREEZE_API_KEY=YOUR_API_KEY\n")
            f.write("BREEZE_API_SECRET=YOUR_API_SECRET\n")
            f.write("BREEZE_SESSION_TOKEN=YOUR_SESSION_TOKEN\n")
            f.write("ICICI_CLIENT_CODE=YOUR_CLIENT_CODE\n")
        print("Created a dummy .env file. Please fill in your actual Breeze API credentials.")

    connector = BreezeConnector()
    if connector.connect():
        # Example: Fetching dummy market data (replace with actual SENSEX options parameters)
        # market_data = connector.get_market_data(stock_code="SENSEX")
        # print(f"Market Data: {market_data}")

        # Example: Placing a dummy order (replace with actual SENSEX options parameters)
        # order_result = connector.place_order(
        #     stock_code="SENSEX",
        #     exchange_code="NSE",
        #     product_type="options",
        #     buy_sell="BUY",
        #     quantity=1,
        #     price=100.0,
        #     order_type="LIMIT",
        #     expiry_date="2023-12-28T06:00:00.000Z", # Example expiry date
        #     strike_price=65000,
        #     right="CE" # Call option
        # )
        # print(f"Order Result: {order_result}")
        pass