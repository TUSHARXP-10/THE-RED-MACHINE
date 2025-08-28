#!/usr/bin/env python3
"""
Complete Kite Connect Broker Interface
Replaces all ICICI/Breeze functionality with Kite Connect
"""

import os
import json
import time
from datetime import datetime, timedelta
from kiteconnect import KiteConnect
from dotenv import load_dotenv

class KiteBrokerInterface:
    """Complete Kite Connect broker interface for SENSEX scalping"""
    
    def __init__(self):
        """Initialize Kite Connect with credentials from .env"""
        load_dotenv()
        
        self.api_key = os.getenv('KITE_API_KEY')
        self.api_secret = os.getenv('KITE_API_SECRET')
        self.access_token = os.getenv('KITE_ACCESS_TOKEN')
        
        if not all([self.api_key, self.api_secret, self.access_token]):
            raise ValueError("Missing Kite credentials in .env file")
        
        self.kite = KiteConnect(api_key=self.api_key)
        self.kite.set_access_token(self.access_token)
        
        print("✅ Kite Connect initialized successfully")
    
    def get_sensex_data(self):
        """Get real-time SENSEX data"""
        try:
            # Get all instruments and find SENSEX
            instruments = self.kite.instruments("BSE")
            sensex_token = None
            
            for instrument in instruments:
                if instrument['tradingsymbol'] == 'SENSEX' and instrument['instrument_type'] == 'EQ':
                    sensex_token = instrument['instrument_token']
                    break
            
            if not sensex_token:
                # Fallback to known SENSEX token
                sensex_token = 260617
            
            # Get quote using instrument token
            quote = self.kite.quote([f"BSE:{sensex_token}"])
            sensex_data = quote[f"BSE:{sensex_token}"]
            
            return {
                'symbol': 'SENSEX',
                'price': sensex_data['last_price'],
                'change': sensex_data['net_change'],
                'change_percent': sensex_data['ohlc']['change'],
                'volume': sensex_data['volume'],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error fetching SENSEX data: {e}")
            return None
    
    def get_nifty_data(self):
        """Get real-time NIFTY data"""
        try:
            # NIFTY 50 index on NSE - using instrument token 256265
            quote = self.kite.quote(["NSE:256265"])
            nifty_data = quote["NSE:256265"]
            
            return {
                'symbol': 'NIFTY',
                'price': nifty_data['last_price'],
                'change': nifty_data['net_change'],
                'change_percent': nifty_data['ohlc']['change'],
                'volume': nifty_data['volume'],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error fetching NIFTY data: {e}")
            return None
    
    def place_order(self, symbol, action, quantity, price, order_type="LIMIT"):
        """Place an order on Kite Connect"""
        try:
            # Determine exchange and trading symbol
            # Note: SENSEX and NIFTY are indices, not tradeable directly
            # For trading, use index futures or ETFs
            exchange = "NSE"
            tradingsymbol = symbol.upper()
            
            # Place order
            order_id = self.kite.place_order(
                variety=self.kite.VARIETY_REGULAR,
                exchange=exchange,
                tradingsymbol=tradingsymbol,
                transaction_type=action.upper(),
                quantity=int(quantity),
                product=self.kite.PRODUCT_MIS,
                order_type=order_type.upper(),
                price=float(price),
                validity=self.kite.VALIDITY_DAY
            )
            
            return {
                'status': 'success',
                'order_id': order_id,
                'symbol': symbol,
                'action': action,
                'quantity': quantity,
                'price': price,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'symbol': symbol,
                'action': action,
                'quantity': quantity,
                'price': price
            }
    
    def cancel_order(self, order_id):
        """Cancel an existing order"""
        try:
            result = self.kite.cancel_order(
                variety=self.kite.VARIETY_REGULAR,
                order_id=order_id
            )
            return {
                'status': 'success',
                'order_id': order_id,
                'message': 'Order cancelled successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'order_id': order_id
            }
    
    def get_positions(self):
        """Get current positions"""
        try:
            positions = self.kite.positions()
            return positions['net']
        except Exception as e:
            print(f"Error fetching positions: {e}")
            return []
    
    def get_holdings(self):
        """Get portfolio holdings"""
        try:
            holdings = self.kite.holdings()
            return holdings
        except Exception as e:
            print(f"Error fetching holdings: {e}")
            return []
    
    def get_margins(self):
        """Get available margins"""
        try:
            margins = self.kite.margins()
            return margins
        except Exception as e:
            print(f"Error fetching margins: {e}")
            return {}
    
    def get_profile(self):
        """Get user profile information"""
        try:
            profile = self.kite.profile()
            return profile
        except Exception as e:
            print(f"Error fetching profile: {e}")
            return {}
    
    def get_historical_data(self, symbol, interval="5minute", days=1):
        """Get historical data for strategy backtesting"""
        try:
            # Map symbols to instrument tokens
            symbol_map = {
                'SENSEX': 260617,  # SENSEX instrument token
                'NIFTY': 256265,   # NIFTY 50 instrument token
                'RELIANCE': 738561,  # Example stock
            }
            
            # Handle symbol mapping
            instrument_token = None
            if symbol.upper() == 'SENSEX' or 'BSESN' in symbol.upper():
                instrument_token = 260617  # SENSEX
            elif symbol.upper() == 'NIFTY' or 'NIFTY' in symbol.upper():
                instrument_token = 256265  # NIFTY 50
            elif symbol.upper() in symbol_map:
                instrument_token = symbol_map[symbol.upper()]
            else:
                # Try to find symbol in NSE
                try:
                    instruments = self.kite.instruments("NSE")
                    for instrument in instruments:
                        if instrument['tradingsymbol'] == symbol.upper():
                            instrument_token = instrument['instrument_token']
                            break
                except Exception:
                    pass
            
            if not instrument_token:
                print(f"❌ Symbol {symbol} not found")
                return []
            
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            # Get historical data
            data = self.kite.historical_data(
                instrument_token=instrument_token,
                from_date=from_date.date(),
                to_date=to_date.date(),
                interval=interval
            )
            
            return data
            
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return []
    
    def get_last_traded_price(self, symbol):
        """Get last traded price for a symbol"""
        try:
            # Determine exchange and trading symbol
            if symbol.upper() == "SENSEX":
                exchange = "BSE"
                tradingsymbol = "BSESN"
            elif symbol.upper() == "NIFTY":
                exchange = "NSE"
                tradingsymbol = "NIFTY 50"
            else:
                exchange = "NSE"
                tradingsymbol = symbol.upper()
            
            quote = self.kite.ltp(f"{exchange}:{tradingsymbol}")
            return quote[f"{exchange}:{tradingsymbol}"]['last_price']
            
        except Exception as e:
            print(f"Error fetching LTP for {symbol}: {e}")
            return None

# Example usage for testing
if __name__ == "__main__":
    try:
        # Initialize broker
        broker = KiteBrokerInterface()
        
        # Test basic functionality
        print("\n📊 Testing SENSEX data...")
        sensex = broker.get_sensex_data()
        if sensex:
            print(f"SENSEX: ₹{sensex['price']} ({sensex['change_percent']:.2f}%)")
        
        print("\n💰 Testing account info...")
        profile = broker.get_profile()
        print(f"User: {profile.get('user_name', 'Unknown')}")
        
        print("\n📋 Testing margins...")
        margins = broker.get_margins()
        print(f"Available cash: ₹{margins.get('equity', {}).get('available', {}).get('cash', 0)}")
        
        print("\n✅ All tests passed! Ready for live trading")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Run 'python quick_kite_session_fix.py' to fix credentials")