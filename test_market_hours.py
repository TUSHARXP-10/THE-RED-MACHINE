#!/usr/bin/env python3
"""
Test script to verify market hours validation is working correctly.
Run this to check if your system will respect market hours.
"""

import datetime as dt
from zoneinfo import ZoneInfo
import sys
import os

# Add current directory to path to import from minimal_trading_system
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_market_hours():
    """Test the market hours validation"""
    print("🧪 Testing Market Hours Validation")
    print("=" * 50)
    
    # Import the function from minimal_trading_system
    try:
        from minimal_trading_system import is_indian_market_open, get_next_market_open
        
        # Test current time
        now = dt.datetime.now(ZoneInfo('Asia/Kolkata'))
        print(f"\n📅 Current IST: {now.strftime('%A, %Y-%m-%d %H:%M:%S')}")
        
        # Test market status
        market_open = is_indian_market_open()
        print(f"\n🕐 Market Status: {'🟢 OPEN' if market_open else '🔴 CLOSED'}")
        
        # Test next market open
        next_open = get_next_market_open()
        print(f"\n⏰ Next Market Open: {next_open.strftime('%A, %Y-%m-%d %H:%M:%S IST')}")
        
        # Calculate time until next open
        time_until_open = (next_open - now).total_seconds()
        hours = int(time_until_open // 3600)
        minutes = int((time_until_open % 3600) // 60)
        print(f"⏳ Time until next open: {hours}h {minutes}m")
        
        # Test weekend scenario
        print(f"\n📊 Weekday Check: {now.strftime('%A')} ({'Weekday' if now.weekday() < 5 else 'Weekend'})")
        
        # Test edge cases
        print(f"\n🔍 Market Hours: 9:15 AM - 3:30 PM IST")
        
        if market_open:
            print("\n✅ System will ALLOW trading operations")
        else:
            print("\n❌ System will PREVENT trading operations")
            print("   - No API calls will be made")
            print("   - No alerts will be sent")
            print("   - System will sleep until next market open")
        
        return market_open
        
    except ImportError as e:
        print(f"❌ Error importing market hours functions: {e}")
        print("Make sure minimal_trading_system.py has the market hours functions")
        return False

def simulate_trading_hours():
    """Simulate different times to test market hours"""
    print("\n" + "=" * 50)
    print("🧪 Simulating Different Trading Hours")
    print("=" * 50)
    
    # Test scenarios
    test_times = [
        dt.datetime(2025, 7, 31, 9, 0, 0),    # 9:00 AM (before open)
        dt.datetime(2025, 7, 31, 9, 15, 0),   # 9:15 AM (market open)
        dt.datetime(2025, 7, 31, 12, 0, 0),   # 12:00 PM (midday)
        dt.datetime(2025, 7, 31, 15, 30, 0),  # 3:30 PM (market close)
        dt.datetime(2025, 7, 31, 18, 0, 0),   # 6:00 PM (after close)
        dt.datetime(2025, 8, 2, 10, 0, 0),    # Saturday (weekend)
        dt.datetime(2025, 8, 3, 10, 0, 0),    # Sunday (weekend)
    ]
    
    for test_time in test_times:
        # Convert to IST
        test_time_ist = test_time.replace(tzinfo=ZoneInfo('Asia/Kolkata'))
        
        # Manually check market hours
        weekday_check = test_time_ist.weekday() < 5
        market_open = dt.datetime.combine(test_time_ist.date(), dt.time(9, 15))
        market_close = dt.datetime.combine(test_time_ist.date(), dt.time(15, 30))
        time_check = market_open <= test_time_ist <= market_close
        
        is_open = weekday_check and time_check
        
        print(f"{test_time_ist.strftime('%A %H:%M')} → {'🟢 OPEN' if is_open else '🔴 CLOSED'}")

if __name__ == "__main__":
    print("🚀 THE-RED MACHINE - Market Hours Test")
    
    # Test current market hours
    market_open = test_market_hours()
    
    # Simulate different scenarios
    simulate_trading_hours()
    
    print(f"\n" + "=" * 50)
    print("📋 Test Summary")
    print("=" * 50)
    
    if market_open:
        print("🟢 Ready to start trading - Market is OPEN")
        print("   Run: start_trading_during_market_hours.bat")
    else:
        print("🔴 Market is CLOSED - System will wait")
        print("   Use Task Scheduler for automatic startup")
    
    print(f"\n💡 Check MARKET_HOURS_SETUP.md for detailed instructions")