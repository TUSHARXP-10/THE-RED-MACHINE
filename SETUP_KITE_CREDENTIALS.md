# Kite Connect Setup Guide for THE RED MACHINE

## 🔑 Complete Kite Integration Setup

### Step 1: Get Your Kite Connect Credentials

1. **Login to Kite Connect**
   - Go to https://kite.trade
   - Login with your Zerodha account
   - Navigate to "My Apps" → "Create New App"

2. **Create Your App**
   - App Name: `THE-RED-MACHINE`
   - Redirect URL: `http://localhost:8080`
   - App Type: `Connect` (for trading)
   - Save your `API Key` and `API Secret`

### Step 2: Update Configuration Files

#### Update kite_config.json
```json
{
  "api_key": "your_api_key_here",
  "api_secret": "your_api_secret_here",
  "access_token": "will_be_generated",
  "redirect_url": "http://localhost:8080"
}
```

#### Update .env file
```
KITE_API_KEY=your_api_key_here
KITE_API_SECRET=your_api_secret_here
KITE_ACCESS_TOKEN=your_access_token_here
```

### Step 3: Generate Access Token

1. **Run the credential setup script:**
   ```bash
   python setup_kite_api.py
   ```

2. **Or manually generate token:**
   ```python
   from kiteconnect import KiteConnect
   
   kite = KiteConnect(api_key="your_api_key")
   print(kite.login_url())
   # Visit the URL, login, and copy the `request_token` from redirect URL
   
   data = kite.generate_session("request_token", api_secret="your_secret")
   print("Access Token:", data["access_token"])
   ```

### Step 4: Test Kite Integration

```bash
# Test basic connectivity
python test_kite_connection.py

# Test live data feed
python test_kite_connector.py

# Run full system test
python test_system.py
```

### Step 5: Start Trading System

Once credentials are configured:

```bash
# One-click startup
start_trading.bat

# Or manual startup
python start_complete_system.py --mode start --wait-market
```

## 📋 Verification Checklist

- [ ] API Key configured in kite_config.json
- [ ] API Secret configured in kite_config.json
- [ ] Access Token generated and saved
- [ ] Test connection successful
- [ ] Live data feed working
- [ ] Paper trading mode enabled (recommended for testing)

## 🔍 Troubleshooting

### Common Issues:

1. **Invalid Credentials**
   - Double-check API key/secret in kite_config.json
   - Ensure no extra spaces or quotes

2. **Session Expired**
   - Access tokens expire daily
   - Re-run `setup_kite_api.py` to refresh

3. **Permission Denied**
   - Ensure your Kite app has trading permissions
   - Check if your Zerodha account is active

4. **Network Issues**
   - Check internet connectivity
   - Verify firewall settings

## 📱 Mobile Access

For mobile monitoring:
1. Use the enhanced dashboard at http://localhost:8501
2. Enable Telegram notifications via telegram_bot.py
3. Check trades on Kite mobile app

## 🚀 Quick Start Commands

```bash
# Complete setup in one command
python setup_kite_api.py

# Test everything
python test_system.py

# Start trading
start_trading.bat
```

## 📊 Dashboard URLs

- **Main Dashboard**: http://localhost:8501
- **Airflow UI**: http://localhost:8080
- **Kite Login**: Generated via setup script

Your Kite integration is now ready for live trading with ₹3000 capital! 🎯