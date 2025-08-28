# Test script for enhanced prediction endpoint

Write-Host "Testing enhanced prediction endpoint..." -ForegroundColor Yellow

# Sample request body
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

Write-Host "Sending request to http://localhost:8002/predict/enhanced..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8002/predict/enhanced" -Method POST -Body $body -ContentType "application/json" -Headers $headers -ErrorAction Stop
    
    Write-Host "\n✅ Enhanced prediction endpoint test successful!" -ForegroundColor Green
    Write-Host "\nResponse details:" -ForegroundColor Cyan
    Write-Host "------------------" -ForegroundColor Cyan
    Write-Host "Prediction: $($response.prediction)" -ForegroundColor White
    Write-Host "Risk Flag: $($response.risk_flag)" -ForegroundColor White
    Write-Host "Trade Type: $($response.trade_type)" -ForegroundColor White
    Write-Host "Holding Hours: $($response.holding_hours)" -ForegroundColor White
    Write-Host "Risk Score: $($response.risk_score)" -ForegroundColor White
    Write-Host "Exit Time: $($response.exit_time)" -ForegroundColor White
    Write-Host "Position Multiplier: $($response.position_multiplier)" -ForegroundColor White
    Write-Host "Recommended Amount: ₹$($response.recommended_amount)" -ForegroundColor Green
    Write-Host "Stop Loss: ₹$($response.stop_loss)" -ForegroundColor Red
    Write-Host "Target Profit: ₹$($response.target_profit)" -ForegroundColor Green
    Write-Host "Capital Percentage: $($response.capital_percentage)%" -ForegroundColor White
    Write-Host "Risk Check Action: $($response.risk_check_action)" -ForegroundColor White
} catch {
    Write-Host "\n❌ Enhanced prediction endpoint test failed!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "\nTroubleshooting tips:" -ForegroundColor Yellow
    Write-Host "1. Make sure the API server is running on port 8002" -ForegroundColor Yellow
    Write-Host "2. Verify you're using the correct API token ('secure_token')" -ForegroundColor Yellow
    Write-Host "3. Check that the Authorization header is formatted correctly" -ForegroundColor Yellow
    Write-Host "4. Ensure the request body is properly formatted" -ForegroundColor Yellow
}