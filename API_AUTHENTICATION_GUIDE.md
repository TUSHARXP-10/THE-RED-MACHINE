# API Authentication Guide

## Authentication for Enhanced Prediction Endpoint

The `/predict/enhanced` endpoint requires authentication using a Bearer token. This guide explains how to properly authenticate your requests.

## Authentication Token

The correct authentication token for the enhanced prediction endpoint is:

```
secure_token
```

## Making Authenticated Requests

### PowerShell Example

```powershell
# Set up request body
$body = @{ 
    data = @{ 
        stock_price = 1500
        volatility = 0.25
        volume = 1000000 
    }
    current_capital = 30000 
} | ConvertTo-Json

# Set authorization header with correct token
$headers = @{"Authorization" = "Bearer secure_token"}

# Make the request
$response = Invoke-RestMethod -Uri "http://localhost:8002/predict/enhanced" -Method POST -Body $body -ContentType "application/json" -Headers $headers
```

### Python Example

```python
import requests
import json

# Set up request body
body = {
    "data": {
        "stock_price": 1500,
        "volatility": 0.25,
        "volume": 1000000
    },
    "current_capital": 30000
}

# Set authorization header with correct token
headers = {"Authorization": "Bearer secure_token"}

# Make the request
response = requests.post(
    "http://localhost:8002/predict/enhanced",
    json=body,
    headers=headers
)

# Print the response
print(json.dumps(response.json(), indent=2))
```

## Troubleshooting Authentication Errors

If you receive a "Not authenticated" error:

1. Verify you're using the correct token (`secure_token`)
2. Ensure the Authorization header is formatted correctly with the `Bearer` prefix
3. Check that the content type is set to `application/json`
4. Make sure the API server is running on port 8002

## Testing the Authentication

You can use the included test script to verify the authentication is working correctly:

```powershell
.\test_enhanced_endpoint.ps1
```

This script will send a properly authenticated request to the enhanced prediction endpoint and display the results.