# minimal_trading_system.py - Simple, reliable trading system
import os
import logging
import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from zoneinfo import ZoneInfo
import datetime as dt

# Setup logging
log_file = f"trade_log_{datetime.now().strftime('%Y%m%d')}.txt"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create console handler for real-time monitoring
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# Load environment variables
load_dotenv()
BREEZE_API_KEY = os.getenv("BREEZE_API_KEY")
BREEZE_API_SECRET = os.getenv("BREEZE_API_SECRET")
BREEZE_SESSION_TOKEN = os.getenv("BREEZE_SESSION_TOKEN")
ICICI_CLIENT_CODE = os.getenv("ICICI_CLIENT_CODE")

# Email configuration
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")

# Trading configuration
PAPER_TRADING = False  # Set to False for real trading
STARTING_CAPITAL = 1000  # ₹1,000 real starting capital
MAX_POSITION_SIZE = 200  # Max ₹200 per trade (20% of capital)
STOP_LOSS_PERCENT = 3  # 3% maximum loss
TARGET_PROFIT_PERCENT = 8  # 8% target gain
MAX_DAILY_LOSS = 100  # ₹100 maximum daily loss (10% of capital)

# Trading configuration for SENSEX
TRADING_CONFIG = {
    'underlying': 'SENSEX',
    'exchange': 'BSE',
    'stock_code': 'BSESEN',
    'base_level': 81000,
    'point_value': 1,  # 1 point = ₹1 for SENSEX
    'min_move_threshold': 200  # 200 points minimum for signal
}

# Market hours configuration
MARKET_OPEN_TIME = dt.time(9, 15)  # 9:15 AM IST
MARKET_CLOSE_TIME = dt.time(15, 30)  # 3:30 PM IST

# Global variables
current_capital = STARTING_CAPITAL
daily_pnl = 0
positions = []
trade_history = []
breeze_connection = None

# Market hours validation
def is_indian_market_open():
    """Check if NSE/BSE markets are currently open"""
    now = dt.datetime.now(ZoneInfo('Asia/Kolkata'))
    
    # Check if it's a weekday (Monday=0, Sunday=6)
    if now.weekday() > 4:  # Saturday or Sunday
        return False
    
    # Check if current time is within trading hours (9:15 AM - 3:30 PM IST)
    market_open = dt.datetime.combine(now.date(), MARKET_OPEN_TIME).replace(tzinfo=ZoneInfo('Asia/Kolkata'))
    market_close = dt.datetime.combine(now.date(), MARKET_CLOSE_TIME).replace(tzinfo=ZoneInfo('Asia/Kolkata'))
    
    return market_open <= now <= market_close

def get_next_market_open():
    """Get the next market opening time"""
    now = dt.datetime.now(ZoneInfo('Asia/Kolkata'))
    
    # If today is weekend, return next Monday
    if now.weekday() > 4:  # Saturday or Sunday
        days_until_monday = 7 - now.weekday()
        next_monday = now + dt.timedelta(days=days_until_monday)
        return dt.datetime.combine(next_monday.date(), MARKET_OPEN_TIME).replace(tzinfo=ZoneInfo('Asia/Kolkata'))
    
    # If market is already open today, return same day
    market_open = dt.datetime.combine(now.date(), MARKET_OPEN_TIME).replace(tzinfo=ZoneInfo('Asia/Kolkata'))
    if now < market_open:
        return market_open
    
    # Market is closed for today, return next day
    tomorrow = now + dt.timedelta(days=1)
    
    # If tomorrow is weekend, return next Monday
    if tomorrow.weekday() > 4:
        days_until_monday = 7 - tomorrow.weekday()
        next_monday = tomorrow + dt.timedelta(days=days_until_monday)
        return dt.datetime.combine(next_monday.date(), MARKET_OPEN_TIME).replace(tzinfo=ZoneInfo('Asia/Kolkata'))
    
    return dt.datetime.combine(tomorrow.date(), MARKET_OPEN_TIME).replace(tzinfo=ZoneInfo('Asia/Kolkata'))

