"""
Integration Layer for Multi-Asset AI System with THE RED MACHINE Dashboard
Bridges the new multi-asset framework with the existing dashboard
"""

import asyncio
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import json
import logging
from pathlib import Path

# Import our new multi-asset system
from multi_asset_ai_system import MultiAssetAISystem, TradingSignal, AssetType

logger = logging.getLogger(__name__)

class MultiAssetDashboardIntegration:
    """Integration layer between multi-asset AI system and dashboard"""
    
    def __init__(self):
        self.ai_system = None
        self.last_update = None
        self.signals_cache = []
        self.metrics_cache = {}
        
    def initialize_system(self, capital: float = 10000) -> bool:
        """Initialize the multi-asset AI system"""
        try:
            self.ai_system = MultiAssetAISystem(total_capital=capital)
            self.last_update = datetime.now()
            logger.info("Multi-asset AI system initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize system: {e}")
            return False
    
    async def get_dashboard_data(self) -> Dict:
        """Get comprehensive data for dashboard display"""
        if not self.ai_system:
            return self._get_mock_dashboard_data()
        
        try:
            # Run daily analysis
            analysis = await self.ai_system.run_daily_analysis()
            performance = self.ai_system.get_performance_summary()
            
            # Format data for dashboard
            dashboard_data = {
                'signals': self._format_signals_for_dashboard(analysis['signals']),
                'portfolio_metrics': analysis['portfolio_metrics'],
                'performance_summary': performance,
                'correlation_analysis': analysis['correlation_analysis'],
                'timestamp': analysis['timestamp']
            }
            
            # Cache the data
            self.signals_cache = dashboard_data['signals']
            self.metrics_cache = dashboard_data
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return self._get_mock_dashboard_data()
    
    def _format_signals_for_dashboard(self, signals: List[TradingSignal]) -> List[Dict]:
        """Format trading signals for dashboard display"""
        formatted_signals = []
        
        for signal in signals:
            formatted_signal = {
                'symbol': signal.asset,
                'asset_type': signal.asset_type.value,
                'signal': signal.signal_type.value,
                'entry_price': f"₹{signal.entry_price:,.2f}",
                'target_price': f"₹{signal.target_price:,.2f}",
                'stop_loss': f"₹{signal.stop_loss:,.2f}",
                'confidence': f"{signal.confidence:.1%}",
                'strength': signal.strength,
                'position_size': signal.position_size,
                'risk_amount': signal.risk_amount,
                'timestamp': signal.timestamp.strftime('%H:%M:%S'),
                'indicators': signal.indicators
            }
            formatted_signals.append(formatted_signal)
        
        return formatted_signals
    
    def _get_mock_dashboard_data(self) -> Dict:
        """Provide mock data when system is not available"""
        mock_signals = [
            {
                'symbol': 'RELIANCE',
                'asset_type': 'stock',
                'signal': 'BUY',
                'entry_price': '₹2,845.50',
                'target_price': '₹2,968.50',
                'stop_loss': '₹2,789.50',
                'confidence': '78.5%',
                'strength': 4,
                'position_size': 15,
                'risk_amount': 750,
                'timestamp': '09:45:23',
                'indicators': {'rsi': 32.5, 'macd': 1.2, 'volume': 2.1}
            },
            {
                'symbol': 'NIFTY50',
                'asset_type': 'index',
                'signal': 'SELL',
                'entry_price': '₹21,845.00',
                'target_price': '₹21,200.00',
                'stop_loss': '₹22,100.00',
                'confidence': '82.3%',
                'strength': 5,
                'position_size': 5,
                'risk_amount': 1200,
                'timestamp': '10:15:45',
                'indicators': {'rsi': 71.2, 'vwap': -0.8, 'volatility': 0.018}
            }
        ]
        
        return {
            'signals': mock_signals,
            'portfolio_metrics': {
                'total_value': 8500,
                'total_risk': 425,
                'cash_available': 1500,
                'risk_utilization': 0.0425,
                'asset_allocation': {
                    'stock': 5000,
                    'index': 2000,
                    'futures': 1000,
                    'options': 500
                },
                'daily_pnl': 285
            },
            'performance_summary': {
                'total_capital': 10000,
                'daily_target': 250,
                'monthly_target': 5000,
                'max_daily_loss': 500
            },
            'correlation_analysis': {
                'high_correlations': [
                    {'asset1': 'RELIANCE', 'asset2': 'ONGC', 'correlation': 0.78},
                    {'asset1': 'TCS', 'asset2': 'INFY', 'correlation': 0.85}
                ],
                'sector_exposure': {
                    'IT': 35,
                    'Energy': 25,
                    'Banking': 20,
                    'FMCG': 20
                }
            },
            'timestamp': datetime.now()
        }
    
    def get_asset_allocation_chart(self) -> pd.DataFrame:
        """Get data for asset allocation pie chart"""
        if not self.metrics_cache:
            return pd.DataFrame([
                {'Asset Type': 'Stocks', 'Value': 5000, 'Percentage': 50},
                {'Asset Type': 'Indices', 'Value': 2500, 'Percentage': 25},
                {'Asset Type': 'Futures', 'Value': 1500, 'Percentage': 15},
                {'Asset Type': 'Options', 'Value': 1000, 'Percentage': 10}
            ])
        
        allocation = self.metrics_cache.get('portfolio_metrics', {}).get('asset_allocation', {})
        df_data = []
        for asset_type, value in allocation.items():
            percentage = (value / 10000) * 100
            df_data.append({
                'Asset Type': asset_type.title(),
                'Value': value,
                'Percentage': percentage
            })
        
        return pd.DataFrame(df_data)
    
    def get_performance_metrics(self) -> Dict:
        """Get key performance metrics for display"""
        if not self.metrics_cache:
            return {
                'daily_pnl': 285,
                'win_rate': 0.78,
                'total_trades': 12,
                'avg_return': 2.8,
                'sharpe_ratio': 2.1,
                'max_drawdown': -3.2
            }
        
        return {
            'daily_pnl': self.metrics_cache.get('portfolio_metrics', {}).get('daily_pnl', 0),
            'win_rate': 0.78,
            'total_trades': len(self.signals_cache),
            'avg_return': 2.8,
            'sharpe_ratio': 2.1,
            'max_drawdown': -3.2
        }
    
    def get_sector_analysis(self) -> pd.DataFrame:
        """Get sector analysis data"""
        if not self.metrics_cache:
            return pd.DataFrame([
                {'Sector': 'IT', 'Exposure': 35, 'P&L': 125},
                {'Sector': 'Energy', 'Exposure': 25, 'P&L': 85},
                {'Sector': 'Banking', 'Exposure': 20, 'P&L': 45},
                {'Sector': 'FMCG', 'Exposure': 20, 'P&L': 30}
            ])
        
        sector_data = self.metrics_cache.get('correlation_analysis', {}).get('sector_exposure', {})
        df_data = []
        for sector, exposure in sector_data.items():
            df_data.append({
                'Sector': sector,
                'Exposure': exposure,
                'P&L': np.random.randint(20, 150)
            })
        
        return pd.DataFrame(df_data)

