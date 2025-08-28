@echo off
echo ===================================
echo MINIMAL TRADING SYSTEM - TEST SUITE
echo ===================================
echo.

echo This script will run all test components to verify your setup.
echo.

echo Press any key to begin testing...
pause > nul

echo.
echo ===================================
echo STEP 1: Testing Breeze API Connection
echo ===================================
python test_breeze_connection.py
echo.

echo Press any key to continue to the next test...
pause > nul

echo.
echo ===================================
echo STEP 2: Testing Model Loading
echo ===================================
python test_model_loading.py
echo.

echo Press any key to continue to the next test...
pause > nul

echo.
echo ===================================
echo STEP 3: Testing Email Notifications
echo ===================================
python test_email_notification.py
echo.

echo ===================================
echo All tests completed!
echo ===================================
echo.
echo If all tests passed, you're ready to run the full trading system with:
echo python minimal_trading_system.py
echo.
echo If any tests failed, please fix the issues before running the trading system.
echo.

echo Press any key to exit...
pause > nul