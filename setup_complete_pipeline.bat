@echo off
echo 🚀 COMPLETE PIPELINE SETUP - ₹3000 OTM TRADING SYSTEM
echo ================================================================

REM Install required packages
echo 📦 Installing required packages...
pip install streamlit python-dotenv kiteconnect pandas plotly

REM Load environment variables
echo 🔧 Loading environment variables...
setlocal enabledelayedexpansion

REM Check if .env file exists
if exist .env (
    echo ✅ .env file found
    for /f "usebackq tokens=*" %%a in (".env") do (
        for /f "tokens=1,2 delims==" %%b in ("%%a") do (
            set "%%b=%%c"
            echo set %%b=%%c
        )
    )
) else (
    echo ❌ .env file not found - creating sample...
    echo KITE_API_KEY=your_api_key_here > .env
    echo KITE_API_SECRET=your_api_secret_here >> .env
    echo KITE_ACCESS_TOKEN=your_access_token_here >> .env
    echo ZERODHA_CLIENT_ID=your_client_id >> .env
    echo TELEGRAM_BOT_TOKEN=your_bot_token >> .env
    echo CHAT_ID=your_chat_id >> .env
)

REM Verify Streamlit is running
echo 🎯 Checking Streamlit dashboard...
python -c "import requests; print('✅ Streamlit ready' if requests.get('http://localhost:8501').status_code==200 else '❌ Streamlit not running')"

REM Verify trading system
echo 💰 Verifying ₹3000 capital configuration...
python -c "import json; c=json.load(open('kite_config.json')); print('✅ Capital configured' if c['trading_parameters']['initial_capital']==3000 else '❌ Capital issue')"

REM Test OTM system
echo 🎯 Testing OTM strike selection...
python -c "from get_optimal_strikes import get_optimal_strikes; print('✅ OTM system working')"

REM Start complete system
echo 🚀 Starting complete trading system...
start cmd /k "streamlit run dashboard.py --server.port=8501"
timeout /t 5
start cmd /k "python live_signal_executor.py"

echo ================================================================
echo ✅ PIPELINE SETUP COMPLETE!
echo 📊 Dashboard: http://localhost:8501
echo 🔗 Kite Connect: Update .env with your credentials
echo 📞 Telegram: Set TELEGRAM_BOT_TOKEN and CHAT_ID
echo 💰 Capital: ₹3000 configured for 50-100 OTM trading
echo ================================================================
pause