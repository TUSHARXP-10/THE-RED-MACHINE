import os
import pandas as pd
from breeze_connect import BreezeConnect
from breeze_connector import BreezeConnector
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class TradeExecutor:
    def __init__(self, mode='paper'):
        if mode not in ['paper', 'live']:
            raise ValueError("Mode must be 'paper' or 'live'")
        self.mode = mode

        self.api_key = os.getenv("BREEZE_API_KEY")
        self.api_secret = os.getenv("BREEZE_API_SECRET")
        self.session_token = os.getenv("BREEZE_SESSION_TOKEN")

        if not all([self.api_key, self.api_secret, self.session_token]):
            raise ValueError("Breeze API credentials (BREEZE_API_KEY, BREEZE_API_SECRET, BREEZE_SESSION_TOKEN) must be set in the .env file.")

        self.breeze_connector = BreezeConnector()
        if self.mode == 'live':
            if not self.breeze_connector.connect():
                raise ConnectionError("Failed to connect to Breeze API in live mode.")
            self.breeze = self.breeze_connector.breeze # Get the connected breeze object
        print(f"TradeExecutor initialized in {self.mode} mode.")

        self.trade_log_path = 'trade_log.csv'
        self._initialize_trade_log()

    def _initialize_trade_log(self):
        if not os.path.exists(self.trade_log_path):
            log_df = pd.DataFrame(columns=[
                'timestamp', 'strategy_name', 'action', 'instrument', 
                'quantity', 'price', 'status', 'mode', 'order_id', 'message'
            ])
            log_df.to_csv(self.trade_log_path, index=False)

    def _log_trade(self, strategy_name, action, instrument, quantity, price, status, order_id=None, message=""):
        timestamp = datetime.now().isoformat()
        new_log = pd.DataFrame([{
            'timestamp': timestamp, 
            'strategy_name': strategy_name, 
            'action': action, 
            'instrument': instrument, 
            'quantity': quantity, 
            'price': price, 
            'status': status, 
            'mode': self.mode,
            'order_id': order_id,
            'message': message
        }])
        new_log.to_csv(self.trade_log_path, mode='a', header=False, index=False)
        print(f"Trade Logged: {timestamp} | {strategy_name} | {action} {quantity} of {instrument} at {price} | Status: {status}")

    def execute_trade(self, strategy_name, action, instrument_code, exchange_code, product_type, quantity, price=0, stop_loss=0, target_price=0):
        # Implement risk controls here before execution
        # For now, basic execution logic
        print(f"Attempting to {action} {quantity} of {instrument_code} in {self.mode} mode...")

        order_id = None
        status = "FAILED"
        message = ""

        try:
            if self.mode == 'paper':
                # Simulate trade execution
                status = "PAPER_EXECUTED"
                message = "Paper trade executed successfully."
                order_id = f"PAPER_{datetime.now().timestamp()}"
            elif self.mode == 'live':
                # Live trade execution using Breeze API via BreezeConnector
                print("Placing live order via Breeze API...")
                order_response = self.breeze_connector.place_order(
                    stock_code=instrument_code,
                    exchange_code=exchange_code,
                    product_type=product_type,
                    buy_sell=action,
                    quantity=quantity,
                    price=price
                    # Add other parameters like expiry_date, strike_price, right for options if needed
                )
                if order_response and order_response.get("Status") == 200 and order_response.get("Success"):
                    order_id = order_response["Success"][0]["order_id"]
                    status = "LIVE_ORDER_PLACED"
                    message = f"Live order placed successfully. Order ID: {order_id}"
                else:
                    status = "LIVE_ORDER_FAILED"
                    message = f"Live order placement failed: {order_response.get('Error') if order_response else 'Unknown error'}"

        except Exception as e:
            message = f"Exception during trade execution: {e}"
            status = "ERROR"
        finally:
            self._log_trade(strategy_name, action, instrument_code, quantity, price, status, order_id, message)
            return status, order_id, message

    def get_trade_log(self):
        if os.path.exists(self.trade_log_path):
            return pd.read_csv(self.trade_log_path)
        return pd.DataFrame()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Execute paper or live trades.")
    parser.add_argument('--mode', type=str, default='paper', help="Trading mode: 'paper' or 'live'")
    parser.add_argument('--strategy', type=str, default='DefaultStrategy', help="Name of the strategy to execute")
    parser.add_argument('--action', type=str, default='BUY', help="Trade action: 'BUY' or 'SELL'")
    parser.add_argument('--instrument', type=str, default='NIFTY', help="Instrument code (e.g., NIFTY, BANKNIFTY)")
    parser.add_argument('--exchange', type=str, default='NSE', help="Exchange code (e.g., NSE)")
    parser.add_argument('--product_type', type=str, default='options', help="Product type (e.g., options, futures)")
    parser.add_argument('--quantity', type=int, default=50, help="Quantity of the instrument")
    parser.add_argument('--price', type=float, default=0, help="Price of the instrument (0 for market order)")

    args = parser.parse_args()

    executor = TradeExecutor(mode=args.mode)
    status, order_id, msg = executor.execute_trade(
        strategy_name=args.strategy,
        action=args.action,
        instrument_code=args.instrument,
        exchange_code=args.exchange,
        product_type=args.product_type,
        quantity=args.quantity,
        price=args.price
    )
    print(f"Trade Result ({args.mode} mode): Status={status}, OrderID={order_id}, Message={msg}")

    print("\nFull Trade Log:")
    print(executor.get_trade_log().to_string())