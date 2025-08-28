# 🟢 THE RED MACHINE - Live Trading Integration Guide

## Phase 2: Live Trading Integration - Complete Setup

Welcome to Phase 2 of THE RED MACHINE! This guide will help you transition from mock data to live trading with real market data from Kite Connect API.

## 🚀 Quick Start (2 Minutes)

### Step 1: Configure Kite API Credentials
```bash
python setup_live_kite.py setup
```

### Step 2: Launch Live Dashboard
```bash
streamlit run live_dashboard.py --server.port=8520
```

### Step 3: Enable Live Trading in Main Dashboard
1. Open main dashboard: `streamlit run dashboard.py`
2. Toggle "Enable Live Trading" switch
3. Click "Launch Live Dashboard"

## 📋 Prerequisites

### Kite API Setup
1. **Zerodha Account**: You need a Zerodha trading account
2. **Kite Connect API**: Subscribe to Kite Connect (₹2000/month)
3. **API Credentials**: Get your API Key and Secret from [Kite Connect](https://developers.kite.trade)

### Environment Variables
Create `.env` file in project root:
```bash
# Kite API Credentials
KITE_API_KEY=your_api_key_here
KITE_API_SECRET=your_api_secret_here
KITE_ACCESS_TOKEN=your_access_token_here

# Optional: Redis for caching
REDIS_URL=redis://localhost:6379

# Optional: Supabase for data storage
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## 🔧 Configuration Files

### 1. `kite_live_config.py`
Contains all live trading configurations:
- **Symbols**: NIFTY, BANKNIFTY, SENSEX, and top stocks
- **Intervals**: 1min, 5min, 15min, 1hour, 1day
- **Risk Parameters**: Position sizing, stop loss, take profit
- **Order Types**: MARKET, LIMIT, SL, SL-M
- **Products**: MIS, CNC, NRML

### 2. `live_kite_integration.py`
Core live trading engine:
- **Real-time data streaming** via WebSocket
- **Order execution** with retry logic
- **Position management** with P&L tracking
- **Risk management** with automatic exits
- **Error handling** and logging

### 3. `live_dashboard.py`
Enhanced dashboard with:
- **Real-time price updates** every second
- **Live positions** with P&L tracking
- **Order book** with status updates
- **AI signals** based on live data
- **Risk monitoring** with alerts

## 📊 Features Overview

### Live Data Integration
- ✅ Real-time market data via WebSocket
- ✅ Live price streaming for all NSE symbols
- ✅ Historical data for backtesting
- ✅ Options chain data (OI, IV, Greeks)

### Order Management
- ✅ Market orders with instant execution
- ✅ Limit orders with price monitoring
- ✅ Stop loss and take profit orders
- ✅ Bracket orders (BO) and cover orders (CO)

### Risk Management
- ✅ Real-time P&L calculation
- ✅ Position sizing based on risk
- ✅ Automatic stop loss execution
- ✅ Daily loss limits

### AI Integration
- ✅ Live signal generation
- ✅ Real-time market analysis
- ✅ Predictive modeling with live data
- ✅ Adaptive risk adjustment

## 🎯 Trading Strategies

### 1. Intraday Trading
```python
# Example: Moving Average Crossover
symbol = "RELIANCE"
if live_price > sma_20 and live_price > sma_50:
    signal = "BUY"
    target = live_price * 1.02  # 2% target
    stop_loss = live_price * 0.99  # 1% stop loss
```

### 2. Options Trading
```python
# Example: Straddle Strategy
nifty_spot = get_live_price("NIFTY")
call_strike = nifty_spot + 100
put_strike = nifty_spot - 100

# Sell ATM straddle
sell_call(call_strike)
sell_put(put_strike)
```

### 3. Swing Trading
```python
# Example: RSI + MACD strategy
if rsi < 30 and macd_crossover_up:
    signal = "BUY"
    target = resistance_level
    stop_loss = support_level
```

## 📈 Dashboard Navigation

### Main Dashboard (`dashboard.py`)
- **Overview**: Portfolio summary and performance
- **Trading Signals**: AI-generated signals
- **Active Positions**: Live positions with P&L
- **Risk Management**: Risk metrics and controls
- **Market Data**: Historical and real-time data

### Live Dashboard (`live_dashboard.py`)
- **Live Overview**: Real-time portfolio metrics
- **Real-time Prices**: Live price streaming
- **Live Positions**: Active positions with updates
- **Order Book**: Live order status
- **Live Signals**: Real-time AI signals
- **Risk Monitor**: Live risk metrics
- **Portfolio Analytics**: Advanced analytics

## ⚙️ Configuration Examples

### Custom Symbol Configuration
```python
# Add custom symbols in kite_live_config.py
custom_symbols = [
    {"symbol": "RELIANCE", "exchange": "NSE", "segment": "NSE_EQ"},
    {"symbol": "TCS", "exchange": "NSE", "segment": "NSE_EQ"},
    {"symbol": "NIFTY", "exchange": "NSE", "segment": "NSE_INDEX"},
]
```

### Risk Parameters
```python
# Risk settings in kite_live_config.py
risk_config = {
    "max_positions": 5,
    "risk_per_trade": 0.02,  # 2% of capital
    "max_daily_loss": 0.05,  # 5% of capital
    "min_risk_reward_ratio": 1.5,
    "max_slippage": 0.01,  # 1% max slippage
}
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Connection Errors
```bash
# Check API credentials
python setup_live_kite.py validate

# Test connection
python setup_live_kite.py test
```

#### 2. WebSocket Issues
```bash
# Restart WebSocket connection
python setup_live_kite.py restart

# Check network connectivity
ping api.kite.trade
```

#### 3. Order Rejections
- **Insufficient funds**: Check available margin
- **Circuit limits**: Check price bands
- **Invalid quantity**: Check lot sizes
- **Market closed**: Check trading hours

### Debug Mode
```bash
# Enable debug logging
export DEBUG=true
python live_dashboard.py
```

## 📊 Performance Monitoring

### Key Metrics to Track
1. **Win Rate**: % of profitable trades
2. **Risk-Reward Ratio**: Average profit vs loss
3. **Sharpe Ratio**: Risk-adjusted returns
4. **Max Drawdown**: Maximum peak-to-trough decline
5. **Profit Factor**: Gross profit / Gross loss

### Real-time Alerts
- **Price alerts**: When price crosses levels
- **P&L alerts**: When P&L exceeds thresholds
- **Risk alerts**: When risk limits are breached
- **System alerts**: Connection issues, API errors

## 🛡️ Security Best Practices

### API Security
- **Never share API credentials**
- **Use environment variables for secrets**
- **Enable 2FA on Zerodha account**
- **Regularly rotate access tokens**

### Risk Controls
- **Start with paper trading**
- **Use stop losses on every trade**
- **Limit position sizes**
- **Monitor daily loss limits**

## 🚀 Next Steps

### Advanced Features (Coming Soon)
1. **Options Strategy Builder**
2. **Portfolio Optimization**
3. **Advanced AI Models**
4. **Social Trading Integration**
5. **Mobile App Integration**

### Production Deployment
1. **Cloud hosting** (AWS/GCP)
2. **Database scaling** (PostgreSQL)
3. **Redis caching**
4. **Load balancing**
5. **Monitoring and alerting**

## 📞 Support

### Getting Help
- **Documentation**: Check `docs/` folder
- **Community**: Join our Discord server
- **Issues**: Report on GitHub
- **Email**: support@theredmachine.ai

### Regular Updates
- **Daily**: Market analysis and signals
- **Weekly**: Performance reports
- **Monthly**: Strategy updates
- **Quarterly**: Major feature releases

---

**🎯 Ready to start live trading? Run the setup script now!**

```bash
python setup_live_kite.py setup
```

**Happy Trading! 🚀**