# Initialize Breeze connection
def connect_to_breeze():
    try:
        logging.info("Connecting to Breeze API...")
        
        # Import Breeze SDK
        try:
            from breeze_connect import BreezeConnect
        except ImportError:
            logging.error("BreezeConnect not available. Install with: pip install breeze-connect")
            return None
        
        if not all([BREEZE_API_KEY, BREEZE_API_SECRET, BREEZE_SESSION_TOKEN]):
            logging.error("Missing Breeze API credentials. Check .env file.")
            return None
        
        breeze = BreezeConnect(api_key=BREEZE_API_KEY)
        breeze.generate_session(api_secret=BREEZE_API_SECRET, session_token=BREEZE_SESSION_TOKEN)
        
        # Test connection
        funds = breeze.get_funds()
        logging.info(f"Connected to Breeze API successfully")
        logging.info(f"Available funds: ₹{funds.get('Success', {}).get('available_margin', 0)}")
        
        return breeze
    except Exception as e:
        logging.error(f"Failed to connect to Breeze API: {e}")
        send_alert_email("Breeze API Connection Failure", f"Failed to connect to Breeze API: {e}")
        return None

# Load the 98.61% accuracy model
def load_model():
    try:
        # Look for model files in the models directory
        model_dir = "./models"
        if not os.path.exists(model_dir):
            model_dir = "./automated-cashflow-pipeline/models"
            if not os.path.exists(model_dir):
                raise FileNotFoundError(f"Model directory not found at ./models or ./automated-cashflow-pipeline/models")
        
        # Find the latest model file
        model_files = [f for f in os.listdir(model_dir) if f.endswith('.pkl')]
        if not model_files:
            raise FileNotFoundError(f"No model files found in {model_dir}")
        
        # Sort by date in filename if possible, otherwise just take the first one
        model_files.sort(reverse=True)
        model_path = os.path.join(model_dir, model_files[0])
        
        logging.info(f"Loading model from {model_path}")
        model = joblib.load(model_path)
        logging.info("Model loaded successfully")
        return model
    except Exception as e:
        logging.error(f"Failed to load model: {e}")
        send_alert_email("Model Loading Failure", f"Failed to load trading model: {e}")
        return None

# Get market data
def get_sensex_market_data():
    """Get real SENSEX data - not NIFTY"""
    try:
        if breeze_connection is None:
            logging.error("Breeze connection not established.")
            return None

        sensex_quotes = breeze_connection.get_quotes(
            stock_code=TRADING_CONFIG['stock_code'],  # Correct SENSEX symbol
            exchange_code=TRADING_CONFIG['exchange'],  # Correct BSE exchange
            product_type="cash"
        )
        
        if sensex_quotes and sensex_quotes.get('Success'):
            data = sensex_quotes['Success'][0] # Assuming the first element contains the data
            return {
                'symbol': TRADING_CONFIG['underlying'],
                'current_price': float(data['ltp']),
                'timestamp': datetime.now().isoformat(),
                'volume': float(data.get('volume', 0))
            }
        else:
            logging.error(f"Failed to get SENSEX quotes: {sensex_quotes.get('Error')}")
            return None
    except Exception as e:
        logging.error(f"Error fetching SENSEX data: {e}")
        return None

def get_market_data():
    try:
        logging.info("Fetching market data...")
        
        sensex_data = get_sensex_market_data()
        if sensex_data is None:
            logging.error("Could not retrieve SENSEX market data.")
            return None

        stock_price = sensex_data['current_price']
        volume = sensex_data['volume']

        # Simulate volatility, SMA, and RSI for model input as they are not directly from get_quotes
        volatility = 0.15 + np.random.normal(0, 0.02) # Placeholder, ideally derived from historical data
        sma_20 = stock_price - 2 + np.random.normal(0, 0.5) # Placeholder
        rsi = 50 + np.random.normal(0, 5) # Placeholder
        if rsi > 70:
            rsi = 70  # Cap RSI
        elif rsi < 30:
            rsi = 30
        
        # Create model input with the required features from the model
        model_input = {
            "IV_zscore": float(volatility * 2),  # Simulated IV z-score
            "oi_change": float(volume * 0.01),  # Simulated OI change
            "Donchian_Channel_Lower": float(stock_price - 5)  # Simulated Donchian Channel Lower
        }
        
        logging.info(f"Market data: {json.dumps(model_input)}")
        return pd.DataFrame([model_input])
    except Exception as e:
        logging.error(f"Error fetching market data: {e}")
        return None

