@echo off
title THE RED MACHINE - Complete Trading System
color 0A
echo.
echo    ╔═══════════════════════════════════════════════════════════════╗
echo    ║                  THE RED MACHINE                            ║
echo    ║         Complete Trading System Startup                     ║
echo    ║                                                              ║
echo    ║  Starting Airflow + Model + Dashboard + Kite Integration    ║
echo    ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Change to project directory
cd /d "%~dp0"

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install required packages
echo Installing required packages...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r streamlit_requirements.txt >nul 2>&1
python -m pip install apache-airflow >nul 2>&1

REM Initialize Airflow if not already done
if not exist "airflow" (
    echo Initializing Airflow...
    set AIRFLOW_HOME=%~dp0airflow
    airflow db init >nul 2>&1
    airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com >nul 2>&1
)

REM Start the complete system
echo.
echo Starting complete trading system...
echo.
python start_complete_system.py --mode start --wait-market

echo.
echo System started successfully!
echo.
echo Services running:
echo - Airflow: http://localhost:8080 (admin/admin)
echo - Dashboard: http://localhost:8501
echo.
echo Press any key to stop all services...
pause >nul

REM Stop all services
echo Stopping all services...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im airflow.exe >nul 2>&1

echo All services stopped.
pause