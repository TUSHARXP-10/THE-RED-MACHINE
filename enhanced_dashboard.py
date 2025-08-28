#!/usr/bin/env python3
"""
Enhanced Streamlit Dashboard with Full Pipeline Monitoring
One-stop control center for live trading with 3000 capital
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import os
import subprocess
import psutil
import time
import requests
from pathlib import Path
import logging

# Configure page
st.set_page_config(
    page_title="THE RED MACHINE - Full Pipeline Control",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #ff4757;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem;
    }
    .status-indicator {
        padding: 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .status-running {
        background-color: #2ed573;
        color: white;
    }
    .status-stopped {
        background-color: #ff4757;
        color: white;
    }
    .status-warning {
        background-color: #ffa502;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

class EnhancedTradingDashboard:
    def __init__(self):
        self.config_file = "dashboard_config.json"
        self.model_dir = "models"
        self.logs_dir = "logs"
        self.setup_directories()
        
    def setup_directories(self):
        """Create necessary directories"""
        for directory in [self.model_dir, self.logs_dir]:
            Path(directory).mkdir(exist_ok=True)
    
    def load_config(self):
        """Load dashboard configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except:
            return self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration"""
        config = {
            "capital": 3000,
            "paper_trading": True,
            "risk_per_trade": 0.02,
            "max_positions": 3,
            "kite_api_key": "",
            "kite_access_token": "",
            "telegram_bot_token": "",
            "telegram_chat_id": "",
            "refresh_interval": 5,
            "alerts_enabled": True,
            "auto_restart": True
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def check_service_status(self, service_name):
        """Check if a service is running"""
        try:
            if service_name == "airflow":
                result = subprocess.run(
                    ["airflow", "webserver", "--help"],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
            elif service_name == "streamlit":
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    if 'streamlit' in str(proc.info['cmdline']).lower():
                        return True
                return False
            elif service_name == "data_simulator":
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    if 'data_simulator.py' in str(proc.info['cmdline']).lower():
                        return True
                return False
        except:
            return False
    
    def get_system_metrics(self):
        """Get system performance metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu": cpu_percent,
            "memory": {
                "total": memory.total // (1024**3),
                "used": memory.used // (1024**3),
                "percent": memory.percent
            },
            "disk": {
                "total": disk.total // (1024**3),
                "used": disk.used // (1024**3),
                "percent": disk.percent
            }
        }
    
    def get_trading_metrics(self):
        """Get current trading metrics"""
        try:
            # Load paper trading data
            if os.path.exists("paper_trades.csv"):
                trades_df = pd.read_csv("paper_trades.csv")
                
                total_trades = len(trades_df)
                profitable_trades = len(trades_df[trades_df['pnl'] > 0])
                total_pnl = trades_df['pnl'].sum()
                win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
                
                return {
                    "total_trades": total_trades,
                    "win_rate": win_rate,
                    "total_pnl": total_pnl,
                    "current_balance": 3000 + total_pnl
                }
        except:
            pass
        
        return {
            "total_trades": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "current_balance": 3000
        }
    
    def start_trading_system(self):
        """Start the complete trading system"""
        try:
            # Start Airflow
            subprocess.Popen(
                ["airflow", "webserver", "--port", "8080"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Start Airflow scheduler
            subprocess.Popen(
                ["airflow", "scheduler"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Start data simulator
            subprocess.Popen(
                ["python", "data_simulator.py", "--continuous"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            st.success("Trading system started successfully!")
            
        except Exception as e:
            st.error(f"Error starting system: {str(e)}")
    
    def stop_trading_system(self):
        """Stop all trading services"""
        try:
            # Kill Airflow processes
            for proc in psutil.process_iter(['pid', 'name']):
                if 'airflow' in proc.info['name'].lower():
                    proc.kill()
            
            # Kill data simulator
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'data_simulator' in str(proc.info['cmdline']).lower():
                    proc.kill()
            
            st.success("Trading system stopped!")
            
        except Exception as e:
            st.error(f"Error stopping system: {str(e)}")
    
    def retrain_model(self):
        """Retrain the model with progress"""
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("Loading training data...")
            progress_bar.progress(20)
            
            # Run retraining script
            result = subprocess.run(
                ["python", "retrain_model_3000.py"],
                capture_output=True,
                text=True
            )
            
            progress_bar.progress(100)
            
            if result.returncode == 0:
                st.success("Model retrained successfully!")
                
                # Display results
                if os.path.exists("models/training_metadata.json"):
                    with open("models/training_metadata.json", 'r') as f:
                        metadata = json.load(f)
                    
                    st.json(metadata)
            else:
                st.error(f"Training failed: {result.stderr}")
                
        except Exception as e:
            st.error(f"Error retraining model: {str(e)}")
        
        finally:
            progress_bar.empty()
            status_text.empty()

# Initialize dashboard
dashboard = EnhancedTradingDashboard()

# Sidebar
st.sidebar.title("🎯 Control Panel")

# Navigation
page = st.sidebar.selectbox(
    "Navigate",
    ["Dashboard", "Trading Control", "Model Management", "System Status", "Settings", "Logs"]
)

# Quick actions
st.sidebar.markdown("---")
if st.sidebar.button("🚀 Start All Systems", use_container_width=True):
    dashboard.start_trading_system()
    st.rerun()

if st.sidebar.button("⏹️ Stop All Systems", use_container_width=True):
    dashboard.stop_trading_system()
    st.rerun()

if st.sidebar.button("🔄 Retrain Model", use_container_width=True):
    dashboard.retrain_model()

# Main content
if page == "Dashboard":
    st.markdown("<h1 class='main-header'>THE RED MACHINE - Full Pipeline Dashboard</h1>", unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    trading_metrics = dashboard.get_trading_metrics()
    system_metrics = dashboard.get_system_metrics()
    
    with col1:
        st.metric("Capital", f"Rs.{trading_metrics['current_balance']:,}", 
                 f"{trading_metrics['total_pnl']:.2f}")
    
    with col2:
        st.metric("Total Trades", trading_metrics['total_trades'])
    
    with col3:
        st.metric("Win Rate", f"{trading_metrics['win_rate']:.1f}%")
    
    with col4:
        st.metric("CPU Usage", f"{system_metrics['cpu']:.1f}%")
    
    # Real-time charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Live P&L")
        if os.path.exists("paper_trades.csv"):
            trades_df = pd.read_csv("paper_trades.csv")
            if len(trades_df) > 0:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=trades_df.index,
                    y=trades_df['pnl'].cumsum(),
                    mode='lines+markers',
                    name='Cumulative P&L'
                ))
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("⚡ System Performance")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=system_metrics['cpu'],
            title={'text': "CPU Usage"},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': "darkblue"},
                   'steps': [{'range': [0, 50], 'color': "lightgray"},
                           {'range': [50, 100], 'color': "gray"}],
                   'threshold': {'line': {'color': "red", 'width': 4},
                               'thickness': 0.75, 'value': 90}}
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

elif page == "Trading Control":
    st.header("🎯 Trading Control Center")
    
    config = dashboard.load_config()
    
    # Trading mode toggle
    st.subheader("Trading Mode")
    col1, col2 = st.columns(2)
    
    with col1:
        paper_mode = st.toggle("Paper Trading", value=config.get('paper_trading', True))
    
    with col2:
        auto_restart = st.toggle("Auto Restart", value=config.get('auto_restart', True))
    
    # Risk management
    st.subheader("Risk Management")
    col1, col2 = st.columns(2)
    
    with col1:
        risk_per_trade = st.slider("Risk per Trade (%)", 0.5, 5.0, 
                                 config.get('risk_per_trade', 2.0), 0.1)
    
    with col2:
        max_positions = st.slider("Max Positions", 1, 10, 
                                config.get('max_positions', 3))
    
    # Save configuration
    if st.button("Save Configuration"):
        config.update({
            'paper_trading': paper_mode,
            'auto_restart': auto_restart,
            'risk_per_trade': risk_per_trade,
            'max_positions': max_positions
        })
        
        with open(dashboard.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        st.success("Configuration saved!")

elif page == "Model Management":
    st.header("🧠 Model Management")
    
    # Model status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if os.path.exists("models/capital_optimized_model.h5"):
            st.success("✅ Model Available")
            model_size = os.path.getsize("models/capital_optimized_model.h5") / (1024*1024)
            st.metric("Model Size", f"{model_size:.1f} MB")
        else:
            st.error("❌ Model Not Found")
    
    with col2:
        if os.path.exists("models/training_metadata.json"):
            with open("models/training_metadata.json", 'r') as f:
                metadata = json.load(f)
            st.metric("Last Trained", 
                     datetime.fromisoformat(metadata['training_date']).strftime("%Y-%m-%d %H:%M"))
    
    with col3:
        config = dashboard.load_config()
        st.metric("Capital", f"Rs.{config.get('capital', 3000):,}")
    
    # Model actions
    st.subheader("Model Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Retrain Model", use_container_width=True):
            dashboard.retrain_model()
    
    with col2:
        if st.button("📊 Backtest Model", use_container_width=True):
            try:
                result = subprocess.run(
                    ["python", "backtest_3000_capital.py"],
                    capture_output=True,
                    text=True
                )
                st.text(result.stdout)
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    with col3:
        uploaded_file = st.file_uploader("Upload New Model", type=['h5'])
        if uploaded_file is not None:
            with open("models/uploaded_model.h5", "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("Model uploaded successfully!")

elif page == "System Status":
    st.header("🔧 System Status")
    
    # Service status
    st.subheader("Service Status")
    
    services = ["Airflow", "Streamlit", "Data Simulator"]
    
    for service in services:
        status = dashboard.check_service_status(service.lower())
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.write(f"**{service}**")
        
        with col2:
            if status:
                st.markdown("<div class='status-indicator status-running'>RUNNING</div>", 
                           unsafe_allow_html=True)
            else:
                st.markdown("<div class='status-indicator status-stopped'>STOPPED</div>", 
                           unsafe_allow_html=True)
        
        with col3:
            if st.button(f"Restart {service}", key=f"restart_{service}"):
                st.rerun()
    
    # System resources
    st.subheader("System Resources")
    metrics = dashboard.get_system_metrics()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("CPU Usage", f"{metrics['cpu']:.1f}%")
    
    with col2:
        st.metric("Memory Usage", 
                 f"{metrics['memory']['used']}/{metrics['memory']['total']} GB")
    
    with col3:
        st.metric("Disk Usage", 
                 f"{metrics['disk']['used']}/{metrics['disk']['total']} GB")

elif page == "Settings":
    st.header("⚙️ Settings")
    
    config = dashboard.load_config()
    
    # API Configuration
    st.subheader("API Configuration")
    
    kite_api_key = st.text_input("Kite API Key", 
                                value=config.get('kite_api_key', ''),
                                type="password")
    
    kite_access_token = st.text_input("Kite Access Token", 
                                     value=config.get('kite_access_token', ''),
                                     type="password")
    
    # Notifications
    st.subheader("Notifications")
    
    telegram_bot_token = st.text_input("Telegram Bot Token", 
                                     value=config.get('telegram_bot_token', ''),
                                     type="password")
    
    telegram_chat_id = st.text_input("Telegram Chat ID", 
                                   value=config.get('telegram_chat_id', ''))
    
    # Advanced settings
    st.subheader("Advanced Settings")
    
    refresh_interval = st.slider("Refresh Interval (seconds)", 
                               1, 30, config.get('refresh_interval', 5))
    
    alerts_enabled = st.toggle("Enable Alerts", 
                             value=config.get('alerts_enabled', True))
    
    if st.button("Save All Settings"):
        config.update({
            'kite_api_key': kite_api_key,
            'kite_access_token': kite_access_token,
            'telegram_bot_token': telegram_bot_token,
            'telegram_chat_id': telegram_chat_id,
            'refresh_interval': refresh_interval,
            'alerts_enabled': alerts_enabled
        })
        
        with open(dashboard.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        st.success("Settings saved successfully!")

elif page == "Logs":
    st.header("📋 System Logs")
    
    # Log files
    log_files = [
        "morning_scalping.log",
        "model_retraining.log",
        "backtest_3000.log"
    ]
    
    selected_log = st.selectbox("Select Log File", log_files)
    
    if os.path.exists(selected_log):
        with open(selected_log, 'r') as f:
            log_content = f.read()
        
        st.text_area("Log Content", log_content, height=400)
        
        if st.button("Download Log"):
            st.download_button(
                label="Download",
                data=log_content,
                file_name=f"{selected_log}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    else:
        st.info("No logs available yet.")

# Auto-refresh
if st.sidebar.checkbox("Auto Refresh", value=True):
    config = dashboard.load_config()
    time.sleep(config.get('refresh_interval', 5))
    st.rerun()