import asyncio
import datetime
import logging
import os
import time
from typing import Dict, List, Optional

import pandas as pd
from dotenv import load_dotenv

from smart_execution_engine import SmartExecutionEngine, TradeDirection
from signal_engine import SignalEngine, TradingSignal
from comprehensive_risk_manager import ComprehensiveRiskManager
from multi_asset_ai import MultiAssetAI
from supabase import create_client

load_dotenv()

class TradingSystem:
    """Main trading system that orchestrates all components"""
    
    def __init__(self):
        # Initialize components
        self.multi_asset_ai = MultiAssetAI()
        self.risk_manager = ComprehensiveRiskManager(total_capital=100000)
        self.signal_engine = SignalEngine()
        
        # Initialize Supabase
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
        
        # Initialize execution engine (mock for now)
        self.execution_engine = SmartExecutionEngine(
            kite_client=None,  # Would be actual broker client
            capital_manager=self.risk_manager
        )
        
        # System configuration
        self.is_running = False
        self.scan_interval = 10  # seconds
        self.max_daily_trades = 50
        self.trade_count = 0
        
        # Logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize the trading system"""
        self.logger.info("🚀 Initializing Trading System...")
        
        # Train AI models
        self.logger.info("🧠 Training AI models...")
        await self.train_models()
        
        # Load historical data
        self.logger.info("📊 Loading historical data...")
        await self.load_historical_data()
        
        # Initialize risk manager
        self.logger.info("🛡️ Initializing risk manager...")
        await self.initialize_risk_manager()
        
        self.logger.info("✅ Trading System initialized successfully!")
        
    async def train_models(self):
        """Train AI models for different asset types"""
        try:
            # Train stock models
            self.multi_asset_ai.train_asset_specific_models('stocks')
            self.logger.info("📈 Stock models trained")
            
            # Train index models
            self.multi_asset_ai.train_asset_specific_models('indices')
            self.logger.info("📊 Index models trained")
            
            # Train options models
            self.multi_asset_ai.train_asset_specific_models('options')
            self.logger.info("⚡ Options models trained")
            
        except Exception as e:
            self.logger.error(f"Error training models: {e}")
            
    async def load_historical_data(self):
        """Load historical market data"""
        # This would load actual historical data
        self.logger.info("Historical data loaded")
        
    async def initialize_risk_manager(self):
        """Initialize risk management parameters"""
        # Load risk parameters from database
        self.logger.info("Risk manager initialized")
        
    async def run_trading_loop(self):
        """Main trading loop"""
        self.is_running = True
        self.logger.info("🔄 Starting trading loop...")
        
        while self.is_running:
            try:
                # Check if market is open
                if not self.is_market_open():
                    self.logger.info("Market closed, waiting...")
                    await asyncio.sleep(60)
                    continue
                    
                # Emergency stop check
                if self.risk_manager.emergency_stop_check():
                    self.logger.critical("🚨 Emergency stop triggered!")
                    await self.emergency_shutdown()
                    break
                    
                # Generate trading signals
                signals = await self.generate_signals()
                
                # Process signals
                await self.process_signals(signals)
                
                # Monitor positions
                await self.monitor_positions()
                
                # Generate risk report
                await self.generate_risk_report()
                
                # Wait for next cycle
                await asyncio.sleep(self.scan_interval)
                
            except Exception as e:
                self.logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(5)
                
    def is_market_open(self) -> bool:
        """Check if market is open"""
        now = datetime.datetime.now()
        
        # Mock implementation - replace with actual market hours
        market_open = datetime.time(9, 15)
        market_close = datetime.time(15, 30)
        
        return market_open <= now.time() <= market_close
        
    async def generate_signals(self) -> List[TradingSignal]:
        """Generate trading signals"""
        try:
            signals = self.signal_engine.get_live_signals()
            self.logger.info(f"Generated {len(signals)} signals")
            return signals
        except Exception as e:
            self.logger.error(f"Error generating signals: {e}")
            return []
            
    async def process_signals(self, signals: List[TradingSignal]):
        """Process trading signals"""
        for signal in signals:
            try:
                # Check daily trade limit
                if self.trade_count >= self.max_daily_trades:
                    self.logger.warning("Daily trade limit reached")
                    break
                    
                # Validate with risk manager
                position_size = self.calculate_position_size(signal)
                is_valid, message = self.risk_manager.validate_trade_risk(
                    {
                        'asset': signal.asset,
                        'entry_price': signal.entry_price,
                        'stop_loss': signal.stop_loss,
                        'sector': self.get_asset_sector(signal.asset)
                    },
                    position_size
                )
                
                if not is_valid:
                    self.logger.warning(f"Signal rejected: {message}")
                    continue
                    
                # Execute trade
                await self.execute_trade(signal, position_size)
                self.trade_count += 1
                
            except Exception as e:
                self.logger.error(f"Error processing signal: {e}")
                
    def calculate_position_size(self, signal: TradingSignal) -> float:
        """Calculate position size based on risk"""
        # Risk-based position sizing
        risk_amount = abs(signal.entry_price - signal.stop_loss)
        risk_per_trade = self.risk_manager.total_capital * 0.01  # 1% risk per trade
        
        position_size = risk_per_trade / risk_amount
        
        # Adjust based on signal strength
        position_size *= signal.strength
        
        # Apply confidence adjustment
        position_size *= signal.confidence
        
        return int(position_size)
        
    def get_asset_sector(self, asset: str) -> str:
        """Get sector for an asset"""
        # Mock implementation - replace with actual sector mapping
        sector_map = {
            'RELIANCE': 'Energy',
            'TCS': 'IT',
            'HDFC': 'Financial',
            'INFY': 'IT',
            'ITC': 'FMCG',
            'SBIN': 'Financial',
            'BHARTIARTL': 'Telecom',
            'ICICIBANK': 'Financial',
            'KOTAKBANK': 'Financial',
            'LT': 'Infrastructure',
            'HINDUNILVR': 'FMCG',
            'AXISBANK': 'Financial',
            'MARUTI': 'Auto',
            'ASIANPAINT': 'Chemicals',
            'BAJFINANCE': 'Financial',
            'WIPRO': 'IT',
            'ONGC': 'Energy',
            'NTPC': 'Power',
            'ULTRACEMCO': 'Cement',
            'POWERGRID': 'Power',
            'SUNPHARMA': 'Pharma',
            'NESTLEIND': 'FMCG',
            'TITAN': 'Consumer',
            'BAJAJFINSV': 'Financial',
            'TECHM': 'IT',
            'INDUSINDBK': 'Financial',
            'ADANIPORTS': 'Infrastructure',
            'HCLTECH': 'IT',
            'DRREDDY': 'Pharma',
            'GRASIM': 'Cement',
            'DIVISLAB': 'Pharma',
            'JSWSTEEL': 'Metals',
            'HEROMOTOCO': 'Auto',
            'SHREECEM': 'Cement',
            'COALINDIA': 'Energy',
            'BRITANNIA': 'FMCG',
            'IOC': 'Energy',
            'M&M': 'Auto',
            'BPCL': 'Energy',
            'EICHERMOT': 'Auto',
            'UPL': 'Chemicals',
            'APOLLOHOSP': 'Healthcare',
            'CIPLA': 'Pharma',
            'TATAMOTORS': 'Auto',
            'ADANIENT': 'Infrastructure',
            'SBILIFE': 'Insurance',
            'TATASTEEL': 'Metals'
        }
        
        return sector_map.get(asset, 'Unknown')
        
    async def execute_trade(self, signal: TradingSignal, position_size: int):
        """Execute a trade"""
        try:
            # Create trade order
            trade_order = {
                'asset': signal.asset,
                'direction': signal.direction.lower(),
                'quantity': position_size,
                'entry_price': signal.entry_price,
                'target': signal.target_price,
                'stop_loss': signal.stop_loss,
                'signal_strength': signal.strength,
                'timestamp': datetime.datetime.now()
            }
            
            # Store trade in database
            self.supabase.table('trades').insert({
                'asset': signal.asset,
                'direction': signal.direction,
                'entry_price': signal.entry_price,
                'quantity': position_size,
                'signal_strength': signal.strength,
                'timestamp': datetime.datetime.now().isoformat()
            }).execute()
            
            self.logger.info(
                f"🚀 Executed trade: {signal.direction} {position_size} {signal.asset} @ {signal.entry_price}"
            )
            
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            
    async def monitor_positions(self):
        """Monitor existing positions"""
        # This would monitor actual positions
        # For now, just log status
        self.logger.debug("Monitoring positions...")
        
    async def generate_risk_report(self):
        """Generate and store risk report"""
        try:
            risk_data = self.risk_manager.get_risk_dashboard_data()
            
            # Store risk metrics
            self.supabase.table('performance_metrics').insert({
                'timestamp': datetime.datetime.now().isoformat(),
                'daily_pnl': risk_data['current_metrics']['daily_pnl'],
                'total_trades': self.trade_count,
                'active_positions': risk_data['current_metrics']['active_positions'],
                'available_capital': risk_data['current_metrics']['available_capital']
            }).execute()
            
            # Log risk alerts
            for alert in risk_data['risk_alerts']:
                self.logger.warning(alert)
                
        except Exception as e:
            self.logger.error(f"Error generating risk report: {e}")
            
    async def emergency_shutdown(self):
        """Emergency shutdown procedure"""
        self.logger.critical("🚨 Emergency shutdown initiated")
        self.is_running = False
        
        # Close all positions
        # This would close actual positions
        
        # Generate final report
        await self.generate_risk_report()
        
        self.logger.info("Emergency shutdown complete")
        
    def stop(self):
        """Stop the trading system"""
        self.is_running = False
        self.logger.info("Trading system stopped")
        
    async def get_system_status(self) -> Dict:
        """Get current system status"""
        risk_data = self.risk_manager.get_risk_dashboard_data()
        
        return {
            'is_running': self.is_running,
            'trade_count': self.trade_count,
            'market_open': self.is_market_open(),
            'risk_metrics': risk_data,
            'timestamp': datetime.datetime.now().isoformat()
        }

# Example usage
async def main():
    """Main function to run the trading system"""
    
    # Initialize trading system
    trading_system = TradingSystem()
    
    try:
        # Initialize system
        await trading_system.initialize()
        
        # Run trading loop
        await trading_system.run_trading_loop()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping trading system...")
        trading_system.stop()
    except Exception as e:
        print(f"❌ Error: {e}")
        trading_system.stop()

if __name__ == "__main__":
    # Run the trading system
    asyncio.run(main())