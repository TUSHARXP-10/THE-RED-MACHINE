# Breeze API Connection Test Script

try:
    from breeze_integration import EnhancedBreezeTrading
    
    print("\n🔍 Testing Breeze API Connection...\n")
    
    # Initialize the trading object
    trader = EnhancedBreezeTrading()
    
    # Test connection
    if trader.connect_breeze():
        print("✅ BREEZE READY! Connection successful.")
        
        # Get available funds
        try:
            funds = trader.get_available_funds()
            print(f"💰 Available Funds: ₹{funds}")
        except Exception as e:
            print(f"⚠️ Could not retrieve funds: {str(e)}")
            
        # Get holdings
        try:
            holdings = trader.get_holdings()
            if holdings:
                print(f"📊 Current Holdings: {len(holdings)} positions")
                for holding in holdings[:3]:  # Show first 3 holdings
                    print(f"   - {holding['symbol']}: {holding['quantity']} @ ₹{holding['average_price']}")
                if len(holdings) > 3:
                    print(f"   - ... and {len(holdings) - 3} more positions")
            else:
                print("📊 No current holdings")
        except Exception as e:
            print(f"⚠️ Could not retrieve holdings: {str(e)}")
    else:
        print("❌ Breeze API connection failed!")
        print("   Please check your API credentials in the .env file")
        
except ImportError:
    print("❌ Could not import EnhancedBreezeTrading from breeze_integration")
    print("   Please check if the module exists and is properly installed")
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\nTest completed.")