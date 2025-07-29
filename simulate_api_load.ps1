# simulate_api_load.ps1 - Updated API Load Simulation Script

$uri = "http://localhost:8002/predict"
$headers = @{"Authorization"="Bearer test_secure_token"; "Content-Type"="application/json"}
$body = '{"data": [{"IV_zscore": 0.5, "oi_change": 100.0, "rsi": 50.0, "close": 103.0}]}'  # Sample payload from history

for ($i = 1; $i -le 10; $i++) {
    try {
        $response = Invoke-RestMethod -Uri $uri -Method POST -Headers $headers -Body $body -TimeoutSec 30 -ErrorAction Stop
        Write-Output "Request $i successful: $($response | ConvertTo-Json -Compress)"
    } catch {
        Write-Output "Request $i failed: $($_.Exception.Message)"
    }
    Start-Sleep -Seconds 1
}