# THE RED MACHINE - Complete Trading System Startup
# PowerShell script for one-click startup

param(
    [switch]$WaitForMarket,
    [switch]$Interactive,
    [switch]$Stop,
    [switch]$Status
)

# Set console colors
$Host.UI.RawUI.ForegroundColor = 'Green'
$Host.UI.RawUI.BackgroundColor = 'Black'

Clear-Host

Write-Host @"
╔═══════════════════════════════════════════════════════════════╗
║                  THE RED MACHINE                            ║
║         Complete Trading System Startup                     ║
║                                                              ║
║  Starting Airflow + Model + Dashboard + Kite Integration    ║
╚═══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Red

# Change to script directory
Set-Location $PSScriptRoot

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    Read-Host "Press Enter to exit..."
    exit 1
}

# Install required packages
Write-Host "📦 Installing required packages..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
python -m pip install -r streamlit_requirements.txt --quiet
python -m pip install apache-airflow --quiet

# Initialize Airflow if needed
if (-not (Test-Path "airflow")) {
    Write-Host "🔄 Initializing Airflow..." -ForegroundColor Yellow
    $env:AIRFLOW_HOME = "$PSScriptRoot\airflow"
    airflow db init --quiet
    airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com --quiet
}

# Handle different modes
if ($Stop) {
    Write-Host "🛑 Stopping all services..." -ForegroundColor Red
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process airflow -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "✅ All services stopped" -ForegroundColor Green
    exit
}

if ($Status) {
    Write-Host "📊 Checking system status..." -ForegroundColor Cyan
    python start_complete_system.py --mode status
    Read-Host "Press Enter to continue..."
    exit
}

if ($Interactive) {
    Write-Host "🎮 Starting interactive mode..." -ForegroundColor Cyan
    python start_complete_system.py --mode interactive
    exit
}

# Start complete system
Write-Host "🚀 Starting complete trading system..." -ForegroundColor Green

$arguments = @("start_complete_system.py", "--mode", "start")

if ($WaitForMarket) {
    Write-Host "⏰ Waiting for market to open..." -ForegroundColor Yellow
    $arguments += "--wait-market"
}

# Start the system
python @arguments

Write-Host @"

✅ System started successfully!

📍 Access Points:
   • Airflow: http://localhost:8080 (admin/admin)
   • Dashboard: http://localhost:8501
   • Logs: system_startup.log

🎯 Features Available:
   • Real-time paper trading with ₹3000 capital
   • Live market data via Kite Connect
   • Model backtesting and retraining
   • Complete pipeline monitoring
   • One-click trade execution

⚠️  To stop all services, run: .\start_trading.ps1 -Stop
"@ -ForegroundColor Green

# Keep window open
Read-Host "Press Enter to stop all services..."

Write-Host "🛑 Stopping all services..." -ForegroundColor Red
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process airflow -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "✅ All services stopped" -ForegroundColor Green

Start-Sleep 2