import os
from breeze_connect import BreezeConnect
from dotenv import load_dotenv

class BreezeConnector:
    def __init__(self):
        load_dotenv() # Load environment variables from .env file
        self.api_key = os.getenv("BREEZE_API_KEY")
        self.api_secret = os.getenv("BREEZE_API_SECRET")
        self.session_token = os.getenv("BREEZE_SESSION_TOKEN").strip('"') if os.getenv("BREEZE_SESSION_TOKEN") else None
        self.client_code = os.getenv("ICICI_CLIENT_CODE")
        self.breeze = None

        if not all([self.api_key, self.api_secret, self.session_token, self.client_code]):
            print("Warning: Breeze API credentials not fully set in .env. Live trading may fail.")
        
        # Initialize BreezeConnect
        self.breeze = BreezeConnect(api_key=self.api_key)

    def connect(self):
        try:
            load_dotenv() # Reload environment variables to get the latest session token
            self.session_token = os.getenv("BREEZE_SESSION_TOKEN").strip('"') if os.getenv("BREEZE_SESSION_TOKEN") else None
            
            if not self.session_token:
                print("Error: BREEZE_SESSION_TOKEN is empty after reloading. Cannot connect.")
                return False

            # Ensure the BreezeConnect object has the latest user_id and session_token
            self.breeze.user_id = self.client_code
            self.breeze.session_key = self.session_token
            self.breeze.generate_session(api_secret=self.api_secret, session_token=self.session_token)
            print("Successfully connected to BreezeConnect.")
            return True
        except Exception as e:
            print(f"Error connecting to BreezeConnect: {e}")
            self.breeze = None
            return False

def refresh_session():
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



    def get_market_data(self, stock_code, exchange_code="NSE", product_type="options", expiry_date=None, strike_price=None, right=None):
        if not self.breeze:
            print("BreezeConnect not connected. Cannot fetch market data.")
            return None
        try:
            # This is a simplified example. BreezeConnect's get_quotes might require more specific parameters.
            # You'll need to adjust this based on the actual BreezeConnect API documentation for options.
            data = self.breeze.get_quotes(stock_code=stock_code, exchange_code=exchange_code)
            # Filter for SENSEX options if needed, and extract relevant price
            # For now, returning dummy data or a simplified response
            print(f"Fetching market data for {stock_code}...")
            return data # This will be the raw response from BreezeConnect
        except Exception as e:
            print(f"Error fetching market data from BreezeConnect: {e}")
            return None

    def place_order(self, stock_code, exchange_code, product_type, buy_sell, quantity, price, order_type="LIMIT", expiry_date=None, strike_price=None, right=None):
        if not self.breeze:
            print("BreezeConnect not connected. Cannot place order.")
            return None
        try:
            # This is a simplified example. BreezeConnect's place_order might require more specific parameters.
            # Ensure all required parameters for SENSEX options are passed.
            order_response = self.breeze.place_order(
                stock_code=stock_code,
                exchange_code=exchange_code,
                product_type=product_type,
                buy_sell=buy_sell,
                quantity=quantity,
                price=price,
                order_type=order_type,
                # Add other parameters like expiry_date, strike_price, right for options
            )
            print(f"Order placed: {order_response}")
            return order_response
        except Exception as e:
            print(f"Error placing order with BreezeConnect: {e}")
            return None

# Example usage (for testing purposes)
if __name__ == "__main__":
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