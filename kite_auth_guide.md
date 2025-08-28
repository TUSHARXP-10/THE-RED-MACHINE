# 🔑 Kite API Authentication Guide

## Current Status
❌ **Authentication Failed**: Incorrect `api_key` or `access_token`

## Quick Fix Steps

### 1. Verify Your Credentials
Check your `.env` file contains:
```
KITE_API_KEY='q23715gf6tzjmyf5'
KITE_API_SECRET='87ivk3royi2z30lhzprgovhrocp8yq1g'
KITE_ACCESS_TOKEN='your_current_token'
```

### 2. Generate New Access Token

**Step 1**: Get Fresh Request Token
```bash
# Open this URL in your browser:
https://kite.trade/connect/login?api_key=q23715gf6tzjmyf5&v=3
```

**Step 2**: After logging in, you'll be redirected to:
```
https://localhost/?action=login&type=login&status=success&request_token=XXXXXXX
```

**Step 3**: Extract just the `request_token` value (the part after `request_token=`)

### 3. Update Access Token

**Option A**: Use the interactive tool:
```bash
python kite_session_refresh.py
```

**Option B**: Manual update with Python:
```python
from kiteconnect import KiteConnect
import os

# Your credentials
api_key = "q23715gf6tzjmyf5"
api_secret = "87ivk3royi2z30lhzprgovhrocp8yq1g"
request_token = "YOUR_FRESH_REQUEST_TOKEN"

# Generate new access token
kite = KiteConnect(api_key=api_key)
data = kite.generate_session(request_token, api_secret=api_secret)
print(f"New access token: {data['access_token']}")

# Update your .env file with the new token
```

### 4. Verify Connection
```bash
python -c "
from kiteconnect import KiteConnect
import os
from dotenv import load_dotenv
load_dotenv()

kite = KiteConnect(api_key=os.getenv('KITE_API_KEY').strip('\"'))
kite.set_access_token(os.getenv('KITE_ACCESS_TOKEN').strip('\"'))
profile = kite.profile()
print(f'✅ Connected as: {profile[\"user_name\"]}')
"
```

## Troubleshooting

### Common Issues:
1. **"Token is invalid or has expired"**: Use a fresh request token
2. **"Invalid checksum"**: Ensure API secret is correct
3. **"Incorrect api_key"**: Verify your Kite API key

### Manual Token Update:
If automated tools fail, manually update your `.env`:
```
KITE_ACCESS_TOKEN="your_new_token_here"
```

### Test Live Trading:
```bash
python quick_start_live.py
```

## Dashboard Access
After fixing authentication:
- **Standard Dashboard**: http://localhost:8519
- **Live Trading Dashboard**: http://localhost:8520

## Support
If issues persist:
1. Check Kite Connect app settings
2. Verify API key permissions
3. Ensure client ID matches: `GSS065`