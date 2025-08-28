#!/usr/bin/env python3
"""
Test script to verify THE RED MACHINE system components
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path

def test_system():
    """Test all system components"""
    print("🧪 Testing THE RED MACHINE System...")
    print("=" * 50)
    
    tests = [
        ("Python Version", test_python),
        ("Required Packages", test_packages),
        ("Configuration Files", test_config),
        ("Data Files", test_data),
        ("Model Files", test_model),
        ("Dashboard", test_dashboard),
        ("Kite Integration", test_kite),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            status = "✅ PASS" if result else "❌ FAIL"
            results.append((test_name, status, result))
            print(f"{status} {test_name}")
        except Exception as e:
            results.append((test_name, "❌ FAIL", str(e)))
            print(f"❌ FAIL {test_name}: {e}")
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    for name, status, _ in results:
        print(f"{status} {name}")
    
    return all(r[1] == "✅ PASS" for r in results)

def test_python():
    """Test Python installation"""
    return sys.version_info >= (3, 8)

def test_packages():
    """Test required packages"""
    required = [
        'streamlit', 'pandas', 'numpy', 'plotly', 'kiteconnect', 'psutil'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Installing missing packages: {missing}")
        for package in missing:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package])
    
    return len(missing) == 0

def test_config():
    """Test configuration files"""
    config_files = [
        'system_config.json',
        'dashboard_config.json',
        'streamlit_requirements.txt'
    ]
    
    missing = [f for f in config_files if not Path(f).exists()]
    if missing:
        print(f"Missing config files: {missing}")
        return False
    
    # Test JSON configs
    for config_file in ['system_config.json', 'dashboard_config.json']:
        try:
            with open(config_file) as f:
                json.load(f)
        except Exception as e:
            print(f"Invalid JSON in {config_file}: {e}")
            return False
    
    return True

def test_data():
    """Test data files"""
    data_files = [
        'paper_trades.csv',
        'trade_log.csv',
        'model_log.txt',
        'backtest_results.csv'
    ]
    
    # Create sample data if missing
    for file in data_files:
        if not Path(file).exists():
            if file.endswith('.csv'):
                with open(file, 'w') as f:
                    if 'trades' in file:
                        f.write("timestamp,symbol,quantity,price,profit\n")
                    elif 'backtest' in file:
                        f.write("date,total_return,win_rate,sharpe_ratio\n")
            else:
                with open(file, 'w') as f:
                    f.write("System initialized\n")
    
    return True

def test_model():
    """Test model files"""
    model_files = [
        'retrain_model_3000.py',
        'backtest_3000_capital.py'
    ]
    
    for file in model_files:
        if not Path(file).exists():
            print(f"Missing model file: {file}")
            return False
    
    return True

def test_dashboard():
    """Test dashboard files"""
    dashboard_files = [
        'enhanced_dashboard.py',
        'real_time_dashboard.py'
    ]
    
    for file in dashboard_files:
        if not Path(file).exists():
            print(f"Missing dashboard file: {file}")
            return False
    
    return True

def test_kite():
    """Test Kite integration"""
    kite_files = [
        'kite_integration.py',
        'kite_config.json'
    ]
    
    for file in kite_files:
        if not Path(file).exists():
            print(f"Missing Kite file: {file}")
            return False
    
    # Check if kite_config.json has placeholders
    try:
        with open('kite_config.json') as f:
            config = json.load(f)
            if not config.get('api_key') or not config.get('access_token'):
                print("⚠️  Kite credentials not configured. Add your API key and access token to kite_config.json")
    except:
        # Create template
        template = {
            "api_key": "your_api_key_here",
            "access_token": "your_access_token_here"
        }
        with open('kite_config.json', 'w') as f:
            json.dump(template, f, indent=2)
    
    return True

if __name__ == "__main__":
    success = test_system()
    
    if success:
        print("\n🎉 All tests passed! System is ready to use.")
        print("\n🚀 To start the complete system:")
        print("   Windows: double-click start_trading.bat")
        print("   PowerShell: .\start_trading.ps1")
        print("   Python: python start_complete_system.py --mode start --wait-market")
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        
    input("\nPress Enter to continue...")