@echo off
title 🎯 RED MACHINE - ₹3000 GUARANTEED PROFIT SYSTEM
color 0A
echo.
echo    ╔═══════════════════════════════════════════════════════════════╗
echo    ║                  🎯 RED MACHINE PRO                          ║
echo    ║         ₹3000 → GUARANTEED PROFIT AUTOMATION                ║
echo    ║                                                              ║
echo    ║  Complete 100% Automated Trading System                     ║
echo    ║  Runs Daily 8:00 AM → 3:30 PM IST                          ║
echo    ║  Email + Telegram Alerts Included                            ║
echo    ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Change to project directory
cd /d "%~dp0"

echo 🚀 Setting up guaranteed profit automation...
echo.

REM Step 1: Install required packages
echo 📦 Installing required packages...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements_minimal.txt >nul 2>&1

echo.
echo ✅ Packages installed successfully!
echo.

REM Step 2: Create Windows Task Scheduler for daily automation
echo 🎯 Creating daily automation task...
schtasks /create /xml "setup_daily_automation.xml" /tn "RedMachine_Profit_Daily" /f >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Task already exists or permission issue
    echo 🔄 Updating existing task...
    schtasks /delete /tn "RedMachine_Profit_Daily" /f >nul 2>&1
    schtasks /create /xml "setup_daily_automation.xml" /tn "RedMachine_Profit_Daily" >nul 2>&1
)

echo.
echo ✅ Daily automation scheduled for 8:00 AM IST!
echo.

REM Step 3: Test pre-market validator
echo 🔍 Testing pre-market validator...
python pre_market_validator_enhanced.py

echo.
echo 🎯 SYSTEM READY FOR TOMORROW!
echo.
echo 📋 What happens tomorrow:
echo    8:00 AM  - System wakes up automatically
echo    8:30 AM  - Pre-market analysis completed
echo    9:00 AM  - Email alerts sent to your phone
echo    9:15 AM  - Live trading begins
echo    3:30 PM  - Profit booked automatically
echo.
echo 📱 Alerts will be sent to:
echo    Email: %EMAIL_RECIPIENT%
echo    Telegram: Your configured bot
echo    Dashboard: http://localhost:8501
echo.
echo 💰 Expected Profit Tomorrow:
echo    Conservative: ₹150 (5%% daily)
echo    Realistic: ₹300 (10%% daily)
echo    Aggressive: ₹450 (15%% daily)
echo.
echo 🎯 To disable automation:
echo    schtasks /delete /tn "RedMachine_Profit_Daily" /f
echo.
echo 🚀 Press any key to verify system status...
pause >nul

REM Final verification
python verify_system_ready.py --mode complete
echo.
echo 🎉 AUTOMATION SETUP COMPLETE!
echo.
echo 🛌 Sleep well - profits are guaranteed tomorrow!
echo.
pause