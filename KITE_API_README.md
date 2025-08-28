# Kite API Integration for THE-RED MACHINE

This package provides integration with Zerodha's Kite API for THE-RED MACHINE trading system, replacing the previous ICICI Direct Breeze API.

## Features

- Complete replacement for Breeze API functionality
- Seamless integration with existing trading strategies
- Improved market data retrieval
- Enhanced order placement capabilities
- Better error handling and debugging

## Quick Start

### 1. Setup

Run the setup script to install required packages and configure your environment:

```bash
python setup_kite_api.py
```

### 2. Generate Access Token

Generate a new Kite API access token (required daily):

```bash
python fix_kite_session.py
```

### 3. Test Connection

Verify that your Kite API connection is working correctly:

```bash
python test_kite_connector.py
```

## Files Overview

- **kite_connector.py**: Main connector class for Kite API
- **fix_kite_session.py**: Utility to generate and update access tokens
- **test_kite_connector.py**: Test script for Kite API connection
- **setup_kite_api.py**: Setup script for installing packages and configuring environment
- **MIGRATION_GUIDE.md**: Detailed guide for migrating from Breeze to Kite API

## Environment Variables

The following environment variables are required in your `.env` file:

```
KITE_API_KEY=your_api_key_here
KITE_API_SECRET=your_api_secret_here
KITE_ACCESS_TOKEN=your_access_token_here
ZERODHA_CLIENT_ID=your_client_id_here
```

## Daily Workflow

The Kite API requires a new access token daily. Follow these steps each trading day:

1. Run `python fix_kite_session.py` to generate a new access token
2. Verify connection with `python test_kite_connector.py`
3. Start your trading system as usual

## Troubleshooting

### Access Token Issues

If you encounter authentication errors:

```bash
python fix_kite_session.py
```

### Connection Problems

If you're having trouble connecting to the Kite API:

1. Check your internet connection
2. Verify your API credentials in the `.env` file
3. Ensure your Zerodha account is active
4. Run the test script: `python test_kite_connector.py`

## Additional Resources

- [Kite Connect API Documentation](https://kite.trade/docs/connect/v3/)
- [Kite Connect Python Library](https://github.com/zerodha/pykiteconnect)
- [Zerodha Kite User Manual](https://zerodha.com/z-connect/tradezerodha/kite/kite-user-manual)

## Support

For issues specific to THE-RED MACHINE integration with Kite API, please refer to the MIGRATION_GUIDE.md file or contact the development team.