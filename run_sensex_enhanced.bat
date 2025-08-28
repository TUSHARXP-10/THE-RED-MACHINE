@echo off
title 🎯 Sensex Domain Knowledge - Quick Start
color 0A

echo.
echo    ╔═══════════════════════════════════════════════════════════════╗
echo    ║                                                               ║
echo    ║    🎯 SENSEX DOMAIN KNOWLEDGE - QUICK START                   ║
echo    ║    Transform your 98.61% model with institutional-grade     ║
echo    ║    Sensex domain knowledge                                    ║
echo    ║                                                               ║
echo    ╚═══════════════════════════════════════════════════════════════╝
echo.

:MENU
echo Choose an option:
echo.
echo    [1] 🧪 Run Comprehensive Tests
echo    [2] 📊 Generate Integration Report
echo    [3] 🔍 Check Features Extracted
echo    [4] 📈 Test with Sample Data
echo    [5] 🚀 Quick Live Integration
echo    [6] 📋 View Usage Guide
echo    [7] ❌ Exit
echo.

set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto TEST
if "%choice%"=="2" goto REPORT
if "%choice%"=="3" goto FEATURES
if "%choice%"=="4" goto SAMPLE
if "%choice%"=="5" goto LIVE
if "%choice%"=="6" goto GUIDE
if "%choice%"=="7" goto EXIT

echo Invalid choice. Please try again.
goto MENU

:TEST
echo.
echo 🧪 Running comprehensive tests...
echo.
python integrate_sensex_knowledge.py --test
if errorlevel 1 (
    echo ❌ Tests failed - check sensex_integration.log for details
) else (
    echo ✅ Tests completed successfully!
)
pause
goto MENU

:REPORT
echo.
echo 📊 Generating integration report...
echo.
python integrate_sensex_knowledge.py --report
if exist "sensex_integration_report.md" (
    echo ✅ Report saved to sensex_integration_report.md
    echo Opening report...
    start sensex_integration_report.md
) else (
    echo ❌ Report generation failed
)
pause
goto MENU

:FEATURES
echo.
echo 🔍 Checking Sensex domain features...
echo.
python -c "
from sensex_domain_knowledge import SensexDomainKnowledge
import pandas as pd
import numpy as np

# Create sample data
dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
np.random.seed(42)

sample_data = pd.DataFrame({
    'RELIANCE': np.random.normal(2500, 50, 30),
    'HDFC': np.random.normal(1600, 30, 30),
    'INFOSYS': np.random.normal(1500, 25, 30),
    'ICICIBANK': np.random.normal(1000, 20, 30),
    'TCS': np.random.normal(3200, 40, 30),
    'SENSEX': np.random.normal(50000, 500, 30),
    'VIX': np.random.normal(15, 2, 30)
}, index=dates)

dk = SensexDomainKnowledge()
features = dk.extract_sensex_domain_features(sample_data)

print(f'✅ Extracted {len(features)} Sensex domain features:')
print()
for name, value in list(features.items())[:10]:
    print(f'   {name}: {value:.4f}')
if len(features) > 10:
    print(f'   ... and {len(features)-10} more features')
"
pause
goto MENU

:SAMPLE
echo.
echo 📈 Testing with realistic sample data...
echo.
python -c "
from integrate_sensex_knowledge import SensexIntegrationTester

tester = SensexIntegrationTester()
results = tester.test_domain_features()

print('📊 Sample Data Test Results:')
print(f'   Features Extracted: {results[\"features_extracted\"]}')
print(f'   Non-zero Features: {results[\"non_zero_features\"]}')
print(f'   Key Insights: {len(results[\"key_insights\"])}')
print()
print('🎯 Top Insights:')
for insight in results['key_insights'][:3]:
    print(f'   • {insight}')
"
pause
goto MENU

:LIVE
echo.
echo 🚀 Setting up quick live integration...
echo.

if exist "your_model.py" (
    echo ✅ Found your_model.py - creating integration wrapper...
    
    echo Creating enhanced_model_wrapper.py...
    (
        echo from sensex_domain_knowledge import SensexDomainAwareModel
        echo import pandas as pd
        echo.
        echo class EnhancedSensexModel:
        echo     def __init__(self, base_model):
        echo         self.base_model = base_model
        echo         self.enhanced = SensexDomainAwareModel(base_model)
        echo         self.current_position = 0.0
        echo.
        echo     def predict(self, market_data):
        echo         base_pred = self.base_model.predict(market_data)
        echo         enhanced_pred = self.enhanced.predict_with_domain_knowledge(
        echo             market_data, base_pred, self.current_position
        echo         )
        echo         explanation = self.enhanced.get_domain_explanation(
        echo             market_data, base_pred, self.current_position
        echo         )
        echo         return enhanced_pred, explanation
        echo.
        echo     def update_position(self, position):
        echo         self.current_position = position
        echo.
        echo # Usage example
        echo if __name__ == "__main__":
        echo     from your_model import YourModel  # Replace with your model
        echo     base_model = YourModel()
        echo     enhanced_model = EnhancedSensexModel(base_model)
        echo.
        echo     # Test with sample data
        echo     sample_data = pd.read_csv('your_market_data.csv')
        echo     signal, explanation = enhanced_model.predict(sample_data)
        echo     print(f"Enhanced Signal: {signal:.3f}")
    ) > enhanced_model_wrapper.py
    
    echo ✅ Created enhanced_model_wrapper.py
    echo.
    echo 📋 Integration template created!
    echo Edit enhanced_model_wrapper.py to match your model interface
    
) else (
    echo ❌ Could not find your_model.py
    echo.
    echo 📋 Creating template for your reference...
    (
        echo # Replace this with your actual 98.61% model
        echo import pandas as pd
        echo import numpy as np
        echo.
        echo class YourModel:
        echo     def predict(self, market_data):
        echo         # Your 98.61% model logic here
        echo         return np.random.choice([-1, 0, 1], p=[0.15, 0.70, 0.15])
    ) > your_model_template.py
    
    echo ✅ Created your_model_template.py for reference
    echo Update this file with your actual model
)
pause
goto MENU

:GUIDE
echo.
echo 📋 Opening usage guide...
echo.
if exist "SENSEX_USAGE_GUIDE.md" (
    start SENSEX_USAGE_GUIDE.md
) else (
    echo ❌ Usage guide not found
    echo Creating quick usage summary...
    (
        echo 🎯 Quick Sensex Integration Steps:
        echo.
        echo 1. python integrate_sensex_knowledge.py --test
        echo 2. python integrate_sensex_knowledge.py --report  
        echo 3. Use EnhancedSensexModel wrapper
        echo 4. Monitor performance daily
        echo.
        echo See sensex_domain_knowledge.py for full documentation
    ) > quick_steps.txt
    start quick_steps.txt
)
pause
goto MENU

:EXIT
echo.
echo 👋 Thank you for using Sensex Domain Knowledge!
echo.
echo 💡 Remember:
echo    • Test thoroughly before live deployment
echo    • Monitor performance metrics
echo    • Adjust weights based on market conditions
echo.
pause
exit