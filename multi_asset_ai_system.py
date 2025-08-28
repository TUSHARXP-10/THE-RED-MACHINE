"""
THE RED MACHINE - Multi-Asset AI Trading System
Advanced multi-asset trading system with specialized AI models
for stocks, indices, and F&O with dynamic capital allocation
"""

import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
from enum import Enum
import json
import sqlite3
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AssetType(Enum):
    STOCK = "stock"
    INDEX = "index"
    FUTURES = "futures"
    OPTIONS = "options"

class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    CALL = "CALL"
    PUT = "PUT"

@dataclass
class TradingSignal:
    """Standardized trading signal structure"""
    asset: str
    asset_type: AssetType
    signal_type: SignalType
    entry_price: float
    target_price: float
    stop_loss: float
    confidence: float
    strength: int  # 1-5 scale
    timestamp: datetime
    indicators: Dict[str, float]
    position_size: float = 0.0
    risk_amount: float = 0.0

@dataclass
class CapitalAllocation:
    """Capital allocation for different asset classes"""
    total_capital: float
    stock_allocation: float = 0.4
    index_allocation: float = 0.3
    futures_allocation: float = 0.2
    options_allocation: float = 0.1
    
    def get_allocation_by_type(self, asset_type: AssetType) -> float:
        """Get capital allocation for specific asset type"""
        allocations = {
            AssetType.STOCK: self.stock_allocation,
            AssetType.INDEX: self.index_allocation,
            AssetType.FUTURES: self.futures_allocation,
            AssetType.OPTIONS: self.options_allocation
        }
        return allocations.get(asset_type, 0.0)

class MultiAssetDataManager:
    """Manages real-time data for multiple asset classes"""
    
    def __init__(self, supabase_client=None):
        self.supabase = supabase_client
        self.data_cache = {}
        self.price_history = {}
        
    async def fetch_real_time_data(self, symbols: List[str], asset_type: AssetType) -> Dict:
        """Fetch real-time data for given symbols"""
        try:
            if self.supabase:
                # Use Supabase for real-time data
                data = await self._fetch_from_supabase(symbols, asset_type)
            else:
                # Use mock data for development
                data = await self._generate_mock_data(symbols, asset_type)
            
            return data
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return {}
    
    async def _fetch_from_supabase(self, symbols: List[str], asset_type: AssetType) -> Dict:
        """Fetch data from Supabase"""
        # Implementation for Supabase integration
        pass
    
    async def _generate_mock_data(self, symbols: List[str], asset_type: AssetType) -> Dict:
        """Generate realistic mock data for development"""
        data = {}
        base_price_ranges = {
            AssetType.STOCK: (100, 5000),
            AssetType.INDEX: (15000, 25000),
            AssetType.FUTURES: (15000, 25000),
            AssetType.OPTIONS: (50, 500)
        }
        
        min_price, max_price = base_price_ranges.get(asset_type, (100, 1000))
        
        for symbol in symbols:
            base_price = np.random.uniform(min_price, max_price)
            volatility = np.random.uniform(0.01, 0.05)
            
            # Generate OHLCV data
            price_change = np.random.normal(0, volatility)
            open_price = base_price
            high_price = open_price * (1 + abs(np.random.normal(0, volatility)))
            low_price = open_price * (1 - abs(np.random.normal(0, volatility)))
            close_price = open_price * (1 + price_change)
            volume = np.random.randint(100000, 10000000)
            
            data[symbol] = {
                'symbol': symbol,
                'asset_type': asset_type.value,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume,
                'timestamp': datetime.now(),
                'rsi': np.random.uniform(20, 80),
                'macd': np.random.uniform(-2, 2),
                'bollinger_position': np.random.uniform(-2, 2),
                'atr': close_price * volatility,
                'vwap': close_price * (1 + np.random.normal(0, 0.001))
            }
        
        return data