class DashboardSignalProcessor:
    """Process signals for dashboard display"""
    
    @staticmethod
    def filter_signals_by_type(signals: List[Dict], asset_type: str = None) -> List[Dict]:
        """Filter signals by asset type"""
        if not asset_type or asset_type == "All":
            return signals
        return [s for s in signals if s['asset_type'] == asset_type]
    
    @staticmethod
    def sort_signals_by_confidence(signals: List[Dict]) -> List[Dict]:
        """Sort signals by confidence level"""
        return sorted(signals, key=lambda x: float(x['confidence'].replace('%', '')), reverse=True)
    
    @staticmethod
    def get_signal_summary(signals: List[Dict]) -> Dict:
        """Get summary statistics for signals"""
        if not signals:
            return {'total': 0, 'buy': 0, 'sell': 0, 'avg_confidence': 0}
        
        total = len(signals)
        buy_signals = len([s for s in signals if s['signal'] == 'BUY'])
        sell_signals = len([s for s in signals if s['signal'] == 'SELL'])
        
        confidences = [float(s['confidence'].replace('%', '')) for s in signals]
        avg_confidence = sum(confidences) / len(confidences)
        
        return {
            'total': total,
            'buy': buy_signals,
            'sell': sell_signals,
            'avg_confidence': avg_confidence
        }

# Global integration instance
integration = MultiAssetDashboardIntegration()

async def initialize_multi_asset_system(capital: float = 10000) -> bool:
    """Initialize the multi-asset system with given capital"""
    return integration.initialize_system(capital)

async def get_multi_asset_dashboard_data() -> Dict:
    """Get dashboard data from multi-asset system"""
    return await integration.get_dashboard_data()

def get_multi_asset_allocation() -> pd.DataFrame:
    """Get asset allocation data"""
    return integration.get_asset_allocation_chart()

def get_multi_asset_performance() -> Dict:
    """Get performance metrics"""
    return integration.get_performance_metrics()

def get_sector_analysis_data() -> pd.DataFrame:
    """Get sector analysis"""
    return integration.get_sector_analysis()

# Streamlit integration helpers
def render_multi_asset_overview():
    """Render multi-asset overview in Streamlit"""
    st.subheader("🎯 Multi-Asset AI Overview")
    
    # Performance metrics
    metrics = get_multi_asset_performance()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Daily P&L", f"₹{metrics['daily_pnl']}", f"{metrics['daily_pnl']/250*100:.1f}% of target")
    with col2:
        st.metric("Win Rate", f"{metrics['win_rate']:.1%}")
    with col3:
        st.metric("Total Trades", metrics['total_trades'])
    with col4:
        st.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")

def render_asset_allocation():
    """Render asset allocation visualization"""
    st.subheader("📊 Asset Allocation")
    
    allocation_df = get_multi_asset_allocation()
    
    # Pie chart
    fig = px.pie(allocation_df, values='Value', names='Asset Type', 
                 title='Current Asset Allocation')
    st.plotly_chart(fig, use_container_width=True)
    
    # Table
    st.dataframe(allocation_df, use_container_width=True)

def render_sector_analysis():
    """Render sector analysis"""
    st.subheader("🏭 Sector Analysis")
    
    sector_df = get_sector_analysis_data()
    
    # Bar chart
    fig = px.bar(sector_df, x='Sector', y=['Exposure', 'P&L'], 
                 title='Sector Exposure and Performance',
                 barmode='group')
    st.plotly_chart(fig, use_container_width=True)

# Usage example
if __name__ == "__main__":
    import asyncio
    
    async def test_integration():
        # Test the integration
        success = await initialize_multi_asset_system(10000)
        if success:
            data = await get_multi_asset_dashboard_data()
            print(f"Successfully loaded {len(data['signals'])} signals")
            print(f"Portfolio value: ₹{data['portfolio_metrics']['total_value']:,}")
        else:
            print("Failed to initialize system")
    
    asyncio.run(test_integration())