import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
import random

class RealTimeDataSimulator:
    def __init__(self):
        self.base_price = 75000
        self.volatility = 0.02
        self.start_balance = 100000
        self.current_balance = self.start_balance
        self.trades = []
        
    def generate_price_data(self, hours=24):
        """Generate realistic price data"""
        times = []
        prices = []
        
        current_time = datetime.now()
        for i in range(hours * 60):  # 1-minute intervals
            timestamp = current_time - timedelta(minutes=i)
            noise = np.random.normal(0, self.volatility * self.base_price)
            price = self.base_price + noise + np.sin(i * 0.01) * 100  # Add some trend
            
            times.append(timestamp)
            prices.append(max(price, self.base_price * 0.9))  # Floor at 90%
            
        return pd.DataFrame({
            'timestamp': times,
            'price': prices
        })
    
    def generate_trade(self):
        """Generate a mock trade"""
        actions = ['BUY', 'SELL']
        action = random.choice(actions)
        
        # Generate realistic P&L
        pnl = random.uniform(-500, 1000)
        
        trade = {
            'timestamp': datetime.now(),
            'action': action,
            'price': self.base_price + random.uniform(-100, 100),
            'quantity': random.randint(1, 10),
            'pnl': pnl,
            'mode': 'paper',
            'status': 'PAPER_EXECUTED',
            'signal_strength': random.uniform(0.1, 0.95)
        }
        
        return trade
    
    def simulate_real_time_data(self, duration_minutes=60):
        """Generate continuous real-time data"""
        print("Starting real-time data simulation...")
        
        # Create initial data files
        self.create_initial_files()
        
        start_time = datetime.now()
        trade_count = 0
        
        while (datetime.now() - start_time).total_seconds() < duration_minutes * 60:
            try:
                # Generate new price data
                price_data = self.generate_price_data(hours=1)
                price_data.to_csv('simulated_prices.csv', index=False)
                
                # Generate trades occasionally
                if random.random() < 0.1:  # 10% chance per minute
                    trade = self.generate_trade()
                    self.trades.append(trade)
                    
                    # Update balance
                    self.current_balance += trade['pnl']
                    
                    # Save trades
                    trades_df = pd.DataFrame(self.trades)
                    trades_df.to_csv('paper_trades.csv', index=False)
                    
                    # Update balance file
                    with open('paper_balance.json', 'w') as f:
                        json.dump({
                            'balance': self.current_balance,
                            'timestamp': str(datetime.now()),
                            'total_trades': len(self.trades),
                            'daily_pnl': sum(t['pnl'] for t in self.trades[-10:])  # Last 10 trades
                        }, f, indent=2)
                
                # Generate signal data
                signal_data = {
                    'timestamp': str(datetime.now()),
                    'current_price': float(price_data['price'].iloc[-1]),
                    'signal': random.choice(['BUY', 'SELL', 'HOLD']),
                    'confidence': random.uniform(0.1, 0.95),
                    'volume': random.randint(1000, 10000)
                }
                
                with open('latest_signal.json', 'w') as f:
                    json.dump(signal_data, f, indent=2)
                
                print(f"Data updated at {datetime.now().strftime('%H:%M:%S')} - "
                      f"Balance: ₹{self.current_balance:,.2f}, Trades: {len(self.trades)}")
                
                time.sleep(5)  # Update every 5 seconds
                
            except KeyboardInterrupt:
                print("\nSimulation stopped by user")
                break
            except Exception as e:
                print(f"Error in simulation: {e}")
                time.sleep(5)
    
    def create_initial_files(self):
        """Create initial data files"""
        # Create initial price data
        price_data = self.generate_price_data(hours=1)
        price_data.to_csv('simulated_prices.csv', index=False)
        
        # Create initial balance
        with open('paper_balance.json', 'w') as f:
            json.dump({
                'balance': self.start_balance,
                'timestamp': str(datetime.now()),
                'total_trades': 0,
                'daily_pnl': 0
            }, f, indent=2)
        
        # Create empty trades file
        empty_trades = pd.DataFrame(columns=[
            'timestamp', 'action', 'price', 'quantity', 'pnl', 
            'mode', 'status', 'signal_strength'
        ])
        empty_trades.to_csv('paper_trades.csv', index=False)
        
        # Create initial signal
        initial_signal = {
            'timestamp': str(datetime.now()),
            'current_price': self.base_price,
            'signal': 'HOLD',
            'confidence': 0.5,
            'volume': 5000
        }
        
        with open('latest_signal.json', 'w') as f:
            json.dump(initial_signal, f, indent=2)
        
        print("Initial data files created successfully")

def main():
    """Main function to run the simulator"""
    simulator = RealTimeDataSimulator()
    
    print("Real-Time Data Simulator")
    print("=" * 50)
    print("This will generate mock real-time trading data")
    print("for testing the Streamlit dashboard")
    print()
    
    duration = input("Enter simulation duration in minutes (default 60): ") or "60"
    
    try:
        duration_minutes = int(duration)
        simulator.simulate_real_time_data(duration_minutes)
    except ValueError:
        print("Invalid duration. Using 60 minutes.")
        simulator.simulate_real_time_data(60)

if __name__ == "__main__":
    main()