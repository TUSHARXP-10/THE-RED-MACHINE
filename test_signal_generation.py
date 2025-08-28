#!/usr/bin/env python3
"""
SENSEX Scalping System - Signal Generation Test
Testing mode to ensure signals are generated without NO_SIGNAL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from morning_scalper import MorningScalper
import time
import random

class TestScalper(MorningScalper):
    def __init__(self):
        super().__init__()
        self.test_mode = True
    
    def is_market_open(self):
        """Override market hours check for testing"""
        return True  # Always open for testing
    
    def is_prime_scalping_time(self):
        """Override prime time check for testing"""
        return True  # Always prime time for testing
    
    def get_live_sensex_data(self):
        """Generate simulated SENSEX data for testing"""
        base_price = 80949.0
        # Simulate small price movements
        price_change = random.uniform(-0.5, 0.5)
        current_price = base_price + (base_price * price_change / 100)
        
        return {
            'price': current_price,
            'volume': random.randint(800000, 1200000),
            'timestamp': time.strftime('%H:%M:%S')
        }

def test_signal_generation():
    """Test signal generation continuously"""
    print("=== SENSEX SCALPING SYSTEM - TESTING MODE ===")
    print("Testing continuous signal generation...")
    print("Market hours: ALWAYS OPEN")
    print("Prime time: ALWAYS ACTIVE")
    print("Signal threshold: MINIMUM (0.01%)")
    print("=" * 50)
    
    scalper = TestScalper()
    
    # Run for 10 iterations to demonstrate signal generation
    for iteration in range(10):
        try:
            # Get simulated market data
            market_data = scalper.get_live_sensex_data()
            
            if market_data:
                # Generate signal
                signal = scalper.generate_signal(market_data)
                
                # Execute trade if signal generated
                if signal != "NO_SIGNAL":
                    scalper.execute_trade(signal, market_data)
                    
                    # Monitor trades
                    scalper.monitor_trades()
                    
                    # Log results
                    current_time = market_data['timestamp']
                    current_price = market_data['price']
                    total_trades = len(scalper.trades_today)
                    
                    print(f"{current_time} | SENSEX: Rs.{current_price:,.2f} | Signal: {signal} | Total Trades: {total_trades}")
                else:
                    print(f"ERROR: NO_SIGNAL detected at {market_data['timestamp']}")
                    return False
                
                time.sleep(1)  # Fast iteration for testing
                
        except KeyboardInterrupt:
            print("\nTesting stopped by user")
            break
        except Exception as e:
            print(f"Error in testing: {e}")
            continue
    
    # Final results
    summary = scalper.get_session_summary()
    print("\n=== TESTING RESULTS ===")
    print(f"Total Signals Generated: {summary['total_trades']}")
    print(f"Signals: {[t['signal'] for t in scalper.trades_today]}")
    print(f"Open Trades: {summary['open_trades']}")
    
    if summary['total_trades'] > 0:
        print("✅ SUCCESS: System generates signals and executes trades without NO_SIGNAL!")
        return True
    else:
        print("❌ FAILED: No trades generated")
        return False

if __name__ == "__main__":
    test_signal_generation()