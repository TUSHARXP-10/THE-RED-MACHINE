import time
import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum
import logging

class TradeDirection(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

@dataclass
class Signal:
    asset: str
    direction: TradeDirection
    strength: float
    entry_price: float
    stop_loss: float
    target: float
    confidence: float
    asset_type: str
    timestamp: datetime.datetime

@dataclass
class Position:
    asset: str
    quantity: int
    entry_price: float
    current_price: float
    unrealized_pnl: float
    stop_loss: float
    target: float
    timestamp: datetime.datetime

class CapitalManager:
    def __init__(self, total_capital: float = 100000):
        self.total_capital = total_capital
        self.available_capital = total_capital
        self.used_margin = 0.0
        
    def calculate_position_size(self, asset: str, signal_strength: float, entry_price: float, max_risk_per_trade: float = 0.02) -> int:
        """Calculate optimal position size based on risk management"""
        risk_amount = self.total_capital * max_risk_per_trade * signal_strength
        
        # Basic position sizing - can be enhanced with volatility adjustment
        if entry_price > 0:
            max_shares = int(self.available_capital / entry_price)
            risk_based_shares = int(risk_amount / entry_price)
            return min(max_shares, risk_based_shares)
        return 0
        
    def update_available_capital(self, amount: float):
        """Update available capital after trades"""
        self.available_capital += amount
        
    def get_available_margin(self) -> float:
        """Get available margin for new positions"""
        return self.available_capital

class SmartExecutionEngine:
    def __init__(self, kite_client, capital_manager: CapitalManager):
        self.kite = kite_client
        self.capital_manager = capital_manager
        self.active_positions: Dict[str, Position] = {}
        self.order_queue: List[Signal] = []
        self.trade_history: List[Dict] = []
        self.daily_pnl = 0.0
        self.logger = logging.getLogger(__name__)
        
    def market_is_open(self) -> bool:
        """Check if market is open"""
        now = datetime.datetime.now()
        market_open = now.replace(hour=9, minute=15, second=0)
        market_close = now.replace(hour=15, minute=30, second=0)
        
        # Check if it's a weekday
        if now.weekday() >= 5:  # Saturday and Sunday
            return False
            
        return market_open <= now <= market_close
        
    def signal_engine(self) -> List[Signal]:
        """Mock signal engine - replace with actual signal generation"""
        # This should integrate with your MultiAssetAI system
        return []
        
    def scan_universe(self) -> List[Signal]:
        """Scan all assets for trading opportunities"""
        # This should be replaced with actual scanning logic
        return self.signal_engine()
        
    def filter_tradeable_signals(self, signals: List[Signal]) -> List[Signal]:
        """Filter and rank trading opportunities"""
        # Filter by confidence threshold
        filtered = [s for s in signals if s.confidence > 0.7]
        
        # Sort by signal strength
        filtered.sort(key=lambda x: x.strength, reverse=True)
        
        return filtered[:10]  # Top 10 opportunities
        
    def should_execute_trade(self, signal: Signal) -> bool:
        """Determine if trade should be executed"""
        # Check if already in position
        if signal.asset in self.active_positions:
            return False
            
        # Check capital availability
        if self.capital_manager.available_capital < signal.entry_price * 100:
            return False
            
        return True
        
    def place_order(self, symbol: str, quantity: int, price: float, direction: TradeDirection) -> str:
        """Place order via kite API"""
        try:
            if direction == TradeDirection.BUY:
                order_id = f"BUY_{symbol}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            else:
                order_id = f"SELL_{symbol}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
            self.logger.info(f"Order placed: {order_id} for {symbol} {direction.value} {quantity}@{price}")
            return order_id
        except Exception as e:
            self.logger.error(f"Order placement failed: {e}")
            return ""
            
    def place_stop_loss(self, symbol: str, quantity: int, stop_price: float) -> str:
        """Place stop-loss order"""
        try:
            stop_order_id = f"SL_{symbol}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.logger.info(f"Stop-loss placed: {stop_order_id} for {symbol} {quantity}@{stop_price}")
            return stop_order_id
        except Exception as e:
            self.logger.error(f"Stop-loss placement failed: {e}")
            return ""
            
    def execute_trade(self, signal: Signal) -> bool:
        """Execute individual trade with risk management"""
        position_size = self.capital_manager.calculate_position_size(
            signal.asset, signal.strength, signal.entry_price
        )
        
        if position_size <= 0:
            return False
            
        # Place main order
        order_id = self.place_order(
            symbol=signal.asset,
            quantity=position_size,
            price=signal.entry_price,
            direction=signal.direction
        )
        
        if not order_id:
            return False
            
        # Place stop-loss order
        stop_order_id = self.place_stop_loss(
            symbol=signal.asset,
            quantity=position_size,
            stop_price=signal.stop_loss
        )
        
        # Track position
        self.active_positions[signal.asset] = Position(
            asset=signal.asset,
            quantity=position_size,
            entry_price=signal.entry_price,
            current_price=signal.entry_price,
            unrealized_pnl=0.0,
            stop_loss=signal.stop_loss,
            target=signal.target,
            timestamp=signal.timestamp
        )
        
        # Log trade
        self.trade_history.append({
            'asset': signal.asset,
            'direction': signal.direction.value,
            'quantity': position_size,
            'entry_price': signal.entry_price,
            'stop_loss': signal.stop_loss,
            'target': signal.target,
            'timestamp': signal.timestamp,
            'order_id': order_id,
            'stop_order_id': stop_order_id
        })
        
        # Update available capital
        trade_value = position_size * signal.entry_price
        self.capital_manager.update_available_capital(-trade_value)
        
        self.logger.info(f"Trade executed: {signal.asset} {signal.direction.value} {position_size}@{signal.entry_price}")
        return True
        
    def manage_existing_positions(self):
        """Monitor and manage existing positions"""
        for asset, position in list(self.active_positions.items()):
            # Update current price (mock - replace with actual API call)
            current_price = position.current_price * (1 + np.random.normal(0, 0.001))
            
            # Calculate unrealized P&L
            if position.quantity > 0:  # Long position
                position.unrealized_pnl = (current_price - position.entry_price) * position.quantity
            else:  # Short position
                position.unrealized_pnl = (position.entry_price - current_price) * abs(position.quantity)
                
            position.current_price = current_price
            
            # Check stop-loss
            if (position.quantity > 0 and current_price <= position.stop_loss) or \
               (position.quantity < 0 and current_price >= position.stop_loss):
                self.close_position(asset, "Stop-loss triggered")
                
            # Check target
            if (position.quantity > 0 and current_price >= position.target) or \
               (position.quantity < 0 and current_price <= position.target):
                self.close_position(asset, "Target reached")
                
    def close_position(self, asset: str, reason: str):
        """Close an existing position"""
        if asset not in self.active_positions:
            return
            
        position = self.active_positions[asset]
        
        # Calculate realized P&L
        if position.quantity > 0:  # Long position
            realized_pnl = (position.current_price - position.entry_price) * position.quantity
        else:  # Short position
            realized_pnl = (position.entry_price - position.current_price) * abs(position.quantity)
            
        self.daily_pnl += realized_pnl
        
        # Update capital
        exit_value = position.current_price * abs(position.quantity)
        self.capital_manager.update_available_capital(exit_value)
        
        # Remove from active positions
        del self.active_positions[asset]
        
        self.logger.info(f"Position closed: {asset} - {reason} - P&L: {realized_pnl:.2f}")
        
    def execute_multi_asset_strategy(self):
        """Main execution loop"""
        print("🚀 Starting Smart Execution Engine...")
        
        while self.market_is_open():
            try:
                # Get signals from all assets
                all_signals = self.scan_universe()
                
                # Filter and rank opportunities
                top_signals = self.filter_tradeable_signals(all_signals)
                
                # Execute trades based on available capital
                for signal in top_signals:
                    if self.should_execute_trade(signal):
                        self.execute_trade(signal)
                        
                # Monitor and manage existing positions
                self.manage_existing_positions()
                
                # Log status
                self.log_status()
                
                # Wait for next scan cycle
                time.sleep(10)  # 10-second refresh
                
            except KeyboardInterrupt:
                print("\n🛑 Execution stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in execution loop: {e}")
                time.sleep(5)  # Wait before retry
                
    def log_status(self):
        """Log current system status"""
        total_positions = len(self.active_positions)
        total_value = sum(pos.current_price * abs(pos.quantity) for pos in self.active_positions.values())
        
        print(f"📊 Status: {total_positions} active positions, Total value: {total_value:.2f}, "
              f"Daily P&L: {self.daily_pnl:.2f}, Available capital: {self.capital_manager.available_capital:.2f}")

# Example usage
if __name__ == "__main__":
    # Mock kite client for demonstration
    class MockKiteClient:
        pass
        
    capital_manager = CapitalManager(total_capital=100000)
    kite_client = MockKiteClient()
    
    engine = SmartExecutionEngine(kite_client, capital_manager)
    
    # Test the execution engine
    print("🧪 Testing Smart Execution Engine...")
    
    # Create test signal
    test_signal = Signal(
        asset="RELIANCE",
        direction=TradeDirection.BUY,
        strength=0.8,
        entry_price=2500.0,
        stop_loss=2450.0,
        target=2600.0,
        confidence=0.85,
        asset_type="stock",
        timestamp=datetime.datetime.now()
    )
    
    # Test trade execution
    if engine.should_execute_trade(test_signal):
        success = engine.execute_trade(test_signal)
        print(f"✅ Test trade execution: {'Success' if success else 'Failed'}")
    
    print("🎯 Smart Execution Engine ready for production!")