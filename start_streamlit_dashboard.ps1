# PowerShell script to start Streamlit Dashboard
Write-Host "Starting Real-Time Trading Dashboard..." -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python is not installed or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit..."
    exit 1
}

# Install required packages
Write-Host "Installing required packages..." -ForegroundColor Yellow
pip install -r streamlit_requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install packages. Please check your internet connection." -ForegroundColor Red
    Read-Host "Press Enter to exit..."
    exit 1
}

# Start Streamlit dashboard
Write-Host ""
Write-Host "Launching dashboard..." -ForegroundColor Green
Write-Host "Dashboard will open in your browser at http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the dashboard" -ForegroundColor Yellow

streamlit run real_time_dashboard.py --server.port=8501 --server.address=0.0.0.0

Read-Host "Press Enter to exit..."