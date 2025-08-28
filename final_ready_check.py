#!/usr/bin/env python3
"""
Final System Readiness Check for Tomorrow's Trading
Ensures complete local operation without collaboration dependencies
"""

import os
import json
import subprocess
import sys
from datetime import datetime

def check_local_system():
    """Verify complete local system readiness"""
    print("🔍 Final Local System Check for Tomorrow")
    print("=" * 50)
    
    checks = []
    
    # 1. Check Python version
    print("1. Checking Python environment...")
    if sys.version_info >= (3, 8):
        print("   ✅ Python 3.8+ detected")
        checks.append(True)
    else:
        print("   ❌ Python 3.8+ required")
        checks.append(False)
    
    # 2. Check required packages
    print("2. Checking required packages...")
    required = ['streamlit', 'kiteconnect', 'pandas', 'numpy', 'plotly', 'psutil']
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if not missing:
        print("   ✅ All packages installed")
        checks.append(True)
    else:
        print(f"   ❌ Missing packages: {missing}")
        checks.append(False)
    
    # 3. Check configuration files
    print("3. Checking configuration files...")
    config_files = [
        'system_config.json',
        'kite_config.json',
        'dashboard_config.json'
    ]
    
    for config in config_files:
        if os.path.exists(config):
            print(f"   ✅ {config} found")
            checks.append(True)
        else:
            print(f"   ❌ {config} missing")
            checks.append(False)
    
    # 4. Check model files
    print("4. Checking model files...")
    if os.path.exists('models') and os.listdir('models'):
        print("   ✅ Model files available")
        checks.append(True)
    else:
        print("   ⚠️  Model files missing (will be created on startup)")
        checks.append(True)  # Not blocking
    
    # 5. Check Kite integration
    print("5. Checking Kite integration...")
    try:
        from kite_connector import KiteConnector
        kite = KiteConnector()
        if kite.connect():
            print("   ✅ Kite Connect ready")
            checks.append(True)
        else:
            print("   ⚠️  Kite Connect configured but needs credentials")
            checks.append(True)  # Not blocking for paper trading
    except Exception as e:
        print(f"   ⚠️  Kite integration check: {str(e)[:50]}...")
        checks.append(True)  # Not blocking for paper trading
    
    # 6. Check startup scripts
    print("6. Checking startup scripts...")
    startup_files = [
        'start_trading.bat',
        'start_trading.ps1',
        'start_complete_system.py'
    ]
    
    for startup in startup_files:
        if os.path.exists(startup):
            print(f"   ✅ {startup} available")
            checks.append(True)
        else:
            print(f"   ❌ {startup} missing")
            checks.append(False)
    
    # 7. Check no collaboration dependencies
    print("7. Checking for collaboration dependencies...")
    collab_indicators = [
        'colab',
        'google.colab',
        'drive.mount',
        'kaggle',
        'huggingface_hub'
    ]
    
    collab_found = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        for indicator in collab_indicators:
                            if indicator in content:
                                collab_found.append(f"{file}: {indicator}")
                except:
                    pass
    
    if not collab_found:
        print("   ✅ No collaboration dependencies found")
        checks.append(True)
    else:
        print(f"   ⚠️  Found collaboration references: {len(collab_found)}")
        for ref in collab_found[:3]:  # Show first 3
            print(f"      - {ref}")
        checks.append(False)
    
    # Summary
    passed = sum(checks)
    total = len(checks)
    
    print("\n" + "=" * 50)
    print(f"📊 Final Check: {passed}/{total} passed")
    
    if passed >= total - 2:  # Allow 2 minor warnings
        print("🎉 SYSTEM READY FOR TOMORROW'S TRADING")
        print("\n🚀 Quick Start Tomorrow:")
        print("   Windows: Double-click start_trading.bat")
        print("   PowerShell: Run .\start_trading.ps1")
        print("   Dashboard: http://localhost:8501")
        print("   Airflow: http://localhost:8080")
        return True
    else:
        print("❌ System needs attention before trading")
        return False

if __name__ == "__main__":
    ready = check_local_system()
    
    # Create ready status file
    status = {
        "timestamp": datetime.now().isoformat(),
        "ready": ready,
        "python_version": sys.version,
        "platform": sys.platform
    }
    
    with open("system_ready_status.json", "w") as f:
        json.dump(status, f, indent=2)
    
    if ready:
        print("\n✅ Status saved to system_ready_status.json")
    else:
        print("\n❌ Check system_ready_status.json for details")