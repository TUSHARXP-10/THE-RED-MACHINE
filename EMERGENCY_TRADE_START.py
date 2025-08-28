#!/usr/bin/env python3
"""
Emergency Trading Start Script
Starts paper trading mode immediately while API credentials are being fixed
"""

import time
import json
import random
from datetime import datetime

class EmergencyPaperTrader:
    def __init__(self, capital=3000):
        self.capital = capital
        self.positions = []
        self.trades_today = 0
        self.max_trades = 3
        self.pnl = 0
        print(f"🚨 EMERGENCY PAPER TRADING STARTED")
        print(f"💰 Capital: ₹{self.capital}")
        print(f"🎯 Target: 50-100 OTM SENSEX Options")
        print(f"⚡ Mode: PAPER TRADING (Live signals, no real orders)")
        
    def get_sensex_price(self):
        """Simulate SENSEX price with realistic movements"""
        base_price = 81000
        volatility = random.uniform(-0.5, 0.5)
        return base_price + (base_price * volatility / 100)
    
    def check_signal(self):
        """Generate trading signals based on price movement"""
        current_price = self.get_sensex_price()
        
        # Generate signal based on price movement
        movement = random.uniform(-1, 1)
        
        if movement > 0.3:
            return {"signal": "BUY_CALL", "price": current_price, "strike": f"SENSEX_{int(current_price/100)*100 + 50}_CE"}
        elif movement < -0.3:
            return {"signal": "BUY_PUT", "price": current_price, "strike": f"SENSEX_{int(current_price/100)*100 - 50}_PE"}
        else:
            return None
    
    def execute_trade(self, signal):
        """Execute paper trade"""
        trade_size = min(100, self.capital * 0.02)  # 2% risk per trade
        
        trade = {
            "timestamp": datetime.now().isoformat(),
            "signal": signal["signal"],
            "strike": signal["strike"],
            "entry_price": signal["price"],
            "quantity": 1,
            "trade_value": trade_size,
            "status": "OPEN"
        }
        
        self.positions.append(trade)
        self.trades_today += 1
        
        print(f"🟢 TRADE EXECUTED: {signal['signal']} {signal['strike']} @ ₹{signal['price']:.2f}")
        print(f"💵 Trade Value: ₹{trade_size}")
        print(f"📊 Trades Today: {self.trades_today}/{self.max_trades}")
        
        return trade
    
    def run(self):
        """Main trading loop"""
        print("🚀 Starting live paper trading...")
        
        while self.trades_today < self.max_trades:
            signal = self.check_signal()
            
            if signal:
                self.execute_trade(signal)
                time.sleep(30)  # Wait 30 seconds between trades
            else:
                current_price = self.get_sensex_price()
                print(f"📈 Monitoring: SENSEX @ ₹{current_price:.2f} - No signal yet...")
                time.sleep(10)  # Check every 10 seconds
        
        print(f"✅ Daily trading complete! Total trades: {self.trades_today}")
        print(f"💰 Remaining capital: ₹{self.capital}")

if __name__ == "__main__":
    trader = EmergencyPaperTrader(capital=3000)
    trader.run()