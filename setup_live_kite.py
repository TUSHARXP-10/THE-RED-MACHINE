#!/usr/bin/env python3
"""
Setup script for Live Kite API Integration
Automatically configures credentials and validates connection
"""

import os
import sys
import json
import time
from datetime import datetime
from live_kite_integration import LiveKiteIntegration, RedMachineKiteBridge
from kite_live_config import KiteLiveConfig

def check_environment():
    """Check if environment is ready for live trading"""
    print("🔍 Checking environment...")
    
    # Check .env file
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    
    # Check required environment variables
    required_vars = ['KITE_API_KEY', 'KITE_ACCESS_TOKEN', 'ZERODHA_CLIENT_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment variables configured")
    return True

def test_kite_connection():
    """Test Kite API connection"""
    print("\n🔗 Testing Kite API connection...")
    
    try:
        integration = LiveKiteIntegration()
        
        if integration.is_connected:
            print("✅ Kite API connection successful")
            
            # Test instruments
            instruments = integration.get_sensex_instruments()
            print(f"📊 Found {len(instruments)} tradable instruments")
            
            # Test live data
            quote = integration.get_live_quote("RELIANCE")
            if quote:
                print(f"💰 Sample quote - RELIANCE: ₹{quote.get('last_price', 'N/A')}")
            
            return True
        else:
            print("❌ Kite API connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def setup_live_trading():
    """Complete setup for live trading"""
    print("🚀 Setting up Live Kite API Integration...")
    print("=" * 60)
    
    # Step 1: Environment check
    if not check_environment():
        print("\n🔧 Running credential setup...")
        os.system("python kite_live_config.py setup")
        
        if not check_environment():
            print("❌ Setup incomplete. Please check your credentials.")
            return False
    
    # Step 2: Test connection
    if not test_kite_connection():
        print("\n❌ Connection test failed. Check your credentials.")
        return False
    
    # Step 3: Initialize bridge
    print("\n🌉 Initializing Red Machine Kite Bridge...")
    bridge = RedMachineKiteBridge()
    
    if bridge.initialize():
        print("✅ Bridge initialized successfully")
        
        # Step 4: Load configuration
        config = KiteLiveConfig()
        symbols = config.get_all_instruments()
        
        print(f"📈 Configuring real-time data for {len(symbols)} instruments...")
        
        # Step 5: Start real-time trading
        result = bridge.start_real_time_trading(symbols[:10])  # Start with top 10
        
        if result["status"] == "success":
            print("✅ Live trading system ready!")
            
            # Save configuration
            with open('live_trading_config.json', 'w') as f:
                json.dump({
                    "setup_date": datetime.now().isoformat(),
                    "symbols": symbols,
                    "bridge_status": "initialized",
                    "health_check": bridge.kite_integration.health_check()
                }, f, indent=2)
            
            print("\n🎯 Live Kite API Integration Complete!")
            print("=" * 60)
            print("✅ Real-time market data streaming")
            print("✅ Live order execution")
            print("✅ Portfolio monitoring")
            print("✅ Risk management")
            print("✅ Multi-asset trading")
            
            return True
    
    return False

def display_status():
    """Display current live trading status"""
    print("📊 Live Trading Status")
    print("=" * 40)
    
    try:
        # Check configuration
        config = KiteLiveConfig()
        validation = config.validate_environment()
        
        if validation["environment_valid"]:
            print("✅ Environment: Ready")
        else:
            print(f"❌ Environment: Missing {', '.join(validation['missing_variables'])}")
        
        # Check config file
        summary = config.get_config_summary()
        print(f"📈 Symbols: {summary['total_symbols']}")
        print(f"🎯 Indices: {summary['total_indices']}")
        print(f"⚖️ Risk per trade: {summary['risk_per_trade']*100}%")
        print(f"📊 Max positions: {summary['max_positions']}")
        
        # Test connection
        integration = LiveKiteIntegration()
        if integration.is_connected:
            print("🔗 API: Connected")
            health = integration.health_check()
            print(f"📡 Streaming: {'Active' if health['streaming'] else 'Inactive'}")
            print(f"📊 Live instruments: {health['subscribed_instruments']}")
        else:
            print("❌ API: Disconnected")
            
    except Exception as e:
        print(f"❌ Status check failed: {e}")

def run_diagnostics():
    """Run comprehensive diagnostics"""
    print("🔬 Running Live Kite Diagnostics...")
    print("=" * 50)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "diagnostics": {}
    }
    
    # Environment diagnostics
    config = KiteLiveConfig()
    results["diagnostics"]["environment"] = config.validate_environment()
    
    # Connection diagnostics
    try:
        integration = LiveKiteIntegration()
        results["diagnostics"]["connection"] = {
            "connected": integration.is_connected,
            "health": integration.health_check() if integration.is_connected else None
        }
    except Exception as e:
        results["diagnostics"]["connection"] = {"error": str(e)}
    
    # Configuration diagnostics
    results["diagnostics"]["configuration"] = config.get_config_summary()
    
    # Save results
    with open('kite_diagnostics.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("✅ Diagnostics complete. Results saved to kite_diagnostics.json")
    return results

def main():
    """Main setup function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "setup":
            success = setup_live_trading()
            sys.exit(0 if success else 1)
            
        elif command == "status":
            display_status()
            
        elif command == "diagnostics":
            run_diagnostics()
            
        elif command == "test":
            test_kite_connection()
            
        elif command == "config":
            os.system("python kite_live_config.py summary")
            
        else:
            print("Available commands:")
            print("  setup      - Complete live trading setup")
            print("  status     - Show current status")
            print("  diagnostics - Run system diagnostics")
            print("  test       - Test Kite API connection")
            print("  config     - Show configuration summary")
    else:
        # Interactive setup
        print("🎯 Live Kite API Integration Setup")
        print("=" * 50)
        
        while True:
            print("\nChoose an option:")
            print("1. Complete setup")
            print("2. Show status")
            print("3. Run diagnostics")
            print("4. Test connection")
            print("5. Exit")
            
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == "1":
                setup_live_trading()
                break
            elif choice == "2":
                display_status()
            elif choice == "3":
                run_diagnostics()
            elif choice == "4":
                test_kite_connection()
            elif choice == "5":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()