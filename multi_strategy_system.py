"""
Multi-Strategy Trading System
Implements 3-tier signal generation to prevent signal starvation
"""

import numpy as np
from datetime import datetime, time
import logging
from morning_scalper import HighConfidenceScalper

class MultiStrategySystem:
    """
    Multi-strategy system that runs conservative, moderate, and aggressive
    strategies simultaneously to ensure signal generation
    """
    
    def __init__(self, kite_api_key, kite_api_secret):
        self.conservative = HighConfidenceScalper(kite_api_key, kite_api_secret)
        self.moderate = ModerateConfidenceScalper(kite_api_key, kite_api_secret)
        self.aggressive = ForceTradeScalper(kite_api_key, kite_api_secret)
        
        # Performance tracking
        self.strategy_performance = {
            'conservative': {'wins': 0, 'losses': 0, 'total': 0},
            'moderate': {'wins': 0, 'losses': 0, 'total': 0},
            'aggressive': {'wins': 0, 'losses': 0, 'total': 0}
        }
        
    def get_best_signal(self, market_data):
        """Get signal from whichever strategy triggers first"""
        strategies = [
            ('conservative', self.conservative),
            ('moderate', self.moderate),
            ('aggressive', self.aggressive)
        ]
        
        signals = []
        for strategy_name, strategy in strategies:
            try:
                signal = strategy.generate_signal(market_data)
                if signal and signal[0] != "NO_SIGNAL":
                    signals.append({
                        'strategy': strategy_name,
                        'signal': signal[0],
                        'option': signal[1],
                        'confidence': signal[2],
                        'timestamp': datetime.now()
                    })
            except Exception as e:
                logging.error(f"Error in {strategy_name} strategy: {e}")
        
        # Return the highest confidence signal
        if signals:
            best_signal = max(signals, key=lambda x: x['confidence'])
            logging.info(f"Selected signal from {best_signal['strategy']} strategy")
            return best_signal
            
        return None
    
    def update_performance(self, strategy_name, result):
        """Update performance metrics for a strategy"""
        self.strategy_performance[strategy_name]['total'] += 1
        if result == 'win':
            self.strategy_performance[strategy_name]['wins'] += 1
        else:
            self.strategy_performance[strategy_name]['losses'] += 1
    
    def get_performance_summary(self):
        """Get performance summary for all strategies"""
        summary = {}
        for strategy, stats in self.strategy_performance.items():
            total = stats['total']
            if total > 0:
                win_rate = (stats['wins'] / total) * 100
                summary[strategy] = {
                    'total_trades': total,
                    'win_rate': f"{win_rate:.1f}%",
                    'wins': stats['wins'],
                    'losses': stats['losses']
                }
        return summary


class ModerateConfidenceScalper(HighConfidenceScalper):
    """Moderate confidence strategy with relaxed thresholds"""
    
    def __init__(self, kite_api_key, kite_api_secret):
        super().__init__(kite_api_key, kite_api_secret)
        self.MIN_CONFIDENCE = 0.70  # 70% confidence
        self.profit_target = 20  # 20 point profit
        self.stop_loss = -20    # 20 point stop loss


class ForceTradeScalper(HighConfidenceScalper):
    """Aggressive strategy that always trades in morning"""
    
    def __init__(self, kite_api_key, kite_api_secret):
        super().__init__(kite_api_key, kite_api_secret)
        self.MIN_CONFIDENCE = 0.55  # 55% confidence
        self.profit_target = 15  # 15 point profit
        self.stop_loss = -15    # 15 point stop loss
    
    def should_force_trade(self, current_time):
        """Force trades during key market hours"""
        # Force trade at 9:15 AM
        if current_time.hour == 9 and current_time.minute <= 30:
            return True
            
        # Force trade at market open
        if current_time.hour == 9 and current_time.minute == 15:
            return True
            
        # Force trade if no trades today after 10 AM
        if len(self.trades_today) == 0 and current_time.hour >= 10:
            return True
            
        return False
    
    def generate_signal(self, market_data):
        """Generate signal with force trading logic"""
        current_time = datetime.now().time()
        
        # Check if we should force a trade
        if self.should_force_trade(current_time):
            # Get basic market data
            sensex_data = self.get_live_sensex_data()
            if not sensex_data:
                return None
                
            # Determine direction based on momentum
            momentum = sensex_data['last_price'] - sensex_data['open']
            signal = "CALL" if momentum > 0 else "PUT"
            
            # Get any available option
            selected_option = self.get_high_oi_option(signal)
            if selected_option:
                return signal, selected_option, 0.55  # Minimum confidence
        
        # Fall back to regular signal generation
        return super().generate_signal(market_data)


# Quick test function
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    kite_api_key = os.getenv('KITE_API_KEY')
    kite_api_secret = os.getenv('KITE_ACCESS_TOKEN')
    
    if kite_api_key and kite_api_secret:
        system = MultiStrategySystem(kite_api_key, kite_api_secret)
        
        # Test signal generation
        market_data = {'price': 75000, 'volume': 100000}
        signal = system.get_best_signal(market_data)
        
        if signal:
            print(f"Generated signal: {signal}")
        else:
            print("No signals generated")
    else:
        print("Missing API credentials")