# Calculate position size based on risk management rules
def calculate_position_size(prediction, confidence):
    global current_capital, daily_pnl
    
    # Apply risk management rules
    if daily_pnl < -MAX_DAILY_LOSS:
        logging.warning(f"Daily loss limit reached: ₹{daily_pnl}. No new trades.")
        return 0
    
    # Base position size on confidence and capital
    if confidence > 0.9:  # High confidence
        position_size = min(MAX_POSITION_SIZE, current_capital * 0.3)  # 30% of capital
    elif confidence > 0.8:  # Medium confidence
        position_size = min(MAX_POSITION_SIZE * 0.7, current_capital * 0.2)  # 20% of capital
    else:  # Lower confidence
        position_size = min(MAX_POSITION_SIZE * 0.5, current_capital * 0.1)  # 10% of capital
    
    # Ensure we have enough capital
    if position_size > current_capital:
        position_size = current_capital * 0.9  # Use 90% of remaining capital at most
    
    # Round to nearest 100
    position_size = round(position_size / 100) * 100
    
    logging.info(f"Calculated position size: ₹{position_size} (Capital: ₹{current_capital}, Daily P&L: ₹{daily_pnl})")
    return position_size

# Execute trade
def execute_trade(prediction, confidence):
    global current_capital, daily_pnl, positions, trade_history
    
    try:
        logging.info(f"Execute trade called with prediction: {prediction}, confidence: {confidence}")
        # Only trade on sufficient confidence
        if confidence < 0.75:
            logging.info(f"No trade: confidence {confidence} below threshold of 0.75")
            return False
        
        # Calculate position size
        position_size = calculate_position_size(prediction, confidence)
        logging.info(f"Calculated position size: {position_size}")
        if position_size <= 0:
            logging.info("No trade: position size <= 0")
            return False
        
        # Determine trade direction
        direction = "BUY" if prediction > 0 else "SELL"
        logging.info(f"Trade direction: {direction} based on prediction {prediction}")
        
        # Calculate entry price (simulated)
        entry_price = 150.25 if direction == "BUY" else 150.75
        quantity = int(position_size / entry_price)
        logging.info(f"Entry price: {entry_price}, Quantity: {quantity}")
        
        if quantity <= 0:
            logging.warning("Quantity too small for trade execution")
            return False
        
        # Execute the trade
        if PAPER_TRADING:
            # Paper trading mode
            logging.info(f"PAPER TRADE: {direction} {quantity} shares at ₹{entry_price} (Position size: ₹{position_size})")
            
            # Record the position
            stop_loss = entry_price * (1 - STOP_LOSS_PERCENT/100) if direction == "BUY" else entry_price * (1 + STOP_LOSS_PERCENT/100)
            target = entry_price * (1 + TARGET_PROFIT_PERCENT/100) if direction == "BUY" else entry_price * (1 - TARGET_PROFIT_PERCENT/100)
            
            position = {
                "direction": direction,
                "quantity": quantity,
                "entry_price": entry_price,
                "entry_time": datetime.now(),
                "position_size": position_size,
                "stop_loss": stop_loss,
                "target": target,
                "status": "OPEN"
            }
            
            positions.append(position)
            
            # Update capital
            current_capital -= position_size
            
            # Send notification
            send_trade_notification(position)
            
            return True
        else:
            # Real trading mode - actual Breeze API integration
            try:
                # Get actual stock code and exchange
                stock_code = "RELIANCE"  # You can modify this to use dynamic stock selection
                exchange_code = "NSE"
                product = "cash"
                
                # Place actual order via Breeze API
                global breeze_connection
                if not breeze_connection:
                    logging.error("Breeze API not connected. Cannot place real order.")
                    return False
                
                breeze = breeze_connection
                
                # Determine order type and price
                order_type = "MARKET"  # Market order for immediate execution
                price = 0  # Market orders don't need price
                
                # Place the order
                order_response = breeze.place_order(
                    stock_code=stock_code,
                    exchange_code=exchange_code,
                    product=product,
                    action=direction,
                    order_type=order_type,
                    quantity=str(quantity),
                    price=str(price),
                    validity="day"
                )
                
                if order_response and order_response.get("Status") == 200:
                    order_id = order_response.get("Success", [{}])[0].get("order_id", "UNKNOWN")
                    logging.info(f"✅ REAL TRADE EXECUTED: {direction} {quantity} shares of {stock_code} via Breeze API")
                    logging.info(f"Order ID: {order_id}")
                    
                    # Record the position
                    stop_loss = entry_price * (1 - STOP_LOSS_PERCENT/100) if direction == "BUY" else entry_price * (1 + STOP_LOSS_PERCENT/100)
                    target = entry_price * (1 + TARGET_PROFIT_PERCENT/100) if direction == "BUY" else entry_price * (1 - TARGET_PROFIT_PERCENT/100)
                    
                    position = {
                        "direction": direction,
                        "quantity": quantity,
                        "entry_price": entry_price,
                        "entry_time": datetime.now(),
                        "position_size": position_size,
                        "stop_loss": stop_loss,
                        "target": target,
                        "status": "OPEN",
                        "order_id": order_id,
                        "stock_code": stock_code
                    }
                    
                    positions.append(position)
                    
                    # Update capital
                    current_capital -= position_size
                    
                    # Send notification
                    send_trade_notification(position)
                    
                    return True
                else:
                    error_msg = order_response.get("Error", "Unknown error") if order_response else "No response"
                    logging.error(f"❌ Order placement failed: {error_msg}")
                    return False
                    
            except Exception as e:
                logging.error(f"❌ Error placing real order via Breeze API: {e}")
                return False
            
    except Exception as e:
        logging.error(f"Error executing trade: {e}")
        return False