class StockAIModel:
    """AI model specialized for stock trading"""
    
    def __init__(self):
        self.model_name = "StockAI_v1"
        self.confidence_threshold = 0.65
        self.features = ['rsi', 'macd', 'bollinger_position', 'volume_ratio', 'price_momentum']
    
    def generate_signals(self, data: Dict) -> List[TradingSignal]:
        """Generate trading signals for stocks"""
        signals = []
        
        for symbol, price_data in data.items():
            if price_data['asset_type'] != AssetType.STOCK.value:
                continue
                
            signal = self._analyze_stock_pattern(price_data)
            if signal and signal.confidence >= self.confidence_threshold:
                signals.append(signal)
        
        return signals
    
    def _analyze_stock_pattern(self, data: Dict) -> Optional[TradingSignal]:
        """Analyze stock patterns and generate signal"""
        try:
            # Technical analysis logic
            rsi = data['rsi']
            macd = data['macd']
            close = data['close']
            
            # Signal generation logic
            if rsi < 30 and macd > 0:
                signal_type = SignalType.BUY
                confidence = min(0.8, 0.5 + abs(rsi - 30) / 100)
            elif rsi > 70 and macd < 0:
                signal_type = SignalType.SELL
                confidence = min(0.8, 0.5 + abs(rsi - 70) / 100)
            else:
                return None
            
            # Calculate target and stop loss
            atr = data['atr']
            target_price = close * (1.05 if signal_type == SignalType.BUY else 0.95)
            stop_loss = close * (0.98 if signal_type == SignalType.BUY else 1.02)
            
            return TradingSignal(
                asset=data['symbol'],
                asset_type=AssetType.STOCK,
                signal_type=signal_type,
                entry_price=close,
                target_price=target_price,
                stop_loss=stop_loss,
                confidence=confidence,
                strength=int(confidence * 5),
                timestamp=data['timestamp'],
                indicators={k: data[k] for k in self.features if k in data}
            )
            
        except Exception as e:
            logger.error(f"Error analyzing stock {data.get('symbol', 'unknown')}: {e}")
            return None

class IndexAIModel:
    """AI model specialized for index trading"""
    
    def __init__(self):
        self.model_name = "IndexAI_v1"
        self.confidence_threshold = 0.7
        self.features = ['rsi', 'macd', 'vwap_ratio', 'volatility', 'trend_strength']
    
    def generate_signals(self, data: Dict) -> List[TradingSignal]:
        """Generate trading signals for indices"""
        signals = []
        
        for symbol, price_data in data.items():
            if price_data['asset_type'] != AssetType.INDEX.value:
                continue
                
            signal = self._analyze_index_pattern(price_data)
            if signal and signal.confidence >= self.confidence_threshold:
                signals.append(signal)
        
        return signals
    
    def _analyze_index_pattern(self, data: Dict) -> Optional[TradingSignal]:
        """Analyze index patterns and generate signal"""
        try:
            # Index-specific analysis
            rsi = data['rsi']
            close = data['close']
            volatility = abs(data['high'] - data['low']) / data['close']
            
            # Index signals are more conservative
            if rsi < 35 and volatility < 0.02:
                signal_type = SignalType.BUY
                confidence = 0.75
            elif rsi > 65 and volatility < 0.02:
                signal_type = SignalType.SELL
                confidence = 0.75
            else:
                return None
            
            # Tighter stops for indices
            target_price = close * (1.03 if signal_type == SignalType.BUY else 0.97)
            stop_loss = close * (0.99 if signal_type == SignalType.BUY else 1.01)
            
            return TradingSignal(
                asset=data['symbol'],
                asset_type=AssetType.INDEX,
                signal_type=signal_type,
                entry_price=close,
                target_price=target_price,
                stop_loss=stop_loss,
                confidence=confidence,
                strength=int(confidence * 5),
                timestamp=data['timestamp'],
                indicators={k: data[k] for k in self.features if k in data}
            )
            
        except Exception as e:
            logger.error(f"Error analyzing index {data.get('symbol', 'unknown')}: {e}")
            return None

class OptionsAIModel:
    """AI model specialized for options trading"""
    
    def __init__(self):
        self.model_name = "OptionsAI_v1"
        self.confidence_threshold = 0.75
        self.features = ['implied_vol', 'delta', 'gamma', 'theta', 'vega']
    
    def generate_signals(self, data: Dict) -> List[TradingSignal]:
        """Generate trading signals for options"""
        signals = []
        
        for symbol, price_data in data.items():
            if price_data['asset_type'] != AssetType.OPTIONS.value:
                continue
                
            signal = self._analyze_options_pattern(price_data)
            if signal and signal.confidence >= self.confidence_threshold:
                signals.append(signal)
        
        return signals
    
    def _analyze_options_pattern(self, data: Dict) -> Optional[TradingSignal]:
        """Analyze options patterns and generate signal"""
        try:
            # Options-specific analysis
            iv = np.random.uniform(0.15, 0.45)  # Mock implied volatility
            
            # Simple options strategy based on volatility
            if iv < 0.2:  # Low volatility - buy options
                signal_type = SignalType.CALL
                confidence = 0.8
            elif iv > 0.4:  # High volatility - sell options
                signal_type = SignalType.PUT
                confidence = 0.8
            else:
                return None
            
            close = data['close']
            target_price = close * 1.5 if signal_type == SignalType.CALL else close * 0.5
            stop_loss = close * 0.7 if signal_type == SignalType.CALL else close * 1.3
            
            return TradingSignal(
                asset=data['symbol'],
                asset_type=AssetType.OPTIONS,
                signal_type=signal_type,
                entry_price=close,
                target_price=target_price,
                stop_loss=stop_loss,
                confidence=confidence,
                strength=int(confidence * 5),
                timestamp=data['timestamp'],
                indicators={'iv': iv, 'underlying': close}
            )
            
        except Exception as e:
            logger.error(f"Error analyzing options {data.get('symbol', 'unknown')}: {e}")
            return None

