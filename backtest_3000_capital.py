#!/usr/bin/env python3
"""
Backtesting Script for 3000 Capital Investment
Comprehensive backtesting with position sizing for small capital
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backtest_3000.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CapitalOptimizedBacktester:
    def __init__(self, initial_capital=3000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = []
        self.trades = []
        self.max_position_size = 0.1  # 10% of capital per trade
        self.max_daily_loss = 0.05    # 5% daily loss limit
        self.daily_loss = 0
        
    def load_historical_data(self, days=30):
        """Load historical SENSEX data for backtesting"""
        try:
            # Try to load from existing files
            data_files = [
                'simulated_prices.csv',
                'backtest_results.csv',
                'detailed_trades.csv'
            ]
            
            for file in data_files:
                if Path(file).exists():
                    df = pd.read_csv(file)
                    if 'price' in df.columns:
                        logger.info(f"Loaded data from {file}")
                        return df
                        
            # Generate sample data if no files exist
            logger.info("Generating sample historical data...")
            return self.generate_sample_data(days)
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return self.generate_sample_data(days)
    
    def generate_sample_data(self, days=30):
        """Generate realistic SENSEX sample data"""
        np.random.seed(42)
        
        # Generate 1-minute candles for specified days
        minutes_per_day = 375  # 6.25 hours * 60 minutes
        total_minutes = days * minutes_per_day
        
        # Base SENSEX around 80000
        base_price = 80000
        prices = [base_price]
        
        for i in range(1, total_minutes):
            # Add realistic volatility (0.5-2% daily)
            volatility = np.random.normal(0, 0.001)  # 0.1% per minute
            new_price = prices[-1] * (1 + volatility)
            prices.append(max(new_price, base_price * 0.95))  # Floor at 5% below
        
        df = pd.DataFrame({
            'timestamp': pd.date_range(
                start=datetime.now() - timedelta(days=days),
                periods=total_minutes,
                freq='1min'
            ),
            'price': prices,
            'volume': np.random.randint(100000, 1000000, total_minutes)
        })
        
        return df
    
    def calculate_position_size(self, signal_strength):
        """Calculate optimal position size based on capital and risk"""
        max_trade_amount = self.capital * self.max_position_size
        
        # Risk-adjusted position sizing
        if signal_strength > 0.8:
            position_multiplier = 1.0
        elif signal_strength > 0.6:
            position_multiplier = 0.75
        elif signal_strength > 0.4:
            position_multiplier = 0.5
        else:
            position_multiplier = 0.25
            
        return max_trade_amount * position_multiplier
    
    def generate_signals(self, df):
        """Generate trading signals with capital optimization"""
        df = df.copy()
        
        # Technical indicators optimized for small capital
        df['sma_5'] = df['price'].rolling(window=5).mean()
        df['sma_20'] = df['price'].rolling(window=20).mean()
        df['rsi'] = self.calculate_rsi(df['price'], 14)
        
        # Volatility filter
        df['volatility'] = df['price'].rolling(window=10).std()
        df['volatility_pct'] = df['volatility'] / df['price']
        
        # Signal generation
        df['signal'] = 0
        df['signal_strength'] = 0
        
        # Trend following signals
        bullish = (df['sma_5'] > df['sma_20']) & (df['rsi'] < 70)
        bearish = (df['sma_5'] < df['sma_20']) & (df['rsi'] > 30)
        
        # Low volatility filter for small capital
        low_volatility = df['volatility_pct'] < 0.005
        
        df.loc[bullish & low_volatility, 'signal'] = 1
        df.loc[bearish & low_volatility, 'signal'] = -1
        
        # Signal strength based on RSI distance from 50
        df['signal_strength'] = abs(df['rsi'] - 50) / 50
        
        return df
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def backtest_strategy(self, df):
        """Run comprehensive backtest with 3000 capital"""
        logger.info(f"Starting backtest with Rs.{self.initial_capital} capital")
        
        df = self.generate_signals(df)
        
        for i in range(20, len(df)):
            row = df.iloc[i]
            
            # Skip if no signal
            if row['signal'] == 0:
                continue
                
            # Check daily loss limit
            if self.daily_loss >= self.capital * self.max_daily_loss:
                logger.warning("Daily loss limit reached, stopping trading")
                break
            
            # Calculate position size
            position_size = self.calculate_position_size(row['signal_strength'])
            
            # Entry logic
            if len(self.positions) == 0:  # Only one position at a time
                trade = {
                    'entry_time': row['timestamp'],
                    'entry_price': row['price'],
                    'signal': row['signal'],
                    'position_size': position_size,
                    'target_price': row['price'] * (1.005 if row['signal'] > 0 else 0.995),  # 0.5% target
                    'stop_price': row['price'] * (0.998 if row['signal'] > 0 else 1.002),  # 0.2% stop
                    'status': 'OPEN'
                }
                
                self.positions.append(trade)
                logger.info(f"New position: {trade}")
            
            # Exit logic for open positions
            for pos in self.positions:
                if pos['status'] == 'OPEN':
                    exit_triggered = False
                    
                    if row['signal'] > 0:  # Long position
                        if row['price'] >= pos['target_price']:
                            exit_triggered = True
                            profit = (pos['target_price'] - pos['entry_price']) * pos['position_size']
                        elif row['price'] <= pos['stop_price']:
                            exit_triggered = True
                            profit = (pos['stop_price'] - pos['entry_price']) * pos['position_size']
                    else:  # Short position
                        if row['price'] <= pos['target_price']:
                            exit_triggered = True
                            profit = (pos['entry_price'] - pos['target_price']) * pos['position_size']
                        elif row['price'] >= pos['stop_price']:
                            exit_triggered = True
                            profit = (pos['entry_price'] - pos['stop_price']) * pos['position_size']
                    
                    if exit_triggered:
                        pos['exit_time'] = row['timestamp']
                        pos['exit_price'] = row['price']
                        pos['profit'] = profit
                        pos['status'] = 'CLOSED'
                        
                        self.capital += profit
                        self.trades.append(pos)
                        self.daily_loss += min(0, profit)
                        
                        logger.info(f"Position closed: Profit ₹{profit:.2f}, New capital: ₹{self.capital:.2f}")
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive backtest report"""
        if not self.trades:
            return {
                'status': 'No trades executed',
                'initial_capital': self.initial_capital,
                'final_capital': self.capital,
                'total_profit': 0,
                'total_return_percent': 0,
                'total_trades': 0,
                'profitable_trades': 0,
                'losing_trades': 0,
                'win_rate_percent': 0,
                'average_profit': 0,
                'max_profit': 0,
                'max_loss': 0,
                'recommendation': 'No trades - Need more data'
            }
        
        df_trades = pd.DataFrame(self.trades)
        
        # Calculate metrics
        total_trades = len(df_trades)
        profitable_trades = len(df_trades[df_trades['profit'] > 0])
        losing_trades = len(df_trades[df_trades['profit'] < 0])
        
        total_profit = df_trades['profit'].sum()
        total_return = (total_profit / self.initial_capital) * 100
        
        win_rate = (profitable_trades / total_trades) * 100 if total_trades > 0 else 0
        avg_profit = df_trades['profit'].mean()
        max_profit = df_trades['profit'].max()
        max_loss = df_trades['profit'].min()
        
        report = {
            'initial_capital': self.initial_capital,
            'final_capital': self.capital,
            'total_profit': total_profit,
            'total_return_percent': total_return,
            'total_trades': total_trades,
            'profitable_trades': profitable_trades,
            'losing_trades': losing_trades,
            'win_rate_percent': win_rate,
            'average_profit': avg_profit,
            'max_profit': max_profit,
            'max_loss': max_loss,
            'recommendation': self.get_recommendation(total_return, win_rate)
        }
        
        # Save detailed report
        with open('backtest_3000_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Backtest completed: {report}")
        return report
    
    def get_recommendation(self, total_return, win_rate):
        """Provide recommendation based on backtest results"""
        if total_return > 5 and win_rate > 60:
            return "EXCELLENT - Ready for live trading"
        elif total_return > 2 and win_rate > 55:
            return "GOOD - Proceed with caution"
        elif total_return > 0:
            return "MODERATE - Consider parameter optimization"
        else:
            return "POOR - Need strategy adjustment"

def main():
    """Run backtest with 3000 capital"""
    backtester = CapitalOptimizedBacktester(initial_capital=3000)
    
    # Load data
    df = backtester.load_historical_data(days=30)
    
    # Run backtest
    results = backtester.backtest_strategy(df)
    
    print("=" * 50)
    print("BACKTEST RESULTS - Rs.3000 CAPITAL")
    print("=" * 50)
    print(f"Initial Capital: Rs.{results['initial_capital']:,}")
    print(f"Final Capital: Rs.{results['final_capital']:,}")
    print(f"Total Profit: Rs.{results['total_profit']:.2f}")
    print(f"Total Return: {results['total_return_percent']:.2f}%")
    print(f"Total Trades: {results['total_trades']}")
    print(f"Win Rate: {results['win_rate_percent']:.1f}%")
    print(f"Recommendation: {results['recommendation']}")
    print("=" * 50)
    
    return results

if __name__ == "__main__":
    main()