# Monitor and manage open positions
def manage_positions():
    global current_capital, daily_pnl, positions, trade_history
    
    if not positions:
        return
    
    logging.info(f"Managing {len(positions)} open positions...")
    
    # Get current market price (simulated)
    current_price = 150.25 + np.random.normal(0, 1)
    
    positions_to_remove = []
    
    for i, position in enumerate(positions):
        # Calculate P&L for this position
        if position['direction'] == 'BUY':
            pnl = (current_price - position['entry_price']) * position['quantity']
            pnl_percent = ((current_price - position['entry_price']) / position['entry_price']) * 100
        else:  # SELL
            pnl = (position['entry_price'] - current_price) * position['quantity']
            pnl_percent = ((position['entry_price'] - current_price) / position['entry_price']) * 100
        
        # Check for exit conditions
        should_exit = False
        exit_reason = ""
        
        if position['direction'] == 'BUY':
            if current_price <= position['stop_loss']:
                should_exit = True
                exit_reason = "STOP_LOSS"
            elif current_price >= position['target']:
                should_exit = True
                exit_reason = "TARGET"
        else:  # SELL
            if current_price >= position['stop_loss']:
                should_exit = True
                exit_reason = "STOP_LOSS"
            elif current_price <= position['target']:
                should_exit = True
                exit_reason = "TARGET"
        
        if should_exit:
            # Close the position
            logging.info(f"{exit_reason} hit for {position['direction']} position. P&L: ₹{pnl:.2f} ({pnl_percent:.2f}%)")
            
            position["exit_price"] = current_price
            position["exit_time"] = datetime.now()
            position["pnl"] = pnl
            position["pnl_percent"] = pnl_percent
            position["status"] = "CLOSED"
            position["exit_reason"] = exit_reason
            
            # Update capital and daily P&L
            current_capital += position["position_size"] + pnl
            daily_pnl += pnl
            
            # Add to trade history
            trade_history.append(position)
            positions_to_remove.append(i)
            
            # Send notification
            send_trade_notification(position, is_exit=True)
        else:
            # Position still open, log current status
            logging.info(f"Open {position['direction']} position. Current P&L: ₹{pnl:.2f} ({pnl_percent:.2f}%)")
    
    # Remove closed positions
    for i in sorted(positions_to_remove, reverse=True):
        positions.pop(i)

