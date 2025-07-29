import json
import os
from datetime import datetime
from breeze_connector import BreezeConnector

class BrokerInterface:
    def __init__(self, config_path='signal_config.json'):
        self.config = self._load_config(config_path)
        self.mode = self.config.get('mode', 'paper')
        self.signal_log_path = 'signal_log.csv'
        self._initialize_signal_log()
        self.breeze_connector = None
        if self.mode == "live":
            self.breeze_connector = BreezeConnector()
            if not self.breeze_connector.connect():
                print("Failed to connect to Breeze. Reverting to paper mode.")
                self.mode = "paper"

    def _load_config(self, config_path):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found at {config_path}")
        with open(config_path, 'r') as f:
            return json.load(f)

    def _initialize_signal_log(self):
        if not os.path.exists(self.signal_log_path):
            with open(self.signal_log_path, 'w') as f:
                f.write("timestamp,strike,type,price,strategy_id,status,mode\n")

    def place_order(self, strike, order_type, price, strategy_id):
        timestamp = datetime.now().isoformat()
        
        if self.mode == "paper":
            status = "PAPER_PLACED"
            log_entry = f"{timestamp},{strike},{order_type},{price},{strategy_id},{status},{self.mode}\n"
            with open(self.signal_log_path, 'a') as f:
                f.write(log_entry)
            print(f"Order {status}: Strategy {strategy_id}, Type {order_type}, Strike {strike}, Price {price}")
            return {"status": "success", "message": "Paper trade placed successfully"}
        
        elif self.mode == "live":
            if not self.breeze_connector or not self.breeze_connector.breeze:
                print("Breeze connector not initialized or connected. Cannot place live order.")
                return {"status": "error", "message": "Breeze not connected"}
            
            # Assuming strike, order_type (BUY/SELL), price are sufficient for Breeze place_order
            # You might need to map these to Breeze-specific parameters (e.g., stock_code, exchange_code, product_type)
            # For SENSEX options, you'll need to extract expiry, strike, and right from 'strike'
            # This is a placeholder for actual Breeze API call with proper parameters
            try:
                # Example: Parse strike to get components for Breeze API
                # This part needs to be robust for actual SENSEX options
                # For now, using dummy values for Breeze API call
                breeze_order_type = "BUY" if order_type == "BUY" else "SELL"
                order_response = self.breeze_connector.place_order(
                    stock_code="SENSEX", # This needs to be dynamic based on actual SENSEX options
                    exchange_code="NFO", # Or relevant exchange for SENSEX options
                    product_type="OPTIONS",
                    buy_sell=breeze_order_type,
                    quantity=1, # This should come from strategy or config
                    price=price,
                    order_type="LIMIT" # Or "MARKET"
                    # Add expiry_date, strike_price, right based on 'strike'
                )
                if order_response and order_response.get('status') == 'Success': # Adjust based on actual Breeze response
                    status = "LIVE_PLACED"
                    log_entry = f"{timestamp},{strike},{order_type},{price},{strategy_id},{status},{self.mode}\n"
                    with open(self.signal_log_path, 'a') as f:
                        f.write(log_entry)
                    print(f"Live Order PLACED: {order_response}")
                    return {"status": "success", "message": "Live trade placed successfully", "response": order_response}
                else:
                    status = "LIVE_FAILED"
                    log_entry = f"{timestamp},{strike},{order_type},{price},{strategy_id},{status},{self.mode}\n"
                    with open(self.signal_log_path, 'a') as f:
                        f.write(log_entry)
                    print(f"Live Order FAILED: {order_response}")
                    return {"status": "error", "message": "Live trade failed", "response": order_response}
            except Exception as e:
                status = "LIVE_ERROR"
                log_entry = f"{timestamp},{strike},{order_type},{price},{strategy_id},{status},{self.mode},Error: {e}\n"
                with open(self.signal_log_path, 'a') as f:
                    f.write(log_entry)
                print(f"Error placing live order: {e}")
                return {"status": "error", "message": f"Error placing live order: {e}"}
        else:
            return {"status": "error", "message": "Invalid mode specified in config"}

    def get_market_data(self, symbol):
        if self.mode == "live" and self.breeze_connector and self.breeze_connector.breeze:
            # This needs to be adapted to fetch SENSEX options data specifically
            # For example, you might need to specify exchange, product type, expiry, strike, right
            print(f"Fetching live market data for {symbol} via Breeze...")
            try:
                # Placeholder for actual BreezeConnect market data call for SENSEX options
                # You'll need to pass appropriate parameters to get_quotes or similar method
                data = self.breeze_connector.get_market_data(stock_code=symbol) # Assuming 'symbol' is like 'SENSEX'
                if data:
                    # Extract relevant price from Breeze response
                    # This is highly dependent on the structure of Breeze's get_quotes response for options
                    current_price = data.get('last_traded_price', 0) # Example key
                    return {"symbol": symbol, "current_price": current_price, "timestamp": datetime.now().isoformat()}
                else:
                    print("No market data received from Breeze.")
                    return None
            except Exception as e:
                print(f"Error fetching live market data: {e}")
                return None
        else:
            print(f"Fetching market data for {symbol} (paper mode/Breeze not connected)")
            # For now, return dummy data for paper mode or if Breeze is not connected
            return {"symbol": symbol, "current_price": 100.0, "timestamp": datetime.now().isoformat()}