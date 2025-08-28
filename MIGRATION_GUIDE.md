# Migration Guide: Breeze to Kite API

This guide will help you migrate from the ICICI Direct Breeze API to the Zerodha Kite API in THE-RED MACHINE trading system.

## Prerequisites

1. **Zerodha Account**: You need an active Zerodha trading account
2. **Kite Developer Credentials**: Register at [Kite Connect Developer Portal](https://developers.kite.trade/) to get your API key and secret

## Setup Steps

### 1. Update Environment Variables

Update your `.env` file with the following Kite API credentials:

```
KITE_API_KEY=your_api_key_here
KITE_API_SECRET=your_api_secret_here
KITE_ACCESS_TOKEN=your_access_token_here
ZERODHA_CLIENT_ID=your_client_id_here
KITE_REDIRECT_URL=https://localhost
```

### 2. Install Required Packages

Run the following command to install the Kite Connect Python library:

```bash
pip install -r requirements.txt
```

### 3. Generate Access Token

The Kite API requires an access token that expires daily. Run the following script to generate a new token:

```bash
python fix_kite_session.py
```

This script will:
1. Open a browser window for Zerodha login
2. Ask you to paste the redirect URL after successful login (example: https://kite.zerodha.com/connect/login?api_key=d2371g2f412eyfs&v=3)
3. Extract the request token and generate an access token
4. Update your `.env` file with the new access token

For emergency or quick fixes, you can also use:

```bash
python fix_kite_session_immediately.py
```

or

```bash
python quick_kite_session_fix.py
```

### 4. Test the Connection

Verify that your Kite API connection is working correctly:

```bash
python test_kite_connector.py
```

## Key Differences Between Breeze and Kite APIs

### Authentication

- **Breeze**: Uses API key, secret, and session token
- **Kite**: Uses API key, secret, and access token (expires daily)

### Market Data

- **Breeze**: Uses `get_market_data()` with specific parameters
- **Kite**: Uses `quote()` method with exchange:symbol format

### Order Placement

- **Breeze**: Uses string parameters for quantity and price
- **Kite**: Uses integer for quantity and float for price

### Symbol Format

- **Breeze**: Uses stock codes like "BSESEN" for SENSEX
- **Kite**: Uses exchange:symbol format like "BSE:SENSEX"

## Troubleshooting

### Access Token Expired

If you encounter authentication errors, your access token may have expired. Run `fix_kite_session.py` to generate a new token.

### Connection Issues

If you're having trouble connecting to the Kite API:

1. Verify your API credentials in the `.env` file
2. Check your internet connection
3. Ensure your Zerodha account is active and not blocked
4. Run the diagnostic tool to identify specific issues:

```bash
python diagnose_kite_connection.py
```

### Order Placement Failures

Common reasons for order placement failures:

1. Insufficient funds
2. Invalid order parameters
3. Market closed
4. Circuit limits reached

## Additional Resources

- [Kite Connect API Documentation](https://kite.trade/docs/connect/v3/)
- [Kite Connect Python Library](https://github.com/zerodha/pykiteconnect)
- [Zerodha Kite User Manual](https://zerodha.com/z-connect/tradezerodha/kite/kite-user-manual)