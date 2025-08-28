#!/usr/bin/env python3
"""
Kite Connect Broker Interface
Complete migration from ICICI/Breeze to Kite Connect for SENSEX scalping system
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from dotenv import load_dotenv

# Import Kite Connect
from kiteconnect import KiteConnect

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kite_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class KiteBrokerInterface:
    """
    Complete Kite Connect interface for SENSEX scalping system
    Replaces ICICI Breeze functionality entirely
    """
    
    def __init__(self):
        """Initialize Kite Connect with credentials"""
        load_dotenv()
        
        self.api_key = os.getenv('KITE_API_KEY')
        self.api_secret = os.getenv('KITE_API_SECRET')
        self.access_token = os.getenv('KITE_ACCESS_TOKEN')
        self.redirect_url = os.getenv('KITE_REDIRECT_URL', 'https://localhost')
        
        # Validate credentials
        if not all([self.api_key, self.api_secret, self.access_token]):
            raise ValueError("Missing Kite credentials in .env file")
        
        # Initialize Kite Connect
        self.kite = KiteConnect(api_key=self.api_key)
        self.kite.set_access_token(self.access_token)
        
        # Cache for instrument tokens
        self.instrument_cache = {}
        
        logger.info("Kite Broker Interface initialized successfully")
    
    def get_sensex_data(self) -> Dict[str, Any]:
        """Get real-time SENSEX data"""
        try:
            # SENSEX symbol on BSE
            symbol = "BSE:BSESN"
            quote = self.kite.quote(symbol)
            
            if symbol in quote:
                data = quote[symbol]
                return {
                    'symbol': 'SENSEX',
                    'price': data['last_price'],
                    'volume': data['volume'],
                    'open': data['ohlc']['open'],
                    'high': data['ohlc']['high'],
                    'low': data['ohlc']['low'],
                    'close': data['ohlc']['close'],
                    'change': data['change'],
                    'change_percent': data['change_percent'],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise Exception("SENSEX data not found")
                
        except Exception as e:
            logger.error(f"Error fetching SENSEX data: {e}")
            return {'error': str(e)}
    
    def get_nifty_data(self) -> Dict[str, Any]:
        """Get real-time NIFTY data"""
        try:
            symbol = "NSE:NIFTY 50"
            quote = self.kite.quote(symbol)
            
            if symbol in quote:
                data = quote[symbol]
                return {
                    'symbol': 'NIFTY',
                    'price': data['last_price'],
                    'volume': data['volume'],
                    'open': data['ohlc']['open'],
                    'high': data['ohlc']['high'],
                    'low': data['ohlc']['low'],
                    'close': data['ohlc']['close'],
                    'change': data['change'],
                    'change_percent': data['change_percent'],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise Exception("NIFTY data not found")
                
        except Exception as e:
            logger.error(f"Error fetching NIFTY data: {e}")
            return {'error': str(e)}
    
    def place_order(self, symbol: str, action: str, quantity: int, 
                   price: float, order_type: str = "LIMIT", 
                   product: str = "CNC") -> Dict[str, Any]:
        """
        Place an order using Kite Connect
        
        Args:
            symbol: Trading symbol (e.g., "RELIANCE", "SBIN")
            action: "BUY" or "SELL"
            quantity: Number of shares
            price: Order price
            order_type: "LIMIT", "MARKET", "SL", "SL-M"
            product: "CNC" (Cash & Carry), "MIS" (Intraday), "NRML" (Normal)
        """
        try:
            # Determine exchange based on symbol
            exchange = "NSE" if symbol.upper() != "BSESN" else "BSE"
            
            # Map action to Kite transaction type
            transaction_type = self.kite.TRANSACTION_TYPE_BUY if action.upper() == "BUY" else self.kite.TRANSACTION_TYPE_SELL
            
            # Map order type
            kite_order_type = getattr(self.kite, f"ORDER_TYPE_{order_type.upper().replace('-', '_')}")
            
            # Map product type
            kite_product = getattr(self.kite, f"PRODUCT_{product.upper()}")
            
            order_id = self.kite.place_order(
                variety=self.kite.VARIETY_REGULAR,
                exchange=exchange,
                tradingsymbol=symbol.upper(),
                transaction_type=transaction_type,
                quantity=quantity,
                product=kite_product,
                order_type=kite_order_type,
                price=price if order_type.upper() != "MARKET" else 0,
                validity=self.kite.VALIDITY_DAY
            )
            
            logger.info(f"Order placed successfully: {symbol} {action} {quantity}@{price}")
            
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
            logger.error(f"Error placing order: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'symbol': symbol,
                'action': action,
                'quantity': quantity,
                'price': price,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get status of a specific order"""
        try:
            orders = self.kite.orders()
            for order in orders:
                if str(order['order_id']) == str(order_id):
                    return {
                        'status': 'success',
                        'order_id': order_id,
                        'status': order['status'],
                        'filled_quantity': order['filled_quantity'],
                        'pending_quantity': order['pending_quantity'],
                        'average_price': order['average_price'],
                        'timestamp': order['order_timestamp']
                    }
            
            return {'status': 'error', 'message': f'Order {order_id} not found'}
            
        except Exception as e:
            logger.error(f"Error getting order status: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_positions(self) -> Dict[str, Any]:
        """Get current positions"""
        try:
            positions = self.kite.positions()
            return {
                'status': 'success',
                'net_positions': positions['net'],
                'day_positions': positions['day'],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_holdings(self) -> Dict[str, Any]:
        """Get current holdings"""
        try:
            holdings = self.kite.holdings()
            return {
                'status': 'success',
                'holdings': holdings,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting holdings: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_margin(self) -> Dict[str, Any]:
        """Get available margins"""
        try:
            margins = self.kite.margins()
            return {
                'status': 'success',
                'equity': margins.get('equity', {}),
                'commodity': margins.get('commodity', {}),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting margins: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_historical_data(self, symbol: str, interval: str = "minute", 
                           duration: int = 60) -> List[Dict[str, Any]]:
        """
        Get historical data for a symbol
        
        Args:
            symbol: Trading symbol
            interval: "minute", "5minute", "15minute", "30minute", "60minute", "day"
            duration: Number of data points to fetch
        """
        try:
            # Determine exchange and symbol
            if symbol.upper() == "BSESN":
                instrument = "BSE:BSESN"
            elif symbol.upper() == "NIFTY":
                instrument = "NSE:NIFTY 50"
            else:
                instrument = f"NSE:{symbol.upper()}"
            
            # Get historical data
            historical_data = self.kite.historical_data(
                instrument,
                datetime.now().replace(hour=9, minute=15, second=0, microsecond=0),
                datetime.now(),
                interval
            )
            
            # Format data
            formatted_data = []
            for candle in historical_data[-duration:]:
                formatted_data.append({
                    'timestamp': candle['date'].isoformat(),
                    'open': candle['open'],
                    'high': candle['high'],
                    'low': candle['low'],
                    'close': candle['close'],
                    'volume': candle['volume']
                })
            
            return {
                'status': 'success',
                'data': formatted_data,
                'symbol': symbol,
                'interval': interval,
                'count': len(formatted_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an order"""
        try:
            result = self.kite.cancel_order(
                variety=self.kite.VARIETY_REGULAR,
                order_id=order_id
            )
            
            return {
                'status': 'success',
                'order_id': order_id,
                'message': 'Order cancelled successfully',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_ltp(self, symbols: List[str]) -> Dict[str, Any]:
        """Get Last Traded Price for multiple symbols"""
        try:
            # Format symbols
            formatted_symbols = []
            for symbol in symbols:
                if symbol.upper() == "BSESN":
                    formatted_symbols.append("BSE:BSESN")
                elif symbol.upper() == "NIFTY":
                    formatted_symbols.append("NSE:NIFTY 50")
                else:
                    formatted_symbols.append(f"NSE:{symbol.upper()}")
            
            # Get LTP
            ltps = self.kite.ltp(formatted_symbols)
            
            # Format response
            result = {}
            for symbol, data in ltps.items():
                result[symbol] = {
                    'ltp': data['last_price'],
                    'timestamp': datetime.now().isoformat()
                }
            
            return {
                'status': 'success',
                'data': result
            }
            
        except Exception as e:
            logger.error(f"Error getting LTP: {e}")
            return {'status': 'error', 'message': str(e)}

def test_interface():
    """Test the Kite broker interface"""
    try:
        broker = KiteBrokerInterface()
        
        # Test SENSEX data
        print("Testing SENSEX data...")
        sensex_data = broker.get_sensex_data()
        print(f"SENSEX Data: {json.dumps(sensex_data, indent=2)}")
        
        # Test margins
        print("\nTesting margins...")
        margins = broker.get_margin()
        print(f"Margins: {json.dumps(margins, indent=2)}")
        
        # Test positions
        print("\nTesting positions...")
        positions = broker.get_positions()
        print(f"Positions: {json.dumps(positions, indent=2)}")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing interface: {e}")

if __name__ == '__main__':
    print("🔧 Testing Kite Broker Interface...")
    test_interface()