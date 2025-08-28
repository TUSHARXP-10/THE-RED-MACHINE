@echo off
echo 🎯 T-75 Trading System Launch Script
echo ======================================
echo.
echo 📅 Date: %date%
echo 🕐 Time: %time%
echo.

REM Check if it's trading day
echo 🔍 Checking market hours...
python -c "
from datetime import datetime
from zoneinfo import ZoneInfo
now = datetime.now(ZoneInfo('Asia/Kolkata'))
weekday = now.weekday()
if weekday > 4:
    print('❌ Weekend detected - no trading today')
    exit(1)
print(f'✅ Weekday detected: {weekday}')
print(f'✅ Current time: {now.strftime(\"%H:%M:%S IST\")}')
"

if %errorlevel% neq 0 (
    echo.
    echo 🛑 Weekend detected - no trading today
    pause
    exit /b 1
)

REM Final system verification
echo.
echo 🔍 Running final system check...
python verify_system_ready.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ System not ready - fix issues first
    pause
    exit /b 1
)

REM Check if market is open
echo.
echo 📈 Checking if market is open...
python -c "
from datetime import datetime
from zoneinfo import ZoneInfo
now = datetime.now(ZoneInfo('Asia/Kolkata'))
market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
if now < market_open:
    print('⚠️ Market not open yet - waiting until 9:15 AM')
    exit(1)
else:
    print('✅ Market is OPEN - launching system!')
"

if %errorlevel% neq 0 (
    echo.
    echo ⏰ Market not open yet - waiting until 9:15 AM
    echo 🕐 Current time: %time%
    echo 📋 Launch checklist: T75_PRE_LAUNCH_CHECKLIST.md
    pause
    exit /b 1
)

REM Launch the trading system
echo.
echo 🚀 LAUNCHING TRADING SYSTEM!
echo ==============================
echo 🎯 Starting minimal_trading_system.py...
echo 📊 Logs: trade_log_%date:~-4,4%%date:~-10,2%%date:~-7,2%.txt
echo 🔔 Monitor: Keep this window open for live updates

python minimal_trading_system.py

echo.
echo 🏁 Trading session completed
echo 📊 Check trade_log_%date:~-4,4%%date:~-10,2%%date:~-7,2%.txt for results
echo.
pause