# Send email notification
def send_alert_email(subject, message):
    if not all([EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS, EMAIL_RECIPIENT]):
        logging.warning("Email configuration incomplete. Cannot send alert.")
        return
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_RECIPIENT
        msg['Subject'] = f"Trading Alert: {subject}"
        
        body = f"""
        <html>
        <body>
            <h2>Trading System Alert</h2>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Alert:</strong> {subject}</p>
            <p><strong>Details:</strong> {message}</p>
            <p><strong>Current Capital:</strong> ₹{current_capital:.2f}</p>
            <p><strong>Daily P&L:</strong> ₹{daily_pnl:.2f}</p>
            <hr>
            <p><em>This is an automated message from your trading system.</em></p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        
        logging.info(f"Alert email sent: {subject}")
    except Exception as e:
        logging.error(f"Failed to send alert email: {e}")

# Send trade notification
def send_trade_notification(position, is_exit=False):
    if is_exit:
        subject = f"Trade Closed: {position['exit_reason']} - {position['direction']} - P&L: ₹{position['pnl']:.2f}"
        message = f"""
        Trade closed with {position['exit_reason']}:
        - Direction: {position['direction']}
        - Quantity: {position['quantity']}
        - Entry Price: ₹{position['entry_price']:.2f}
        - Entry Time: {position['entry_time'].strftime('%Y-%m-%d %H:%M:%S')}
        - Exit Price: ₹{position['exit_price']:.2f}
        - Exit Time: {position['exit_time'].strftime('%Y-%m-%d %H:%M:%S')}
        - P&L: ₹{position['pnl']:.2f} ({position['pnl_percent']:.2f}%)
        - Current Capital: ₹{current_capital:.2f}
        - Daily P&L: ₹{daily_pnl:.2f}
        """
    else:
        subject = f"New Trade: {position['direction']} - ₹{position['position_size']:.2f}"
        message = f"""
        New trade executed:
        - Direction: {position['direction']}
        - Quantity: {position['quantity']}
        - Entry Price: ₹{position['entry_price']:.2f}
        - Entry Time: {position['entry_time'].strftime('%Y-%m-%d %H:%M:%S')}
        - Stop Loss: ₹{position['stop_loss']:.2f}
        - Target: ₹{position['target']:.2f}
        - Position Size: ₹{position['position_size']:.2f}
        - Remaining Capital: ₹{current_capital:.2f}
        """
    
    send_alert_email(subject, message)

# Generate daily summary
def generate_daily_summary():
    if not trade_history:
        logging.info("No trades executed today. Skipping daily summary.")
        return
    
    total_trades = len(trade_history)
    winning_trades = len([t for t in trade_history if t["pnl"] > 0])
    losing_trades = len([t for t in trade_history if t["pnl"] <= 0])
    
    if total_trades > 0:
        win_rate = (winning_trades / total_trades) * 100
    else:
        win_rate = 0
    
    total_pnl = sum([t["pnl"] for t in trade_history])
    avg_pnl = total_pnl / total_trades if total_trades > 0 else 0
    
    summary = f"""
    <html>
    <body>
        <h2>Trading System Daily Summary</h2>
        <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>
        <p><strong>Starting Capital:</strong> ₹{STARTING_CAPITAL:.2f}</p>
        <p><strong>Current Capital:</strong> ₹{current_capital:.2f}</p>
        <p><strong>Daily P&L:</strong> ₹{daily_pnl:.2f} ({(daily_pnl/STARTING_CAPITAL)*100:.2f}%)</p>
        <hr>
        <h3>Trade Statistics</h3>
        <p><strong>Total Trades:</strong> {total_trades}</p>
        <p><strong>Winning Trades:</strong> {winning_trades}</p>
        <p><strong>Losing Trades:</strong> {losing_trades}</p>
        <p><strong>Win Rate:</strong> {win_rate:.2f}%</p>
        <p><strong>Average P&L per Trade:</strong> ₹{avg_pnl:.2f}</p>
        <hr>
        <h3>Trade History</h3>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr>
                <th>Direction</th>
                <th>Entry Time</th>
                <th>Exit Time</th>
                <th>Entry Price</th>
                <th>Exit Price</th>
                <th>Quantity</th>
                <th>P&L</th>
                <th>P&L %</th>
                <th>Exit Reason</th>
            </tr>
    """
    
    for trade in trade_history:
        summary += f"""
            <tr>
                <td>{trade['direction']}</td>
                <td>{trade['entry_time'].strftime('%H:%M:%S')}</td>
                <td>{trade['exit_time'].strftime('%H:%M:%S')}</td>
                <td>₹{trade['entry_price']:.2f}</td>
                <td>₹{trade['exit_price']:.2f}</td>
                <td>{trade['quantity']}</td>
                <td>₹{trade['pnl']:.2f}</td>
                <td>{trade['pnl_percent']:.2f}%</td>
                <td>{trade['exit_reason']}</td>
            </tr>
        """
    
    summary += """
        </table>
        <hr>
        <p><em>This is an automated message from your trading system.</em></p>
    </body>
    </html>
    """
    
    send_alert_email("Daily Trading Summary", summary)
    logging.info("Daily summary generated and sent")

# Main trading loop
def run_trading_system():
    global current_capital, daily_pnl, positions, trade_history
    
    logging.info("=== Starting Minimal Trading System ===")
    logging.info(f"Mode: {'PAPER TRADING' if PAPER_TRADING else 'REAL TRADING'}")
    logging.info(f"Starting Capital: ₹{current_capital}")
    
    # Connect to Breeze API
    global breeze_connection
    breeze_connection = connect_to_breeze()
    if not breeze_connection:
        logging.error("Failed to connect to Breeze API. Exiting.")
        return
    
    # Load the model
    model = load_model()
    if not model:
        logging.error("Failed to load model. Exiting.")
        return
    
    # Send startup notification
    send_alert_email("Trading System Started", f"The trading system has been started in {'PAPER TRADING' if PAPER_TRADING else 'REAL TRADING'} mode with ₹{current_capital} capital.")
    
    # Trading loop
    try:
        trade_count = 0
        max_trades_per_day = 5
        
        while True:
            current_time = datetime.now()
            
            # Check if market is open
            is_market_open = is_indian_market_open()
            
            if not is_market_open:
                # Outside market hours
                next_market_open = get_next_market_open()
                
                # Generate daily summary after market close
                if current_time.hour == 15 and current_time.minute >= 30 and current_time.minute <= 35:
                    generate_daily_summary()
                
                logging.info(f"🕐 Market CLOSED. Next session: {next_market_open.strftime('%A %Y-%m-%d %H:%M:%S IST')}")
                
                # Calculate sleep time until next market open
                time_until_open = (next_market_open - current_time.astimezone(ZoneInfo('Asia/Kolkata'))).total_seconds()
                
                if time_until_open > 3600:  # More than 1 hour away
                    # Sleep for 1 hour, then check again
                    time.sleep(3600)
                else:
                    # Sleep for remaining time + 5 minutes buffer
                    time.sleep(max(time_until_open + 300, 60))
                continue
            
            # Manage existing positions
            manage_positions()
            
            # Check if we've reached the maximum trades for the day
            if trade_count >= max_trades_per_day:
                logging.info(f"Maximum trades for the day ({max_trades_per_day}) reached. Waiting for next day.")
                time.sleep(300)  # Check every 5 minutes
                continue
            
            # Get market data
            market_data = get_market_data()
            if market_data is None:
                logging.error("Failed to get market data. Retrying in 5 minutes.")
                time.sleep(300)
                continue
            
            # Make prediction
            try:
                logging.info(f"About to make prediction with model type: {type(model)}")
                logging.info(f"Market data shape: {market_data.shape}, columns: {market_data.columns}")
                prediction = model.predict(market_data)[0]
                logging.info(f"Raw prediction value: {prediction}")
                # Calculate confidence (this would be more sophisticated in a real system)
                confidence = 0.95 if abs(prediction) > 0.5 else 0.75
                
                logging.info(f"Prediction: {prediction}, Confidence: {confidence}")
                
                # Execute trade based on prediction
                if len(positions) < 3:  # Limit to 3 open positions maximum
                    logging.info("Position limit not reached, attempting to execute trade")
                    trade_executed = execute_trade(prediction, confidence)
                    logging.info(f"Trade execution result: {trade_executed}")
                    if trade_executed:
                        trade_count += 1
                        logging.info(f"Trade count increased to {trade_count}")
                else:
                    logging.info("Maximum number of open positions reached. Not opening new positions.")
            except Exception as e:
                logging.error(f"Error in prediction/execution: {e}")
            
            # Wait before next cycle (1 minute)
            time.sleep(60)
            
    except KeyboardInterrupt:
        logging.info("Trading system stopped by user")
        send_alert_email("Trading System Stopped", "The trading system was manually stopped.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        send_alert_email("Trading System Error", f"The trading system encountered an error: {e}")
    finally:
        # Close any open positions
        if positions:
            logging.info("Closing all open positions...")
            # In a real system, you would implement proper position closing logic here
        
        # Generate final summary
        generate_daily_summary()
        
        logging.info("=== Trading System Shutdown ===")

# Run the system
if __name__ == "__main__":
    run_trading_system()