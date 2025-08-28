import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import json
import os
from kite_connector import KiteConnect
from morning_scalper import HighConfidenceScalper
import threading
import queue
import logging
from collections import deque
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for real-time data
trade_queue = queue.Queue()
real_time_data = {
    'current_pnl': 0.0,
    'total_trades': 0,
    'win_rate': 0.0,
    'current_position': None,
    'last_update': None,
    'sensex_price': 0.0,
    'signal_strength': 0.0,
    'account_balance': 100000.0,  # Starting paper trading balance
    'daily_pnl': 0.0,
    'trades_today': 0
}

class RealTimeTradingDashboard:
    def __init__(self):
        self.kite = None
        self.scalper = None
        self.is_running = False
        self.update_thread = None
        self.paper_trades = []
        
    def initialize_connections(self):
        """Initialize Kite Connect and trading system"""
        try:
            self.kite = KiteConnect()
            self.scalper = HighConfidenceScalper()
            logger.info("Successfully initialized Kite Connect and scalper")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize connections: {e}")
            return False
    
    def fetch_real_time_data(self):
        """Fetch real-time market data and trading information"""
        try:
            # Get SENSEX price
            sensex_data = self.kite.ltp(["NSE:NIFTY 50"])
            real_time_data['sensex_price'] = sensex_data["NSE:NIFTY 50"]['last_price']
            
            # Get account balance (paper trading)
            real_time_data['account_balance'] = self.get_paper_balance()
            
            # Calculate P&L
            real_time_data['daily_pnl'] = self.calculate_daily_pnl()
            real_time_data['current_pnl'] = real_time_data['daily_pnl']
            
            # Get trade statistics
            trades = self.get_today_trades()
            real_time_data['trades_today'] = len(trades)
            real_time_data['win_rate'] = self.calculate_win_rate(trades)
            
            real_time_data['last_update'] = datetime.now()
            
        except Exception as e:
            logger.error(f"Error fetching real-time data: {e}")
    
    def get_paper_balance(self):
        """Get current paper trading balance"""
        try:
            if os.path.exists('paper_balance.json'):
                with open('paper_balance.json', 'r') as f:
                    data = json.load(f)
                    return data.get('balance', 100000.0)
            return 100000.0
        except:
            return 100000.0
    
    def save_paper_balance(self, balance):
        """Save paper trading balance"""
        try:
            with open('paper_balance.json', 'w') as f:
                json.dump({'balance': balance, 'timestamp': str(datetime.now())}, f)
        except Exception as e:
            logger.error(f"Error saving paper balance: {e}")
    
    def calculate_daily_pnl(self):
        """Calculate today's P&L"""
        try:
            trades = self.get_today_trades()
            return sum(trade.get('pnl', 0) for trade in trades)
        except:
            return 0.0
    
    def get_today_trades(self):
        """Get today's trades from trade log"""
        try:
            if os.path.exists('trade_log.csv'):
                df = pd.read_csv('trade_log.csv', parse_dates=['timestamp'])
                today = datetime.now().date()
                today_trades = df[df['timestamp'].dt.date == today]
                return today_trades.to_dict('records')
            return []
        except:
            return []
    
    def calculate_win_rate(self, trades):
        """Calculate win rate from trades"""
        if not trades:
            return 0.0
        wins = sum(1 for trade in trades if trade.get('pnl', 0) > 0)
        return (wins / len(trades)) * 100
    
    def generate_signal(self):
        """Generate trading signal using the scalper"""
        try:
            signal = self.scalper.generate_signal()
            return signal
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return None
    
    def execute_paper_trade(self, signal):
        """Execute paper trade based on signal"""
        if signal and signal.get('action') != 'HOLD':
            trade = {
                'timestamp': datetime.now(),
                'action': signal['action'],
                'price': real_time_data['sensex_price'],
                'quantity': 1,
                'signal_strength': signal.get('confidence', 0),
                'mode': 'paper',
                'status': 'PAPER_EXECUTED',
                'pnl': 0  # Will be calculated on exit
            }
            
            # Update balance
            if signal['action'] == 'BUY':
                real_time_data['account_balance'] -= real_time_data['sensex_price']
            elif signal['action'] == 'SELL':
                real_time_data['account_balance'] += real_time_data['sensex_price']
                
            self.save_paper_balance(real_time_data['account_balance'])
            self.log_paper_trade(trade)
            return trade
        return None
    
    def log_paper_trade(self, trade):
        """Log paper trade to CSV"""
        try:
            df = pd.DataFrame([trade])
            df.to_csv('paper_trades.csv', mode='a', header=not os.path.exists('paper_trades.csv'), index=False)
        except Exception as e:
            logger.error(f"Error logging paper trade: {e}")

