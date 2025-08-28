import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import datetime
import logging
from multi_asset_ai import MultiAssetAI
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class TradingSignal:
    asset: str
    direction: str  # 'BUY' or 'SELL'
    strength: float  # 0-1 confidence score
    entry_price: float
    target_price: float
    stop_loss: float
    timestamp: datetime.datetime
    signal_type: str  # 'LONG', 'SHORT', 'EXIT'
    confidence: float
    technical_score: float
    fundamental_score: float
    sentiment_score: float
    risk_score: float

class SignalEngine:
    def __init__(self):
        self.ai_system = MultiAssetAI()
        self.supabase = self._initialize_supabase()
        self.logger = logging.getLogger(__name__)
        
        # Signal thresholds
        self.min_confidence = 0.65
        self.min_strength = 0.7
        self.max_positions_per_asset = 1
        self.cooldown_period = datetime.timedelta(minutes=30)
        
        # Track recent signals to avoid duplicates
        self.recent_signals = {}
        
    def _initialize_supabase(self):
        """Initialize Supabase client with mock fallback"""
        try:
            # Check if credentials exist
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")
            
            if not supabase_url or not supabase_key:
                from mock_supabase import MockSupabase
                logging.warning("Using mock Supabase - no real database connection")
                return MockSupabase()
                
            from supabase import create_client
            client = create_client(supabase_url, supabase_key)
            logging.info("✅ Supabase client initialized successfully")
            return client
            
        except ImportError:
            logging.warning("Supabase library not installed - using mock Supabase")
            from mock_supabase import MockSupabase
            return MockSupabase()
        except Exception as e:
            logging.error(f"Supabase initialization failed: {e}")
            from mock_supabase import MockSupabase
            return MockSupabase()
    
    def log_to_supabase(self, data):
        """Log data to Supabase if available, otherwise skip"""
        if hasattr(self, 'supabase') and self.supabase:
            try:
                return self.supabase.table('signals').insert(data).execute()
            except Exception as e:
                logging.error(f"Failed to log to Supabase: {e}")
        else:
            logging.info(f"Offline mode - would log: {data}")
        
    def scan_universe(self, universe: List[str] = None) -> List[TradingSignal]:
        """Scan entire universe for trading signals"""
        if universe is None:
            universe = self.get_default_universe()
            
        all_signals = []
        
        for asset in universe:
            try:
                signal = self.generate_signal_for_asset(asset)
                if signal and self.validate_signal(signal):
                    all_signals.append(signal)
            except Exception as e:
                self.logger.error(f"Error generating signal for {asset}: {e}")
                
        # Rank signals by strength and confidence
        ranked_signals = sorted(all_signals, key=lambda x: x.strength * x.confidence, reverse=True)
        
        return ranked_signals
        
    def get_default_universe(self) -> List[str]:
        """Get default trading universe"""
        return [
            'RELIANCE', 'TCS', 'HDFC', 'INFY', 'ITC', 'SBIN', 'BHARTIARTL',
            'ICICIBANK', 'KOTAKBANK', 'LT', 'HINDUNILVR', 'AXISBANK',
            'MARUTI', 'ASIANPAINT', 'BAJFINANCE', 'WIPRO', 'ONGC',
            'NTPC', 'ULTRACEMCO', 'POWERGRID', 'SUNPHARMA', 'NESTLEIND',
            'TITAN', 'BAJAJFINSV', 'TECHM', 'INDUSINDBK', 'ADANIPORTS',
            'HCLTECH', 'DRREDDY', 'GRASIM', 'DIVISLAB', 'JSWSTEEL',
            'HEROMOTOCO', 'SHREECEM', 'COALINDIA', 'BRITANNIA', 'IOC',
            'M&M', 'BPCL', 'EICHERMOT', 'UPL', 'APOLLOHOSP',
            'CIPLA', 'TATAMOTORS', 'ADANIENT', 'SBILIFE', 'TATASTEEL'
        ]
        
    def generate_signal_for_asset(self, asset: str) -> Optional[TradingSignal]:
        """Generate trading signal for a specific asset"""
        
        # Get market data
        market_data = self.get_market_data(asset)
        if not market_data:
            return None
            
        # Get AI prediction
        prediction = self.ai_system.predict_asset_movement(asset, market_data)
        if prediction['confidence'] < self.min_confidence:
            return None
            
        # Calculate technical indicators
        technical_score = self.calculate_technical_score(market_data)
        
        # Calculate fundamental score
        fundamental_score = self.calculate_fundamental_score(asset)
        
        # Calculate sentiment score
        sentiment_score = self.calculate_sentiment_score(asset)
        
        # Calculate risk score
        risk_score = self.calculate_risk_score(asset, market_data)
        
        # Calculate overall signal strength
        strength = (technical_score * 0.4 + 
                   fundamental_score * 0.3 + 
                   sentiment_score * 0.2 + 
                   (1 - risk_score) * 0.1)
                   
        if strength < self.min_strength:
            return None
            
        # Calculate entry, target, and stop loss
        entry_price = market_data['close'].iloc[-1]
        target_price = self.calculate_target_price(market_data, prediction)
        stop_loss = self.calculate_stop_loss(market_data, prediction)
        
        # Determine signal direction
        direction = prediction['direction']
        
        # Check for recent signals
        if self.is_recent_signal(asset, direction):
            return None
            
        signal = TradingSignal(
            asset=asset,
            direction=direction,
            strength=strength,
            entry_price=entry_price,
            target_price=target_price,
            stop_loss=stop_loss,
            timestamp=datetime.datetime.now(),
            signal_type='LONG' if direction == 'BUY' else 'SHORT',
            confidence=prediction['confidence'],
            technical_score=technical_score,
            fundamental_score=fundamental_score,
            sentiment_score=sentiment_score,
            risk_score=risk_score
        )
        
        return signal
        
    def get_market_data(self, asset: str) -> Optional[pd.DataFrame]:
        """Get market data for an asset"""
        try:
            # Fetch from Supabase
            response = self.supabase.table('market_data').select('*').eq(
                'asset', asset
            ).order('timestamp', desc=True).limit(100).execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                return df.set_index('timestamp')
                
        except Exception as e:
            self.logger.error(f"Error fetching market data for {asset}: {e}")
            
        # Fallback to mock data for testing
        return self.generate_mock_data(asset)
        
    def generate_mock_data(self, asset: str) -> pd.DataFrame:
        """Generate mock market data for testing"""
        dates = pd.date_range(end=datetime.datetime.now(), periods=100, freq='1min')
        
        # Generate realistic price data
        np.random.seed(hash(asset) % 2**32)
        returns = np.random.normal(0.001, 0.02, len(dates))
        prices = 100 * np.exp(np.cumsum(returns))
        
        # Generate volume data
        volumes = np.random.normal(100000, 20000, len(dates))
        
        # Generate technical indicators
        sma_20 = pd.Series(prices).rolling(20).mean()
        sma_50 = pd.Series(prices).rolling(50).mean()
        rsi = self.calculate_rsi(prices)
        
        df = pd.DataFrame({
            'close': prices,
            'volume': volumes,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'rsi': rsi
        }, index=dates)
        
        return df.dropna()
        
    def calculate_rsi(self, prices: np.ndarray, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = pd.Series(prices).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
        
    def calculate_technical_score(self, market_data: pd.DataFrame) -> float:
        """Calculate technical analysis score"""
        score = 0.5  # Base score
        
        # Price vs SMA crossover
        if len(market_data) >= 50:
            current_price = market_data['close'].iloc[-1]
            sma_20 = market_data['sma_20'].iloc[-1]
            sma_50 = market_data['sma_50'].iloc[-1]
            
            if current_price > sma_20 > sma_50:
                score += 0.3
            elif current_price < sma_20 < sma_50:
                score -= 0.3
                
            # RSI momentum
            rsi = market_data['rsi'].iloc[-1]
            if 30 <= rsi <= 70:
                score += 0.2
            elif rsi < 30:
                score += 0.1
            else:
                score -= 0.1
                
        return max(0, min(1, score))
        
    def calculate_fundamental_score(self, asset: str) -> float:
        """Calculate fundamental analysis score"""
        # Mock implementation - replace with actual fundamental data
        return np.random.uniform(0.4, 0.8)
        
    def calculate_sentiment_score(self, asset: str) -> float:
        """Calculate sentiment analysis score"""
        # Mock implementation - replace with actual sentiment data
        return np.random.uniform(0.3, 0.9)
        
    def calculate_risk_score(self, asset: str, market_data: pd.DataFrame) -> float:
        """Calculate risk score (lower is better)"""
        # Volatility-based risk
        returns = market_data['close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)  # Annualized volatility
        
        # Normalize volatility risk (0-1 scale)
        vol_risk = min(1, volatility / 0.5)  # 50% volatility as max risk
        
        # Liquidity risk
        avg_volume = market_data['volume'].mean()
        liquidity_risk = max(0, 1 - avg_volume / 1000000)  # 1M volume as benchmark
        
        # Combined risk score
        risk_score = (vol_risk * 0.7 + liquidity_risk * 0.3)
        
        return risk_score
        
    def calculate_target_price(self, market_data: pd.DataFrame, prediction: dict) -> float:
        """Calculate target price based on prediction"""
        current_price = market_data['close'].iloc[-1]
        
        # Mock calculation - replace with actual target calculation
        if prediction['direction'] == 'BUY':
            target = current_price * (1 + 0.02)  # 2% upside target
        else:
            target = current_price * (1 - 0.02)  # 2% downside target
            
        return target
        
    def calculate_stop_loss(self, market_data: pd.DataFrame, prediction: dict) -> float:
        """Calculate stop loss based on volatility"""
        current_price = market_data['close'].iloc[-1]
        
        # ATR-based stop loss (mock implementation)
        volatility = market_data['close'].pct_change().std()
        atr_multiplier = 2.0
        stop_distance = volatility * atr_multiplier * current_price
        
        if prediction['direction'] == 'BUY':
            stop_loss = current_price - stop_distance
        else:
            stop_loss = current_price + stop_distance
            
        return max(0, stop_loss)  # Ensure non-negative
        
    def validate_signal(self, signal: TradingSignal) -> bool:
        """Validate signal against various criteria"""
        
        # Check minimum thresholds
        if signal.confidence < self.min_confidence:
            return False
            
        if signal.strength < self.min_strength:
            return False
            
        # Check risk/reward ratio
        risk_reward = abs(signal.target_price - signal.entry_price) / abs(signal.entry_price - signal.stop_loss)
        if risk_reward < 1.5:  # Minimum 1.5:1 risk/reward
            return False
            
        # Check if already have position in this asset
        if self.has_active_position(signal.asset):
            return False
            
        return True
        
    def is_recent_signal(self, asset: str, direction: str) -> bool:
        """Check if there was a recent signal for this asset"""
        key = f"{asset}_{direction}"
        
        if key in self.recent_signals:
            last_signal_time = self.recent_signals[key]
            if datetime.datetime.now() - last_signal_time < self.cooldown_period:
                return True
                
        return False
        
    def has_active_position(self, asset: str) -> bool:
        """Check if there's an active position for this asset"""
        # This would typically check with the execution engine
        return False
        
    def store_signal(self, signal: TradingSignal):
        """Store signal in Supabase"""
        try:
            self.supabase.table('signals').insert({
                'asset': signal.asset,
                'direction': signal.direction,
                'strength': signal.strength,
                'entry_price': signal.entry_price,
                'target_price': signal.target_price,
                'stop_loss': signal.stop_loss,
                'timestamp': signal.timestamp.isoformat(),
                'signal_type': signal.signal_type,
                'confidence': signal.confidence,
                'technical_score': signal.technical_score,
                'fundamental_score': signal.fundamental_score,
                'sentiment_score': signal.sentiment_score,
                'risk_score': signal.risk_score
            }).execute()
            
            # Update recent signals cache
            key = f"{signal.asset}_{signal.direction}"
            self.recent_signals[key] = signal.timestamp
            
        except Exception as e:
            self.logger.error(f"Failed to store signal: {e}")
            
    def get_signal_history(self, asset: str = None, days: int = 7) -> List[Dict]:
        """Get historical signals"""
        try:
            query = self.supabase.table('signals').select('*')
            
            if asset:
                query = query.eq('asset', asset)
                
            start_date = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
            query = query.gte('timestamp', start_date)
            
            response = query.execute()
            return response.data or []
            
        except Exception as e:
            self.logger.error(f"Failed to get signal history: {e}")
            return []
            
    def get_live_signals(self) -> List[TradingSignal]:
        """Get live trading signals"""
        signals = self.scan_universe()
        
        # Store signals in database
        for signal in signals:
            self.store_signal(signal)
            
        return signals

# Example usage
if __name__ == "__main__":
    engine = SignalEngine()
    
    # Generate signals
    signals = engine.scan_universe(['RELIANCE', 'TCS', 'HDFC'])
    
    print("🎯 Signal Engine Results:")
    for signal in signals:
        print(f"{signal.asset}: {signal.direction} @ {signal.entry_price:.2f}")
        print(f"  Strength: {signal.strength:.2f}, Confidence: {signal.confidence:.2f}")
        print(f"  Target: {signal.target_price:.2f}, Stop: {signal.stop_loss:.2f}")
        print()
        
    print("🤖 Signal Engine initialized!")