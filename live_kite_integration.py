#!/usr/bin/env python3
"""
Live Kite API Integration for THE RED MACHINE
Real-time market data streaming and order execution
"""

import os
import json
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from kiteconnect import KiteConnect, KiteTicker
from dotenv import load_dotenv
import logging
import time
import queue
import websockets

# Load environment variables
load_dotenv()

class LiveKiteIntegration:
    """
    Live Kite API integration for real-time market data and trading
    """
    
    def __init__(self):
        self.api_key = os.getenv("KITE_API_KEY", "").strip('"')
        self.access_token = os.getenv("KITE_ACCESS_TOKEN", "").strip('"')
        self.kite = None
        self.ticker = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('live_kite_trading.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Real-time data storage
        self.live_data = {}
        self.order_book = {}
        self.positions = {}
        self.holdings = {}
        self.funds = {}
        
        # Thread-safe queues for real-time updates
        self.data_queue = queue.Queue()
        self.order_queue = queue.Queue()
        
        # Subscriptions
        self.subscribed_tokens = set()
        self.instrument_map = {}
        
        # Trading state
        self.is_connected = False
        self.is_streaming = False
        
        # Initialize connection
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize Kite Connect and validate credentials"""
        try:
            if not all([self.api_key, self.access_token]):
                self.logger.error("Kite API credentials missing. Check .env file.")
                self.logger.error("Run: python fix_auth_now.py to fix authentication")
                return False
                
            self.kite = KiteConnect(api_key=self.api_key)
            self.kite.set_access_token(self.access_token)
            
            # Validate connection
            profile = self.kite.profile()
            self.logger.info(f"Connected to Kite as {profile.get('user_name', 'Unknown')}")
            self.is_connected = True
            
            # Initialize ticker for real-time data
            self.ticker = KiteTicker(self.api_key, self.access_token)
            self._setup_ticker_callbacks()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Kite connection: {e}")
            self.logger.error("Authentication failed. Run: python fix_auth_now.py")
            self.logger.error("Or check: kite_auth_guide.md for manual steps")
            return False
    
    def _setup_ticker_callbacks(self):
        """Setup WebSocket callbacks for real-time data"""
        
        def on_ticks(ws, ticks):
            """Handle incoming tick data"""
            for tick in ticks:
                instrument_token = tick['instrument_token']
                self.live_data[instrument_token] = {
                    'last_price': tick.get('last_price', 0),
                    'volume': tick.get('volume', 0),
                    'oi': tick.get('oi', 0),
                    'buy_quantity': tick.get('buy_quantity', 0),
                    'sell_quantity': tick.get('sell_quantity', 0),
                    'timestamp': datetime.now().isoformat(),
                    'raw': tick
                }
                
                # Add to queue for processing
                self.data_queue.put({
                    'type': 'tick',
                    'instrument_token': instrument_token,
                    'data': self.live_data[instrument_token]
                })
        
        def on_connect(ws, response):
            """Handle WebSocket connection"""
            self.logger.info("WebSocket connected successfully")
            self.is_streaming = True
            
            # Subscribe to existing tokens
            if self.subscribed_tokens:
                ws.subscribe(list(self.subscribed_tokens))
                ws.set_mode(ws.MODE_FULL, list(self.subscribed_tokens))
        
        def on_close(ws, code, reason):
            """Handle WebSocket disconnection"""
            self.logger.warning(f"WebSocket closed: {code} - {reason}")
            self.is_streaming = False
        
        def on_error(ws, code, reason):
            """Handle WebSocket errors"""
            self.logger.error(f"WebSocket error: {code} - {reason}")
            self.is_streaming = False
        
        def on_reconnect(ws, attempts_count):
            """Handle reconnection attempts"""
            self.logger.info(f"Reconnection attempt: {attempts_count}")
        
        def on_noreconnect(ws):
            """Handle max reconnection attempts reached"""
            self.logger.error("Max reconnection attempts reached")
            self.is_streaming = False
        
        # Assign callbacks
        self.ticker.on_ticks = on_ticks
        self.ticker.on_connect = on_connect
        self.ticker.on_close = on_close
        self.ticker.on_error = on_error
        self.ticker.on_reconnect = on_reconnect
        self.ticker.on_noreconnect = on_noreconnect
    
    def get_sensex_instruments(self) -> List[Dict]:
        """Get SENSEX and major stocks for trading"""
        try:
            # Get NSE instruments
            instruments = self.kite.instruments("NSE")
            
            # Filter for major SENSEX stocks
            sensex_stocks = [
                'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ITC', 'ICICIBANK',
                'SBIN', 'BHARTIARTL', 'HINDUNILVR', 'LARTOUCH', 'AXISBANK',
                'KOTAKBANK', 'LT', 'MARUTI', 'NESTLEIND', 'POWERGRID',
                'SUNPHARMA', 'ULTRACEMCO', 'WIPRO', 'ADANIPORTS'
            ]
            
            filtered_instruments = [
                inst for inst in instruments
                if inst['tradingsymbol'] in sensex_stocks
                and inst['segment'] == 'NSE'
                and inst['instrument_type'] == 'EQ'
            ]
            
            # Add index instruments
            indices = [
                {'instrument_token': 256265, 'tradingsymbol': 'NIFTY50', 'name': 'NIFTY 50'},
                {'instrument_token': 260105, 'tradingsymbol': 'BANKNIFTY', 'name': 'BANK NIFTY'},
                {'instrument_token': 265, 'tradingsymbol': 'SENSEX', 'name': 'SENSEX'}
            ]
            
            return filtered_instruments + indices
            
        except Exception as e:
            self.logger.error(f"Error fetching instruments: {e}")
            return []
    
    def subscribe_realtime_data(self, symbols: List[str]):
        """Subscribe to real-time data for given symbols"""
        if not self.is_connected:
            self.logger.error("Not connected to Kite")
            return False
        
        try:
            # Get instruments for symbols
            instruments = self.get_sensex_instruments()
            
            tokens = []
            for symbol in symbols:
                instrument = next((i for i in instruments 
                                 if i['tradingsymbol'] == symbol.upper()), None)
                if instrument:
                    tokens.append(instrument['instrument_token'])
                    self.instrument_map[instrument['instrument_token']] = symbol.upper()
            
            if tokens:
                self.subscribed_tokens.update(tokens)
                
                if self.is_streaming:
                    self.ticker.subscribe(tokens)
                    self.ticker.set_mode(self.ticker.MODE_FULL, tokens)
                else:
                    # Start streaming if not already started
                    self.start_realtime_streaming()
                
                self.logger.info(f"Subscribed to {len(tokens)} instruments")
                return True
            
        except Exception as e:
            self.logger.error(f"Error subscribing to data: {e}")
        
        return False
    
    def start_realtime_streaming(self):
        """Start real-time data streaming"""
        if not self.ticker:
            self.logger.error("Ticker not initialized")
            return False
        
        try:
            self.ticker.connect(threaded=True)
            return True
        except Exception as e:
            self.logger.error(f"Error starting streaming: {e}")
            return False
    
    def stop_realtime_streaming(self):
        """Stop real-time data streaming"""
        if self.ticker and self.is_streaming:
            try:
                self.ticker.close()
                self.is_streaming = False
                return True
            except Exception as e:
                self.logger.error(f"Error stopping streaming: {e}")
        return False
    
    def get_live_quote(self, symbol: str) -> Optional[Dict]:
        """Get latest quote for a symbol"""
        try:
            # Find instrument token
            instruments = self.get_sensex_instruments()
            instrument = next((i for i in instruments 
                             if i['tradingsymbol'] == symbol.upper()), None)
            
            if not instrument:
                return None
            
            # Check if we have real-time data
            token = instrument['instrument_token']
            if token in self.live_data:
                return self.live_data[token]
            
            # Fallback to API call
            quote = self.kite.quote([f"NSE:{symbol.upper()}"])
            return quote.get(f"NSE:{symbol.upper()}")
            
        except Exception as e:
            self.logger.error(f"Error getting live quote: {e}")
            return None
    
    def place_market_order(self, symbol: str, quantity: int, 
                          transaction_type: str, product: str = "MIS") -> Dict:
        """Place a market order"""
        if not self.is_connected:
            return {"status": "error", "message": "Not connected to Kite"}
        
        try:
            order_params = {
                "tradingsymbol": symbol.upper(),
                "exchange": "NSE",
                "transaction_type": transaction_type.upper(),
                "quantity": quantity,
                "order_type": "MARKET",
                "product": product,
                "variety": "regular"
            }
            
            order_id = self.kite.place_order(**order_params)
            
            # Store order details
            self.order_book[order_id] = {
                "symbol": symbol.upper(),
                "quantity": quantity,
                "transaction_type": transaction_type.upper(),
                "order_type": "MARKET",
                "status": "PLACED",
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Market order placed: {transaction_type} {quantity} {symbol}")
            
            return {
                "status": "success", 
                "order_id": order_id,
                "details": self.order_book[order_id]
            }
            
        except Exception as e:
            self.logger.error(f"Error placing market order: {e}")
            return {"status": "error", "message": str(e)}
    
    def place_limit_order(self, symbol: str, quantity: int, price: float,
                         transaction_type: str, product: str = "MIS") -> Dict:
        """Place a limit order"""
        if not self.is_connected:
            return {"status": "error", "message": "Not connected to Kite"}
        
        try:
            order_params = {
                "tradingsymbol": symbol.upper(),
                "exchange": "NSE",
                "transaction_type": transaction_type.upper(),
                "quantity": quantity,
                "price": price,
                "order_type": "LIMIT",
                "product": product,
                "variety": "regular"
            }
            
            order_id = self.kite.place_order(**order_params)
            
            self.order_book[order_id] = {
                "symbol": symbol.upper(),
                "quantity": quantity,
                "price": price,
                "transaction_type": transaction_type.upper(),
                "order_type": "LIMIT",
                "status": "PLACED",
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Limit order placed: {transaction_type} {quantity} {symbol} @ {price}")
            
            return {
                "status": "success", 
                "order_id": order_id,
                "details": self.order_book[order_id]
            }
            
        except Exception as e:
            self.logger.error(f"Error placing limit order: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_order_status(self, order_id: str) -> Dict:
        """Get order status"""
        if not self.is_connected:
            return {"status": "error", "message": "Not connected to Kite"}
        
        try:
            order = self.kite.order_history(order_id)
            return {"status": "success", "data": order}
        except Exception as e:
            self.logger.error(f"Error getting order status: {e}")
            return {"status": "error", "message": str(e)}
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel an order"""
        if not self.is_connected:
            return {"status": "error", "message": "Not connected to Kite"}
        
        try:
            self.kite.cancel_order(variety="regular", order_id=order_id)
            
            if order_id in self.order_book:
                self.order_book[order_id]["status"] = "CANCELLED"
            
            self.logger.info(f"Order cancelled: {order_id}")
            return {"status": "success", "order_id": order_id}
            
        except Exception as e:
            self.logger.error(f"Error cancelling order: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_portfolio_summary(self) -> Dict:
        """Get complete portfolio summary"""
        if not self.is_connected:
            return {"status": "error", "message": "Not connected to Kite"}
        
        try:
            # Get all portfolio data
            positions = self.kite.positions()
            holdings = self.kite.holdings()
            margins = self.kite.margins()
            
            summary = {
                "positions": positions,
                "holdings": holdings,
                "funds": margins,
                "timestamp": datetime.now().isoformat()
            }
            
            return {"status": "success", "data": summary}
            
        except Exception as e:
            self.logger.error(f"Error getting portfolio summary: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_historical_data(self, symbol: str, from_date: datetime, 
                           to_date: datetime, interval: str = "5minute") -> pd.DataFrame:
        """Get historical data for backtesting"""
        if not self.is_connected:
            return pd.DataFrame()
        
        try:
            # Find instrument token
            instruments = self.get_sensex_instruments()
            instrument = next((i for i in instruments 
                             if i['tradingsymbol'] == symbol.upper()), None)
            
            if not instrument:
                return pd.DataFrame()
            
            data = self.kite.historical_data(
                instrument_token=instrument['instrument_token'],
                from_date=from_date,
                to_date=to_date,
                interval=interval
            )
            
            df = pd.DataFrame(data)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error getting historical data: {e}")
            return pd.DataFrame()
    
    def start_background_updates(self):
        """Start background thread for processing real-time updates"""
        def process_updates():
            while True:
                try:
                    # Process data queue
                    while not self.data_queue.empty():
                        update = self.data_queue.get()
                        self._process_data_update(update)
                    
                    # Process order queue
                    while not self.order_queue.empty():
                        order_update = self.order_queue.get()
                        self._process_order_update(order_update)
                    
                    time.sleep(0.1)  # Small delay to prevent CPU overload
                    
                except Exception as e:
                    self.logger.error(f"Error in background updates: {e}")
        
        thread = threading.Thread(target=process_updates, daemon=True)
        thread.start()
        self.logger.info("Background updates started")
    
    def _process_data_update(self, update: Dict):
        """Process real-time data updates"""
        # This method can be extended to trigger trading logic
        symbol = self.instrument_map.get(update['instrument_token'], 'Unknown')
        price = update['data']['last_price']
        
        self.logger.debug(f"Data update: {symbol} @ {price}")
    
    def _process_order_update(self, update: Dict):
        """Process order updates"""
        self.logger.info(f"Order update: {update}")
    
    def health_check(self) -> Dict:
        """Check system health"""
        return {
            "connected": self.is_connected,
            "streaming": self.is_streaming,
            "subscribed_instruments": len(self.subscribed_tokens),
            "live_data_points": len(self.live_data),
            "orders_placed": len(self.order_book),
            "timestamp": datetime.now().isoformat()
        }

# Integration with THE RED MACHINE
class RedMachineKiteBridge:
    """Bridge between LiveKiteIntegration and THE RED MACHINE"""
    
    def __init__(self):
        self.kite_integration = LiveKiteIntegration()
        self.is_initialized = False
    
    def initialize(self) -> bool:
        """Initialize the bridge"""
        if self.kite_integration.is_connected:
            self.kite_integration.start_background_updates()
            self.is_initialized = True
            return True
        return False
    
    def start_real_time_trading(self, symbols: List[str]):
        """Start real-time trading for given symbols"""
        if not self.is_initialized:
            return {"status": "error", "message": "Bridge not initialized"}
        
        # Subscribe to real-time data
        success = self.kite_integration.subscribe_realtime_data(symbols)
        
        if success:
            return {
                "status": "success",
                "message": f"Started real-time trading for {symbols}",
                "health": self.kite_integration.health_check()
            }
        
        return {"status": "error", "message": "Failed to subscribe to symbols"}

if __name__ == "__main__":
    # Test the integration
    print("Testing Live Kite Integration...")
    
    # Initialize
    bridge = RedMachineKiteBridge()
    
    if bridge.initialize():
        print("✅ Kite integration initialized successfully")
        
        # Start real-time trading for major SENSEX stocks
        symbols = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ITC']
        result = bridge.start_real_time_trading(symbols)
        print(f"Trading status: {result}")
        
        # Keep running for demo
        try:
            while True:
                health = bridge.kite_integration.health_check()
                print(f"Health: {health}")
                time.sleep(5)
        except KeyboardInterrupt:
            print("Stopping...")
            bridge.kite_integration.stop_realtime_streaming()
    else:
        print("❌ Failed to initialize Kite integration")