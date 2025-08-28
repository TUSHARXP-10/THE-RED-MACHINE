#!/usr/bin/env python3
"""
Kite Connect SDK Integration for THE RED MACHINE
Replaces Breeze SDK with full Kite Connect functionality
"""

import kiteconnect
from kiteconnect import KiteConnect, KiteTicker
import pandas as pd
import numpy as np
import json
import logging
import time
from datetime import datetime, timedelta
import threading
from typing import Dict, List, Optional
import yaml

class KiteIntegration:
    def __init__(self, api_key: str, access_token: str):
        """Initialize Kite Connect"""
        self.api_key = api_key
        self.access_token = access_token
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)
        self.ticker = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('kite_trading.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Trading state
        self.positions = {}
        self.orders = {}
        self.holdings = {}
        self.balance = 3000.0
        self.is_trading = False
        
        # Initialize
        self.load_instruments()
        
    def load_instruments(self):
        """Load NSE instruments for SENSEX"""
        try:
            # Get SENSEX instruments
            self.sensex_instruments = [
                {'instrument_token': 128083204, 'tradingsymbol': 'SENSEX', 'name': 'SENSEX'},
                {'instrument_token': 128083460, 'tradingsymbol': 'BANKNIFTY', 'name': 'BANK NIFTY'},
                {'instrument_token': 128083716, 'tradingsymbol': 'NIFTY', 'name': 'NIFTY 50'}
            ]
            
            # Get active SENSEX stocks
            instruments = self.kite.instruments("NSE")
            self.stocks = [
                inst for inst in instruments 
                if inst['segment'] == 'NSE' and 
                inst['tradingsymbol'] in [
                    'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ITC', 'ICICIBANK', 
                    'SBIN', 'BHARTIARTL', 'HINDUNILVR', 'LARTOUCH'
                ]
            ]
            
            self.logger.info(f"Loaded {len(self.stocks)} SENSEX stocks")
            
        except Exception as e:
            self.logger.error(f"Error loading instruments: {e}")
            self.stocks = []
    
    def get_live_data(self, instrument_token: int) -> Dict:
        """Get live market data for an instrument"""
        try:
            quote = self.kite.quote([f"NSE:{instrument_token}"])
            return quote[f"NSE:{instrument_token}"]
        except Exception as e:
            self.logger.error(f"Error getting live data: {e}")
            return {}
    
    def get_historical_data(self, instrument_token: int, 
                          from_date: datetime, 
                          to_date: datetime, 
                          interval: str = "5minute") -> pd.DataFrame:
        """Get historical data"""
        try:
            data = self.kite.historical_data(
                instrument_token=instrument_token,
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
    
    def place_order(self, symbol: str, quantity: int, 
                   order_type: str = "MARKET", 
                   transaction_type: str = "BUY",
                   price: Optional[float] = None,
                   stop_loss: Optional[float] = None,
                   target: Optional[float] = None) -> Dict:
        """Place an order"""
        try:
            # Find instrument
            instrument = next((s for s in self.stocks 
                             if s['tradingsymbol'] == symbol), None)
            
            if not instrument:
                self.logger.error(f"Instrument {symbol} not found")
                return {"status": "error", "message": "Instrument not found"}
            
            # Calculate order value
            current_price = self.get_live_data(instrument['instrument_token']).get('last_price', 0)
            order_value = current_price * quantity
            
            # Check if sufficient balance
            if transaction_type == "BUY" and order_value > self.balance:
                return {"status": "error", "message": "Insufficient balance"}
            
            # Place order
            order_params = {
                "tradingsymbol": symbol,
                "exchange": "NSE",
                "transaction_type": transaction_type,
                "order_type": order_type,
                "quantity": quantity,
                "product": "MIS",  # Intraday
                "variety": "regular"
            }
            
            if price and order_type in ["LIMIT", "SL", "SL-M"]:
                order_params["price"] = price
            
            if stop_loss:
                order_params["stoploss"] = stop_loss
            
            order_id = self.kite.place_order(**order_params)
            
            # Store order
            self.orders[order_id] = {
                "symbol": symbol,
                "quantity": quantity,
                "price": price or current_price,
                "transaction_type": transaction_type,
                "timestamp": datetime.now(),
                "status": "PLACED"
            }
            
            self.logger.info(f"Order placed: {symbol} {transaction_type} {quantity} @ {price or current_price}")
            
            return {"status": "success", "order_id": order_id}
            
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_positions(self) -> Dict:
        """Get current positions"""
        try:
            positions = self.kite.positions()
            return {
                "net": positions.get("net", []),
                "day": positions.get("day", [])
            }
        except Exception as e:
            self.logger.error(f"Error getting positions: {e}")
            return {"net": [], "day": []}
    
    def get_holdings(self) -> List[Dict]:
        """Get holdings"""
        try:
            holdings = self.kite.holdings()
            return holdings
        except Exception as e:
            self.logger.error(f"Error getting holdings: {e}")
            return []
    
    def get_funds(self) -> Dict:
        """Get available funds"""
        try:
            margins = self.kite.margins()
            return {
                "available_cash": margins.get("equity", {}).get("available", {}).get("cash", 0),
                "used_margin": margins.get("equity", {}).get("used", {}).get("cash", 0),
                "net": margins.get("equity", {}).get("net", {}).get("cash", 0)
            }
        except Exception as e:
            self.logger.error(f"Error getting funds: {e}")
            return {"available_cash": 0, "used_margin": 0, "net": 0}
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel an order"""
        try:
            self.kite.cancel_order(variety="regular", order_id=order_id)
            
            if order_id in self.orders:
                self.orders[order_id]["status"] = "CANCELLED"
            
            self.logger.info(f"Order cancelled: {order_id}")
            return {"status": "success", "message": "Order cancelled"}
            
        except Exception as e:
            self.logger.error(f"Error cancelling order: {e}")
            return {"status": "error", "message": str(e)}
    
    def start_websocket(self, symbols: List[str]):
        """Start WebSocket for real-time data"""
        try:
            self.ticker = KiteTicker(self.api_key, self.access_token)
            
            def on_ticks(ws, ticks):
                for tick in ticks:
                    symbol = tick['instrument_token']
                    self.live_data[symbol] = {
                        'last_price': tick['last_price'],
                        'volume': tick['volume_traded'],
                        'timestamp': datetime.fromtimestamp(tick['timestamp'])
                    }
            
            def on_connect(ws, response):
                self.logger.info("WebSocket connected")
                # Subscribe to symbols
                tokens = [s['instrument_token'] for s in self.stocks 
                         if s['tradingsymbol'] in symbols]
                ws.subscribe(tokens)
                ws.set_mode(ws.MODE_FULL, tokens)
            
            def on_close(ws, code, reason):
                self.logger.info(f"WebSocket closed: {code} - {reason}")
            
            self.ticker.on_ticks = on_ticks
            self.ticker.on_connect = on_connect
            self.ticker.on_close = on_close
            
            self.ticker.connect(threaded=True)
            
        except Exception as e:
            self.logger.error(f"Error starting WebSocket: {e}")
    
    def get_trades_history(self, from_date: datetime, to_date: datetime) -> List[Dict]:
        """Get trades history"""
        try:
            trades = self.kite.trades()
            return trades
        except Exception as e:
            self.logger.error(f"Error getting trades: {e}")
            return []
    
    def calculate_pnl(self) -> Dict:
        """Calculate P&L for current positions"""
        try:
            positions = self.get_positions()
            total_pnl = 0
            
            for position in positions.get("net", []):
                if position['quantity'] != 0:
                    pnl = (position['last_price'] - position['average_price']) * position['quantity']
                    total_pnl += pnl
            
            return {
                "total_pnl": total_pnl,
                "realized_pnl": 0,
                "unrealized_pnl": total_pnl
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating P&L: {e}")
            return {"total_pnl": 0, "realized_pnl": 0, "unrealized_pnl": 0}
    
    def get_order_book(self) -> List[Dict]:
        """Get order book"""
        try:
            orders = self.kite.orders()
            return orders
        except Exception as e:
            self.logger.error(f"Error getting order book: {e}")
            return []

# Test function
def test_kite_integration():
    """Test Kite integration"""
    try:
        # Load credentials from config
        with open('kite_config.json', 'r') as f:
            config = json.load(f)
        
        kite = KiteIntegration(
            api_key=config['api_key'],
            access_token=config['access_token']
        )
        
        # Test connection
        funds = kite.get_funds()
        print(f"Available funds: Rs.{funds['available_cash']}")
        
        # Test getting live data
        if kite.stocks:
            symbol = kite.stocks[0]['tradingsymbol']
            live_data = kite.get_live_data(kite.stocks[0]['instrument_token'])
            print(f"Live data for {symbol}: {live_data}")
        
        print("✅ Kite integration test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Kite integration test failed: {e}")
        return False

if __name__ == "__main__":
    test_kite_integration()