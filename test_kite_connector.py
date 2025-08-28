import os
import sys
from kite_connector import KiteConnector

def test_kite_connection():
    """Test the KiteConnector connection"""
    print("\n🔍 Testing Kite Connector")
    print("========================\n")
    
    # Initialize KiteConnector
    print("Initializing KiteConnector...")
    connector = KiteConnector()
    
    # Test connection
    print("\nTesting connection to Kite API...")
    if connector.connect():
        print("\n✅ Connection successful!")
        
        # Test market data retrieval
        print("\nTesting market data retrieval...")
        try:
            # Try to get SENSEX data
            sensex_data = connector.get_market_data("SENSEX")
            if sensex_data:
                print(f"✅ Successfully retrieved SENSEX data:")
                print(f"   Current price: {sensex_data['current_price']}")
                print(f"   Timestamp: {sensex_data['timestamp']}")
            else:
                print("❌ Failed to retrieve SENSEX data")
                
            # Try to get RELIANCE data
            reliance_data = connector.get_market_data("RELIANCE", "NSE")
            if reliance_data:
                print(f"\n✅ Successfully retrieved RELIANCE data:")
                print(f"   Current price: {reliance_data['current_price']}")
                print(f"   Volume: {reliance_data['volume']}")
                print(f"   Timestamp: {reliance_data['timestamp']}")
            else:
                print("❌ Failed to retrieve RELIANCE data")
        except Exception as e:
            print(f"❌ Error retrieving market data: {e}")
        
        # Test positions retrieval
        print("\nTesting positions retrieval...")
        try:
            positions = connector.get_positions()
            if positions is not None:
                print(f"✅ Successfully retrieved positions")
                if positions:
                    print(f"   Number of positions: {len(positions)}")
                else:
                    print("   No positions found")
            else:
                print("❌ Failed to retrieve positions")
        except Exception as e:
            print(f"❌ Error retrieving positions: {e}")
        
        # Test margins retrieval
        print("\nTesting margins retrieval...")
        try:
            margins = connector.get_margins()
            if margins is not None:
                print(f"✅ Successfully retrieved margins")
                if 'equity' in margins:
                    print(f"   Available margin: {margins['equity'].get('available', {}).get('cash', 0)}")
            else:
                print("❌ Failed to retrieve margins")
        except Exception as e:
            print(f"❌ Error retrieving margins: {e}")
        
        print("\n✅ All tests completed!")
        return True
    else:
        print("\n❌ Connection failed!")
        print("Please check your Kite API credentials and access token.")
        print("Run 'python fix_kite_session.py' to fix session issues.")
        return False

def main():
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ Error: .env file not found")
        print("Please create a .env file with your Kite API credentials:")
        print("KITE_API_KEY, KITE_API_SECRET, KITE_ACCESS_TOKEN, ZERODHA_CLIENT_ID")
        return
    
    # Run the test
    test_result = test_kite_connection()
    
    # Exit with appropriate status code
    if test_result:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()