@echo off
title THE-RED MACHINE - Market Hours Trading System

echo.
echo ================================================
echo THE-RED MACHINE - Market Hours Trading System
echo ================================================
echo.

REM Check if market is currently open
python -c "
import datetime as dt
from zoneinfo import ZoneInfo
import sys

now = dt.datetime.now(ZoneInfo('Asia/Kolkata'))

# Check weekday
if now.weekday() > 4:
    print(f'Markets CLOSED - Weekend ({now.strftime(\"%A\"))')
    sys.exit(1)

# Check market hours
market_open = dt.datetime.combine(now.date(), dt.time(9, 15))
market_close = dt.datetime.combine(now.date(), dt.time(15, 30))

if market_open <= now <= market_close:
    print(f'Markets OPEN - Current time: {now.strftime(\"%H:%M IST\")}')
    sys.exit(0)
else:
    if now < market_open:
        next_open = market_open
    else:
        next_open = market_open + dt.timedelta(days=1)
        if next_open.weekday() > 4:
            days_until_monday = 7 - next_open.weekday()
            next_open += dt.timedelta(days=days_until_monday)
    
    print(f'Markets CLOSED - Next open: {next_open.strftime(\"%A %H:%M IST\")}')
    sys.exit(1)
"

if errorlevel 1 (
    echo.
    echo ❌ Market is CLOSED. Trading system will NOT start.
    echo.
    echo 💡 Use Windows Task Scheduler to run this script:
    echo    - Monday-Friday: 9:15 AM - 3:30 PM IST
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Market is OPEN. Starting trading system...
echo.

REM Start the trading system
python minimal_trading_system.py

echo.
echo Trading system stopped.
pause