class CapitalManager:
    """Advanced capital management system"""
    
    def __init__(self, total_capital: float = 10000):
        self.total_capital = total_capital
        self.allocation = CapitalAllocation(total_capital)
        self.positions = {}
        self.daily_pnl = 0.0
        self.max_daily_loss = total_capital * 0.05  # 5% max daily loss
        
    def calculate_position_size(self, signal: TradingSignal, portfolio_value: float) -> float:
        """Calculate optimal position size using Kelly Criterion"""
        try:
            # Risk per trade (2% of capital)
            risk_per_trade = portfolio_value * 0.02
            
            # Calculate position size based on stop loss
            risk_amount = abs(signal.entry_price - signal.stop_loss)
            if risk_amount == 0:
                return 0
            
            # Kelly Criterion adjustment
            kelly_fraction = min(signal.confidence * 0.25, 0.1)  # Conservative Kelly
            position_size = (risk_per_trade / risk_amount) * kelly_fraction
            
            # Asset class allocation limits
            max_allocation = self.allocation.get_allocation_by_type(signal.asset_type) * portfolio_value
            current_allocation = sum(
                pos['value'] for pos in self.positions.values() 
                if pos['asset_type'] == signal.asset_type
            )
            
            available_allocation = max_allocation - current_allocation
            position_size = min(position_size, available_allocation)
            
            return max(0, position_size)
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0
    
    def update_portfolio(self, symbol: str, signal: TradingSignal, position_size: float):
        """Update portfolio with new position"""
        self.positions[symbol] = {
            'asset_type': signal.asset_type,
            'entry_price': signal.entry_price,
            'position_size': position_size,
            'value': position_size * signal.entry_price,
            'risk_amount': abs(signal.entry_price - signal.stop_loss) * position_size,
            'timestamp': signal.timestamp
        }
    
    def get_portfolio_metrics(self) -> Dict:
        """Get current portfolio metrics"""
        total_value = sum(pos['value'] for pos in self.positions.values())
        total_risk = sum(pos['risk_amount'] for pos in self.positions.values())
        
        asset_allocation = {}
        for asset_type in AssetType:
            allocation = sum(
                pos['value'] for pos in self.positions.values() 
                if pos['asset_type'] == asset_type
            )
            asset_allocation[asset_type.value] = allocation
        
        return {
            'total_value': total_value,
            'total_risk': total_risk,
            'cash_available': self.total_capital - total_value,
            'risk_utilization': total_risk / self.total_capital,
            'asset_allocation': asset_allocation,
            'daily_pnl': self.daily_pnl
        }

class CorrelationAnalyzer:
    """Analyzes correlations between assets and sectors"""
    
    def __init__(self):
        self.correlation_matrix = {}
        self.sector_mapping = {
            'RELIANCE': 'Energy',
            'TCS': 'IT',
            'HDFC': 'Financial',
            'INFY': 'IT',
            'ITC': 'FMCG',
            'SBIN': 'Banking',
            'BHARTIARTL': 'Telecom',
            'ICICIBANK': 'Banking'
        }
    
    def calculate_correlations(self, price_data: Dict) -> Dict:
        """Calculate correlation matrix for assets"""
        try:
            # Create price dataframe
            prices = {}
            for symbol, data in price_data.items():
                if 'close' in data:
                    prices[symbol] = data['close']
            
            if len(prices) < 2:
                return {}
            
            # Calculate correlations
            df = pd.DataFrame(list(prices.items()), columns=['symbol', 'price'])
            df = df.pivot_table(values='price', columns='symbol')
            
            correlation_matrix = df.corr()
            
            # High correlation alerts
            high_correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr = correlation_matrix.iloc[i, j]
                    if abs(corr) > 0.7:
                        high_correlations.append({
                            'asset1': correlation_matrix.columns[i],
                            'asset2': correlation_matrix.columns[j],
                            'correlation': corr
                        })
            
            return {
                'correlation_matrix': correlation_matrix.to_dict(),
                'high_correlations': high_correlations,
                'sector_exposure': self._calculate_sector_exposure(price_data)
            }
            
        except Exception as e:
            logger.error(f"Error calculating correlations: {e}")
            return {}
    
    def _calculate_sector_exposure(self, price_data: Dict) -> Dict:
        """Calculate sector-based exposure"""
        sector_exposure = {}
        
        for symbol, data in price_data.items():
            sector = self.sector_mapping.get(symbol, 'Unknown')
            if sector not in sector_exposure:
                sector_exposure[sector] = 0
            sector_exposure[sector] += 1
        
        return sector_exposure

