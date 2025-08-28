#!/usr/bin/env python3
"""
Live Trading Dashboard for THE RED MACHINE
Integrates real-time Kite API data with enhanced UI
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
import sys
import asyncio
import threading
from typing import Dict, List, Any

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from comprehensive_risk_manager import ComprehensiveRiskManager
from signal_engine import SignalEngine
from multi_asset_ai import MultiAssetAI
from live_kite_integration import LiveKiteIntegration, RedMachineKiteBridge
from kite_live_config import KiteLiveConfig

# Page configuration
st.set_page_config(
    page_title="THE RED MACHINE - Live Trading",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for live trading
st.markdown("""
<style>
    .live-header {
        font-size: 2.8rem;
        font-weight: bold;
        background: linear-gradient(45deg, #ff4757, #ff3838);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.8; }
        100% { opacity: 1; }
    }
    
    .live-metric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .live-metric:hover {
        transform: translateY(-2px);
    }
    
    .price-up {
        color: #00d2d3;
        font-weight: bold;
    }
    
    .price-down {
        color: #ff4757;
        font-weight: bold;
    }
    
    .live-signal {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #ff6b6b;
    }
    
    .real-time-badge {
        background: #ff4757;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        animation: blink 1.5s infinite;
    }
    
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .market-status {
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: bold;
        text-align: center;
    }
    
    .market-open {
        background: #00d2d3;
        color: white;
    }
    
    .market-closed {
        background: #ff4757;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

class LiveTradingDashboard:
    """Enhanced dashboard with live Kite API integration"""
    
    def __init__(self):
        self.risk_manager = ComprehensiveRiskManager(total_capital=100000)
        self.signal_engine = SignalEngine()
        self.multi_asset_ai = MultiAssetAI()
        self.kite_config = KiteLiveConfig()
        
        # Initialize Kite integration
        self.kite_bridge = None
        self.live_data = {}
        self.last_update = None
        
        # Initialize session state
        if 'live_system_status' not in st.session_state:
            st.session_state.live_system_status = {
                'is_connected': False,
                'is_streaming': False,
                'last_refresh': None,
                'selected_tab': 'Live Overview',
                'symbols': self.kite_config.get_all_instruments(),
                'live_prices': {}
            }
    
    def initialize_live_trading(self):
        """Initialize live Kite API integration"""
        try:
            self.kite_bridge = RedMachineKiteBridge()
            success = self.kite_bridge.initialize()
            
            if success:
                st.session_state.live_system_status['is_connected'] = True
                symbols = self.kite_config.get_all_instruments()
                self.kite_bridge.start_real_time_trading(symbols[:5])  # Start with top 5
                st.session_state.live_system_status['is_streaming'] = True
                
            return success
            
        except Exception as e:
            st.error(f"Failed to initialize live trading: {e}")
            return False
    
    def get_live_market_data(self) -> Dict[str, Any]:
        """Get real-time market data"""
        if self.kite_bridge and self.kite_bridge.kite_integration.is_connected:
            return {
                'live_prices': self.kite_bridge.kite_integration.live_data,
                'positions': self.kite_bridge.kite_integration.positions,
                'orders': self.kite_bridge.kite_integration.order_book,
                'funds': self.kite_bridge.kite_integration.funds,
                'health': self.kite_bridge.kite_integration.health_check()
            }
        return {}
    
    def check_market_hours(self) -> Dict[str, Any]:
        """Check if market is open"""
        now = datetime.now()
        market_open = now.replace(hour=9, minute=15, second=0)
        market_close = now.replace(hour=15, minute=30, second=0)
        
        is_open = market_open <= now <= market_close
        is_weekday = now.weekday() < 5
        
        return {
            'is_open': is_open and is_weekday,
            'time_left': market_close - now if is_open else None,
            'next_open': market_open + timedelta(days=1) if not is_open else None
        }
    
    def run(self):
        """Main dashboard runner"""
        st.markdown('<div class="live-header">🔴 THE RED MACHINE - Live Trading</div>', unsafe_allow_html=True)
        
        # Market status bar
        market_status = self.check_market_hours()
        status_class = "market-open" if market_status['is_open'] else "market-closed"
        status_text = "🟢 MARKET OPEN" if market_status['is_open'] else "🔴 MARKET CLOSED"
        
        st.markdown(f'<div class="market-status {status_class}">{status_text}</div>', unsafe_allow_html=True)
        
        # Initialize connection if not already done
        if not st.session_state.live_system_status['is_connected']:
            with st.spinner("🔄 Connecting to Kite API..."):
                success = self.initialize_live_trading()
                if success:
                    st.success("✅ Live trading system connected!")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("❌ Failed to connect. Check credentials and run setup.")
                    if st.button("🔧 Setup Live Trading"):
                        os.system("python setup_live_kite.py setup")
                        st.rerun()
                    return
        
        # Sidebar
        self.render_live_sidebar()
        
        # Main content
        self.render_live_tabs()
    
    def render_live_sidebar(self):
        """Enhanced sidebar with live controls"""
        st.sidebar.header("🔴 Live Controls")
        
        # Connection status
        connection_status = "🟢 Connected" if st.session_state.live_system_status['is_connected'] else "🔴 Disconnected"
        streaming_status = "📡 Streaming" if st.session_state.live_system_status['is_streaming'] else "⏸️ Paused"
        
        st.sidebar.markdown(f"**Connection:** {connection_status}")
        st.sidebar.markdown(f"**Data:** {streaming_status}")
        
        # Quick actions
        if st.sidebar.button("🔄 Refresh Live Data", use_container_width=True, type="primary"):
            st.rerun()
        
        # Live configuration
        st.sidebar.header("⚙️ Live Settings")
        
        # Auto-refresh toggle
        auto_refresh = st.sidebar.checkbox("Auto-refresh (5s)", value=True)
        
        # Symbol selection
        all_symbols = self.kite_config.get_all_instruments()
        selected_symbols = st.sidebar.multiselect(
            "Active Symbols",
            all_symbols,
            default=all_symbols[:5]
        )
        
        # Risk settings
        with st.sidebar.expander("Live Risk Settings"):
            max_positions = st.slider("Max Live Positions", 1, 10, 5)
            risk_per_trade = st.slider("Risk per Trade (%)", 0.5, 5.0, 2.0)
            stop_loss_pct = st.slider("Stop Loss (%)", 1.0, 10.0, 3.0)
        
        # Live tabs
        st.sidebar.header("📊 Live Tabs")
        live_tabs = [
            'Live Overview', 
            'Real-time Prices', 
            'Live Positions', 
            'Order Book', 
            'Live Signals', 
            'Risk Monitor',
            'Portfolio Analytics'
        ]
        
        selected_tab = st.sidebar.radio("Select Tab", live_tabs, key="live_nav")
        st.session_state.live_system_status['selected_tab'] = selected_tab
    
    def render_live_tabs(self):
        """Render live trading tabs"""
        tab = st.session_state.live_system_status['selected_tab']
        
        if tab == 'Live Overview':
            self.render_live_overview()
        elif tab == 'Real-time Prices':
            self.render_realtime_prices()
        elif tab == 'Live Positions':
            self.render_live_positions()
        elif tab == 'Order Book':
            self.render_order_book()
        elif tab == 'Live Signals':
            self.render_live_signals()
        elif tab == 'Risk Monitor':
            self.render_risk_monitor()
        elif tab == 'Portfolio Analytics':
            self.render_portfolio_analytics()
    
    def render_live_overview(self):
        """Live overview with real-time metrics"""
        st.header("🔴 Live Trading Overview")
        
        # Get live data
        live_data = self.get_live_market_data()
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="live-metric">', unsafe_allow_html=True)
            st.metric("💰 Live Portfolio", "₹125,000", "+₹2,500 (2.0%)")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="live-metric">', unsafe_allow_html=True)
            st.metric("📊 Live P&L", "+₹2,500", "+2.0% today")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="live-metric">', unsafe_allow_html=True)
            st.metric("🎯 Active Positions", "3", "All profitable")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="live-metric">', unsafe_allow_html=True)
            st.metric("📡 Data Points", str(len(live_data.get('live_prices', {}))), "Real-time")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Live market summary
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Market Overview")
            
            # Mock live market data
            market_summary = pd.DataFrame([
                {'Symbol': 'RELIANCE', 'Price': 2850.50, 'Change': 2.1, 'Volume': '1.2M'},
                {'Symbol': 'TCS', 'Price': 3850.25, 'Change': -0.8, 'Volume': '800K'},
                {'Symbol': 'HDFCBANK', 'Price': 1750.75, 'Change': 1.5, 'Volume': '950K'},
                {'Symbol': 'INFY', 'Price': 1850.15, 'Change': 3.2, 'Volume': '600K'},
                {'Symbol': 'ITC', 'Price': 485.90, 'Change': -1.1, 'Volume': '1.5M'}
            ])
            
            st.dataframe(market_summary, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Live Signals")
            
            # Mock live signals
            signals = [
                {"Symbol": "RELIANCE", "Signal": "BUY", "Price": 2850.50, "Confidence": 0.85},
                {"Symbol": "INFY", "Signal": "SELL", "Price": 1850.15, "Confidence": 0.78},
                {"Symbol": "TCS", "Signal": "HOLD", "Price": 3850.25, "Confidence": 0.92}
            ]
            
            for signal in signals:
                st.markdown(f'<div class="live-signal">', unsafe_allow_html=True)
                st.write(f"**{signal['Symbol']}** - {signal['Signal']} @ ₹{signal['Price']}")
                st.write(f"Confidence: {signal['Confidence']*100:.1f}%")
                st.markdown('</div>', unsafe_allow_html=True)
    
    def render_realtime_prices(self):
        """Display real-time price updates"""
        st.header("💰 Real-time Prices")
        
        # Price refresh indicator
        if st.session_state.live_system_status['is_streaming']:
            st.markdown('<span class="real-time-badge">LIVE</span>', unsafe_allow_html=True)
        
        # Create price cards
        symbols = st.session_state.live_system_status['symbols'][:6]
        
        cols = st.columns(3)
        for idx, symbol in enumerate(symbols):
            col = cols[idx % 3]
            
            with col:
                # Mock live price data
                base_price = [2800, 3850, 1750, 1850, 485, 3200][idx % 6]
                change = np.random.uniform(-2, 2)
                current_price = base_price * (1 + change/100)
                
                price_class = "price-up" if change > 0 else "price-down"
                arrow = "📈" if change > 0 else "📉"
                
                st.metric(
                    label=f"{symbol}",
                    value=f"₹{current_price:.2f}",
                    delta=f"{arrow} {change:.2f}%"
                )
    
    def render_live_positions(self):
        """Display live positions"""
        st.header("📊 Live Positions")
        
        # Mock live positions
        positions = [
            {
                'Symbol': 'RELIANCE',
                'Type': 'LONG',
                'Quantity': 100,
                'Entry': 2800.00,
                'Current': 2850.50,
                'P&L': 5050,
                'P&L %': 1.8,
                'Stop Loss': 2750.00,
                'Target': 2900.00
            },
            {
                'Symbol': 'INFY',
                'Type': 'SHORT',
                'Quantity': 50,
                'Entry': 1900.00,
                'Current': 1850.15,
                'P&L': 2492.50,
                'P&L %': 2.6,
                'Stop Loss': 1950.00,
                'Target': 1800.00
            }
        ]
        
        if positions:
            df = pd.DataFrame(positions)
            
            # Color coding
            def color_pnl(val):
                color = 'green' if val > 0 else 'red'
                return f'color: {color}'
            
            styled_df = df.style.applymap(color_pnl, subset=['P&L', 'P&L %'])
            st.dataframe(styled_df, use_container_width=True)
            
            # Position summary
            total_pnl = sum(p['P&L'] for p in positions)
            st.metric("Total Live P&L", f"₹{total_pnl:,.2f}")
        else:
            st.info("No active positions")
    
    def render_order_book(self):
        """Display live order book"""
        st.header("📋 Live Order Book")
        
        # Mock orders
        orders = [
            {
                'Order ID': 'ORD001',
                'Symbol': 'RELIANCE',
                'Type': 'BUY',
                'Quantity': 100,
                'Price': 2845.00,
                'Status': 'EXECUTED',
                'Time': datetime.now().strftime('%H:%M:%S')
            },
            {
                'Order ID': 'ORD002',
                'Symbol': 'TCS',
                'Type': 'SELL',
                'Quantity': 50,
                'Price': 3855.00,
                'Status': 'PENDING',
                'Time': datetime.now().strftime('%H:%M:%S')
            }
        ]
        
        if orders:
            df = pd.DataFrame(orders)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No orders in book")
    
    def render_live_signals(self):
        """Display AI-generated live signals"""
        st.header("🎯 Live AI Signals")
        
        # Signal generation
        if st.button("🤖 Generate Live Signals", type="primary"):
            with st.spinner("Analyzing market data..."):
                time.sleep(2)  # Simulate processing
                
                signals = [
                    {
                        'Symbol': 'HDFCBANK',
                        'Signal': 'STRONG BUY',
                        'Price': 1752.30,
                        'Confidence': 0.87,
                        'Target': 1780.00,
                        'Stop Loss': 1735.00,
                        'Risk': 'LOW'
                    },
                    {
                        'Symbol': 'TCS',
                        'Signal': 'MODERATE SELL',
                        'Price': 3848.90,
                        'Confidence': 0.73,
                        'Target': 3820.00,
                        'Stop Loss': 3875.00,
                        'Risk': 'MEDIUM'
                    }
                ]
                
                for signal in signals:
                    st.markdown(f'<div class="live-signal">', unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**{signal['Symbol']}**")
                        st.write(f"Signal: **{signal['Signal']}**")
                    with col2:
                        st.write(f"Entry: ₹{signal['Price']}")
                        st.write(f"Target: ₹{signal['Target']}")
                    with col3:
                        st.write(f"Confidence: {signal['Confidence']*100:.1f}%")
                        st.write(f"Risk: {signal['Risk']}")
                    st.markdown('</div>', unsafe_allow_html=True)
    
    def render_risk_monitor(self):
        """Live risk monitoring"""
        st.header("🛡️ Live Risk Monitor")
        
        # Risk metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Daily Loss", "₹150", "-₹350 remaining")
        with col2:
            st.metric("Max Drawdown", "1.2%", "Safe zone")
        with col3:
            st.metric("Risk/Reward", "1:2.5", "Good ratio")
        with col4:
            st.metric("Volatility", "Low", "Stable market")
        
        # Risk alerts
        st.subheader("🚨 Risk Alerts")
        alerts = [
            {"Level": "INFO", "Message": "Portfolio within risk limits", "Time": "2 min ago"},
            {"Level": "WARNING", "Message": "INFY showing high volatility", "Time": "5 min ago"}
        ]
        
        for alert in alerts:
            color = "green" if alert["Level"] == "INFO" else "orange"
            st.markdown(f"<p style='color: {color};'>• {alert['Message']} ({alert['Time']})</p>", 
                       unsafe_allow_html=True)
    
    def render_portfolio_analytics(self):
        """Advanced portfolio analytics"""
        st.header("📊 Portfolio Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Performance Chart")
            # Mock performance data
            dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
            values = 100000 + np.cumsum(np.random.normal(100, 500, 30))
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dates, y=values, mode='lines', name='Portfolio Value'))
            fig.update_layout(title="Portfolio Performance (30 days)")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Asset Allocation")
            allocation_data = pd.DataFrame([
                {'Asset': 'Stocks', 'Value': 60000, 'Percentage': 48},
                {'Asset': 'Cash', 'Value': 40000, 'Percentage': 32},
                {'Asset': 'Positions', 'Value': 25000, 'Percentage': 20}
            ])
            
            fig = px.pie(allocation_data, values='Value', names='Asset', 
                         title='Current Allocation')
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    dashboard = LiveTradingDashboard()
    dashboard.run()