def create_header():
    """Create dashboard header"""
    st.markdown("""
    <style>
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 0.5rem;
    }
    .real-time-indicator {
        color: #00ff00;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)

def display_metrics():
    """Display real-time metrics"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("SENSEX Price", f"₹{real_time_data['sensex_price']:,.2f}")
    
    with col2:
        pnl_color = "green" if real_time_data['daily_pnl'] >= 0 else "red"
        st.metric("Daily P&L", f"₹{real_time_data['daily_pnl']:,.2f}", 
                   delta=f"₹{real_time_data['daily_pnl']:,.2f}", 
                   delta_color="inverse" if real_time_data['daily_pnl'] < 0 else "normal")
    
    with col3:
        st.metric("Account Balance", f"₹{real_time_data['account_balance']:,.2f}")
    
    with col4:
        st.metric("Trades Today", real_time_data['trades_today'])
    
    with col5:
        st.metric("Win Rate", f"{real_time_data['win_rate']:.1f}%")

def display_charts():
    """Display real-time charts"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Price Chart")
        # Mock price data for demonstration
        price_data = pd.DataFrame({
            'time': [datetime.now() - timedelta(minutes=i) for i in range(60, 0, -1)],
            'price': [real_time_data['sensex_price'] + np.random.normal(0, 50) for _ in range(60)]
        })
        
        fig = px.line(price_data, x='time', y='price', 
                     title='SENSEX Real-time Price')
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💰 P&L Chart")
        trades = dashboard.get_today_trades()
        if trades:
            pnl_data = pd.DataFrame(trades)
            pnl_data['cumulative_pnl'] = pnl_data['pnl'].cumsum()
            
            fig = px.line(pnl_data, x='timestamp', y='cumulative_pnl',
                         title='Daily Cumulative P&L')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No trades executed today")

def display_trade_table():
    """Display recent trades"""
    st.subheader("📊 Recent Trades")
    
    try:
        # Combine real and paper trades
        all_trades = []
        
        if os.path.exists('trade_log.csv'):
            real_trades = pd.read_csv('trade_log.csv', parse_dates=['timestamp'])
            all_trades.extend(real_trades.tail(10).to_dict('records'))
        
        if os.path.exists('paper_trades.csv'):
            paper_trades = pd.read_csv('paper_trades.csv', parse_dates=['timestamp'])
            all_trades.extend(paper_trades.tail(10).to_dict('records'))
        
        if all_trades:
            trades_df = pd.DataFrame(all_trades)
            trades_df = trades_df.sort_values('timestamp', ascending=False)
            st.dataframe(trades_df.tail(20), use_container_width=True)
        else:
            st.info("No trades found")
            
    except Exception as e:
        st.error(f"Error loading trades: {e}")

def display_signal_panel():
    """Display current signal and controls"""
    st.subheader("🎯 Signal Panel")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Generate Signal", type="primary"):
            signal = dashboard.generate_signal()
            if signal:
                st.success(f"Signal Generated: {signal.get('action', 'HOLD')}")
                st.json(signal)
    
    with col2:
        if st.button("Execute Paper Trade", type="secondary"):
            signal = dashboard.generate_signal()
            trade = dashboard.execute_paper_trade(signal)
            if trade:
                st.success("Paper trade executed!")
    
    with col3:
        if st.button("Reset Paper Balance"):
            dashboard.save_paper_balance(100000.0)
            st.success("Paper balance reset to ₹100,000")

def display_system_status():
    """Display system status"""
    st.subheader("🔧 System Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = "🟢 Online" if real_time_data['last_update'] else "🔴 Offline"
        st.metric("System Status", status)
    
    with col2:
        if real_time_data['last_update']:
            last_update = real_time_data['last_update'].strftime('%H:%M:%S')
        else:
            last_update = "Never"
        st.metric("Last Update", last_update)
    
    with col3:
        st.metric("Signal Strength", f"{real_time_data['signal_strength']:.2f}")
    
    with col4:
        st.metric("Active Position", real_time_data['current_position'] or "None")

def auto_refresh():
    """Auto-refresh functionality"""
    if st.checkbox("Auto-refresh every 5 seconds", value=True):
        time.sleep(5)
        st.rerun()

# Initialize dashboard
dashboard = RealTimeTradingDashboard()

# Main app
st.set_page_config(
    page_title="Real-Time Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

create_header()

st.markdown("""
<div class="dashboard-header">
    <h1>🚀 Real-Time Trading Dashboard</h1>
    <p class="real-time-indicator">● LIVE</p>
    <p>Real-time paper trading and live execution monitoring</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📊 Dashboard Controls")
    
    st.subheader("Trading Mode")
    trading_mode = st.selectbox("Select Mode", ["Paper Trading", "Live Trading"])
    
    st.subheader("Risk Settings")
    max_position_size = st.slider("Max Position Size", 1000, 50000, 10000)
    stop_loss_pct = st.slider("Stop Loss %", 1, 10, 2)
    take_profit_pct = st.slider("Take Profit %", 1, 20, 5)
    
    st.subheader("Connection Status")
    if dashboard.initialize_connections():
        st.success("✅ Connected to Kite")
    else:
        st.error("❌ Kite Connection Failed")
    
    if st.button("Initialize System"):
        dashboard.initialize_connections()
        st.success("System initialized!")

# Main content area
col1, col2 = st.columns([3, 1])

with col1:
    display_metrics()
    display_charts()
    display_trade_table()

with col2:
    display_signal_panel()
    display_system_status()

# Footer with auto-refresh
st.divider()
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    auto_refresh()

# Initialize real-time updates
if st.session_state.get('initialized', False) == False:
    st.session_state.initialized = True
    dashboard.initialize_connections()

# Update real-time data
try:
    dashboard.fetch_real_time_data()
except Exception as e:
    st.error(f"Error updating data: {e}")

# Display logs
with st.expander("📋 System Logs"):
    st.code("System initialized successfully...")
    if real_time_data['last_update']:
        st.write(f"Last data update: {real_time_data['last_update']}")
    st.write("Dashboard running in real-time mode...")