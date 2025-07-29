# PowerShell script for load testing the financial API
param(
    [int]$Requests = 100,
    [int]$Concurrent = 5,
    [string]$BaseUrl = "http://localhost:8002",
    [string]$Token = "secure_token"
)

Write-Host "Starting load test: $Requests requests with $Concurrent concurrent users" -ForegroundColor Green
Write-Host "Target: $BaseUrl" -ForegroundColor Yellow

# Test data
$testData = @{
    data = @{
        stock_price = 150.25
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
}

$headers = @{
    "Authorization" = "Bearer $Token"
    "Content-Type" = "application/json"
}

# Measure total time
$totalStart = Get-Date
$results = @()
$successCount = 0
$errorCount = 0

# Create runspace pool for concurrent requests
$runspacePool = [runspacefactory]::CreateRunspacePool(1, $Concurrent)
$runspacePool.Open()

$jobs = @()

for ($i = 1; $i -le $Requests; $i++) {
    $job = [powershell]::Create().AddScript({
        param($url, $data, $headers, $requestId)
        
        try {
            $start = Get-Date
            $response = Invoke-RestMethod -Uri "$url/predict" -Method Post -Body ($data | ConvertTo-Json -Depth 10) -Headers $headers
            $end = Get-Date
            
            $duration = ($end - $start).TotalMilliseconds
            
            return @{
                RequestId = $requestId
                Success = $true
                Duration = $duration
                Prediction = $response.prediction
                RiskFlag = $response.risk_flag
                PositionSize = $response.position_size
                Error = $null
            }
        }
        catch {
            return @{
                RequestId = $requestId
                Success = $false
                Duration = ($end - $start).TotalMilliseconds
                Prediction = $null
                RiskFlag = $null
                PositionSize = $null
                Error = $_.Exception.Message
            }
        }
    }).AddParameters($BaseUrl, $testData, $headers, $i)
    
    $job.RunspacePool = $runspacePool
    $jobs += $job
}

# Wait for all jobs to complete
foreach ($job in $jobs) {
    $result = $job.Invoke()
    $results += $result
    
    if ($result.Success) {
        $successCount++
        Write-Host "✓ Request $($result.RequestId) completed in $($result.Duration)ms" -ForegroundColor Green
    } else {
        $errorCount++
        Write-Host "✗ Request $($result.RequestId) failed: $($result.Error)" -ForegroundColor Red
    }
    
    $job.Dispose()
}

$runspacePool.Close()
$runspacePool.Dispose()

$totalEnd = Get-Date
$totalDuration = ($totalEnd - $totalStart).TotalSeconds

# Calculate statistics
$successfulRequests = $results | Where-Object { $_.Success }
if ($successfulRequests.Count -gt 0) {
    $avgResponseTime = ($successfulRequests | Measure-Object -Property Duration -Average).Average
    $minResponseTime = ($successfulRequests | Measure-Object -Property Duration -Minimum).Minimum
    $maxResponseTime = ($successfulRequests | Measure-Object -Property Duration -Maximum).Maximum
} else {
    $avgResponseTime = $minResponseTime = $maxResponseTime = 0
}

# Display results
Write-Host ""
Write-Host "=== Load Test Results ===" -ForegroundColor Cyan
Write-Host "Total Requests: $Requests" -ForegroundColor White
Write-Host "Successful: $successCount" -ForegroundColor Green
Write-Host "Failed: $errorCount" -ForegroundColor Red
Write-Host "Success Rate: $([math]::Round(($successCount/$Requests)*100, 2))%" -ForegroundColor White
Write-Host "Total Time: $([math]::Round($totalDuration, 2))s" -ForegroundColor White
Write-Host "Requests/Second: $([math]::Round($Requests/$totalDuration, 2))" -ForegroundColor White
Write-Host "Average Response Time: $([math]::Round($avgResponseTime, 2))ms" -ForegroundColor White
Write-Host "Min Response Time: $([math]::Round($minResponseTime, 2))ms" -ForegroundColor Green
Write-Host "Max Response Time: $([math]::Round($maxResponseTime, 2))ms" -ForegroundColor Yellow

# Performance recommendations
Write-Host ""
Write-Host "=== Performance Analysis ===" -ForegroundColor Cyan
if ($avgResponseTime -gt 1000) {
    Write-Host "⚠️  Average response time is high (>1s). Consider:" -ForegroundColor Yellow
    Write-Host "   - Increasing CPU/memory limits" -ForegroundColor White
    Write-Host "   - Optimizing model inference" -ForegroundColor White
    Write-Host "   - Using a more powerful instance" -ForegroundColor White
}

if (($successCount/$Requests)*100 -lt 95) {
    Write-Host "⚠️  Success rate is low (<95%). Check:" -ForegroundColor Red
    Write-Host "   - API health endpoints" -ForegroundColor White
    Write-Host "   - Docker resource limits" -ForegroundColor White
    Write-Host "   - Network connectivity" -ForegroundColor White
}

Write-Host ""
Write-Host "Load test completed!" -ForegroundColor Green