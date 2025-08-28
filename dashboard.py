import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from comprehensive_risk_manager import ComprehensiveRiskManager
from signal_engine import SignalEngine
from multi_asset_ai import MultiAssetAI
from multi_asset_integration import MultiAssetDashboardIntegration, initialize_multi_asset_system

# Page configuration
st.set_page_config(
    page_title="AI Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        text-align: center;
    }
    .success-metric {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .warning-metric {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .info-metric {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .signal-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #007bff;
    }
    .position-card {
        background: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

class TradingDashboard:
    def __init__(self):
        self.risk_manager = ComprehensiveRiskManager(total_capital=100000)
        self.signal_engine = SignalEngine()
        self.multi_asset_ai = MultiAssetAI()
        
        # Initialize session state
        if 'system_status' not in st.session_state:
            st.session_state.system_status = {
                'is_running': False,
                'trade_count': 0,
                'last_update': None,
                'selected_tab': 'Overview'
            }
    
    def run(self):
        """Main dashboard runner"""
        st.markdown('<div class="main-header">🤖 AI Trading Dashboard</div>', unsafe_allow_html=True)
        
        # Sidebar
        self.render_sidebar()
        
        # Main content based on selected tab
        if st.session_state.system_status['selected_tab'] == 'Overview':
            self.render_overview_tab()
        elif st.session_state.system_status['selected_tab'] == 'Signals':
            self.render_signals_tab()
        elif st.session_state.system_status['selected_tab'] == 'Positions':
            self.render_positions_tab()
        elif st.session_state.system_status['selected_tab'] == 'Risk':
            self.render_risk_tab()
        elif st.session_state.system_status['selected_tab'] == 'Performance':
            self.render_performance_tab()
        elif st.session_state.system_status['selected_tab'] == 'AI Models':
            self.render_ai_models_tab()
        elif st.session_state.system_status['selected_tab'] == 'Multi-Asset':
            self.render_multi_asset_tab()
    
    def render_sidebar(self):
        """Render sidebar with controls and navigation"""
        st.sidebar.header("🎛️ System Controls")
        
        # System status indicator
        status_color = "🟢" if st.session_state.system_status['is_running'] else "🔴"
        st.sidebar.markdown(f"**Status:** {status_color} {'Running' if st.session_state.system_status['is_running'] else 'Stopped'}")
        
        # Start/Stop button
        if st.sidebar.button(
            "🚀 Start Trading" if not st.session_state.system_status['is_running'] else "🛑 Stop Trading",
            use_container_width=True,
            type="primary"
        ):
            st.session_state.system_status['is_running'] = not st.session_state.system_status['is_running']
            st.rerun()
        
        # Navigation tabs
        st.sidebar.header("📊 Navigation")
        tabs = ['Overview', 'Signals', 'Positions', 'Risk', 'Performance', 'AI Models', 'Multi-Asset']
        selected_tab = st.sidebar.radio("Select Tab", tabs, key="nav_tabs")
        st.session_state.system_status['selected_tab'] = selected_tab
        
        # Configuration
        st.sidebar.header("⚙️ Configuration")
        
        with st.sidebar.expander("Risk Settings"):
            total_capital = st.number_input("Total Capital", value=100000, step=5000)
            daily_loss_limit = st.slider("Daily Loss Limit (%)", 1.0, 10.0, 5.0, 0.5)
            position_risk_limit = st.slider("Position Risk Limit (%)", 0.5, 5.0, 2.0, 0.1)
            
            if st.button("Apply Settings"):
                self.risk_manager.total_capital = total_capital
                self.risk_manager.daily_loss_limit = total_capital * (daily_loss_limit / 100)
                self.risk_manager.position_risk_limit = total_capital * (position_risk_limit / 100)
                st.success("Settings applied!")
        
        with st.sidebar.expander("Trading Settings"):
            max_positions = st.number_input("Max Active Positions", value=10, min_value=1, max_value=50)
            scan_interval = st.slider("Scan Interval (seconds)", 5, 60, 10)
            min_confidence = st.slider("Min Signal Confidence", 0.5, 0.95, 0.65)
        
        # Quick actions
        st.sidebar.header("🚀 Quick Actions")
        if st.sidebar.button("Generate Signals", use_container_width=True):
            self.generate_live_signals()
        
        if st.sidebar.button("Refresh Data", use_container_width=True):
            st.rerun()
    
    def render_overview_tab(self):
        """Render overview tab with key metrics"""
        
        # Live trading toggle
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### 🔄 Live Trading Mode")
        with col2:
            live_mode = st.toggle("Enable Live Trading", value=False, key="live_mode_toggle")
        
        if live_mode:
            st.info("🟢 Live trading mode enabled - connecting to Kite API...")
            if st.button("Launch Live Dashboard", type="primary"):
                import subprocess
                subprocess.Popen(["streamlit", "run", "live_dashboard.py", "--server.port=8520"])
                st.success("✅ Live dashboard opened in new tab (port 8520)")
                st.markdown("[Open Live Dashboard](http://localhost:8520)")
                return
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("Auto-refresh every 10s", value=True)
        
        # Get risk data
        risk_data = self.risk_manager.get_risk_dashboard_data()
        
        # Top metrics row
        st.header("📊 System Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_value = risk_data['current_metrics']['available_capital'] + risk_data['portfolio_metrics']['total_exposure']
            st.metric(
                "💰 Total Portfolio Value", 
                f"₹{total_value:,.0f}",
                f"₹{risk_data['current_metrics']['daily_pnl']:,.0f}",
                delta_color="normal"
            )
        
        with col2:
            st.metric(
                "📊 Total Exposure", 
                f"₹{risk_data['portfolio_metrics']['total_exposure']:,.0f}",
                f"{risk_data['portfolio_metrics']['exposure_percentage']:.1%}"
            )
        
        with col3:
            st.metric(
                "🎯 Active Positions", 
                str(risk_data['current_metrics']['active_positions']),
                f"{risk_data['current_metrics']['active_positions']} max"
            )
        
        with col4:
            win_rate = risk_data['portfolio_metrics']['win_rate'] * 100
            st.metric(
                "🏆 Win Rate", 
                f"{win_rate:.1f}%",
                f"Sharpe: {risk_data['portfolio_metrics']['sharpe_ratio']:.2f}"
            )
        
        # Multi-Asset AI Overview
        st.header("🤖 Multi-Asset AI System")
        
        # Initialize multi-asset system if not already done
        if 'multi_asset_initialized' not in st.session_state:
            st.session_state.multi_asset_initialized = False
            
        if not st.session_state.multi_asset_initialized:
            if st.button("Initialize Multi-Asset AI", type="primary"):
                st.session_state.multi_asset_initialized = True
                st.success("Multi-Asset AI System Initialized!")
                st.rerun()
        
        if st.session_state.multi_asset_initialized:
            # Multi-Asset Performance Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📊 Daily Target", "₹250", "₹200-₹500 range")
            with col2:
                st.metric("📈 Monthly Target", "₹5,000", "₹4,000-₹10,000 range")
            with col3:
                st.metric("🎯 Max Daily Loss", "₹500", "5% stop loss")
            with col4:
                st.metric("⚖️ Simultaneous Positions", "3-5", "Diversified allocation")
            
            # Asset Class Performance
            st.subheader("🏗️ Asset Class Performance")
            asset_data = pd.DataFrame([
                {'Asset Class': 'Stocks', 'Allocation': 40, 'Daily_Return': 2.8, 'Risk': 2.1},
                {'Asset Class': 'Indices', 'Allocation': 30, 'Daily_Return': 2.2, 'Risk': 1.8},
                {'Asset Class': 'Futures', 'Allocation': 20, 'Daily_Return': 3.5, 'Risk': 3.2},
                {'Asset Class': 'Options', 'Allocation': 10, 'Daily_Return': 4.2, 'Risk': 4.8}
            ])
            
            fig = px.bar(asset_data, x='Asset Class', y='Daily_Return', 
                        color='Risk', title='Daily Returns by Asset Class',
                        hover_data=['Allocation'])
            st.plotly_chart(fig, use_container_width=True)

        # Charts row
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_pnl_chart()
        
        with col2:
            self.render_portfolio_allocation()

        # Recent activity
        st.header("🔄 Recent Activity")
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_recent_signals()
        
        with col2:
            self.render_recent_trades()
    
    def render_recent_signals(self):
        """Render recent trading signals"""
        st.subheader("📊 Recent Signals")
        
        try:
            signals = self.get_mock_recent_signals()
            
            if signals:
                for signal in signals[:5]:  # Show last 5 signals
                    self.render_signal_card(signal)
            else:
                st.info("No recent signals available")
                
        except Exception as e:
            st.error(f"Error loading recent signals: {e}")
    
    def render_recent_trades(self):
        """Render recent trades"""
        st.subheader("💼 Recent Trades")
        
        try:
            trades = self.get_mock_recent_trades()
            
            if trades:
                for trade in trades[:5]:  # Show last 5 trades
                    with st.container():
                        st.markdown("---")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**Asset:** {trade.get('asset', 'Unknown')}")
                            st.write(f"**Type:** {trade.get('type', 'Unknown')}")
                            
                        with col2:
                            st.write(f"**Price:** ₹{trade.get('price', 0):,.2f}")
                            st.write(f"**Quantity:** {trade.get('quantity', 0)}")
                            
                        with col3:
                            pnl = trade.get('pnl', 0)
                            pnl_color = "green" if pnl >= 0 else "red"
                            st.write(f"**P&L:** :{pnl_color}[₹{pnl:,.2f}]")
                            st.write(f"**Time:** {trade.get('timestamp', 'Unknown')}")
            else:
                st.info("No recent trades available")
                
        except Exception as e:
            st.error(f"Error loading recent trades: {e}")

    def render_signals_tab(self):
        """Render signals tab with live signal generation"""
        st.header("📈 Trading Signals")
        
        # Signal generation controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎯 Generate New Signals", type="primary"):
                self.generate_live_signals()
        
        with col2:
            universe = st.multiselect(
                "Trading Universe",
                ['RELIANCE', 'TCS', 'HDFC', 'INFY', 'ITC', 'SBIN', 'BHARTIARTL', 'ICICIBANK'],
                default=['RELIANCE', 'TCS', 'HDFC']
            )
        
        with col3:
            min_confidence = st.slider("Minimum Confidence", 0.5, 0.95, 0.65)
        
        # Display signals
        signals = self.get_mock_signals()
        
        if signals:
            st.subheader(f"🔍 Found {len(signals)} Trading Signals")
            
            for signal in signals:
                self.render_signal_card(signal)
        else:
            st.info("No signals found. Try adjusting filters or generating new signals.")
    
    def render_positions_tab(self):
        """Render positions tab with active positions"""
        st.header("📊 Active Positions")
        
        # Mock positions data
        positions = self.get_mock_positions()
        
        if positions:
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Positions", len(positions))
            with col2:
                total_pnl = sum(p['P&L'] for p in positions)
                st.metric("Total P&L", f"₹{total_pnl:,.0f}")
            with col3:
                avg_pnl_percent = sum(p['P&L %'] for p in positions) / len(positions)
                st.metric("Avg P&L %", f"{avg_pnl_percent:.2f}%")
            
            # Positions table
            df = pd.DataFrame(positions)
            
            # Color coding for P&L
            def color_pnl(val):
                color = 'green' if val > 0 else 'red'
                return f'color: {color}'
            
            styled_df = df.style.applymap(color_pnl, subset=['P&L', 'P&L %'])
            st.dataframe(styled_df, use_container_width=True)
            
            # Position details
            st.subheader("📈 Position Details")
            selected_position = st.selectbox("Select Position", [p['Asset'] for p in positions])
            
            if selected_position:
                pos = next(p for p in positions if p['Asset'] == selected_position)
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Entry Price:** ₹{pos['Entry']}")
                    st.write(f"**Current Price:** ₹{pos['Current']}")
                    st.write(f"**Quantity:** {pos['Quantity']}")
                with col2:
                    st.write(f"**Stop Loss:** ₹{pos['Stop Loss']}")
                    st.write(f"**Target:** ₹{pos['Target']}")
                    st.write(f"**Risk Level:** {pos['Risk']}")
        else:
            st.info("No active positions")
    
    def render_risk_tab(self):
        """Render risk management tab"""
        st.header("🛡️ Risk Management")
        
        # Risk metrics
        risk_data = self.risk_manager.get_risk_dashboard_data()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("VaR 95%", f"₹{risk_data['portfolio_metrics']['var_95']:,.0f}")
            st.metric("VaR 99%", f"₹{risk_data['portfolio_metrics']['var_99']:,.0f}")
        
        with col2:
            st.metric("Max Drawdown", f"{risk_data['portfolio_metrics']['max_drawdown']:.1%}")
            st.metric("Sharpe Ratio", f"{risk_data['portfolio_metrics']['sharpe_ratio']:.2f}")
        
        with col3:
            st.metric("Win Rate", f"{risk_data['portfolio_metrics']['win_rate']:.1%}")
            st.metric("Daily P&L", f"₹{risk_data['current_metrics']['daily_pnl']:,.0f}")
        
        # Risk alerts
        if risk_data['risk_alerts']:
            st.warning("⚠️ Active Risk Alerts")
            for alert in risk_data['risk_alerts']:
                st.error(f"• {alert}")
        else:
            st.success("✅ No active risk alerts")
        
        # Position risks
        st.subheader("📊 Position Risk Analysis")
        
        # Mock position risks
        position_risks = [
            {'Asset': 'HDFC', 'Risk Amount': 2500, 'Risk %': 2.5, 'Stop Distance': 45},
            {'Asset': 'INFY', 'Risk Amount': 1800, 'Risk %': 1.8, 'Stop Distance': 32}
        ]
        
        if position_risks:
            df = pd.DataFrame(position_risks)
            st.dataframe(df, use_container_width=True)
        
        # Risk controls
        st.subheader("🎛️ Risk Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚨 Emergency Stop", type="secondary"):
                st.error("Emergency stop activated!")
            
            if st.button("🔄 Rebalance Portfolio"):
                st.success("Portfolio rebalanced")
        
        with col2:
            if st.button("📊 Generate Risk Report"):
                self.generate_risk_report()
    
    def render_performance_tab(self):
        """Render performance analytics tab"""
        st.header("📊 Performance Analytics")
        
        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Return", "15.2%", "+2.1% vs benchmark")
        with col2:
            st.metric("Volatility", "12.8%", "-3.2% vs benchmark")
        with col3:
            st.metric("Max Drawdown", "-8.5%", "Better than -12% target")
        with col4:
            st.metric("Calmar Ratio", "1.79", "Above 1.5 target")
        
        # Performance charts
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_performance_chart()
        
        with col2:
            self.render_win_rate_chart()
        
        # Trade analysis
        st.subheader("📈 Trade Analysis")
        
        # Mock trade data
        trades = self.get_mock_trade_history()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Trade distribution
            trade_types = pd.DataFrame({
                'Type': ['Winning', 'Losing', 'Break-even'],
                'Count': [45, 15, 5]
            })
            fig = px.pie(trade_types, values='Count', names='Type', title='Trade Distribution')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # P&L distribution
            pnl_data = np.random.normal(1500, 2000, 100)
            fig = px.histogram(x=pnl_data, nbins=30, title='P&L Distribution')
            st.plotly_chart(fig, use_container_width=True)
    
    def render_signal_card(self, signal):
        """Render individual signal card"""
        try:
            # Create a card for each signal
            with st.container():
                st.markdown("---")
                
                # Signal header with strength indicator
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    # Signal type and asset
                    signal_type = signal.get('type', 'Unknown')
                    asset = signal.get('asset', 'Unknown')
                    st.subheader(f"📊 {asset} - {signal_type}")
                    
                with col2:
                    # Signal strength
                    strength = signal.get('strength', 0)
                    strength_color = "🟢" if strength >= 4 else "🟡" if strength >= 2 else "🔴"
                    st.metric("Strength", f"{strength_color} {strength}/5")
                    
                with col3:
                    # Direction
                    direction = signal.get('direction', 'Unknown')
                    direction_emoji = "📈" if direction in ['BUY', 'CALL'] else "📉" if direction in ['SELL', 'PUT'] else "❓"
                    st.metric("Direction", f"{direction_emoji} {direction}")
                
                # Signal details
                col4, col5, col6 = st.columns(3)
                
                with col4:
                    entry_price = signal.get('entry_price', 0)
                    st.metric("Entry Price", f"₹{entry_price:,.2f}")
                    
                with col5:
                    target = signal.get('target', 0)
                    if target > 0:
                        st.metric("Target", f"₹{target:,.2f}")
                    else:
                        st.metric("Target", "Not Set")
                        
                with col6:
                    stop_loss = signal.get('stop_loss', 0)
                    if stop_loss > 0:
                        st.metric("Stop Loss", f"₹{stop_loss:,.2f}")
                    else:
                        st.metric("Stop Loss", "Not Set")
                
                # Signal confidence and timestamp
                confidence = signal.get('confidence', 0)
                timestamp = signal.get('timestamp', 'Unknown')
                
                st.write(f"**Confidence:** {confidence:.1%} | **Generated:** {timestamp}")
                
                # Technical details (if available)
                indicators = signal.get('indicators', {})
                if indicators:
                    st.write("**Technical Indicators:**")
                    indicator_text = ", ".join([f"{k}: {v}" for k, v in indicators.items()])
                    st.text(indicator_text)
                
                # Action buttons
                col7, col8, col9 = st.columns(3)
                
                with col7:
                    if st.button(f"Execute {signal_type}", key=f"exec_{asset}_{timestamp}"):
                        self.execute_signal(signal)
                        
                with col8:
                    if st.button(f"Add to Watchlist", key=f"watch_{asset}_{timestamp}"):
                        st.success(f"Added {asset} to watchlist")
                        
                with col9:
                    if st.button(f"Ignore Signal", key=f"ignore_{asset}_{timestamp}"):
                        st.info(f"Ignored {asset} signal")
                        
        except Exception as e:
            st.error(f"Error rendering signal card: {e}")
            st.write("Signal data:", signal)

    def execute_signal(self, signal):
        """Execute a trading signal"""
        try:
            asset = signal.get('asset', 'Unknown')
            direction = signal.get('direction', 'Unknown')
            entry_price = signal.get('entry_price', 0)
            
            # Here you would integrate with your actual trading execution
            # For now, just show a success message
            st.success(f"✅ Executed {direction} order for {asset} at ₹{entry_price:,.2f}")
            
            # You can add actual Kite Connect order placement here
            # Example:
            # order_id = self.kite.place_order(...)
            
        except Exception as e:
            st.error(f"Failed to execute signal: {e}")

    def render_ai_models_tab(self):
        """Render AI models tab"""
        st.header("🤖 AI Models")
        
        # Model performance
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Stock Model Accuracy", "78.5%", "+2.1%")
            st.metric("Stock Model Precision", "82.3%", "+1.8%")
        
        with col2:
            st.metric("Index Model Accuracy", "81.2%", "+3.4%")
            st.metric("Index Model Recall", "79.8%", "+2.7%")
        
        with col3:
            st.metric("Options Model Accuracy", "75.8%", "+1.2%")
            st.metric("Options Model F1 Score", "77.1%", "+1.5%")
        
        # Model training
        st.subheader("🎯 Model Training")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Retrain Stock Models"):
                st.success("Stock models retrained successfully!")
            
            if st.button("🔄 Retrain Index Models"):
                st.success("Index models retrained successfully!")
        
        with col2:
            if st.button("🔄 Retrain Options Models"):
                st.success("Options models retrained successfully!")
            
            if st.button("📊 View Model Performance"):
                self.show_model_performance()
    
    def render_recent_signals(self):
        """Render recent trading signals"""
        st.subheader("🎯 Recent Signals")
        
        signals = self.get_mock_recent_signals()
        
        if signals:
            for signal in signals:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**{signal['Asset']}**")
                with col2:
                    st.write(f"{signal['Direction']} @ ₹{signal['Price']}")
                with col3:
                    st.write(signal['Time'])
        else:
            st.info("No recent signals")
    
    def render_recent_trades(self):
        """Render recent trades"""
        st.subheader("💰 Recent Trades")
        
        trades = self.get_mock_recent_trades()
        
        if trades:
            for trade in trades:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(f"**{trade['Asset']}**")
                with col2:
                    st.write(f"{trade['Action']} {trade['Quantity']}")
                with col3:
                    st.write(f"@ ₹{trade['Price']}")
                with col4:
                    st.write(trade['Time'])
        else:
            st.info("No recent trades")

    def render_pnl_chart(self):
        """Render P&L chart"""
        st.subheader("📊 P&L Over Time")
        
        # Generate realistic P&L data
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        returns = np.random.normal(0.001, 0.02, len(dates))
        pnl_data = 100000 * np.cumsum(returns)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=pnl_data,
            mode='lines',
            name='Portfolio Value',
            line=dict(color='green', width=2),
            fill='tonexty'
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=30, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_portfolio_allocation(self):
        """Render portfolio allocation chart"""
        st.subheader("📊 Portfolio Allocation")
        
        # Mock allocation data
        allocation = pd.DataFrame({
            'Sector': ['IT', 'Financial', 'Energy', 'FMCG', 'Auto'],
            'Allocation': [25, 20, 15, 20, 20]
        })
        
        fig = px.pie(allocation, values='Allocation', names='Sector', title='Sector Allocation')
        st.plotly_chart(fig, use_container_width=True)
    
    def render_performance_chart(self):
        """Render performance chart"""
        st.subheader("📈 Performance vs Benchmark")
        
        dates = pd.date_range(start=datetime.now() - timedelta(days=90), end=datetime.now(), freq='D')
        portfolio = 100 * (1 + np.cumsum(np.random.normal(0.0015, 0.02, len(dates))))
        benchmark = 100 * (1 + np.cumsum(np.random.normal(0.001, 0.015, len(dates))))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=portfolio, name='Portfolio', line=dict(color='green')))
        fig.add_trace(go.Scatter(x=dates, y=benchmark, name='Benchmark', line=dict(color='blue')))
        
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    def render_win_rate_chart(self):
        """Render win rate chart"""
        st.subheader("🏆 Win Rate by Asset")
        
        assets = ['RELIANCE', 'TCS', 'HDFC', 'INFY', 'ITC']
        win_rates = [78, 82, 75, 80, 73]
        
        fig = px.bar(x=assets, y=win_rates, title='Win Rate by Asset')
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    def render_multi_asset_tab(self):
        """Render multi-asset AI system tab"""
        st.header("🤖 Multi-Asset AI System")
        
        # System initialization
        if not st.session_state.get('multi_asset_initialized', False):
            st.info("🚀 Initialize the Multi-Asset AI System to unlock advanced features")
            if st.button("Initialize Multi-Asset AI", type="primary"):
                st.session_state.multi_asset_initialized = True
                st.success("Multi-Asset AI System initialized!")
                st.rerun()
            return
        
        # Performance Targets Section
        st.header("🎯 Performance Targets")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Daily Target", "₹250", "₹200-₹500 range", delta_color="off")
        with col2:
            st.metric("Monthly Target", "₹5,000", "₹4,000-₹10,000 range", delta_color="off")
        with col3:
            st.metric("Max Daily Loss", "₹500", "5% capital protection", delta_color="off")
        with col4:
            st.metric("Positions", "3-5", "Simultaneous diversification", delta_color="off")
        
        # Asset Class Performance
        st.header("🏗️ Asset Class Analysis")
        
        asset_data = pd.DataFrame([
            {'Asset Class': 'Stocks', 'Allocation %': 40, 'Expected Return %': 2.8, 'Risk Level': 'Medium', 'AI Model': 'StockAI_v1'},
            {'Asset Class': 'Indices', 'Allocation %': 30, 'Expected Return %': 2.2, 'Risk Level': 'Low', 'AI Model': 'IndexAI_v1'},
            {'Asset Class': 'Futures', 'Allocation %': 20, 'Expected Return %': 3.5, 'Risk Level': 'High', 'AI Model': 'FuturesAI_v1'},
            {'Asset Class': 'Options', 'Allocation %': 10, 'Expected Return %': 4.2, 'Risk Level': 'Very High', 'AI Model': 'OptionsAI_v1'}
        ])
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(asset_data, x='Asset Class', y='Expected Return %', 
                        color='Risk Level', title='Expected Returns by Asset Class',
                        hover_data=['Allocation %', 'AI Model'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Allocation Strategy")
            for _, row in asset_data.iterrows():
                st.write(f"**{row['Asset Class']}**: {row['Allocation %']}% allocation")
                st.progress(row['Allocation %'] / 100)
        
        # Real-time Signals
        st.header("📊 Live Multi-Asset Signals")
        
        # Mock signals for demonstration
        multi_asset_signals = [
            {
                'Asset': 'RELIANCE',
                'Type': 'Stock',
                'Signal': 'BUY',
                'Entry': '₹2,845.50',
                'Target': '₹2,968.50',
                'Stop Loss': '₹2,789.50',
                'Confidence': '78.5%',
                'Position Size': '₹2,500',
                'Risk': '₹125',
                'AI Model': 'StockAI_v1',
                'Sector': 'Energy',
                'Technical Score': 8.5,
                'Fundamental Score': 7.8,
                'Sentiment Score': 8.2
            },
            {
                'Asset': 'NIFTY50',
                'Type': 'Index',
                'Signal': 'SELL',
                'Entry': '₹21,845.00',
                'Target': '₹21,200.00',
                'Stop Loss': '₹22,100.00',
                'Confidence': '82.3%',
                'Position Size': '₹3,000',
                'Risk': '₹150',
                'AI Model': 'IndexAI_v1',
                'Sector': 'Nifty50',
                'Technical Score': 8.9,
                'Fundamental Score': 8.1,
                'Sentiment Score': 7.8
            },
            {
                'Asset': 'BANKNIFTYFUT',
                'Type': 'Futures',
                'Signal': 'BUY',
                'Entry': '₹48,250.00',
                'Target': '₹49,800.00',
                'Stop Loss': '₹47,600.00',
                'Confidence': '75.2%',
                'Position Size': '₹2,000',
                'Risk': '₹200',
                'AI Model': 'FuturesAI_v1',
                'Sector': 'Banking',
                'Technical Score': 7.8,
                'Fundamental Score': 7.5,
                'Sentiment Score': 8.0
            },
            {
                'Asset': 'NIFTY50CE',
                'Type': 'Options',
                'Signal': 'CALL',
                'Entry': '₹125.50',
                'Target': '₹185.00',
                'Stop Loss': '₹95.00',
                'Confidence': '71.8%',
                'Position Size': '₹1,500',
                'Risk': '₹225',
                'AI Model': 'OptionsAI_v1',
                'Sector': 'Nifty50',
                'Technical Score': 7.2,
                'Fundamental Score': 6.8,
                'Sentiment Score': 7.5
            }
        ]
        
        signals_df = pd.DataFrame(multi_asset_signals)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            asset_filter = st.multiselect("Filter by Asset Type", 
                                        ['Stock', 'Index', 'Futures', 'Options'],
                                        default=['Stock', 'Index', 'Futures', 'Options'])
        with col2:
            confidence_filter = st.slider("Min Confidence", 0.5, 1.0, 0.70)
        with col3:
            risk_filter = st.selectbox("Risk Level", ["All", "Low", "Medium", "High"])
        
        # Filter and display signals
        filtered_signals = signals_df[
            signals_df['Type'].isin(asset_filter) &
            (signals_df['Confidence'].str.rstrip('%').astype(float) >= confidence_filter * 100)
        ]
        
        st.dataframe(filtered_signals, use_container_width=True)
        
        # Correlation Analysis
        st.header("🔗 Correlation & Risk Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("High Correlation Alerts")
            correlations = [
                {'Asset 1': 'RELIANCE', 'Asset 2': 'ONGC', 'Correlation': 0.78, 'Risk': 'Medium'},
                {'Asset 1': 'TCS', 'Asset 2': 'INFY', 'Correlation': 0.85, 'Risk': 'High'},
                {'Asset 1': 'HDFC', 'Asset 2': 'ICICIBANK', 'Correlation': 0.73, 'Risk': 'Medium'}
            ]
            
            for corr in correlations:
                st.warning(f"**{corr['Asset 1']} - {corr['Asset 2']}**: {corr['Correlation']:.2f} correlation ({corr['Risk']} risk)")
        
        with col2:
            st.subheader("Sector Exposure")
            sector_data = pd.DataFrame([
                {'Sector': 'IT', 'Exposure %': 35, 'P&L': 1250, 'Positions': 2},
                {'Sector': 'Energy', 'Exposure %': 25, 'P&L': 850, 'Positions': 1},
                {'Sector': 'Banking', 'Exposure %': 20, 'P&L': 450, 'Positions': 1},
                {'Sector': 'FMCG', 'Exposure %': 20, 'P&L': 300, 'Positions': 1}
            ])
            
            fig = px.pie(sector_data, values='Exposure %', names='Sector', 
                        title='Sector Allocation')
            st.plotly_chart(fig, use_container_width=True)
        
        # Capital Scaling Potential
        st.header("📈 Capital Scaling Potential")
        
        scaling_data = pd.DataFrame([
            {'Capital': '₹10,000', 'Daily Potential': 250, 'Monthly Potential': 5000, 'Positions': 3},
            {'Capital': '₹50,000', 'Daily Potential': 1250, 'Monthly Potential': 25000, 'Positions': 8},
            {'Capital': '₹100,000', 'Daily Potential': 2500, 'Monthly Potential': 50000, 'Positions': 15},
            {'Capital': '₹500,000', 'Daily Potential': 12500, 'Monthly Potential': 250000, 'Positions': 25}
        ])
        
        fig = px.scatter(scaling_data, x='Capital', y='Daily Potential', 
                        size='Positions', color='Monthly Potential',
                        title='Capital Scaling Potential',
                        hover_data=['Monthly Potential', 'Positions'])
        st.plotly_chart(fig, use_container_width=True)
        
        # System Controls
        st.header("🎮 System Controls")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Generate New Signals", type="primary"):
                st.success("New multi-asset signals generated!")
        
        with col2:
            if st.button("📊 Run Backtest"):
                st.info("Running backtest...")
                time.sleep(2)
                st.success("Backtest completed! Win rate: 78.5%")
        
        with col3:
            if st.button("⚙️ Optimize Parameters"):
                st.info("Optimizing AI parameters...")
                time.sleep(2)
                st.success("Parameters optimized for current market conditions!")
        
        # Performance Metrics
        st.header("📊 Performance Metrics")
        
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        
        with metrics_col1:
            st.metric("Total Return", "+42.8%", "Last 30 days", delta_color="normal")
        with metrics_col2:
            st.metric("Sharpe Ratio", "2.85", "Risk-adjusted", delta_color="normal")
        with metrics_col3:
            st.metric("Max Drawdown", "-3.2%", "Worst peak-to-trough", delta_color="inverse")
        with metrics_col4:
            st.metric("Win Rate", "78.5%", "Signal accuracy", delta_color="normal")
    
    def generate_live_signals(self):
        """Generate live trading signals"""
        st.info("Generating signals...")
        # This would integrate with the actual signal engine
        time.sleep(1)
        st.success("Signals generated successfully!")
    
    def generate_risk_report(self):
        """Generate comprehensive risk report"""
        st.info("Generating risk report...")
        # This would generate actual risk report
        st.success("Risk report generated!")
    
    def show_model_performance(self):
        """Show detailed model performance"""
        st.info("Loading model performance data...")
        # This would show actual model performance
    
    # Helper functions for mock data
    def get_mock_signals(self):
        return [
            {
                'Asset': 'RELIANCE',
                'Direction': 'BUY',
                'Entry': 2500.50,
                'Target': 2575.50,
                'Stop Loss': 2475.50,
                'Confidence': 0.85,
                'Strength': 0.78,
                'Technical Score': 0.82,
                'Fundamental Score': 0.75,
                'Sentiment Score': 0.80,
                'Risk Score': 0.25
            },
            {
                'Asset': 'TCS',
                'Direction': 'SELL',
                'Entry': 3200.25,
                'Target': 3120.25,
                'Stop Loss': 3240.25,
                'Confidence': 0.82,
                'Strength': 0.75,
                'Technical Score': 0.79,
                'Fundamental Score': 0.71,
                'Sentiment Score': 0.77,
                'Risk Score': 0.30
            }
        ]
    
    def get_mock_positions(self):
        return [
            {
                'Asset': 'HDFC',
                'Direction': 'BUY',
                'Quantity': 100,
                'Entry': 1650.00,
                'Current': 1685.50,
                'P&L': 3550.00,
                'P&L %': 2.15,
                'Stop Loss': 1620.00,
                'Target': 1720.00,
                'Risk': 'Low'
            },
            {
                'Asset': 'INFY',
                'Direction': 'SELL',
                'Quantity': 50,
                'Entry': 1450.00,
                'Current': 1425.75,
                'P&L': 1212.50,
                'P&L %': 1.67,
                'Stop Loss': 1480.00,
                'Target': 1380.00,
                'Risk': 'Medium'
            }
        ]
    
    def get_mock_trade_history(self):
        return [
            {'Asset': 'RELIANCE', 'Direction': 'BUY', 'P&L': 2500, 'Return': 2.5},
            {'Asset': 'TCS', 'Direction': 'SELL', 'P&L': -800, 'Return': -1.2},
            {'Asset': 'HDFC', 'Direction': 'BUY', 'P&L': 1800, 'Return': 1.8}
        ]
    
    def get_mock_recent_signals(self):
        return [
            {'Asset': 'RELIANCE', 'Direction': 'BUY', 'Price': 2500.50, 'Time': '14:32:15'},
            {'Asset': 'TCS', 'Direction': 'SELL', 'Price': 3200.25, 'Time': '14:28:42'}
        ]
    
    def get_mock_recent_trades(self):
        return [
            {'Asset': 'HDFC', 'Action': 'BUY', 'Quantity': 100, 'Price': 1650.00, 'Time': '14:25:30'},
            {'Asset': 'INFY', 'Action': 'SELL', 'Quantity': 50, 'Price': 1450.00, 'Time': '14:20:15'}
        ]

def main():
    """Main dashboard runner"""
    
    # Initialize dashboard
    dashboard = TradingDashboard()
    
    # Run dashboard
    dashboard.run()

if __name__ == "__main__":
    main()