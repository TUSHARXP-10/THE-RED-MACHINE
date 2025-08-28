@echo off
echo Starting Real-Time Trading Dashboard...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install required packages
echo Installing required packages...
pip install -r streamlit_requirements.txt

REM Start Streamlit dashboard
echo.
echo Launching dashboard...
echo Dashboard will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the dashboard
streamlit run real_time_dashboard.py --server.port=8501 --server.address=0.0.0.0

pause