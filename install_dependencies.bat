@echo off
echo ===================================
echo MINIMAL TRADING SYSTEM - SETUP
echo ===================================
echo.

echo This script will install all required dependencies for the minimal trading system.
echo.

echo Checking Python installation...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo Python not found! Please install Python 3.10 or higher.
    echo Visit https://www.python.org/downloads/ to download and install Python.
    pause
    exit /b
)

echo.
echo Installing required packages...
echo.

pip install -r requirements_minimal.txt

echo.
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install some packages. Please check the error messages above.
) else (
    echo All dependencies installed successfully!
    echo.
    echo You can now create your .env file with:
    echo python create_env_file.py
    echo.
    echo And run the trading system with:
    echo python minimal_trading_system.py
    echo.
    echo Or use the PowerShell launcher:
    echo powershell -ExecutionPolicy Bypass -File start_trading_system.ps1
)

echo.
echo Press any key to exit...
pause > nul