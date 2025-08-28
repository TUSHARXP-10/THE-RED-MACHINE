import os
from dotenv import load_dotenv
from broker_interface import BrokerInterface

def test_broker_interface():
    """Test the broker interface functionality"""
    print("🔍 Testing Broker Interface")
    print("="*50)
    
    # Load environment variables
    load_dotenv()
    
    # Check if we're in paper trading mode
    paper_trading = os.getenv("PAPER_TRADING", "true").lower() == "true"
    mode = "Paper Trading" if paper_trading else "Live Trading"
    print(f"Mode: {mode}")
    
    try:
        # Initialize broker interface
        print("\n🔍 Initializing broker interface...")
        broker = BrokerInterface()
        print("✅ Broker interface initialized successfully")
        
        # Test getting trading signals
        print("\n🔍 Testing get_trading_signals...")
        signals = broker.get_trading_signals()
        print(f"Signals: {signals}")
        print("✅ Successfully retrieved trading signals")
        
        # Test getting market data
        print("\n🔍 Testing get_market_data...")
        market_data = broker.get_market_data("SENSEX")
        print(f"Market data: {market_data}")
        print("✅ Successfully retrieved market data")
        
        # Don't test order placement in live mode
        if paper_trading:
            # Test placing a test order
            print("\n🔍 Testing place_order (paper trading mode)...")
            order_result = broker.place_order(
                stock_code="TEST_2K",
                exchange="NSE",
                product="C",
                action="B",
                order_type="MKT",
                quantity=1,
                price=0,
                validity="DAY"
            )
            print(f"Order result: {order_result}")
            print("✅ Successfully placed test order")
        else:
            print("\n⚠️ Skipping order placement test in live trading mode")
        
        print("\n🎉 All tests passed! Broker interface is working correctly.")
        return True
    except Exception as e:
        print(f"\n❌ Error testing broker interface: {e}")
        print("Please check the error message and fix the issue.")
        return False

if __name__ == "__main__":
    test_broker_interface()