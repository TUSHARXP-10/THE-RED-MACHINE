#!/usr/bin/env python3
"""
Fixed Trading System for Breeze API
This version uses FNO instruments (NIFTY options) instead of equity
Addresses the "Resource not available" error by using correct instrument codes
"""

import os
import sys
import json
import time
import smtplib
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Check for breeze-connect library
try:
    from breeze_connect import BreezeConnect
except ImportError:
    logger.error("The 'breeze-connect' library is not installed. Please install it using: pip install breeze-connect")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global variables
breeze_connection = None
current_capital = float(os.getenv('STARTING_CAPITAL', 100000))
positions = []
trade_history = []
daily_pnl = 0.0

# Configuration
PAPER_TRADING = os.getenv('PAPER_TRADING', 'true').lower() == 'true'
MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', 50000))
STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', 2.0))
TARGET_PROFIT_PERCENT = float(os.getenv('TARGET_PROFIT_PERCENT', 4.0))

# Email configuration
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')
EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT')

# Breeze API credentials
BREEZE_API_KEY = os.getenv('BREEZE_API_KEY')
BREEZE_API_SECRET = os.getenv('BREEZE_API_SECRET')
BREEZE_SESSION_TOKEN = os.getenv('BREEZE_SESSION_TOKEN')

class BreezeAPI:
    """Wrapper class for Breeze API connection and operations"""
    
    def __init__(self):
        self.breeze = None
        self.connected = False
        
    def connect(self):
        """Establish connection to Breeze API"""
        try:
            from breeze_connect import BreezeConnect
            
            if not all([BREEZE_API_KEY, BREEZE_API_SECRET, BREEZE_SESSION_TOKEN]):
                logger.error("Missing Breeze API credentials in .env file")
                return False
                
            # Initialize BreezeConnect
            self.breeze = BreezeConnect(api_key=BREEZE_API_KEY)
            
            # Generate session
            session_response = self.breeze.generate_session(
                api_secret=BREEZE_API_SECRET,
                session_token=BREEZE_SESSION_TOKEN
            )
            
            if session_response.get('Status') == 200:
                logger.info("SUCCESS - Breeze API connected successfully")
                self.connected = True
                
                # Test connection with customer details
                customer_details = self.breeze.get_customer_details()
                logger.info(f"Customer Details: {customer_details}")
                
                return True
            else:
                logger.error(f"Failed to generate session: {session_response}")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to Breeze API: {e}")
            return False
    
    def get_account_balance(self):
        """Get available account balance"""
        if not self.connected:
            return 0.0
            
        try:
            response = self.breeze.get_funds()
            if response.get('Status') == 200:
                funds = response.get('Success', [])
                for fund in funds:
                    if fund.get('segment') == 'FNO':
                        return float(fund.get('available_margin', 0.0))
            return 0.0
        except:
            return 0.0

    def get_nifty_spot_price(self):
        """Fetch current NIFTY spot price"""
        if not self.connected:
            logger.error("Breeze API not connected for fetching NIFTY spot price.")
            return None
        try:
            # Fetching quote for NIFTY 50 index. The stock_code for NIFTY 50 index is 'NIFTY'.
            # The exchange_code for NIFTY options is 'NFO', but for index spot it's usually 'NSE'.
            # This might require a specific API call for index data, not just stock quotes.
            # Assuming 'get_quotes' can fetch index data if configured correctly.
            response = self.breeze.get_quotes(stock_code="NIFTY", exchange_code="NSE", product_type="others")
            if response.get('Status') == 200 and response.get('Success'):
                # The response structure for index quotes might differ. Adjust as per actual API response.
                # Assuming 'ltp' (Last Traded Price) is available in the first success item.
                ltp = response['Success'][0].get('ltp')
                if ltp:
                    return float(ltp)
            logger.warning(f"Could not fetch NIFTY spot price: {response}")
            return None
        except Exception as e:
            logger.error(f"Error fetching NIFTY spot price: {e}")
            return None

    def get_option_chain(self, symbol, expiry_date):
        """Fetch option chain for a given symbol and expiry"""
        if not self.connected:
            return None
        try:
            # Use the actual BreezeConnect method to get option chain.
            # The `get_option_chain` method in breeze_connect expects expiry_date in 'YYYY-MM-DD' format.
            # Ensure the expiry_date is in the correct format before passing it.
            # If the expiry_date is not in YYYY-MM-DD, convert it.
            try:
                datetime.strptime(expiry_date, '%Y-%m-%d')
            except ValueError:
                logger.error(f"Invalid expiry_date format: {expiry_date}. Expected YYYY-MM-DD.")
                return None

            response = self.breeze.get_option_chain(stock_code=symbol, exchange_code="NFO", expiry_date=expiry_date)
            if response.get('Status') == 200:
                return response.get('Success')
            logger.error(f"Failed to get option chain for {symbol} {expiry_date}: {response}")
            return None
        except Exception as e:
            logger.error(f"Error fetching option chain: {e}")
            return None

    def get_instrument_token(self, symbol, strike, option_type, expiry_date):
        """Get instrument token for FNO option"""
        option_chain = self.get_option_chain(symbol, expiry_date)
        if not option_chain:
            return None

        for option in option_chain:
            try:
                api_expiry_date = datetime.strptime(option.get('expiry_date'), '%Y-%m-%d').date()
                expected_expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                continue

            if (float(option.get('strike_price')) == float(strike) and
                option.get('option_type') == option_type and
                api_expiry_date == expected_expiry_date):
                return option.get('token') or option.get('instrument_token') or option.get('stock_token')
        logger.warning(f"Instrument token not found for {symbol} {strike} {option_type} {expiry_date}")
        return None

    def place_fno_order(self, symbol, strike, option_type, action, quantity, price=None):
        """Place FNO order with proper instrument identification"""
        if not self.connected:
            return None
            
        try:
            # Get current expiry
            expiry = self.get_next_expiry()
            
            # Determine order type
            order_type = "LIMIT" if price else "MARKET"
            
            # Get instrument token
            instrument_token = self.get_instrument_token(symbol, strike, option_type, expiry)
            if not instrument_token:
                logger.error(f"Could not get instrument token for {symbol} {strike} {option_type} {expiry}")
                return None

            # Place order
            order_response = self.breeze.place_order(
                stock_code=symbol,
                exchange_code="NFO",
                product="options",
                action=action,
                order_type=order_type,
                quantity=str(quantity),
                price=str(price) if price else "0",
                validity="day",
                right=option_type,
                strike_price=str(strike),
                expiry_date=expiry,
                token=instrument_token
            )
            
            return order_response
            
        except Exception as e:
            logger.error(f"Error placing FNO order: {e}")
            return None
    
    def get_next_expiry(self):
        """Get next Thursday expiry date"""
        today = datetime.now()
        days_ahead = 3 - today.weekday()  # Thursday is 3
        if days_ahead <= 0:
            days_ahead += 7
        expiry_date = today + timedelta(days=days_ahead)
        return expiry_date.strftime('%Y-%m-%d')

