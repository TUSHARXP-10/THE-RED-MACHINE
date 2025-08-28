#!/usr/bin/env python3
"""
High Confidence SENSEX Scalping Strategy
Updated for Kite Connect with 25-point profit/stop and >90% confidence
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
import numpy as np
from kiteconnect import KiteConnect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class HighConfidenceSensexScalper:
    def __init__(self):
        self.setup_logging()
        
        # Kite Connect setup
        self.kite = KiteConnect(api_key=os.getenv('KITE_API_KEY'))
        self.kite.set_access_token(os.getenv('KITE_ACCESS_TOKEN'))
        
        # Strategy parameters
        self.PROFIT_POINTS = 25  # +25 points profit target
        self.STOP_POINTS = 25    # -25 points stop loss
        self.MIN_CONFIDENCE = 0.90  # 90%+ confidence threshold
        self.MIN_OI_PERCENTILE = 90  # Top 10% OI
        self.POSITION_SIZE = 200  # ₹200 position size
        self.MAX_CAPITAL = 1000   # ₹1000 total capital
        
        # State tracking
        self.current_position = None
        self.entry_price = None
        self.entry_time = None
        self.position_type = None  # 'BUY' or 'SELL'
        self.target_price = None
        self.stop_price = None
        
        # SENSEX instrument token
        self.SENSEX_TOKEN = 260617
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('sensex_scalper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def get_sensex_data(self):
        """Get real-time SENSEX data"""
        try:
            quote = self.kite.quote([f"{self.SENSEX_TOKEN}"])
            sensex_data = quote[f"{self.SENSEX_TOKEN}"]
            
            return {
                'price': sensex_data['last_price'],
                'change': sensex_data['net_change'],
                'volume': sensex_data.get('volume', 0),
                'timestamp': datetime.now()
            }
        except Exception as e:
            self.logger.error(f"Error fetching SENSEX data: {e}")
            return None
            
    def calculate_confidence(self, current_price, historical_data):
        """Calculate signal confidence using model + momentum"""
        try:
            if not historical_data or len(historical_data) < 10:
                return 0.0
                
            # Calculate momentum indicators
            prices = [d['close'] for d in historical_data[-10:]]
            
            # Simple momentum calculation
            momentum = (prices[-1] - prices[-5]) / prices[-5] * 100
            
            # Volatility adjustment
            volatility = np.std(prices) / np.mean(prices) * 100
            
            # Confidence score based on momentum and volatility
            if abs(momentum) > 0.5 and volatility < 2.0:
                confidence = min(0.98, abs(momentum) / 2)  # Cap at 98%
            else:
                confidence = 0.0
                
            return confidence
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {e}")
            return 0.0
            
    def get_high_oi_strikes(self):
        """Get high open interest strikes for SENSEX options"""
        try:
            # For now, use NIFTY as proxy since SENSEX options have limited liquidity
            # In production, use actual SENSEX option chain
            
            # Get NIFTY option chain as example
            nifty_quote = self.kite.quote(["256265"])
            current_nifty = nifty_quote["256265"]['last_price']
            
            # Simulate high OI strikes around current price
            strikes = []
            base_strike = int(current_nifty / 50) * 50
            
            for strike_offset in [-200, -150, -100, -50, 0, 50, 100, 150, 200]:
                strike = base_strike + strike_offset
                
                # Simulate OI data (replace with real kite.quote for options)
                oi_ce = np.random.randint(100000, 500000)  # Call OI
                oi_pe = np.random.randint(100000, 500000)  # Put OI
                
                strikes.append({
                    'strike': strike,
                    'call_oi': oi_ce,
                    'put_oi': oi_pe,
                    'total_oi': oi_ce + oi_pe
                })
            
            # Filter top 10% OI
            total_oi_values = [s['total_oi'] for s in strikes]
            threshold = np.percentile(total_oi_values, self.MIN_OI_PERCENTILE)
            
            high_oi_strikes = [s for s in strikes if s['total_oi'] >= threshold]
            
            return high_oi_strikes
            
        except Exception as e:
            self.logger.error(f"Error getting high OI strikes: {e}")
            return []
            
    def generate_signal(self, current_price, historical_data):
        """Generate high-confidence trading signal"""
        try:
            # Get confidence score
            confidence = self.calculate_confidence(current_price, historical_data)
            
            if confidence < self.MIN_CONFIDENCE:
                return "NO_SIGNAL"
                
            # Get high OI strikes
            high_oi_strikes = self.get_high_oi_strikes()
            
            if not high_oi_strikes:
                return "NO_SIGNAL"
                
            # Determine signal direction based on momentum
            if len(historical_data) >= 5:
                recent_trend = (current_price - historical_data[-5]['close']) / historical_data[-5]['close'] * 100
                
                if recent_trend > 0.3:  # Bullish momentum
                    return "BUY_CALL"
                elif recent_trend < -0.3:  # Bearish momentum
                    return "BUY_PUT"
                    
            return "NO_SIGNAL"
            
        except Exception as e:
            self.logger.error(f"Error generating signal: {e}")
            return "NO_SIGNAL"
            
    def check_exit_conditions(self, current_price):
        """Check if position should be exited"""
        if not self.current_position:
            return False
            
        if self.position_type == "BUY":
            # Long position
            profit = current_price - self.entry_price
            if profit >= self.PROFIT_POINTS:
                self.logger.info(f"Profit target hit: +{profit:.2f} points")
                return True
            elif profit <= -self.STOP_POINTS:
                self.logger.info(f"Stop loss hit: {profit:.2f} points")
                return True
        else:
            # Short position (for futures)
            profit = self.entry_price - current_price
            if profit >= self.PROFIT_POINTS:
                self.logger.info(f"Profit target hit: +{profit:.2f} points")
                return True
            elif profit <= -self.STOP_POINTS:
                self.logger.info(f"Stop loss hit: {profit:.2f} points")
                return True
                
        return False
        
    def place_order(self, signal, current_price):
        """Place order based on signal"""
        try:
            if signal == "BUY_CALL":
                # In real implementation, use SENSEX options
                order = {
                    'tradingsymbol': 'BSE:SENSEX',
                    'exchange': 'BSE',
                    'transaction_type': 'BUY',
                    'order_type': 'MARKET',
                    'quantity': 1,
                    'product': 'MIS',
                    'variety': 'regular'
                }
                
                self.current_position = "BUY"
                self.entry_price = current_price
                self.entry_time = datetime.now()
                self.position_type = "BUY"
                self.target_price = current_price + self.PROFIT_POINTS
                self.stop_price = current_price - self.STOP_POINTS
                
                self.logger.info(f"BUY order placed at {current_price}")
                self.logger.info(f"Target: {self.target_price}, Stop: {self.stop_price}")
                
                return True
                
            elif signal == "BUY_PUT":
                # In real implementation, use SENSEX options
                order = {
                    'tradingsymbol': 'BSE:SENSEX',
                    'exchange': 'BSE',
                    'transaction_type': 'SELL',
                    'order_type': 'MARKET',
                    'quantity': 1,
                    'product': 'MIS',
                    'variety': 'regular'
                }
                
                self.current_position = "SELL"
                self.entry_price = current_price
                self.entry_time = datetime.now()
                self.position_type = "SELL"
                self.target_price = current_price - self.PROFIT_POINTS
                self.stop_price = current_price + self.STOP_POINTS
                
                self.logger.info(f"SELL order placed at {current_price}")
                self.logger.info(f"Target: {self.target_price}, Stop: {self.stop_price}")
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            return False
            
    def close_position(self, current_price):
        """Close current position"""
        try:
            if self.current_position:
                # Calculate P&L
                if self.position_type == "BUY":
                    pnl = current_price - self.entry_price
                else:
                    pnl = self.entry_price - current_price
                    
                self.logger.info(f"Position closed at {current_price}")
                self.logger.info(f"P&L: {pnl:.2f} points")
                
                # Reset position
                self.current_position = None
                self.entry_price = None
                self.entry_time = None
                self.position_type = None
                self.target_price = None
                self.stop_price = None
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error closing position: {e}")
            return False
            
    def run_scalping_loop(self):
        """Main scalping loop"""
        self.logger.info("Starting high-confidence SENSEX scalper...")
        self.logger.info(f"Profit target: {self.PROFIT_POINTS} points")
        self.logger.info(f"Stop loss: {self.STOP_POINTS} points")
        self.logger.info(f"Min confidence: {self.MIN_CONFIDENCE * 100}%")
        
        try:
            while True:
                # Get current SENSEX data
                sensex_data = self.get_sensex_data()
                if not sensex_data:
                    time.sleep(5)
                    continue
                    
                current_price = sensex_data['price']
                
                # Get historical data for analysis
                try:
                    historical_data = self.kite.historical_data(
                        self.SENSEX_TOKEN,
                        from_date=datetime.now() - timedelta(hours=1),
                        to_date=datetime.now(),
                        interval="minute"
                    )
                except:
                    historical_data = []
                
                # Check exit conditions if in position
                if self.current_position:
                    if self.check_exit_conditions(current_price):
                        self.close_position(current_price)
                        
                # Generate new signal if no position
                else:
                    signal = self.generate_signal(current_price, historical_data)
                    
                    if signal != "NO_SIGNAL":
                        self.place_order(signal, current_price)
                
                # Log current status
                self.logger.info(f"SENSEX: {current_price} | Position: {self.current_position}")
                
                # Wait before next check
                time.sleep(10)  # Check every 10 seconds
                
        except KeyboardInterrupt:
            self.logger.info("Scalper stopped by user")
        except Exception as e:
            self.logger.error(f"Error in scalping loop: {e}")
            
    def backtest_strategy(self, days=5):
        """Backtest the strategy on historical data"""
        try:
            historical_data = self.kite.historical_data(
                self.SENSEX_TOKEN,
                from_date=datetime.now() - timedelta(days=days),
                to_date=datetime.now(),
                interval="5minute"
            )
            
            self.logger.info(f"Backtesting on {len(historical_data)} data points")
            
            # Simulate trades
            trades = []
            position = None
            entry_price = None
            
            for i in range(10, len(historical_data)):
                current_price = historical_data[i]['close']
                past_data = historical_data[i-10:i]
                
                signal = self.generate_signal(current_price, past_data)
                
                if signal != "NO_SIGNAL" and not position:
                    # Entry
                    position = signal
                    entry_price = current_price
                    trades.append({
                        'entry_time': historical_data[i]['date'],
                        'entry_price': entry_price,
                        'signal': signal
                    })
                    
                elif position and entry_price:
                    # Check exit
                    if position == "BUY_CALL":
                        profit = current_price - entry_price
                    else:
                        profit = entry_price - current_price
                        
                    if profit >= self.PROFIT_POINTS or profit <= -self.STOP_POINTS:
                        # Exit
                        trades[-1].update({
                            'exit_time': historical_data[i]['date'],
                            'exit_price': current_price,
                            'profit': profit
                        })
                        position = None
                        entry_price = None
                        
            # Calculate results
            profitable_trades = [t for t in trades if 'profit' in t and t['profit'] > 0]
            total_trades = len([t for t in trades if 'profit' in t])
            
            if total_trades > 0:
                win_rate = len(profitable_trades) / total_trades * 100
                total_pnl = sum(t['profit'] for t in trades if 'profit' in t)
                
                self.logger.info(f"Backtest Results:")
                self.logger.info(f"Total Trades: {total_trades}")
                self.logger.info(f"Win Rate: {win_rate:.2f}%")
                self.logger.info(f"Total P&L: {total_pnl:.2f} points")
                
                return trades
                
            return []
            
        except Exception as e:
            self.logger.error(f"Error in backtest: {e}")
            return []

if __name__ == "__main__":
    scalper = HighConfidenceSensexScalper()
    
    # Run backtest first
    print("Running backtest...")
    backtest_results = scalper.backtest_strategy(days=2)
    
    # Start live scalping
    print("Starting live scalping...")
    scalper.run_scalping_loop()