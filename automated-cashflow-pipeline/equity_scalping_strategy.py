"""
Equity Scalping Strategy for ₹5,000 Capital
Week-by-week implementation following the hybrid approach
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, time
import logging
from typing import Dict, List, Tuple
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EquityScalpingStrategy:
    def __init__(self, config_path: str = "equity_scalping_config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.capital = self.config['starting_capital']
        self.max_position = self.config['max_position_size']
        self.trades_today = 0
        self.daily_pnl = 0
        self.current_positions = []
        
        # Performance tracking
        self.trade_history = []
        self.daily_results = []
        
        # Initialize trade log
        self._initialize_trade_log()
        
    def _initialize_trade_log(self):
        """Initialize CSV trade log"""
        log_path = Path(self.config['paper_trading']['log_file'])
        if not log_path.exists():
            with open(log_path, 'w') as f:
                f.write("timestamp,symbol,action,quantity,price,stop_loss,target,result,pnl,model_score\n")
    
    def is_trading_hours(self) -> bool:
        """Check if current time is within trading hours"""
        now = datetime.now().time()
        market_open = time.fromisoformat(self.config['time_based_limits']['market_open'])
        market_close = time.fromisoformat(self.config['time_based_limits']['market_close'])
        lunch_start = time.fromisoformat("12:00")
        lunch_end = time.fromisoformat("13:30")
        
        # Skip lunch break
        if lunch_start <= now <= lunch_end:
            return False
            
        return market_open <= now <= market_close
    
    def calculate_position_size(self, model_score: float, confidence: float) -> float:
        """Calculate position size based on model confidence and score"""
        if model_score < self.config['model_accuracy_threshold']:
            return 0
        
        # Risk-adjusted position sizing
        risk_factor = min(confidence, 0.8)  # Cap at 80% confidence
        base_size = min(self.max_position, self.capital * 0.3)
        
        return base_size * risk_factor
    
    def generate_trade_signal(self, symbol: str, market_data: Dict) -> Dict:
        """Generate buy/sell signal based on model prediction and market data"""
        
        # Placeholder for actual model prediction
        # In real implementation, this would call your 98.61% accuracy model
        model_score = np.random.uniform(0.7, 1.0)  # Simulated high accuracy
        confidence = np.random.uniform(0.6, 0.9)
        
        # Simple momentum-based signal for equity scalping
        current_price = market_data.get('current_price', 0)
        sma_20 = market_data.get('sma_20', current_price)
        rsi = market_data.get('rsi', 50)
        
        signal = "HOLD"
        if current_price > sma_20 and rsi < 70 and model_score > 0.75:
            signal = "BUY"
        elif current_price < sma_20 and rsi > 30 and model_score > 0.75:
            signal = "SELL"
        
        return {
            'signal': signal,
            'model_score': model_score,
            'confidence': confidence,
            'target_price': current_price * 1.08,  # 8% target
            'stop_loss': current_price * 0.97      # 3% stop loss
        }
    
    def execute_trade(self, symbol: str, signal_data: Dict, current_price: float) -> Dict:
        """Execute a trade based on signal"""
        
        if not self.is_trading_hours():
            return {'status': 'skipped', 'reason': 'outside_trading_hours'}
        
        if self.trades_today >= self.config['max_trades_per_day']:
            return {'status': 'skipped', 'reason': 'max_trades_reached'}
        
        if self.daily_pnl <= -self.config['risk_management']['max_daily_loss']:
            return {'status': 'skipped', 'reason': 'daily_loss_limit'}
        
        position_size = self.calculate_position_size(
            signal_data['model_score'], 
            signal_data['confidence']
        )
        
        if position_size == 0:
            return {'status': 'skipped', 'reason': 'low_confidence'}
        
        # Calculate quantity (round to nearest whole share)
        quantity = int(position_size / current_price)
        if quantity == 0:
            return {'status': 'skipped', 'reason': 'position_too_small'}
        
        trade = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'action': signal_data['signal'],
            'quantity': quantity,
            'entry_price': current_price,
            'stop_loss': signal_data['stop_loss'],
            'target_price': signal_data['target_price'],
            'position_size': position_size,
            'model_score': signal_data['model_score']
        }
        
        # Log trade
        self._log_trade(trade)
        self.current_positions.append(trade)
        self.trades_today += 1
        
        return {'status': 'executed', 'trade': trade}
    
    def _log_trade(self, trade: Dict):
        """Log trade to CSV file"""
        with open(self.config['paper_trading']['log_file'], 'a') as f:
            f.write(f"{trade['timestamp']},{trade['symbol']},{trade['action']},{trade['quantity']},"
                   f"{trade['entry_price']},{trade['stop_loss']},{trade['target_price']},"
                   f"PENDING,0,{trade['model_score']}\n")
    
    def update_positions(self, current_prices: Dict[str, float]):
        """Update open positions with current market prices"""
        for position in self.current_positions:
            symbol = position['symbol']
            if symbol in current_prices:
                current_price = current_prices[symbol]
                
                # Check for stop loss or target hit
                if position['action'] == 'BUY':
                    if current_price <= position['stop_loss']:
                        self.close_position(position, current_price, 'STOP_LOSS')
                    elif current_price >= position['target_price']:
                        self.close_position(position, current_price, 'TARGET_HIT')
                elif position['action'] == 'SELL':
                    if current_price >= position['stop_loss']:
                        self.close_position(position, current_price, 'STOP_LOSS')
                    elif current_price <= position['target_price']:
                        self.close_position(position, current_price, 'TARGET_HIT')
    
    def close_position(self, position: Dict, exit_price: float, reason: str):
        """Close an open position"""
        if position['action'] == 'BUY':
            pnl = (exit_price - position['entry_price']) * position['quantity']
        else:  # SELL
            pnl = (position['entry_price'] - exit_price) * position['quantity']
        
        self.daily_pnl += pnl
        self.capital += pnl
        
        # Update trade log
        self._update_trade_log(position, exit_price, pnl, reason)
        
        # Remove from current positions
        self.current_positions.remove(position)
        
        # Record in history
        completed_trade = {
            **position,
            'exit_price': exit_price,
            'pnl': pnl,
            'exit_reason': reason,
            'exit_time': datetime.now().isoformat()
        }
        self.trade_history.append(completed_trade)
    
    def _update_trade_log(self, position: Dict, exit_price: float, pnl: float, reason: str):
        """Update trade log with exit details"""
        # This is a simplified version - in practice, you'd read/modify/write the CSV
        logger.info(f"Position closed: {position['symbol']} at {exit_price}, PnL: {pnl:.2f}, Reason: {reason}")
    
    def get_daily_summary(self) -> Dict:
        """Get daily performance summary"""
        if not self.trade_history:
            return {'message': 'No trades executed today'}
        
        today_trades = [t for t in self.trade_history 
                       if datetime.fromisoformat(t['timestamp']).date() == datetime.now().date()]
        
        if not today_trades:
            return {'message': 'No trades executed today'}
        
        total_pnl = sum(t['pnl'] for t in today_trades)
        winning_trades = [t for t in today_trades if t['pnl'] > 0]
        losing_trades = [t for t in today_trades if t['pnl'] < 0]
        
        return {
            'total_trades': len(today_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'total_pnl': total_pnl,
            'win_rate': len(winning_trades) / len(today_trades) if today_trades else 0,
            'avg_profit_per_win': sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0,
            'avg_loss_per_loss': sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0,
            'current_capital': self.capital
        }
    
    def week_by_week_plan(self, week: int) -> Dict:
        """Return specific configuration for each week"""
        plans = {
            1: {
                'mode': 'equity_only',
                'max_trades': 2,
                'max_position': 1000,
                'symbols': ['RELIANCE', 'TCS', 'HDFCBANK'][:2],
                'description': 'Week 1: Pure equity focus, build confidence'
            },
            2: {
                'mode': 'equity_only',
                'max_trades': 3,
                'max_position': 1200,
                'symbols': ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY'][:3],
                'description': 'Week 2: Expand equity universe, refine strategy'
            },
            3: {
                'mode': 'hybrid',
                'max_trades': 3,
                'max_position': 1000,
                'symbols': ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY'][:3],
                'options_allocation': 0.3,
                'description': 'Week 3: 70% equity, 30% options on high conviction'
            },
            4: {
                'mode': 'hybrid',
                'max_trades': 4,
                'max_position': 1200,
                'symbols': self.config['equity_symbols'][:4],
                'options_allocation': 0.4,
                'description': 'Week 4: Scale up hybrid approach with decay awareness'
            }
        }
        
        return plans.get(week, plans[4])

def setup_breeze_credentials():
    """Interactive setup for Breeze API credentials"""
    print("🚀 Setting up Breeze API Credentials...")
    print("Please follow these steps:")
    print("1. Login to ICICI Direct")
    print("2. Go to 'API Access' section")
    print("3. Generate API Key, Secret, and Session Token")
    print("4. Enter your credentials below:\n")
    
    api_key = input("Enter BREEZE_API_KEY: ").strip()
    api_secret = input("Enter BREEZE_API_SECRET: ").strip()
    session_token = input("Enter BREEZE_SESSION_TOKEN: ").strip()
    client_code = input("Enter ICICI_CLIENT_CODE: ").strip()
    
    env_content = f"""# Breeze API Credentials for ICICI Direct
BREEZE_API_KEY={api_key}
BREEZE_API_SECRET={api_secret}
BREEZE_SESSION_TOKEN={session_token}
ICICI_CLIENT_CODE={client_code}

# Trading Configuration
MODE=paper  # Change to 'live' when ready
MAX_POSITION_SIZE=1500
MAX_DAILY_LOSS=200
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Breeze credentials configured successfully!")
    print("📁 Check .env file for your configuration")

if __name__ == "__main__":
    # Quick test of the strategy
    strategy = EquityScalpingStrategy()
    
    # Test week 1 configuration
    week1_config = strategy.week_by_week_plan(1)
    print(f"Week 1 Configuration: {week1_config}")
    
    # Simulate a trade
    mock_data = {
        'current_price': 150.0,
        'sma_20': 148.5,
        'rsi': 45
    }
    
    signal = strategy.generate_trade_signal('RELIANCE', mock_data)
    print(f"Generated signal: {signal}")
    
    # Setup credentials if needed
    if not os.path.exists('.env'):
        setup_choice = input("Setup Breeze credentials? (y/n): ")
        if setup_choice.lower() == 'y':
            setup_breeze_credentials()