# start_trading_system.ps1 - PowerShell script to start the minimal trading system

# Set error action preference
$ErrorActionPreference = "Stop"

# Function to check if Python is installed
function Check-Python {
    try {
        $pythonVersion = python --version
        Write-Host "✅ Python detected: $pythonVersion" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Python not found! Please install Python 3.10 or higher." -ForegroundColor Red
        return $false
    }
}

# Function to check if required packages are installed
function Check-Packages {
    $requiredPackages = @("pandas", "numpy", "joblib", "python-dotenv", "requests")
    $missingPackages = @()
    
    foreach ($package in $requiredPackages) {
        try {
            $null = python -c "import $package"
            Write-Host "✅ Package found: $package" -ForegroundColor Green
        }
        catch {
            Write-Host "❌ Package missing: $package" -ForegroundColor Red
            $missingPackages += $package
        }
    }
    
    if ($missingPackages.Count -gt 0) {
        Write-Host "`nMissing packages detected. Would you like to install them now? (Y/N)" -ForegroundColor Yellow
        $response = Read-Host
        if ($response -eq "Y" -or $response -eq "y") {
            Write-Host "Installing missing packages..." -ForegroundColor Cyan
            pip install -r requirements_minimal.txt
            return $true
        }
        else {
            Write-Host "Please install the missing packages before running the trading system." -ForegroundColor Red
            return $false
        }
    }
    
    return $true
}

# Function to check if .env file exists
function Check-EnvFile {
    if (Test-Path ".env") {
        Write-Host "✅ .env file found" -ForegroundColor Green
        return $true
    }
    else {
        Write-Host "❌ .env file not found!" -ForegroundColor Red
        Write-Host "Please create a .env file with your API credentials before running the trading system." -ForegroundColor Red
        Write-Host "Example .env file contents:" -ForegroundColor Yellow
        Write-Host "BREEZE_API_KEY=your_api_key" -ForegroundColor Yellow
        Write-Host "BREEZE_API_SECRET=your_api_secret" -ForegroundColor Yellow
        Write-Host "BREEZE_SESSION_TOKEN=your_session_token" -ForegroundColor Yellow
        Write-Host "ICICI_CLIENT_CODE=your_client_code" -ForegroundColor Yellow
        Write-Host "EMAIL_HOST=smtp.example.com" -ForegroundColor Yellow
        Write-Host "EMAIL_PORT=587" -ForegroundColor Yellow
        Write-Host "EMAIL_USER=your_email@example.com" -ForegroundColor Yellow
        Write-Host "EMAIL_PASS=your_email_password" -ForegroundColor Yellow
        Write-Host "EMAIL_RECIPIENT=alerts@example.com" -ForegroundColor Yellow
        return $false
    }
}

# Function to check if model directory exists
function Check-ModelDirectory {
    if (Test-Path "./models" -PathType Container) {
        $modelFiles = Get-ChildItem "./models" -Filter "*.pkl"
        if ($modelFiles.Count -gt 0) {
            Write-Host "✅ Model directory found with $(($modelFiles | Measure-Object).Count) model files" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "❌ No model files found in ./models directory!" -ForegroundColor Red
            return $false
        }
    }
    elseif (Test-Path "./automated-cashflow-pipeline/models" -PathType Container) {
        $modelFiles = Get-ChildItem "./automated-cashflow-pipeline/models" -Filter "*.pkl"
        if ($modelFiles.Count -gt 0) {
            Write-Host "✅ Model directory found at ./automated-cashflow-pipeline/models with $(($modelFiles | Measure-Object).Count) model files" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "❌ No model files found in ./automated-cashflow-pipeline/models directory!" -ForegroundColor Red
            return $false
        }
    }
    else {
        Write-Host "❌ Model directory not found!" -ForegroundColor Red
        Write-Host "Please create a 'models' directory and place your model file(s) there." -ForegroundColor Red
        return $false
    }
}

# Main function
function Start-TradingSystem {
    Clear-Host
    Write-Host "===================================" -ForegroundColor Cyan
    Write-Host "MINIMAL TRADING SYSTEM - LAUNCHER" -ForegroundColor Cyan
    Write-Host "===================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Performing pre-flight checks..." -ForegroundColor Cyan
    Write-Host ""
    
    # Check Python installation
    $pythonOk = Check-Python
    if (-not $pythonOk) { return }
    
    # Check required packages
    $packagesOk = Check-Packages
    if (-not $packagesOk) { return }
    
    # Check .env file
    $envOk = Check-EnvFile
    if (-not $envOk) { return }
    
    # Check model directory
    $modelOk = Check-ModelDirectory
    if (-not $modelOk) { return }
    
    Write-Host ""
    Write-Host "All pre-flight checks passed!" -ForegroundColor Green
    Write-Host ""
    
    # Ask if user wants to run tests first
    Write-Host "Would you like to run the test suite first? (Recommended) (Y/N)" -ForegroundColor Yellow
    $runTests = Read-Host
    
    if ($runTests -eq "Y" -or $runTests -eq "y") {
        Write-Host "Running test suite..." -ForegroundColor Cyan
        & .\run_tests.bat
    }
    
    # Confirm trading mode
    Write-Host ""
    Write-Host "IMPORTANT: The trading system is currently set to PAPER TRADING mode." -ForegroundColor Yellow
    Write-Host "This means no real trades will be executed." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Do you want to continue with PAPER TRADING mode? (Y/N)" -ForegroundColor Yellow
    $confirmMode = Read-Host
    
    if ($confirmMode -ne "Y" -and $confirmMode -ne "y") {
        Write-Host "To switch to REAL TRADING mode, edit minimal_trading_system.py and set PAPER_TRADING = False" -ForegroundColor Red
        Write-Host "Then run this script again." -ForegroundColor Red
        return
    }
    
    # Start the trading system
    Write-Host ""
    Write-Host "Starting minimal trading system in PAPER TRADING mode..." -ForegroundColor Green
    Write-Host "Press Ctrl+C to stop the trading system." -ForegroundColor Yellow
    Write-Host ""
    
    try {
        python minimal_trading_system.py
    }
    catch {
        Write-Host "Error running trading system: $_" -ForegroundColor Red
    }
}

# Run the main function
Start-TradingSystem