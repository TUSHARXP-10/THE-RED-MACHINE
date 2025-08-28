@echo off
echo 🧪 ICICI Direct Testing Suite
echo ==============================
echo.
echo This script will guide you through comprehensive testing
echo of your ICICI Direct Breeze API integration.
echo.
echo ⚠️  IMPORTANT SAFETY NOTES:
echo - Keep only ₹1000 max in your account for testing
echo - Test during market hours only (9:15 AM - 3:30 PM IST)
echo - All test orders will be cancelled immediately
echo.
echo.
echo STEP 1: Check if credentials are set...
python -c "import os; missing=[v for v in ['BREEZE_API_KEY','BREEZE_API_SECRET','BREEZE_SESSION_TOKEN'] if not os.getenv(v)]; print('Missing credentials:', missing) if missing else print('✅ All credentials found')"
echo.
echo STEP 2: If credentials missing, run setup...
if not exist .env (
    echo Setting up credentials...
    python setup_icici_credentials.py
    pause
)
echo.
echo STEP 3: Run comprehensive test...
echo Running comprehensive ICICI Direct test...
echo This may take a few minutes...
echo.
python comprehensive_icici_test.py
echo.
echo STEP 4: Review results...
echo.
echo Test complete! Check the following:
echo - comprehensive_icici_test.log (detailed results)
echo - SAFETY_CHECKLIST.md (pre-trading checklist)
echo.
echo 🎯 Next steps:
echo 1. Fix any failed tests
echo 2. Follow SAFETY_CHECKLIST.md
echo 3. Start with paper trading mode
echo.
pause