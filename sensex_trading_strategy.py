import datetime
import numpy as np
from typing import Dict, List, Optional, Tuple

class RealSENSEXStrategy:
    """
    Real-time SENSEX scalping strategy based on price movement and volatility
    """
    
    def __init__(self):
        self.previous_price = None
        self.price_history = []
        self.volume_history = []
        self.last_signal = None
        self.signal_count = 0
        
        # Strategy parameters
        # SENSEX-appropriate thresholds (different from NIFTY)
        self.price_change_threshold = 400      # 400 points for SENSEX vs 100 for NIFTY
        self.volatility_threshold = 1.0        # 1% for SENSEX movements
        self.support_levels = [80000, 80500, 81000]  # SENSEX levels
        self.resistance_levels = [81500, 82000, 82500]

        self.min_price_change = 0.1  # 0.1% minimum price change
        self.max_volatility = 5.0    # 5% maximum volatility
        self.min_volume = 1000000    # Minimum volume threshold
        self.lookback_period = 5     # Periods for volatility calculation
        
    def calculate_volatility(self, prices: List[float]) -> float:
        """Calculate price volatility over lookback period"""
        if len(prices) < 2:
            return 0.0
        
        returns = [(prices[i] - prices[i-1]) / prices[i-1] * 100 
                  for i in range(1, len(prices))]
        return np.std(returns) if returns else 0.0
    
    def calculate_price_change(self, current_price: float, previous_price: float) -> float:
        """Calculate percentage price change"""
        if previous_price is None or previous_price == 0:
            return 0.0
        return (current_price - previous_price) / previous_price * 100
    
    def evaluate_signal(self, market_data: Dict) -> Tuple[str, float, Dict]:
        """
        Evaluate trading signal based on market data
        
        Args:
            market_data: Dict with keys: 'current_price', 'volume', 'timestamp'
            
        Returns:
            Tuple of (signal, confidence, metadata)
        """
        current_price = market_data.get('current_price', 0)
        current_volume = market_data.get('volume', 0)
        
        if current_price <= 0:
            return "NO_SIGNAL", 0.0, {"reason": "Invalid price"}
        
        # Add to price history
        self.price_history.append(current_price)
        self.volume_history.append(current_volume)
        
        # Keep only recent data
        if len(self.price_history) > self.lookback_period + 1:
            self.price_history.pop(0)
            self.volume_history.pop(0)
        
        # Need at least 2 data points for analysis
        if len(self.price_history) < 2:
            return "NO_SIGNAL", 0.0, {"reason": "Insufficient data"}
        
        # Calculate metrics
        price_change = self.calculate_price_change(current_price, self.previous_price)
        volatility = self.calculate_volatility(self.price_history)
        avg_volume = np.mean(self.volume_history) if self.volume_history else 0
        
        # Generate signal based on conditions
        signal = "NO_SIGNAL"
        confidence = 0.0
        metadata = {
            'current_price': current_price,
            'price_change': price_change,
            'volatility': volatility,
            'volume': current_volume,
            'avg_volume': avg_volume
        }
        
        # Check trading conditions
        # Incorporate SENSEX-specific thresholds
        if volatility > self.volatility_threshold:
            signal = "NO_TRADE"
            confidence = 1.0
            metadata['reason'] = "High volatility"
        elif current_volume < self.min_volume:
            signal = "NO_TRADE"
            confidence = 0.8
            metadata['reason'] = "Low volume"
        elif abs(current_price - self.previous_price) >= self.price_change_threshold:
            if (current_price - self.previous_price) > 0:
                signal = "BUY_CALL"
                confidence = min(abs(current_price - self.previous_price) / self.price_change_threshold, 1.0)  # Scale confidence
                metadata['reason'] = f"Upward momentum: {current_price - self.previous_price:.2f} points"
            else:
                signal = "BUY_PUT"
                confidence = min(abs(current_price - self.previous_price) / self.price_change_threshold, 1.0)  # Scale confidence
                metadata['reason'] = f"Downward momentum: {current_price - self.previous_price:.2f} points"
        
        # Update tracking
        self.previous_price = current_price
        if signal in ["BUY_CALL", "BUY_PUT"]:
            self.signal_count += 1
            self.last_signal = {
                'signal': signal,
                'price': current_price,
                'timestamp': market_data.get('timestamp'),
                'confidence': confidence
            }
        
        return signal, confidence, metadata
    
    def get_strategy_status(self) -> Dict:
        """Get current strategy status"""
        return {
            'total_signals': self.signal_count,
            'last_signal': self.last_signal,
            'price_history_length': len(self.price_history),
            'current_price': self.price_history[-1] if self.price_history else None
        }

class SENSEXSignalGenerator:
    """
    Signal generator that uses RealSENSEXStrategy for live trading
    """
    
    def __init__(self):
        self.strategy = RealSENSEXStrategy()
        self.signals = []
        
    def process_market_data(self, market_data: Dict) -> Dict:
        """Process market data and generate trading signals"""
        signal, confidence, metadata = self.strategy.evaluate_signal(market_data)
        
        result = {
            'symbol': market_data.get('symbol', 'SENSEX'),
            'timestamp': market_data.get('timestamp'),
            'current_price': market_data.get('current_price'),
            'signal': signal,
            'confidence': confidence,
            'metadata': metadata
        }
        
        if signal in ["BUY_CALL", "BUY_PUT"]:
            self.signals.append(result)
            
        return result
    
    def get_recent_signals(self, count: int = 10) -> List[Dict]:
        """Get recent trading signals"""
        return self.signals[-count:] if len(self.signals) > count else self.signals

# Example usage for testing
if __name__ == "__main__":
    import random
    
    # Test the strategy with simulated data
    generator = SENSEXSignalGenerator()
    
    # Simulate realistic SENSEX price movements
    base_price = 81000
    prices = [base_price + random.randint(-200, 200) for _ in range(20)]
    
    print("Testing Real SENSEX Strategy:")
    print("=" * 50)
    
    for i, price in enumerate(prices):
        market_data = {
            'symbol': 'SENSEX',
            'current_price': price,
            'volume': 1000000 + random.randint(-100000, 100000),
            'timestamp': datetime.now().isoformat()
        }
        
        result = generator.process_market_data(market_data)
        
        if result['signal'] in ["BUY_CALL", "BUY_PUT"]:
            print(f"🚨 SIGNAL: {result['signal']} @ ₹{price:.2f}")
            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Reason: {result['metadata']['reason']}")
            print("-" * 30)