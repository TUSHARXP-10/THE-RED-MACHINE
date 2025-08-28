# 🎯 THE RED MACHINE - Complete Startup Guide

## Overview
This guide provides step-by-step instructions to start your complete trading system with ₹3000 capital, including backtesting, model retraining, real-time monitoring, and Kite Connect integration - all with one command.

## 🚀 Quick Start (One Command)

### Method 1: Windows Batch (Recommended)
```bash
# Double-click or run in terminal
start_trading.bat
```

### Method 2: PowerShell
```powershell
# Run in PowerShell
.\start_trading.ps1

# Or with options:
.\start_trading.ps1 -WaitForMarket  # Wait for market open
.\start_trading.ps1 -Interactive    # Interactive mode
.\start_trading.ps1 -Stop           # Stop all services
.\start_trading.ps1 -Status          # Check status
```

### Method 3: Python (Cross-platform)
```bash
python start_complete_system.py --mode start --wait-market
```

## 📋 System Components

### 1. **Airflow Pipeline** (Port 8080)
- **URL**: http://localhost:8080
- **Username**: admin
- **Password**: admin
- **Features**: Automated model retraining, data pipeline, trade scheduling

### 2. **Enhanced Dashboard** (Port 8501)
- **URL**: http://localhost:8501
- **Features**: 
  - Real-time P&L tracking
  - Model performance metrics
  - System health monitoring
  - Trade execution controls
  - One-click model retraining

### 3. **Kite Connect Integration**
- **Replaced**: Breeze SDK → Kite Connect
- **Features**: 
  - Live market data
  - Real-time order placement
  - Position management
  - Fund tracking

### 4. **Model with ₹3000 Capital**
- **Optimized**: Specifically for small capital
- **Risk Management**: 2% per trade max
- **Max Positions**: 3 concurrent trades

## ⚙️ Configuration Setup

### 1. Kite Connect Setup
1. Get API credentials from [Kite Connect](https://kite.trade)
2. Create `kite_config.json`:
```json
{
  "api_key": "your_api_key_here",
  "access_token": "your_access_token_here"
}
```

### 2. System Configuration
Edit `system_config.json`:
```json
{
  "capital": 3000,
  "paper_trading": true,
  "kite_api_key": "your_api_key",
  "kite_access_token": "your_access_token",
  "airflow_port": 8080,
  "dashboard_port": 8501,
  "auto_start_time": "09:00",
  "market_open": "09:15",
  "market_close": "15:30"
}
```

## 🎯 Daily Workflow

### Before Market Opens (9:00 AM)
1. **Run one command**: `start_trading.bat` or `start_trading.ps1`
2. **System will automatically**:
   - Start Airflow services
   - Retrain model with latest data
   - Run backtest with ₹3000 capital
   - Start enhanced dashboard
   - Initialize Kite Connect
   - Begin real-time monitoring

### During Market Hours (9:15 AM - 3:30 PM)
- **Monitor**: Real-time dashboard at http://localhost:8501
- **Control**: All operations via dashboard
- **Track**: Live P&L, positions, system health

### After Market Close
- **Automatic**: System saves logs and performance data
- **Review**: Daily reports in dashboard
- **Prepare**: Next day's setup

## 📊 Dashboard Features

### Navigation Tabs
1. **Dashboard**: Main metrics and charts
2. **Trading Control**: Start/stop trading, risk settings
3. **Model Management**: Retrain, backtest, upload models
4. **System Status**: Service health, resource usage
5. **Settings**: API keys, notifications, preferences
6. **Logs**: Real-time system logs

### Key Metrics Displayed
- **Real-time P&L**: Current profit/loss
- **Win Rate**: Success percentage
- **Total Trades**: Daily trade count
- **System Health**: CPU, memory, disk usage
- **Model Performance**: Latest accuracy scores

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
netstat -ano | findstr :8080
netstat -ano | findstr :8501

# Kill the process
taskkill /PID <process_id> /F
```

#### 2. Python/Package Issues
```bash
# Reinstall packages
pip install -r streamlit_requirements.txt --force-reinstall
pip install apache-airflow --force-reinstall
```

#### 3. Kite Connect Issues
- **Check**: API credentials in `kite_config.json`
- **Verify**: Internet connection
- **Test**: Run `python kite_integration.py` separately

#### 4. Airflow Not Starting
```bash
# Reset Airflow database
set AIRFLOW_HOME=%CD%\airflow
airflow db reset --yes
airflow db init
airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
```

### Log Files
- **System startup**: `system_startup.log`
- **Kite trading**: `kite_trading.log`
- **Model training**: `model_retraining.log`
- **Airflow**: `airflow/logs/`

## 📱 Mobile Access

### Local Network Access
1. **Find your IP**: `ipconfig` (Windows) or `ifconfig` (Linux/Mac)
2. **Access from mobile**: `http://YOUR_IP:8501`
3. **Airflow**: `http://YOUR_IP:8080`

### Example URLs
- **Local**: http://localhost:8501
- **Network**: http://192.168.1.100:8501

## 🔄 Advanced Usage

### Custom Startup Scripts

#### Start with Market Wait
```bash
python start_complete_system.py --mode start --wait-market
```

#### Interactive Mode
```bash
python start_complete_system.py --mode interactive
```

#### Status Check
```bash
python start_complete_system.py --mode status
```

### Scheduled Startup
Create a Windows Task Scheduler job:
1. **Program**: `start_trading.bat`
2. **Trigger**: Daily at 8:45 AM
3. **Action**: Start the task

## 🛡️ Security Notes

### API Keys
- **Never commit**: API keys to Git
- **Use environment**: Variables for sensitive data
- **Rotate**: API keys regularly

### Network Security
- **Firewall**: Allow ports 8080, 8501 only on local network
- **VPN**: Use when accessing remotely
- **SSL**: Consider SSL certificates for production

## 📈 Performance Optimization

### System Requirements
- **RAM**: 8GB minimum, 16GB recommended
- **CPU**: 4 cores minimum
- **Storage**: 10GB free space
- **Network**: Stable broadband connection

### Optimization Tips
1. **Close unnecessary**: Applications
2. **Increase**: Virtual memory if needed
3. **Monitor**: System resources via dashboard
4. **Restart**: Weekly to clear memory leaks

## 🎯 Success Checklist

### Before First Run
- [ ] Python 3.8+ installed
- [ ] Kite Connect API credentials obtained
- [ ] All packages installed (`pip install -r streamlit_requirements.txt`)
- [ ] Configuration files created
- [ ] Test run completed

### Daily Checklist
- [ ] Run startup script before 9:15 AM
- [ ] Verify dashboard is accessible
- [ ] Check system status in dashboard
- [ ] Monitor P&L throughout the day
- [ ] Review logs for any issues

## 🆘 Support

### Getting Help
1. **Check logs**: All log files in project directory
2. **Dashboard**: Real-time system status
3. **GitHub**: Report issues
4. **Documentation**: This guide and inline help

### Emergency Contacts
- **System logs**: Check `system_startup.log`
- **Kite issues**: Verify `kite_config.json`
- **Airflow**: Check `airflow/logs/` directory

---

## 🎉 You're Ready!

Your complete trading system is now ready for one-click startup. Simply run:

**Windows**: Double-click `start_trading.bat`
**PowerShell**: `.\start_trading.ps1`
**Python**: `python start_complete_system.py --mode start --wait-market`

The system will handle everything automatically - from model retraining to real-time monitoring. Happy trading! 🚀