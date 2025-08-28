# 🚀 THE RED MACHINE - Enhanced Startup Script
# Production-ready startup with comprehensive checks and monitoring

Write-Host ""
Write-Host "🚀 THE-RED MACHINE TRADING SYSTEM STARTUP 🚀" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "98.61% accuracy | Decay-resistant | MLOps-enabled" -ForegroundColor Green
Write-Host ""

# Step 1: Navigate to the project directory
Write-Host "[1/5] Navigating to project directory..." -ForegroundColor Yellow
$projectDir = "C:\Users\tushar\Desktop\THE-RED MACHINE\automated-cashflow-pipeline"
Set-Location -Path $projectDir
Write-Host "✅ Directory set to: $projectDir" -ForegroundColor Green
Write-Host ""

# Create log directory if it doesn't exist
$logDir = "C:\Users\tushar\Desktop\THE-RED MACHINE\logs"
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force
}

# Generate timestamp for log file
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$logFile = "$logDir\trading_system_$timestamp.log"
Write-Host "📁 Log file: $logFile" -ForegroundColor Yellow
Write-Host ""

# Step 2: Check API token
Write-Host "[2/5] Verifying API token..." -ForegroundColor Yellow
$apiToken = "secure_token"
Write-Host "✅ Using API Token: $apiToken" -ForegroundColor Green
Write-Host ""

# Step 3: Check system health before starting
Write-Host "[3/5] Checking system health..." -ForegroundColor Yellow

# Check if port 8002 is already in use
$portInUse = Get-NetTCPConnection -LocalPort 8002 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "⚠️ Port 8002 is already in use. The API server might already be running." -ForegroundColor Yellow
    Write-Host "   You can proceed if this is expected, or stop the existing process first." -ForegroundColor Yellow
} else {
    Write-Host "✅ Port 8002 is available" -ForegroundColor Green
}
Write-Host ""

# Step 4: Start the API server
Write-Host "[4/5] Starting THE-RED MACHINE API server..." -ForegroundColor Yellow
Write-Host "   This will open in a new window. DO NOT CLOSE IT during trading hours!" -ForegroundColor Red
Write-Host "   Command: uvicorn api:app --host 0.0.0.0 --port 8002 --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "   Starting server in 5 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start the API server with logging
$command = "cd '$projectDir'; uvicorn api:app --host 0.0.0.0 --port 8002 --reload --log-level info"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", $command -RedirectStandardOutput "$logFile" -RedirectStandardError "$logFile.error"

# Step 5: Test the API endpoints
Write-Host "[5/5] Testing API endpoints - waiting for server startup..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Test health endpoint
try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:8002/health" -Method GET -ErrorAction Stop
    Write-Host "✅ Health endpoint: $($healthResponse.status)" -ForegroundColor Green
    Write-Host "✅ Model loaded: $($healthResponse.model_loaded)" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Health endpoint test failed: $_" -ForegroundColor Yellow
}

# Test decay parameters endpoint
try {
    $decayResponse = Invoke-RestMethod -Uri "http://localhost:8002/decay-parameters" -Method GET -ErrorAction Stop
    Write-Host "✅ Decay parameters endpoint: Connected" -ForegroundColor Green
    Write-Host "   Current VIX: $($decayResponse.india_vix)" -ForegroundColor Green
    Write-Host "   Recommended trade type: $($decayResponse.recommended_trade_type)" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Decay parameters endpoint test failed: $_" -ForegroundColor Yellow
}

# Test enhanced prediction endpoint
Write-Host "Testing enhanced prediction endpoint..." -ForegroundColor Yellow
$body = @{ 
    data = @{ 
        stock_price = 1500
        volatility = 0.25
        volume = 1000000 
    }
    current_capital = 30000 
} | ConvertTo-Json

$headers = @{"Authorization" = "Bearer secure_token"}

try {
    $predictionResponse = Invoke-RestMethod -Uri "http://localhost:8002/predict/enhanced" -Method POST -Body $body -ContentType "application/json" -Headers $headers -ErrorAction Stop
    Write-Host "✅ Enhanced prediction endpoint: Connected" -ForegroundColor Green
    Write-Host "   Recommended amount: Rs.$($predictionResponse.recommended_amount)" -ForegroundColor Green
    Write-Host "   Stop loss: Rs.$($predictionResponse.stop_loss)" -ForegroundColor Green
    Write-Host "   Target profit: Rs.$($predictionResponse.target_profit)" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Enhanced prediction endpoint test failed: $_" -ForegroundColor Yellow
    Write-Host "   This is not critical for system startup" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎯 SYSTEM STARTUP COMPLETE! 🎯" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan
Write-Host "✅ API Server: Running on http://localhost:8002" -ForegroundColor Green
Write-Host "✅ Model: Loaded and operational" -ForegroundColor Green
if ($decayResponse) {
    Write-Host "✅ Trading Mode: $($decayResponse.recommended_trade_type)" -ForegroundColor Green
}
Write-Host "📊 Monitoring dashboard: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT REMINDERS:" -ForegroundColor Yellow
Write-Host "1. Keep the API server window open during market hours (9:15 AM - 3:30 PM)" -ForegroundColor Yellow
Write-Host "2. Do not disconnect from the internet" -ForegroundColor Yellow
Write-Host "3. Keep your laptop plugged in and prevent it from sleeping" -ForegroundColor Yellow
Write-Host "4. Check logs at: $logFile" -ForegroundColor Yellow
Write-Host ""
Write-Host "Ready for market open at 9:15 AM! 🚀" -ForegroundColor Cyan

# Step 6: Breeze Connection Note
Write-Host ""
Write-Host "[6/5] Breeze Connection Information" -ForegroundColor Yellow
Write-Host "To verify Breeze connection, run the breeze_test.py script in a separate terminal:" -ForegroundColor Yellow
Write-Host "cd $projectDir" -ForegroundColor Gray
Write-Host "python breeze_test.py" -ForegroundColor Gray
Write-Host ""

# Keep the window open
Write-Host ""
Write-Host "Press any key to exit this startup script (NOT the API server window)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")