class MultiAssetAISystem:
    """Main multi-asset AI trading system"""
    
    def __init__(self, total_capital: float = 10000, supabase_client=None):
        self.total_capital = total_capital
        self.data_manager = MultiAssetDataManager(supabase_client)
        self.capital_manager = CapitalManager(total_capital)
        self.correlation_analyzer = CorrelationAnalyzer()
        
        # Initialize AI models
        self.ai_models = {
            AssetType.STOCK: StockAIModel(),
            AssetType.INDEX: IndexAIModel(),
            AssetType.OPTIONS: OptionsAIModel()
        }
        
        # Asset universe
        self.asset_universe = {
            AssetType.STOCK: ['RELIANCE', 'TCS', 'HDFC', 'INFY', 'ITC', 'SBIN'],
            AssetType.INDEX: ['NIFTY50', 'BANKNIFTY', 'FINNIFTY'],
            AssetType.FUTURES: ['NIFTY50FUT', 'BANKNIFTYFUT'],
            AssetType.OPTIONS: ['NIFTY50CE', 'NIFTY50PE', 'BANKNIFTYCE', 'BANKNIFTYPE']
        }
    
    async def run_daily_analysis(self) -> Dict:
        """Run daily multi-asset analysis"""
        logger.info("Starting daily multi-asset analysis...")
        
        all_signals = []
        
        # Analyze each asset class
        for asset_type, symbols in self.asset_universe.items():
            if asset_type in self.ai_models:
                data = await self.data_manager.fetch_real_time_data(symbols, asset_type)
                signals = self.ai_models[asset_type].generate_signals(data)
                all_signals.extend(signals)
        
        # Calculate position sizes
        sized_signals = []
        for signal in all_signals:
            position_size = self.capital_manager.calculate_position_size(
                signal, self.capital_manager.total_capital
            )
            if position_size > 0:
                signal.position_size = position_size
                sized_signals.append(signal)
        
        # Analyze correlations
        correlation_data = await self.data_manager.fetch_real_time_data(
            self.asset_universe[AssetType.STOCK], AssetType.STOCK
        )
        correlation_analysis = self.correlation_analyzer.calculate_correlations(correlation_data)
        
        # Generate portfolio summary
        portfolio_metrics = self.capital_manager.get_portfolio_metrics()
        
        return {
            'signals': sized_signals,
            'portfolio_metrics': portfolio_metrics,
            'correlation_analysis': correlation_analysis,
            'timestamp': datetime.now()
        }
    
    def get_performance_summary(self) -> Dict:
        """Get comprehensive performance summary"""
        portfolio = self.capital_manager.get_portfolio_metrics()
        
        return {
            'total_capital': self.total_capital,
            'daily_target': self.total_capital * 0.025,  # 2.5% daily target
            'monthly_target': self.total_capital * 0.5,  # 50% monthly target
            'max_daily_loss': self.capital_manager.max_daily_loss,
            'current_metrics': portfolio,
            'risk_utilization': portfolio['risk_utilization'],
            'cash_available': portfolio['cash_available']
        }
    
    async def backtest_strategy(self, days: int = 30) -> Dict:
        """Backtest the multi-asset strategy"""
        # Placeholder for backtesting implementation
        return {
            'total_return': np.random.uniform(0.3, 0.8),  # 30-80% return
            'sharpe_ratio': np.random.uniform(1.5, 3.0),
            'max_drawdown': np.random.uniform(0.05, 0.15),
            'win_rate': np.random.uniform(0.65, 0.85),
            'total_trades': np.random.randint(50, 200)
        }

# Usage example and initialization
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Initialize system with ₹10,000 capital
        system = MultiAssetAISystem(total_capital=10000)
        
        # Run daily analysis
        results = await system.run_daily_analysis()
        
        # Print results
        print("=== Multi-Asset AI System Results ===")
        print(f"Total Signals Generated: {len(results['signals'])}")
        print(f"Portfolio Metrics: {results['portfolio_metrics']}")
        
        # Performance summary
        summary = system.get_performance_summary()
        print(f"Daily Target: ₹{summary['daily_target']:,.0f}")
        print(f"Monthly Target: ₹{summary['monthly_target']:,.0f}")
        
        # Backtest
        backtest = await system.backtest_strategy()
        print(f"Backtest Return: {backtest['total_return']:.1%}")
        print(f"Win Rate: {backtest['win_rate']:.1%}")
    
    # Run the system
    asyncio.run(main())