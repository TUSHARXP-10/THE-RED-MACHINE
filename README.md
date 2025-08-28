# 🤖 AI Trading System - THE RED MACHINE

A comprehensive AI-powered multi-asset trading system with intelligent execution, real-time risk management, and advanced analytics.

## 🌟 Features

### Core Components
- **Multi-Asset AI Engine**: Specialized models for stocks, indices, and options
- **Smart Execution Engine**: Intelligent order routing and position management
- **Comprehensive Risk Management**: Multi-layer risk controls and real-time monitoring
- **Signal Engine**: Advanced signal generation with technical, fundamental, and sentiment analysis
- **Real-time Dashboard**: Streamlit-based monitoring and control interface
- **Supabase Integration**: Real-time data storage and retrieval

### AI Models
- **Stock Model**: RandomForest-based with technical indicators
- **Index Model**: XGBoost with market breadth analysis
- **Options Model**: LightGBM with Greeks and volatility analysis
- **LSTM Model**: Sequential data analysis for time series prediction

### Risk Management
- **Daily Loss Limits**: Configurable risk thresholds
- **Position Sizing**: Dynamic position sizing based on risk metrics
- **Correlation Analysis**: Sector exposure and correlation monitoring
- **VaR Calculation**: Value at Risk for portfolio assessment
- **Emergency Stops**: Automated risk controls

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/TUSHARXP-10/THE-RED-MACHINE.git
cd THE-RED-MACHINE

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Supabase Configuration

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Create the following tables:

```sql
-- Market data table
CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    asset VARCHAR(50),
    price DECIMAL(10,2),
    volume BIGINT,
    timestamp TIMESTAMP,
    indicators JSONB
);

-- Trades table
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    asset VARCHAR(50),
    direction VARCHAR(10),
    entry_price DECIMAL(10,2),
    quantity INTEGER,
    signal_strength DECIMAL(3,2),
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Signals table
CREATE TABLE signals (
    id SERIAL PRIMARY KEY,
    asset VARCHAR(50),
    direction VARCHAR(10),
    entry_price DECIMAL(10,2),
    target_price DECIMAL(10,2),
    stop_loss DECIMAL(10,2),
    confidence DECIMAL(3,2),
    technical_score DECIMAL(3,2),
    fundamental_score DECIMAL(3,2),
    sentiment_score DECIMAL(3,2),
    risk_score DECIMAL(3,2),
    timestamp TIMESTAMP DEFAULT NOW()
);
```

3. Set environment variables:

```bash
# Create .env file
echo "SUPABASE_URL=your_supabase_url" > .env
echo "SUPABASE_KEY=your_supabase_key" >> .env
echo "KITE_API_KEY=your_kite_api_key" >> .env
```

### 3. Start the System

#### Option 1: Dashboard Mode
```bash
# Start the interactive dashboard
streamlit run dashboard.py
```

#### Option 2: Automated Trading
```bash
# Start the main trading system
python main_trading_system.py
```

#### Option 3: Test Mode
```bash
# Test individual components
python multi_asset_ai.py
python smart_execution_engine.py
python comprehensive_risk_manager.py
```

## 📊 Dashboard Overview

### Navigation Tabs

1. **Overview**: System metrics, P&L charts, and recent activity
2. **Signals**: Live trading signals with confidence scores
3. **Positions**: Active positions with P&L tracking
4. **Risk**: Risk metrics, alerts, and controls
5. **Performance**: Historical performance and analytics
6. **AI Models**: Model performance and training controls

### Key Metrics
- **Portfolio Value**: Total portfolio value with daily P&L
- **Active Positions**: Current open positions count
- **Win Rate**: Historical win rate percentage
- **Sharpe Ratio**: Risk-adjusted returns
- **VaR**: Value at Risk calculations

## 🔧 Configuration

### Risk Settings
```python
# In dashboard sidebar or config file
total_capital = 100000          # Total trading capital
daily_loss_limit = 0.05       # 5% daily loss limit
position_risk_limit = 0.02    # 2% risk per position
max_positions = 10            # Maximum active positions
```

