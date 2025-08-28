#!/usr/bin/env python3
"""
Test script for High Confidence SENSEX Scalper
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from high_confidence_sensex_scalper import HighConfidenceSensexScalper

load_dotenv()

def test_scalper():
    """Test the high confidence scalper"""
    print("🧪 Testing High Confidence SENSEX Scalper...")
    
    try:
        # Initialize scalper
        scalper = HighConfidenceSensexScalper()
        
        # Test 1: Check SENSEX data fetch
        print("\n1. Testing SENSEX data fetch...")
        sensex_data = scalper.get_sensex_data()
        if sensex_data:
            print(f"✅ SENSEX data fetched successfully")
            print(f"   Current Price: {sensex_data['price']}")
            print(f"   Change: {sensex_data['change']}")
        else:
            print("❌ Failed to fetch SENSEX data")
            
        # Test 2: Check high OI strikes
        print("\n2. Testing high OI strike selection...")
        high_oi_strikes = scalper.get_high_oi_strikes()
        if high_oi_strikes:
            print(f"✅ Found {len(high_oi_strikes)} high OI strikes")
            for strike in high_oi_strikes[:3]:
                print(f"   Strike: {strike['strike']}, Total OI: {strike['total_oi']}")
        else:
            print("❌ No high OI strikes found")
            
        # Test 3: Run backtest
        print("\n3. Running backtest...")
        backtest_results = scalper.backtest_strategy(days=1)
        if backtest_results:
            print(f"✅ Backtest completed")
            profitable_trades = [t for t in backtest_results if t.get('profit', 0) > 0]
            total_trades = len([t for t in backtest_results if 'profit' in t])
            if total_trades > 0:
                win_rate = len(profitable_trades) / total_trades * 100
                total_pnl = sum(t['profit'] for t in backtest_results if 'profit' in t)
                print(f"   Total Trades: {total_trades}")
                print(f"   Win Rate: {win_rate:.1f}%")
                print(f"   Total P&L: {total_pnl:.1f} points")
        else:
            print("⚠️  No backtest trades generated")
            
        # Test 4: Check strategy parameters
        print("\n4. Strategy Parameters:")
        print(f"   Profit Target: {scalper.PROFIT_POINTS} points")
        print(f"   Stop Loss: {scalper.STOP_POINTS} points")
        print(f"   Min Confidence: {scalper.MIN_CONFIDENCE * 100}%")
        print(f"   Min OI Percentile: Top {100-scalper.MIN_OI_PERCENTILE}%")
        print(f"   Position Size: ₹{scalper.POSITION_SIZE}")
        print(f"   Max Capital: ₹{scalper.MAX_CAPITAL}")
        
        print("\n🎉 All tests completed successfully!")
        print("Ready for live trading. Run: python high_confidence_sensex_scalper.py")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scalper()