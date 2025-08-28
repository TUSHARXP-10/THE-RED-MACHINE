"""
Live Kite API Configuration for THE RED MACHINE
Configuration management for real-time trading
"""

import os
import json
from typing import Dict, List, Any
from datetime import datetime

class KiteLiveConfig:
    """Configuration manager for live Kite API integration"""
    
    def __init__(self):
        self.config_file = "kite_live_config.json"
        self.default_config = {
            "symbols": [
                "RELIANCE", "TCS", "HDFCBANK", "INFY", "ITC", "ICICIBANK",
                "SBIN", "BHARTIARTL", "HINDUNILVR", "LT", "KOTAKBANK",
                "AXISBANK", "MARUTI", "SUNPHARMA", "ULTRACEMCO", "WIPRO"
            ],
            "indices": ["NIFTY50", "BANKNIFTY"],
            "intervals": ["1minute", "5minute", "15minute", "1hour", "1day"],
            "risk_per_trade": 0.02,  # 2% risk per trade
            "max_positions": 5,
            "order_types": ["MARKET", "LIMIT", "SL", "SL-M"],
            "products": ["MIS", "CNC", "NRML"],
            "streaming_mode": "FULL",  # FULL, LTP, QUOTE
            "auto_reconnect": True,
            "max_reconnect_attempts": 5,
            "heartbeat_interval": 30,  # seconds
            "data_retention_hours": 24,
            "alert_thresholds": {
                "price_change_pct": 2.0,
                "volume_spike_ratio": 3.0,
                "oi_change_pct": 5.0
            }
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults for new keys
                for key, value in self.default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.default_config.copy()
        else:
            # Create default config file
            self.save_config(self.default_config)
            return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_symbols(self) -> List[str]:
        """Get list of symbols to trade"""
        return self.config.get("symbols", [])
    
    def get_indices(self) -> List[str]:
        """Get list of indices"""
        return self.config.get("indices", [])
    
    def get_all_instruments(self) -> List[str]:
        """Get combined list of symbols and indices"""
        return self.get_symbols() + self.get_indices()
    
    def get_risk_params(self) -> Dict[str, float]:
        """Get risk management parameters"""
        return {
            "risk_per_trade": self.config.get("risk_per_trade", 0.02),
            "max_positions": self.config.get("max_positions", 5)
        }
    
    def get_streaming_config(self) -> Dict[str, Any]:
        """Get streaming configuration"""
        return {
            "mode": self.config.get("streaming_mode", "FULL"),
            "auto_reconnect": self.config.get("auto_reconnect", True),
            "max_reconnect_attempts": self.config.get("max_reconnect_attempts", 5),
            "heartbeat_interval": self.config.get("heartbeat_interval", 30)
        }
    
    def add_symbol(self, symbol: str):
        """Add a new symbol to trading list"""
        symbols = self.get_symbols()
        if symbol.upper() not in symbols:
            symbols.append(symbol.upper())
            self.config["symbols"] = symbols
            self.save_config(self.config)
            print(f"Added {symbol} to trading symbols")
    
    def remove_symbol(self, symbol: str):
        """Remove a symbol from trading list"""
        symbols = self.get_symbols()
        if symbol.upper() in symbols:
            symbols.remove(symbol.upper())
            self.config["symbols"] = symbols
            self.save_config(self.config)
            print(f"Removed {symbol} from trading symbols")
    
    def update_risk_params(self, risk_per_trade: float = None, max_positions: int = None):
        """Update risk management parameters"""
        if risk_per_trade is not None:
            self.config["risk_per_trade"] = risk_per_trade
        if max_positions is not None:
            self.config["max_positions"] = max_positions
        self.save_config(self.config)
        print("Risk parameters updated")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        return {
            "total_symbols": len(self.get_symbols()),
            "total_indices": len(self.get_indices()),
            "risk_per_trade": self.config.get("risk_per_trade"),
            "max_positions": self.config.get("max_positions"),
            "streaming_mode": self.config.get("streaming_mode"),
            "config_file": self.config_file,
            "last_updated": datetime.now().isoformat()
        }
    
    def validate_environment(self) -> Dict[str, Any]:
        """Validate environment setup"""
        required_env_vars = [
            "KITE_API_KEY",
            "KITE_ACCESS_TOKEN",
            "ZERODHA_CLIENT_ID"
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        return {
            "environment_valid": len(missing_vars) == 0,
            "missing_variables": missing_vars,
            "config_file_exists": os.path.exists(self.config_file),
            "timestamp": datetime.now().isoformat()
        }

# Global configuration instance
config = KiteLiveConfig()

def setup_kite_credentials():
    """Interactive setup for Kite API credentials"""
    print("🔧 Kite API Credentials Setup")
    print("=" * 50)
    
    print("\n📋 Required Information:")
    print("1. KITE_API_KEY - Your Zerodha API key")
    print("2. KITE_ACCESS_TOKEN - Your access token (expires daily)")
    print("3. ZERODHA_CLIENT_ID - Your Zerodha client ID")
    
    print("\n💡 To get these credentials:")
    print("1. Login to https://kite.trade")
    print("2. Go to 'My Apps' section")
    print("3. Create a new app or use existing one")
    print("4. Generate access token using the login flow")
    
    print("\n📝 Setting up .env file...")
    
    api_key = input("Enter KITE_API_KEY: ").strip()
    access_token = input("Enter KITE_ACCESS_TOKEN: ").strip()
    client_id = input("Enter ZERODHA_CLIENT_ID: ").strip()
    
    env_content = f"""# Kite API Credentials
KITE_API_KEY={api_key}
KITE_ACCESS_TOKEN={access_token}
ZERODHA_CLIENT_ID={client_id}

# Optional: Kite API Secret (for generating access tokens)
KITE_API_SECRET=your_api_secret_here
"""
    
    with open('.env', 'a') as f:
        f.write('\n\n' + env_content)
    
    print("✅ .env file updated with Kite API credentials!")
    print("\n🔄 To generate access tokens, run: python fix_kite_session.py")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "setup":
            setup_kite_credentials()
        elif sys.argv[1] == "summary":
            print(json.dumps(config.get_config_summary(), indent=2))
        elif sys.argv[1] == "validate":
            print(json.dumps(config.validate_environment(), indent=2))
        elif sys.argv[1] == "add" and len(sys.argv) > 2:
            config.add_symbol(sys.argv[2])
        elif sys.argv[1] == "remove" and len(sys.argv) > 2:
            config.remove_symbol(sys.argv[2])
        else:
            print("Usage:")
            print("  python kite_live_config.py setup     - Setup credentials")
            print("  python kite_live_config.py summary   - Show config summary")
            print("  python kite_live_config.py validate  - Validate environment")
            print("  python kite_live_config.py add SYMBOL - Add trading symbol")
            print("  python kite_live_config.py remove SYMBOL - Remove trading symbol")
    else:
        print("Kite Live Configuration Summary:")
        print(json.dumps(config.get_config_summary(), indent=2))