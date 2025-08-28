# Debugging Guide for THE-RED MACHINE

## Common Issues and Solutions

### Session Token Issues

The most common issue with this project is an expired or invalid session token for the Breeze API. The session token is required for live trading and needs to be refreshed periodically.

#### How to Fix Session Token Issues

1. **Use the Quick Session Fix Tool**
   ```
   python quick_session_fix.py
   ```
   This simplified tool will guide you through the process of obtaining a new session token and updating your `.env` file.

2. **Use the Original Fix Script**
   ```
   python fix_session_immediately.py
   ```
   This script provides more detailed instructions and options for fixing session token issues.

3. **Manual Fix**
   - Go to `https://api.icicidirect.com/apiuser/login?api_key=YOUR_API_KEY`
   - Login with your ICICI Direct credentials
   - Enter OTP when prompted
   - After successful login, look for the session token in:
     - URL: `?apisession=XXXXX`
     - Network tab in Developer Tools (F12)
     - Left sidebar for 'API Session' value
   - Update your `.env` file with the new session token

### API Credential Issues

If you're having issues with API credentials, use the diagnostic script to identify and fix the problems:

```
python diagnose_api_connection.py
```

This script will check your API credentials, test the connection, and provide specific solutions for any issues found.

### Environment File Issues

The `.env` file should contain the following credentials without quotes:

```
BREEZE_API_KEY=your_api_key_here
BREEZE_API_SECRET=your_api_secret_here
BREEZE_APP_ID=your_app_id_here
BREEZE_SESSION_TOKEN=your_session_token_here
ICICI_CLIENT_CODE=your_client_code_here
```

To check and fix formatting issues in your `.env` file, run:

```
python check_env_file.py
```

## Testing

### Test Session Token

To test if your session token is valid, run:

```
python test_session_fix.py
```

This script will test your session token and provide detailed error messages if there are any issues.

### Verify Session

For a quick verification of your session token, run:

```
python verify_session.py
```

## Troubleshooting Steps

1. **Check API Credentials**
   - Ensure all required credentials are present in the `.env` file
   - Make sure there are no quotes around the values
   - Verify that the API key and secret are correct

2. **Refresh Session Token**
   - Session tokens expire periodically and need to be refreshed
   - Use one of the fix scripts mentioned above to get a new token

3. **Check Network Connection**
   - Ensure you have a stable internet connection
   - Check if the Breeze API is accessible from your network

4. **Check API Status**
   - Go to `https://api.icicidirect.com/apiuser/home`
   - Verify that your app status is 'Active'
   - If inactive, activate it and wait 5-10 minutes

5. **Update Dependencies**
   - Ensure you have the correct version of the `breeze_connect` package installed
   - Run `pip install -r requirements.txt` to install all dependencies

## Contact Support

If you continue to experience issues after following these steps, please contact support with the following information:

1. Error messages from the diagnostic script
2. Steps you've taken to resolve the issue
3. Any changes made to the codebase

## Additional Resources

- [Breeze API Documentation](https://api.icicidirect.com/apiuser/apidocs)
- [ICICI Direct API User Portal](https://api.icicidirect.com/apiuser/home)