# Initialize global API instance
api = BreezeAPI()

def connect_to_breeze():
    """Initialize Breeze API connection"""
    return api.connect()

def get_market_data():
    """Get market data, including NIFTY spot price for strike selection"""
    # In production, this would fetch real data from Breeze API
    nifty_spot = api.get_nifty_spot_price()
    if not nifty_spot:
        logger.warning("Could not fetch real NIFTY spot price, using synthetic data for now.")
        nifty_spot = 15000 + np.random.normal(0, 100) # Fallback to synthetic

    return {
        'price': nifty_spot, # Using NIFTY spot as a base for market data
        'volume': 100000 + np.random.randint(-50000, 50000),
        'vix': 15 + np.random.normal(0, 1),
        'prediction': np.random.choice(['BUY', 'SELL'], p=[0.5, 0.5]),
        'confidence': 0.75 + np.random.normal(0, 0.1)
    }

def calculate_position_size(signal_confidence):
    """Calculate position size based on confidence and risk parameters"""
    global current_capital
    
    # Base position size (max 5% of capital per trade)
    max_risk_amount = current_capital * 0.05
    
    # Adjust based on confidence
    confidence_multiplier = min(signal_confidence, 0.9)
    position_size = max_risk_amount * confidence_multiplier
    
    # Ensure minimum position size
    position_size = max(position_size, 10000)
    
    # Cap at maximum position size
    position_size = min(position_size, MAX_POSITION_SIZE)
    
    return int(position_size)

