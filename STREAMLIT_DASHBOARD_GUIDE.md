# 🚀 Real-Time Trading Dashboard

A comprehensive Streamlit dashboard for real-time monitoring of algorithmic trading systems with paper trading and live execution capabilities.

## ✨ Features

### 📊 Real-Time Monitoring
- **Live SENSEX Price Tracking**: Real-time price updates every 5 seconds
- **Paper Trading Balance**: Virtual ₹100,000 starting balance
- **Daily P&L Tracking**: Real-time profit and loss calculation
- **Trade Statistics**: Win rate, total trades, success rate

### 🎯 Signal Generation
- **Real-time Signals**: Generated using the HighConfidenceScalper
- **Confidence Scoring**: Each signal includes confidence level
- **Multi-strategy Support**: Conservative, moderate, and aggressive strategies
- **Forced Signal Logic**: Emergency signal generation when needed

### 📈 Visual Analytics
- **Interactive Charts**: Price movement and P&L visualization
- **Trade History**: Complete log of all executed trades
- **Performance Metrics**: Real-time calculation of key indicators
- **Risk Management**: Position sizing and stop-loss tracking

### 🔧 Trading Modes
- **Paper Trading**: Risk-free virtual trading environment
- **Live Trading**: Real execution via Kite Connect (requires API keys)
- **Hybrid Mode**: Paper + Live monitoring simultaneously

## 🚀 Quick Start

### Option 1: Automatic Setup (Recommended)
```bash
# Windows - Double click or run in terminal
start_streamlit_dashboard.bat

# Or PowerShell
.\start_streamlit_dashboard.ps1
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r streamlit_requirements.txt

# Start dashboard
streamlit run real_time_dashboard.py --server.port=8501
```

### Option 3: Test with Simulated Data
```bash
# Generate mock real-time data
python data_simulator.py

# Then start dashboard in another terminal
streamlit run real_time_dashboard.py
```

## 📋 Dashboard Sections

### 1. Real-Time Metrics Panel
- **SENSEX Price**: Current market price with real-time updates
- **Daily P&L**: Today's profit/loss with color-coded indicators
- **Account Balance**: Current paper trading balance
- **Trades Today**: Number of trades executed today
- **Win Rate**: Success rate of recent trades

### 2. Interactive Charts
- **Price Chart**: 1-hour rolling price data with trend indicators
- **P&L Chart**: Cumulative profit/loss over time
- **Volume Chart**: Trading volume visualization

### 3. Signal Panel
- **Generate Signal**: Manual signal generation button
- **Execute Trade**: Paper trade execution
- **Reset Balance**: Reset paper trading balance to ₹100,000
- **Signal Details**: Complete signal information with confidence scores

### 4. Trade History
- **Recent Trades**: Last 20 trades with full details
- **Trade Analytics**: Win/loss ratios and performance metrics
- **Export Functionality**: Download trade data as CSV

### 5. System Status
- **Connection Status**: Kite Connect API status
- **Last Update**: Timestamp of last data refresh
- **Signal Strength**: Current signal confidence level
- **Active Position**: Current open position status

## ⚙️ Configuration

### Dashboard Settings (`dashboard_config.json`)
```json
{
  "refresh_interval": 5,
  "paper_trading": {
    "starting_balance": 100000,
    "max_position_size": 10000
  },
  "live_trading": {
    "enabled": false,
    "max_daily_loss": 2000
  }
}
```

### Environment Variables
```bash
# Required for live trading
KITE_API_KEY=your_api_key_here
KITE_API_SECRET=your_api_secret_here
KITE_ACCESS_TOKEN=your_access_token_here
```

## 🔧 Advanced Usage

### Custom Data Sources
The dashboard supports multiple data sources:

1. **Kite Connect API** (Live data)
2. **Simulated Data** (For testing)
3. **CSV Files** (Historical data)
4. **Custom APIs** (Extendable architecture)

### Integration with Existing System
```python
# Import dashboard components
from real_time_dashboard import RealTimeTradingDashboard

# Initialize dashboard
dashboard = RealTimeTradingDashboard()
dashboard.initialize_connections()

# Use in your trading system
dashboard.fetch_real_time_data()
signal = dashboard.generate_signal()
```

### Custom Strategies
Add your own strategies to the dashboard:

```python
# In real_time_dashboard.py
def custom_strategy(self):
    # Your custom logic here
    return {
        'action': 'BUY',
        'confidence': 0.85,
        'price': current_price
    }
```

## 📊 Data Files

### Generated Files
- `paper_trades.csv`: All paper trading transactions
- `paper_balance.json`: Current paper trading balance
- `simulated_prices.csv`: Price data from simulator
- `latest_signal.json`: Latest generated signal
- `dashboard.log`: System logs

### File Structure
```
trading-dashboard/
├── real_time_dashboard.py      # Main dashboard
├── data_simulator.py           # Mock data generator
├── dashboard_config.json       # Configuration
├── streamlit_requirements.txt  # Dependencies
├── start_streamlit_dashboard.bat  # Windows launcher
├── start_streamlit_dashboard.ps1  # PowerShell launcher
├── paper_trades.csv           # Paper trading log
├── paper_balance.json         # Current balance
└── STREAMLIT_DASHBOARD_GUIDE.md  # This guide
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Kill existing Streamlit processes
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

#### 2. Missing Dependencies
```bash
# Reinstall all dependencies
pip install --force-reinstall -r streamlit_requirements.txt
```

#### 3. API Connection Issues
- Check internet connectivity
- Verify API credentials
- Ensure market hours (9:15 AM - 3:30 PM IST)

#### 4. Dashboard Not Updating
- Check auto-refresh checkbox
- Verify data files exist
- Check system logs for errors

### Debug Mode
```bash
# Run with debug logging
streamlit run real_time_dashboard.py --logger.level=debug
```

## 📱 Mobile Access

The dashboard is fully responsive and works on:
- Desktop browsers (Chrome, Firefox, Safari)
- Mobile browsers (iOS Safari, Android Chrome)
- Tablets and iPads
- Mobile apps via Streamlit sharing

## 🔐 Security Features

- **API Key Protection**: Keys stored in environment variables
- **Rate Limiting**: Built-in API rate limiting
- **Input Validation**: All user inputs sanitized
- **Session Management**: Secure session handling
- **Data Encryption**: Sensitive data encrypted at rest

## 📈 Performance Optimization

### For Large Datasets
- **Data Caching**: Automatic caching of expensive operations
- **Lazy Loading**: Load data on demand
- **Pagination**: Handle large trade histories
- **Compression**: Gzip compression for faster loading

### Memory Management
- **Garbage Collection**: Automatic cleanup
- **Memory Limits**: Configurable memory usage
- **Connection Pooling**: Efficient API connections

## 🤝 Contributing

To add new features:
1. Fork the repository
2. Create feature branch
3. Add your changes
4. Test thoroughly
5. Submit pull request

## 📞 Support

For issues and questions:
1. Check troubleshooting section
2. Review system logs
3. Test with simulated data
4. Contact support with error logs

---

**🎉 Ready to start? Run `start_streamlit_dashboard.bat` and watch your trading system come to life!**