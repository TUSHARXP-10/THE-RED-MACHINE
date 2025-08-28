import os
from dotenv import load_dotenv
from breeze_connector import BreezeConnector

def test_breeze_connector():
    """Test the Breeze connector functionality"""
    print("🔍 Testing Breeze Connector")
    print("="*50)
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Initialize Breeze connector
        print("\n🔍 Initializing Breeze connector...")
        connector = BreezeConnector()
        print("✅ Breeze connector initialized successfully")
        
        # Test connection
        print("\n🔍 Testing connection...")
        connection_result = connector.connect()
        if connection_result:
            print("✅ Successfully connected to Breeze API")
        else:
            print("❌ Failed to connect to Breeze API")
            print("Please run fix_session_immediately.py to get a new session token")
            return False
        
        # Test getting market data
        print("\n🔍 Testing get_market_data...")
        market_data = connector.get_market_data("SENSEX")
        print(f"Market data: {market_data}")
        print("✅ Successfully retrieved market data")
        
        print("\n🎉 All tests passed! Breeze connector is working correctly.")
        return True
    except Exception as e:
        print(f"\n❌ Error testing Breeze connector: {e}")
        print("Please check the error message and fix the issue.")
        return False

if __name__ == "__main__":
    test_breeze_connector()