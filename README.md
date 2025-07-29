# 🚀 Automated Cash Flow Trading System 

 `https://img.shields.io/badge/Python-3.9+-blue.svg` ](https://python.org) 
 `https://img.shields.io/badge/FastAPI-0.104+-green.svg` ](https://fastapi.tiangolo.com) 
 `https://img.shields.io/badge/Model_Accuracy-98.61%25-brightgreen.svg` ](/) 
 `https://img.shields.io/badge/Status-Production_Ready-success.svg` ](/) 

 > **An institutional-grade automated trading system with 98.61% ML accuracy for Indian financial markets (BSE/NSE). Features decay-resistant algorithms, live Breeze API integration, and professional MLOps pipeline.** 

 ## ✨ Key Features 

 - **🎯 98.61% ML Model Accuracy** - RandomForestRegressor with 28+ Indian market features 
 - **⚡ Decay-Resistant Trading** - Theta protection for options strategies 
 - **🔗 Live Market Integration** - Breeze API for ICICI Direct execution 
 - **📊 Professional Monitoring** - Grafana dashboards + Prometheus metrics 
 - **🛡️ Advanced Risk Management** - Multi-layer position sizing and loss limits 
 - **🔄 MLOps Pipeline** - Automated drift detection and weekly retraining 

 ## 🚀 Quick Start 

 ``` 
 # Clone and setup 
 git clone `https://github.com/yourusername/automated-cashflow-pipeline.git`  
 cd automated-cashflow-pipeline 
 pip install -r requirements.txt 

 # Configure environment 
 cp .env.example .env 
 # Add your Breeze API credentials to .env 

 # Start system 
 uvicorn api:app --host 0.0.0.0 --port 8002 --reload 
 python drift_detector.py --start-monitoring 

 # Access monitoring 
 # Grafana: http://localhost:3000 
 # API Health: http://localhost:8002/health 
 ``` 

 ## 📊 Performance Metrics 

 - **Model Accuracy**: 98.61% on 2+ years historical data 
 - **Expected Returns**: 20-30% monthly with risk management 
 - **Win Rate**: 75-85% matching model predictions 
 - **Risk Controls**: ₹2K daily loss limits, dynamic position sizing 

 ## 🛠️ Technology Stack 

 - **Backend**: Python 3.9+, FastAPI, Uvicorn 
 - **ML**: scikit-learn, pandas, numpy, MLflow 
 - **Trading**: Breeze Connect (ICICI Direct API) 
 - **Monitoring**: Grafana, Prometheus 
 - **Infrastructure**: Apache Airflow, Docker 

 ## 📈 Trading Features 

 - **Indian Market Optimization** - BSE SENSEX, NSE NIFTY specialization 
 - **Multi-Asset Support** - Equity, F&O, derivatives trading 
 - **Intelligent Execution** - Options vs equity selection based on decay analysis 
 - **Paper Trading** - Risk-free validation with virtual capital 

 ## ⚙️ API Endpoints 

 ``` 
 # System health 
 GET /health 

 # Enhanced predictions with decay intelligence 
 POST /predict/enhanced 

 # Model performance monitoring 
 GET /model-health 

 # Current decay parameters 
 GET /decay-parameters 
 ``` 

 ## 📠 Configuration 

 Required environment variables: 
 ``` 
 # Breeze API (ICICI Direct) 
 BREEZE_API_KEY=your_api_key 
 BREEZE_API_SECRET=your_secret 
 BREEZE_SESSION_TOKEN=your_token 
 ICICI_CLIENT_CODE=your_client_code 

 # Email alerts 
 EMAIL_USER=your_email@gmail.com 
 EMAIL_PASS=your_app_password 
 EMAIL_RECIPIENT=alerts@yourdomain.com 
 ``` 

 ## 📊 System Architecture 

 ``` 
 Market Data → ML Engine (98.61%) → Risk Management → Breeze API → NSE/BSE 
      ↓              ↓                    ↓              ↓ 
 MLOps Pipeline → Monitoring → Alerts → Portfolio Tracking 
 ``` 

 ## 🛡️ Risk Management 

 - **Position Sizing**: Dynamic allocation based on volatility and confidence 
 - **Stop Losses**: Automated risk control with 15% limits 
 - **Daily Limits**: Maximum ₹2,000 loss per day 
 - **Correlation Control**: Portfolio diversification optimization 

 ## 📈 Performance Monitoring 

 - **Grafana Dashboards**: Real-time P&L, win rate, position tracking 
 - **Email Alerts**: Instant notifications for all trades and system events 
 - **Drift Detection**: Continuous model performance monitoring 
 - **Automated Retraining**: Weekly model updates with fresh market data 

 ## 🧪 Testing & Validation 

 - **Paper Trading**: ₹30K virtual capital for risk-free validation 
 - **Backtesting**: 2+ years historical performance verification 
 - **Walk-forward Analysis**: Rolling window validation 
 - **Live Performance**: Real-time accuracy tracking vs predictions 

 ## 📄 License 

 MIT License - see [LICENSE](LICENSE) file for details. 

 ## ⚖️ Disclaimer 

 This system is for educational purposes. Trading involves substantial risk. Past performance does not guarantee future results. Ensure compliance with local regulations. 

 --- 

 **⭐ Star this repository if you found it helpful!** 

 *Built for the Indian trading community with institutional-grade technology* 
 ``` 

 ## 🎯 **Much Better! This Version is:** 

 - ✅ **75% shorter** but still comprehensive 
 - ✅ **Focused on key features** - highlights your 98.61% accuracy 
 - ✅ **Professional presentation** - clean and organized 
 - ✅ **Quick start friendly** - easy setup instructions 
 - ✅ **GitHub optimized** - proper badges and formatting 

 ## 🚀 **Ready for Your T-3 Hours Launch!** 

 

## Automated Financial Analysis and Trading Pipeline

### Overview
This project is an automated financial analysis and trading system that integrates:
- Data collection and processing pipelines
- Machine learning models for market prediction
- Risk management components
- Automated trading execution

### Features
- **Data Pipeline**: Automated collection and processing of financial data
- **Machine Learning**: Predictive models for market trends and opportunities
- **Risk Management**: Comprehensive risk assessment and mitigation strategies
- **Trading Execution**: Automated trade execution with multiple brokers
- **Monitoring**: Real-time performance tracking and alerts

### Prerequisites
- Python 3.8+
- Docker (for containerized deployment)
- Git

### Installation
```bash
git clone https://github.com/TUSHARXP-10/THE-RED-MACHINE.git
cd THE-RED-MACHINE
pip install -r requirements.txt
```

### Configuration
1. Copy `.env.example` to `.env`
2. Update with your API keys and credentials
3. Configure broker settings in `config/broker_config.yaml`

### Usage
```bash
# Start the main pipeline
python main.py

# Run specific components
python automated-cashflow-pipeline/api.py
python strategy_lab.py
```

### Docker Deployment
```bash
docker-compose up --build
```

### Contributing
Pull requests are welcome. For major changes, please open an issue first.

### License
[MIT](https://choosealicense.com/licenses/mit/)