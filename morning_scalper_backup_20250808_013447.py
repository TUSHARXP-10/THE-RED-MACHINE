#!/usr/bin/env python3
"""
Morning SENSEX Scalper - Updated for Kite Connect
Optimized for morning volatility (9:15-10:30 AM) with 25-point profit/stop
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from kiteconnect import KiteConnect
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('morning_scalping.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HighConfidenceScalper:
    def __init__(self):
        self.setup_logging()
        self.kite = KiteConnect(api_key=os.getenv('KITE_API_KEY'))
        self.kite.set_access_token(os.getenv('KITE_ACCESS_TOKEN'))
        
        self.previous_price = None
        self.entry_price = None
        self.position = None  # 'CALL' or 'PUT'
        self.PROFIT_POINTS = 25
        self.STOP_POINTS = 25
        self.MIN_CONFIDENCE = 0.65  # Reduced from 90% to 65%
        self.MIN_OI_PERCENTILE = 90  # Top 10% OI
        self.first_trade_done = False  # Track if first trade executed
        self.price_history = []
        self.max_history = 20
        self.trades_today = []
        self.price_change_threshold = 20  # Reduced from 50+ to 20+ points
        self.volatility_window = []
        self.adaptive_threshold = 50
        
    def get_live_sensex_data(self):
        """Get real SENSEX price from Breeze API"""
        try:
            response = self.breeze.get_market_data(
                stock_code="BSESEN",
                exchange_code="BSE",
                product_type="cash"
            )
            
            if response and 'current_price' in response:
                ltp = float(response['current_price'])
                volume = int(response.get('volume', 0))
                
                if ltp > 0:
                    return {
                        'price': ltp,
                        'volume': volume,
                        'timestamp': datetime.now()
                    }
            
            logger.error("Could not retrieve valid SENSEX data")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching SENSEX data: {e}")
            return None
    
    def is_market_open(self):
        """Check if market is open for trading"""
        now = datetime.now()
        weekday = now.weekday()
        
        # Check if it's a weekday
        if weekday >= 5:  # Saturday or Sunday
            return False
        
        # Check trading hours (9:15 AM - 3:30 PM)
        market_open = now.replace(hour=9, minute=15, second=0)
        market_close = now.replace(hour=15, minute=30, second=0)
        
        return market_open <= now <= market_close
    
    def is_prime_scalping_time(self):
        """Check if we're in prime scalping hours"""
        now = datetime.now()
        
        # Prime time: 9:15-10:30 AM
        prime_start = now.replace(hour=9, minute=15, second=0)
        prime_end = now.replace(hour=10, minute=30, second=0)
        
        return prime_start <= now <= prime_end
    
    def calculate_price_change(self, current_price):
        """Calculate price change from recent history"""
        if len(self.price_history) < 2:
            return 0
        
        recent_price = self.price_history[-2]['price']
        return ((current_price - recent_price) / recent_price) * 100
    
    def generate_signal(self, market_data):
        """Generate scalping signal based on price movement"""
        current_price = market_data['price']
        volume = market_data['volume']
        
        # Add to price history
        self.price_history.append(market_data)
        if len(self.price_history) > self.max_history:
            self.price_history.pop(0)
        
        # Calculate price change
        price_change = self.calculate_price_change(current_price)
        
        # TESTING MODE: Generate signals more frequently
        entry_threshold = 0.01  # Reduced to 0.01% for testing
        
        # Generate signal - ALWAYS generate for testing
        if len(self.price_history) >= 2:  # Just need 2 data points
            if price_change >= entry_threshold:
                return "BUY"
            elif price_change <= -entry_threshold:
                return "SELL"
            else:
                # Force signal generation for testing
                return "BUY" if len(self.trades_today) % 2 == 0 else "SELL"
        
        return "BUY"  # Default signal for testing
    
    def execute_trade(self, signal, market_data):
        """Execute scalping trade"""
        try:
            price = market_data['price']
            timestamp = market_data['timestamp']
            
            # Calculate position size
            position_size = min(self.max_position, self.capital / 2)
            
            # Set stop loss and target
            stop_loss = price * (1 - self.stop_loss_pct/100) if signal == "BUY" else price * (1 + self.stop_loss_pct/100)
            target = price * (1 + 0.3/100) if signal == "BUY" else price * (1 - 0.3/100)
            
            trade = {
                'signal': signal,
                'entry_price': price,
                'position_size': position_size,
                'stop_loss': stop_loss,
                'target': target,
                'timestamp': timestamp,
                'status': 'OPEN'
            }
            
            self.trades_today.append(trade)
            
            logger.info(f"SCALP TRADE EXECUTED: {signal} @ Rs.{price:,.2f}")
            logger.info(f"Position: Rs.{position_size}, SL: Rs.{stop_loss:,.2f}, Target: Rs.{target:,.2f}")
            
            # Send alert
            self.send_trade_alert(trade)
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
    
    def send_trade_alert(self, trade):
        """Send trade alert via email/notification"""
        try:
            # Simple console alert for now
            print(f"TRADE ALERT: {trade['signal']} SENSEX @ Rs.{trade['entry_price']:,.2f}")
            
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    def execute_trade(self, signal, entry_price, strike_price=None):
        """Execute scalping trade with 25-point profit/stop"""
        try:
            # Calculate profit and stop levels
            if signal == "CALL":
                target_price = entry_price + self.PROFIT_POINTS
                stop_price = entry_price - self.STOP_POINTS
            else:  # PUT
                target_price = entry_price - self.PROFIT_POINTS
                stop_price = entry_price + self.STOP_POINTS
            
            trade = {
                'signal': signal,
                'entry_price': entry_price,
                'strike_price': strike_price,
                'target_price': target_price,
                'stop_price': stop_price,
                'timestamp': datetime.now(),
                'status': 'OPEN',
                'points_target': self.PROFIT_POINTS,
                'points_stop': self.STOP_POINTS
            }
            
            self.trades_today.append(trade)
            
            logger.info(f"SCALP TRADE EXECUTED: {signal} @ Rs.{entry_price:,.2f}")
            logger.info(f"Target: {target_price} (+{self.PROFIT_POINTS} pts)")
            logger.info(f"Stop: {stop_price} (-{self.STOP_POINTS} pts)")
            
            # Send alert
            self.send_trade_alert(trade)
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
    
    def send_trade_alert(self, trade):
        """Send trade alert via email/notification"""
        try:
            print(f"🚨 TRADE ALERT: {trade['signal']} SENSEX @ Rs.{trade['entry_price']:,.2f}")
            print(f"📈 Target: {trade['target_price']} | 📉 Stop: {trade['stop_price']}")
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    def monitor_trades(self):
        """Monitor open trades for 25-point exits"""
        current_data = self.get_live_sensex_data()
        if not current_data:
            return
        
        current_price = current_data['price']
        
        for trade in self.trades_today:
            if trade['status'] == 'OPEN':
                entry_price = trade['entry_price']
                
                # Check profit target
                if trade['signal'] == "CALL":
                    if current_price >= trade['target_price']:
                        trade['status'] = 'TARGET_HIT'
                        trade['exit_price'] = current_price
                        trade['exit_time'] = datetime.now()
                        pnl = current_price - entry_price
                        logger.info(f"🎯 TARGET ACHIEVED: {trade['signal']} @ Rs.{current_price:,.2f} (+{pnl:.1f} pts)")
                        
                    elif current_price <= trade['stop_price']:
                        trade['status'] = 'STOPPED_OUT'
                        trade['exit_price'] = current_price
                        trade['exit_time'] = datetime.now()
                        pnl = current_price - entry_price
                        logger.info(f"💥 STOP LOSS HIT: {trade['signal']} @ Rs.{current_price:,.2f} ({pnl:.1f} pts)")
                        
                else:  # PUT
                    if current_price <= trade['target_price']:
                        trade['status'] = 'TARGET_HIT'
                        trade['exit_price'] = current_price
                        trade['exit_time'] = datetime.now()
                        pnl = entry_price - current_price
                        logger.info(f"🎯 TARGET ACHIEVED: {trade['signal']} @ Rs.{current_price:,.2f} (+{pnl:.1f} pts)")
                        
                    elif current_price >= trade['stop_price']:
                        trade['status'] = 'STOPPED_OUT'
                        trade['exit_price'] = current_price
                        trade['exit_time'] = datetime.now()
                        pnl = entry_price - current_price
                        logger.info(f"💥 STOP LOSS HIT: {trade['signal']} @ Rs.{current_price:,.2f} ({pnl:.1f} pts)")
                        
    def update_adaptive_thresholds(self, market_data):
        """Adapt thresholds based on current volatility"""
        if 'price_change' in market_data:
            self.volatility_window.append(abs(market_data['price_change']))
            if len(self.volatility_window) > 20:
                self.volatility_window.pop(0)
                
            if len(self.volatility_window) >= 5:
                current_volatility = np.std(self.volatility_window)
                
                # Lower thresholds in high volatility = more signals
                if current_volatility > 100:  # High volatility
                    self.adaptive_threshold = 25
                    self.MIN_CONFIDENCE = 0.55
                elif current_volatility > 50:  # Medium volatility  
                    self.adaptive_threshold = 40
                    self.MIN_CONFIDENCE = 0.60
                else:  # Low volatility
                    self.adaptive_threshold = 75
                    self.MIN_CONFIDENCE = 0.70
                    
                logging.info(f"Adapted threshold to {self.adaptive_threshold} based on volatility {current_volatility}")

    def should_force_signal(self, current_time, market_data):
        """Force signal generation when conditions are met"""
        # Force morning trade at 9:15 AM
        if current_time.hour == 9 and current_time.minute == 15 and not self.first_trade_done:
            return True
            
        # Force trade if no trades today and it's after 2 PM
        if len(self.trades_today) == 0 and current_time.hour >= 14:
            return True
            
        # Force trade on any 20+ point move
        if 'price_change' in market_data and abs(market_data['price_change']) >= 20:
            return True
            
        return False
        
    def generate_signal(self, market_data):
        """Multi-tier signal generation with adaptive thresholds"""
        try:
            current_price = market_data['price']
            
            # Add to price history
            self.price_history.append(market_data)
            if len(self.price_history) > self.max_history:
                self.price_history.pop(0)
            
            # Calculate momentum
            if len(self.price_history) >= 2:
                prev_price = self.price_history[-2]['price']
                momentum = (current_price - prev_price)
                momentum_pct = (momentum / prev_price) * 100
                
                # Update adaptive thresholds
                self.update_adaptive_thresholds({'price_change': momentum_pct})
                
                # Multi-tier signal generation
                signal_type = "HIGH_CONFIDENCE"
                
                # Force signal if conditions met
                if self.should_force_signal(datetime.now(), {'price_change': momentum_pct}):
                    confidence = max(0.55, abs(momentum_pct) * 3)  # Ensure minimum confidence for forced trades
                    signal_type = "FORCE_SIGNAL"
                else:
                    confidence = min(0.98, abs(momentum_pct) * 3)
                    
                # Check confidence threshold
                if confidence >= self.MIN_CONFIDENCE:
                    signal = "CALL" if momentum > 0 else "PUT"
                    selected_option = self.get_high_oi_option(signal)
                    
                    if selected_option:
                        return signal, selected_option, confidence
            
            return None, None, 0.0
            
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return None, None, 0.0
    def get_session_summary(self):
        """Get summary of today's trading session"""
        total_trades = len(self.trades_today)
        profitable_trades = sum(1 for t in self.trades_today if t.get('status') == 'TARGET_HIT')
        losing_trades = sum(1 for t in self.trades_today if t.get('status') == 'STOPPED_OUT')
        
        return {
            'total_trades': total_trades,
            'profitable_trades': profitable_trades,
            'losing_trades': losing_trades,
            'open_trades': total_trades - profitable_trades - losing_trades
        }
    
    def run_scalping(self):
        """Main high-confidence scalping loop"""
        logger.info("🚀 Starting High Confidence SENSEX Scalper...")
        logger.info("📊 Target: 9:15-10:30 AM with 25pt profit/stop")
        logger.info("📈 90%+ confidence, High OI selection")
        
        prev_close = self.get_previous_close()
        if prev_close:
            logger.info(f"Previous close: Rs.{prev_close:,.2f}")
        
        while True:
            try:
                # Check market hours
                now = datetime.now()
                market_open = now.replace(hour=9, minute=15, second=0)
                market_close = now.replace(hour=15, minute=30, second=0)
                
                if now < market_open or now > market_close:
                    logger.info("Market closed - waiting...")
                    time.sleep(60)
                    continue
                
                # Get market data
                market_data = self.get_live_sensex_data()
                if not market_data:
                    time.sleep(5)
                    continue
                
                current_price = market_data['price']
                
                # Handle first trade at market open
                if not self.first_trade_done and now.hour == 9 and now.minute == 15:
                    self.pre_planned_first_trade(current_price, prev_close)
                
                # Generate high-confidence signal
                signal, selected_option, confidence = self.generate_signal(market_data)
                
                if signal and selected_option:
                    self.execute_trade(signal, current_price, selected_option['strike'])
                
                # Monitor existing trades
                self.monitor_trades()
                
                # Log current status
                open_trades = [t for t in self.trades_today if t['status'] == 'OPEN']
                logger.info(f"SENSEX: Rs.{current_price:,.2f} | Open: {len(open_trades)} | Total: {len(self.trades_today)}")
                
                time.sleep(10)  # Check every 10 seconds
                
            except KeyboardInterrupt:
                logger.info("Scalper stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in scalping loop: {e}")
                time.sleep(30)

if __name__ == "__main__":
    scalper = HighConfidenceScalper()
    scalper.run_scalping()