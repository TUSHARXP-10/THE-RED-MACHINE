# API Load Test Script for PowerShell
param(
    [int]$RequestCount = 200,
    [int]$DelayMs = 50,
    [string]$ApiUrl = "http://localhost:8000/predict"
)

Write-Host "🚀 Starting API Load Test" -ForegroundColor Green
Write-Host "Target: $ApiUrl" -ForegroundColor Yellow
Write-Host "Requests: $RequestCount" -ForegroundColor Yellow
Write-Host "Delay: ${DelayMs}ms between requests" -ForegroundColor Yellow

# Wait for API to be ready
Write-Host "⏳ Waiting for API to be ready..." -ForegroundColor Yellow
$maxWait = 60
$waited = 0

while ($waited -lt $maxWait) {
    try {
        $response = Invoke-WebRequest -Uri $ApiUrl -Method GET -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 405) {
            Write-Host "✅ API is ready!" -ForegroundColor Green
            break
        }
    } catch {
        Write-Host "." -NoNewline -ForegroundColor Gray
        Start-Sleep 2
        $waited += 2
    }
}

if ($waited -ge $maxWait) {
    Write-Host "❌ API not ready after $maxWait seconds" -ForegroundColor Red
    exit 1
}

# Test data
$testData = @{
    data = @{
        stock_price = 150.0
        volatility = 0.12
        volume = 1000000
        sma_20 = 145.50
        sma_50 = 142.30
        rsi = 65.5
        macd = 2.1
        bollinger_upper = 155.80
        bollinger_lower = 144.70
        vix = 18.5
        treasury_10y = 3.45
        dollar_index = 102.3
    }
} | ConvertTo-Json -Depth 3

# Initialize counters
$successCount = 0
$failureCount = 0
$totalTime = 0
$responseTimes = @()

Write-Host "📊 Starting load test..." -ForegroundColor Green

$startTime = Get-Date

for ($i = 1; $i -le $RequestCount; $i++) {
    $requestStart = Get-Date
    
    try {
        # Add some randomization to stock price
        $randomPrice = 100 + (Get-Random -Minimum 0 -Maximum 100)
        $testData = @{
            data = @{
                stock_price = $randomPrice + 0.0
                volatility = 0.12 + (Get-Random -Minimum -0.05 -Maximum 0.05)
                volume = 1000000 + (Get-Random -Minimum -500000 -Maximum 500000)
                sma_20 = $randomPrice + (Get-Random -Minimum -5 -Maximum 5)
                sma_50 = $randomPrice + (Get-Random -Minimum -10 -Maximum 10)
                rsi = 50 + (Get-Random -Minimum -20 -Maximum 20)
                macd = (Get-Random -Minimum -5 -Maximum 5)
                bollinger_upper = $randomPrice + 10 + (Get-Random -Minimum -5 -Maximum 5)
                bollinger_lower = $randomPrice - 10 + (Get-Random -Minimum -5 -Maximum 5)
                vix = 18 + (Get-Random -Minimum -5 -Maximum 5)
                treasury_10y = 3.5 + (Get-Random -Minimum -1 -Maximum 1)
                dollar_index = 100 + (Get-Random -Minimum -10 -Maximum 10)
            }
        } | ConvertTo-Json -Depth 3
        
        $headers = @{
            "Authorization" = "Bearer secure_token"
            "Content-Type" = "application/json"
        }
        
        $response = Invoke-WebRequest -Uri $ApiUrl -Method POST -Body $testData -Headers $headers -TimeoutSec 10
        
        if ($response.StatusCode -eq 200) {
            $successCount++
            $responseTime = (Get-Date) - $requestStart
            $responseTimes += $responseTime.TotalMilliseconds
            Write-Host "." -NoNewline -ForegroundColor Green
        } else {
            $failureCount++
            Write-Host "x" -NoNewline -ForegroundColor Red
        }
        
    } catch {
        $failureCount++
        Write-Host "x" -NoNewline -ForegroundColor Red
    }
    
    if ($i % 50 -eq 0) {
        Write-Host " ($i/$RequestCount)" -ForegroundColor Cyan
    }
    
    Start-Sleep -Milliseconds $DelayMs
}

$endTime = Get-Date
$totalDuration = ($endTime - $startTime).TotalSeconds

Write-Host ""
Write-Host ""
Write-Host "📈 Load Test Results" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green
Write-Host "Total Requests: $RequestCount" -ForegroundColor White
Write-Host "Successful: $successCount" -ForegroundColor Green
Write-Host "Failed: $failureCount" -ForegroundColor Red
Write-Host "Success Rate: $([math]::Round(($successCount/$RequestCount)*100, 2))%" -ForegroundColor $(if ($successCount/$RequestCount -ge 0.95) { "Green" } else { "Red" })
Write-Host "Total Time: $([math]::Round($totalDuration, 2))s" -ForegroundColor White
Write-Host "Requests/Second: $([math]::Round($RequestCount/$totalDuration, 2))" -ForegroundColor White

if ($responseTimes.Count -gt 0) {
    $avgResponseTime = ($responseTimes | Measure-Object -Average).Average
    $minResponseTime = ($responseTimes | Measure-Object -Minimum).Minimum
    $maxResponseTime = ($responseTimes | Measure-Object -Maximum).Maximum
    
    Write-Host "Average Response Time: $([math]::Round($avgResponseTime, 2))ms" -ForegroundColor White
    Write-Host "Min Response Time: $([math]::Round($minResponseTime, 2))ms" -ForegroundColor Green
    Write-Host "Max Response Time: $([math]::Round($maxResponseTime, 2))ms" -ForegroundColor Yellow
}

# Performance analysis
Write-Host ""
Write-Host "🔍 Performance Analysis" -ForegroundColor Blue
if ($successCount/$RequestCount -ge 0.95) {
    Write-Host "✅ Success rate meets target (>95%)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Success rate below target (<95%)" -ForegroundColor Red
}

if ($responseTimes.Count -gt 0 -and $avgResponseTime -lt 200) {
    Write-Host "✅ Average response time meets target (<200ms)" -ForegroundColor Green
} elseif ($responseTimes.Count -gt 0) {
    Write-Host "⚠️  Average response time above target (>200ms)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 Test Complete! Check Grafana: http://localhost:3000" -ForegroundColor Magenta