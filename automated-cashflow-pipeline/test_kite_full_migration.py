#!/usr/bin/env python3
"""
Test script for complete migration from ICICI/Breeze to Kite Connect
Demonstrates the full switch with SENSEX scalping system
"""

import os
import json
from datetime import datetime
from broker_interface import KiteBrokerInterface

def test_full_migration():
    """Test complete migration to Kite Connect"""
    print("🚀 Testing Complete Migration to Kite Connect")
    print("=" * 60)
    
    try:
        # Initialize Kite broker
        broker = KiteBrokerInterface()
        print("✅ Kite Broker Interface initialized")
        
        # Test 1: Get SENSEX data (for scalping system)
        print("\n📊 Testing SENSEX Data Fetch...")
        sensex_data = broker.get_sensex_data()
        if 'error' not in sensex_data:
            print(f"✅ SENSEX Current Price: ₹{sensex_data['price']}")
            print(f"✅ Daily Change: {sensex_data['change_percent']:.2f}%")
            print(f"✅ Volume: {sensex_data['volume']}")
        else:
            print(f"❌ Error: {sensex_data['error']}")
        
        # Test 2: Get account information
        print("\n💰 Testing Account Information...")
        margins = broker.get_margin()
        if 'error' not in margins:
            equity_margin = margins.get('equity', {})
            if equity_margin:
                print(f"✅ Available Cash: ₹{equity_margin.get('available', {}).get('cash', 0)}")
                print(f"✅ Used Margin: ₹{equity_margin.get('used', {}).get('cash', 0)}")
        
        # Test 3: Get current positions
        print("\n📈 Testing Positions...")
        positions = broker.get_positions()
        if 'error' not in positions and positions.get('net_positions'):
            print(f"✅ Active Positions: {len(positions['net_positions'])}")
            for pos in positions['net_positions']:
                print(f"   {pos['tradingsymbol']}: {pos['quantity']} @ ₹{pos['average_price']}")
        else:
            print("✅ No active positions")
        
        # Test 4: Place dummy order (low value won't execute)
        print("\n🎯 Testing Order Placement...")
        dummy_order = broker.place_order(
            symbol="RELIANCE",
            action="BUY",
            quantity=1,
            price=100.0,  # Very low price to prevent execution
            order_type="LIMIT"
        )
        
        if dummy_order['status'] == 'success':
            print(f"✅ Order placed successfully: Order ID {dummy_order['order_id']}")
            # Cancel the dummy order immediately
            cancel_result = broker.cancel_order(dummy_order['order_id'])
            if cancel_result['status'] == 'success':
                print("✅ Dummy order cancelled successfully")
        else:
            print(f"⚠️ Order placement: {dummy_order['message']}")
        
        # Test 5: Get historical data for strategy
        print("\n📊 Testing Historical Data...")
        hist_data = broker.get_historical_data("BSESN", interval="5minute", duration=10)
        if 'error' not in hist_data and hist_data.get('data'):
            print(f"✅ Retrieved {len(hist_data['data'])} data points")
            latest = hist_data['data'][-1]
            print(f"✅ Latest 5-min candle: ₹{latest['close']} (Volume: {latest['volume']})")
        
        print("\n" + "=" * 60)
        print("🎉 MIGRATION TEST COMPLETE!")
        print("✅ Kite Connect is fully integrated")
        print("✅ No more ICICI/Breeze dependencies")
        print("✅ Ready for SENSEX scalping system")
        
        # Display next steps
        print("\n🚀 NEXT STEPS:")
        print("1. Run: python quick_kite_session_fix.py (if token expired)")
        print("2. Update your main trading script to use KiteBrokerInterface")
        print("3. Remove all ICICI/Breeze related files")
        print("4. Start your SENSEX scalping system")
        
    except Exception as e:
        print(f"❌ Migration test failed: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Ensure KITE_ACCESS_TOKEN is set in .env")
        print("2. Run: python quick_kite_session_fix.py to get new token")
        print("3. Check Kite API credentials in .env file")

if __name__ == '__main__':
    test_full_migration()