### Trading Settings
```python
scan_interval = 10             # Signal scan interval (seconds)
min_confidence = 0.65        # Minimum signal confidence
trading_universe = ['RELIANCE', 'TCS', 'HDFC', 'INFY', 'ITC']
```

### Model Configuration
```python
# Model-specific parameters
stock_model_params = {
    'n_estimators': 100,
    'max_depth': 10,
    'min_samples_split': 5
}

index_model_params = {
    'n_estimators': 200,
    'max_depth': 8,
    'learning_rate': 0.1
}

options_model_params = {
    'n_estimators': 150,
    'max_depth': 12,
    'learning_rate': 0.05
}
```

## 📈 Usage Examples

### 1. Generate Trading Signals
```python
from signal_engine import SignalEngine

engine = SignalEngine()
signals = engine.scan_universe(['RELIANCE', 'TCS', 'HDFC'])

for signal in signals:
    print(f"{signal.asset}: {signal.direction} at {signal.entry_price}")
```

### 2. Execute Trades
```python
from smart_execution_engine import SmartExecutionEngine

engine = SmartExecutionEngine(kite_client, capital_manager)
engine.execute_multi_asset_strategy()
```

### 3. Risk Assessment
```python
from comprehensive_risk_manager import ComprehensiveRiskManager

risk_manager = ComprehensiveRiskManager(total_capital=100000)
is_valid, reason = risk_manager.validate_trade_risk(signal, position_size)
```

### 4. Train AI Models
```python
from multi_asset_ai import MultiAssetAI

ai_system = MultiAssetAI()
accuracy = ai_system.train_asset_specific_models('stocks')
print(f"Stock model accuracy: {accuracy:.2%}")
```

## 🔍 Monitoring

### Real-time Monitoring
- **Dashboard**: Access at `http://localhost:8501`
- **Logs**: Check console output and log files
- **Alerts**: Risk alerts appear in dashboard and via notifications

### Performance Tracking
- **Trade History**: Stored in Supabase `trades` table
- **Signal History**: Stored in Supabase `signals` table
- **Model Performance**: Tracked in dashboard

### Key Alerts
- Daily loss limit reached
- Position size too large
- Correlation risk exceeded
- Emergency stop triggered

## 🛠️ Development

### Project Structure
```
THE-RED-MACHINE/
├── multi_asset_ai.py          # AI models and training
├── smart_execution_engine.py  # Trade execution logic
├── comprehensive_risk_manager.py  # Risk management
├── signal_engine.py          # Signal generation
├── main_trading_system.py    # Main orchestrator
├── dashboard.py            # Streamlit dashboard
├── requirements.txt        # Dependencies
├── README.md            # This file
└── .env.example          # Environment variables template
```

### Adding New Models
1. Inherit from `BaseAssetModel` in `multi_asset_ai.py`
2. Implement required methods: `prepare_features`, `train`, `predict`
3. Add to `MultiAssetAI.models` dictionary
4. Update dashboard configuration

### Custom Indicators
1. Add to `prepare_features` method in respective model class
2. Update feature engineering pipeline
3. Retrain models with new features
4. Validate performance improvement

## 🚨 Safety Features

### Risk Controls
- **Hard Stops**: Automatic position closure at predefined levels
- **Soft Stops**: Warning alerts before hard stops
- **Correlation Monitoring**: Prevents over-concentration
- **Liquidity Checks**: Ensures adequate market liquidity

### Circuit Breakers
- **Daily Loss Limit**: System stops trading if exceeded
- **Position Limits**: Maximum position size constraints
- **Market Hours**: Only trades during market hours
- **Volatility Filters**: Avoids trading during high volatility

## 📞 Support

### Common Issues
1. **Import Errors**: Ensure all dependencies are installed
2. **Supabase Connection**: Check API keys and network connectivity
3. **Model Training**: Ensure sufficient historical data
4. **Dashboard Loading**: Check Streamlit installation

### Getting Help
- Check the logs for error messages
- Review the configuration settings
- Test individual components separately
- Ensure all environment variables are set

## 📝 License

This project is for educational and research purposes. Use at your own risk.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

---

**⚠️ Disclaimer**: This is a sophisticated trading system for educational purposes. Always test thoroughly with paper trading before using real capital. Trading involves substantial risk of loss.