def execute_trade(prediction, confidence):
    """Execute trade based on prediction"""
    global current_capital, positions
    
    try:
        if not prediction or confidence < 0.7:
            logger.info("No valid signal or low confidence")
            return False
        
        # Check market hours
        if not is_market_hours():
            logger.warning("Market is closed")
            return False
        
        # Calculate position size
        position_size = calculate_position_size(confidence)
        
        if position_size <= 0:
            logger.warning("Invalid position size")
            return False
        
        # For FNO trading, use NIFTY options
        # One lot = 50 shares, so calculate lots
        lot_size = 50
        lots = max(1, position_size // (150 * lot_size))  # Assuming 150 as base price
        quantity = lots * lot_size
        
        # Determine direction
        direction = "BUY" if prediction.upper() == "BUY" else "SELL"
        
        # Get current NIFTY level for strike selection
        nifty_level = api.get_nifty_spot_price() # Use the API instance to get spot price
        if not nifty_level:
            logger.error("Could not fetch NIFTY spot price.")
            return False
        
        # Select strike price (ATM for simplicity)
        strike = round(nifty_level / 50) * 50
        
        logger.info(f"Executing {direction} trade: {lots} lots ({quantity} shares) of NIFTY {strike} CE")
        
        if PAPER_TRADING:
            # Paper trading simulation
            entry_price = 150.0  # Simulated option price
            
            # Create position
            position = {
                'direction': direction,
                'quantity': quantity,
                'entry_price': entry_price,
                'entry_time': datetime.now(),
                'position_size': position_size,
                'stop_loss': entry_price * 0.95 if direction == "BUY" else entry_price * 1.05,
                'target': entry_price * 1.04 if direction == "BUY" else entry_price * 0.96,
                'status': 'OPEN',
                'instrument': f'NIFTY {strike} CE',
                'lots': lots
            }
            
            positions.append(position)
            current_capital -= position_size
            
            logger.info(f"PAPER TRADE: {direction} {lots} lots of NIFTY {strike} CE")
            
            # Send notification
            send_trade_notification(position)
            
            return True
            
        else:
            # Real trading via Breeze API
            if not api.connected:
                logger.error("Breeze API not connected")
                return False
            
            # Determine option type based on prediction
            option_type = "Call" if direction == "BUY" else "Put" # Assuming BUY for Call, SELL for Put for simplicity

            # Place order
            order_response = api.place_fno_order(
                symbol="NIFTY", # Or BANKNIFTY, based on strategy
                strike=strike,
                option_type=option_type,
                action=direction,
                quantity=quantity,
                price=None  # Market order
            )
            
            if order_response and order_response.get('Status') == 200:
                order_id = order_response.get('Success', [{}])[0].get('order_id', 'UNKNOWN')
                
                logger.info(f"REAL TRADE: {direction} {lots} lots of NIFTY {strike} CE")
                logger.info(f"Order ID: {order_id}")
                
                # Create position
                position = {
                    'direction': direction,
                    'quantity': quantity,
                    'entry_price': 150.0,  # Will be actual fill price
                    'entry_time': datetime.now(),
                    'position_size': position_size,
                    'status': 'OPEN',
                    'instrument': f'NIFTY {strike} CE',
                    'lots': lots,
                    'order_id': order_id
                }
                
                positions.append(position)
                current_capital -= position_size
                
                send_trade_notification(position)
                return True
            else:
                error_msg = order_response.get('Error', 'Unknown error') if order_response else 'No response'
                logger.error(f"FAILED - Order placement failed: {error_msg}")
                return False
                
    except Exception as e:
        logger.error(f"Error executing trade: {e}")
        return False

def is_market_hours():
    """Check if market is open"""
    now = datetime.now()
    
    # Check if it's a weekday
    if now.weekday() >= 5:  # Saturday and Sunday
        return False
    
    # Check time (9:15 AM to 3:30 PM)
    market_open = now.replace(hour=9, minute=15, second=0)
    market_close = now.replace(hour=15, minute=30, second=0)
    
    return market_open <= now <= market_close

def manage_positions():
    """Monitor and manage open positions"""
    global current_capital, daily_pnl, positions
    
    if not positions:
        return
    
    logger.info(f"Managing {len(positions)} open positions...")
    
    for position in positions[:]:
        # Get current market data
        market_data = get_market_data()
        current_price = market_data['price']
        
        # Calculate P&L
        if position['direction'] == 'BUY':
            pnl = (current_price - position['entry_price']) * position['quantity']
            pnl_percent = ((current_price - position['entry_price']) / position['entry_price']) * 100
        else:
            pnl = (position['entry_price'] - current_price) * position['quantity']
            pnl_percent = ((position['entry_price'] - current_price) / position['entry_price']) * 100
        
        # Check exit conditions
        should_exit = False
        exit_reason = ""
        
        if position['direction'] == 'BUY':
            if current_price <= position['stop_loss']:
                should_exit = True
                exit_reason = "STOP_LOSS"
            elif current_price >= position['target']:
                should_exit = True
                exit_reason = "TARGET"
        else:
            if current_price >= position['stop_loss']:
                should_exit = True
                exit_reason = "STOP_LOSS"
            elif current_price <= position['target']:
                should_exit = True
                exit_reason = "TARGET"
        
        if should_exit:
            logger.info(f"{exit_reason} hit for {position['direction']} position. P&L: {pnl:.2f}")
            
            # Close position
            position['exit_price'] = current_price
            position['exit_time'] = datetime.now()
            position['pnl'] = pnl
            position['pnl_percent'] = pnl_percent
            position['status'] = 'CLOSED'
            position['exit_reason'] = exit_reason
            
            # Update capital and daily P&L
            current_capital += position['position_size'] + pnl
            daily_pnl += pnl
            
            # Move to trade history
            trade_history.append(position)
            positions.remove(position)
            
            send_trade_notification(position, is_exit=True)

def send_trade_notification(position, is_exit=False):
    """Send trade notification via email"""
    if not EMAIL_RECIPIENT:
        return
    
    try:
        if is_exit:
            subject = f"Trade Closed: {position['exit_reason']} - P&L: {position['pnl']:.2f}"
            body = f"""
            Trade closed:
            - Instrument: {position['instrument']}
            - Direction: {position['direction']}
            - Lots: {position['lots']}
            - Entry: {position['entry_price']:.2f}
            - Exit: {position['exit_price']:.2f}
            - P&L: {position['pnl']:.2f} ({position['pnl_percent']:.2f}%)
            - Reason: {position['exit_reason']}
            - Current Capital: {current_capital:.2f}
            """
        else:
            subject = f"Trade Opened: {position['direction']} {position['instrument']}"
            body = f"""
            Trade opened:
            - Instrument: {position['instrument']}
            - Direction: {position['direction']}
            - Lots: {position['lots']}
            - Entry: {position['entry_price']:.2f}
            - Position Size: {position['position_size']:.2f}
            - Current Capital: {current_capital:.2f}
            """
        
        # Send email (implementation depends on your email setup)
        logger.info(f"Notification: {subject}")
        
    except Exception as e:
        logger.error(f"Error sending notification: {e}")

def main():
    """Main trading loop"""
    logger.info("Starting Fixed Trading System...")
    
    global PAPER_TRADING # Declare PAPER_TRADING as global

    # Initialize Breeze API connection
    if not PAPER_TRADING:
        if not connect_to_breeze():
            logger.error("Failed to connect to Breeze API. Starting in paper trading mode.")
            PAPER_TRADING = True
    
    # Main trading loop
    iteration = 0
    while True:
        try:
            iteration += 1
            logger.info(f"Trading iteration {iteration}")
            
            # Check market hours
            if not is_market_hours():
                logger.info("Market is closed. Waiting...")
                time.sleep(300)  # 5 minutes
                continue
            
            # Get market data
            market_data = get_market_data()
            
            # Execute trade based on prediction
            execute_trade(market_data['prediction'], market_data['confidence'])
            
            # Manage open positions
            manage_positions()
            
            # Log current status
            logger.info(f"Status: Capital={current_capital:.2f}, Positions={len(positions)}, Daily P&L={daily_pnl:.2f}")
            
            # Wait before next iteration
            time.sleep(60)  # 1 minute
            
        except KeyboardInterrupt:
            logger.info("Trading system stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()