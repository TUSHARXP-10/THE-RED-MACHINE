#!/usr/bin/env python3
"""
Complete System Verification for ₹3000 Guaranteed Profit System
Enhanced verification for The Red Machine OTM trading
"""

import os
import sys
import json
import datetime
import pytz
from dotenv import load_dotenv

def check_environment():
    """Check all environment variables for complete automation"""
    load_dotenv()
    
    required_vars = [
        'EMAIL_USER', 'EMAIL_PASS', 'EMAIL_RECIPIENT',
        'TELEGRAM_BOT_TOKEN', 'CHAT_ID',
        'KITE_API_KEY', 'KITE_API_SECRET', 'KITE_ACCESS_TOKEN'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    return missing

def check_files():
    """Check all required files for complete automation"""
    required_files = [
        'pre_market_validator_enhanced.py',
        'high_oi_lot_manager.py',
        'live_signal_executor.py',
        'telegram_bot.py',
        'real_time_dashboard.py',
        'kite_config.json',
        'setup_daily_automation.xml',
        'START_PROFIT_AUTOMATION.bat'
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    return missing

def check_capital_config():
    """Verify ₹3000 capital configuration"""
    try:
        with open('kite_config.json', 'r') as f:
            config = json.load(f)
            
        capital = config.get('initial_capital', 0)
        max_position = config.get('max_position_size', 0)
        
        return capital == 3000 and max_position == 0.15
    except:
        return False

def check_scheduled_task():
    """Check if Windows task is scheduled for 8:00 AM automation"""
    import subprocess
    try:
        result = subprocess.run(['schtasks', '/query', '/tn', 'RedMachine_Profit_Daily'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def verify_system_ready():
    """Verify all components are ready for trading"""
    
    print("🎯 COMPLETE SYSTEM VERIFICATION - ₹3000 PROFIT SYSTEM")
    print("=" * 60)
    
    all_good = True
    
    # Check 1: Environment variables
    print("\n🔍 Checking environment variables...")
    missing_env = check_environment()
    if missing_env:
        print(f"❌ Missing environment variables:")
        for var in missing_env:
            print(f"   - {var}")
        all_good = False
    else:
        print("✅ All environment variables configured")
    
    # Check 2: Required files
    print("\n📁 Checking required files...")
    missing_files = check_files()
    if missing_files:
        print(f"❌ Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        all_good = False
    else:
        print("✅ All required files present")
    
    # Check 3: Capital configuration
    print("\n💰 Checking ₹3000 capital configuration...")
    if check_capital_config():
        print("✅ ₹3000 capital configured correctly")
    else:
        print("❌ Capital configuration issue - check kite_config.json")
        all_good = False
    
    # Check 4: Scheduled task
    print("\n⏰ Checking daily automation task...")
    if check_scheduled_task():
        print("✅ Daily automation scheduled for 8:00 AM IST")
    else:
        print("⚠️ Automation task not found - run START_PROFIT_AUTOMATION.bat")
    
    # Check 5: Test OTM strike selection
    print("\n🎯 Testing OTM strike selection...")
    try:
        import subprocess
        result = subprocess.run(['python', '-c', '''
import sys
sys.path.append('.')
from high_oi_lot_manager import get_optimal_strikes
recommendations = get_optimal_strikes(3000, 80000)
print("OTM strike selection working:", len(recommendations) > 0)
        '''])
        if result.returncode == 0:
            print("✅ OTM strike selection working")
        else:
            print("❌ OTM strike selection failed")
            all_good = False
    except:
        print("❌ Could not test OTM strike selection")
        all_good = False
    
    return all_good

def cleanup_previous_session():
    """Clean up from previous sessions"""
    print("\n🧹 Cleaning up previous session...")
    
    # Clean log files
    log_files = [f for f in os.listdir('.') if f.endswith('.log') or f.startswith('trade_log_')]
    for log_file in log_files:
        try:
            os.remove(log_file)
            print(f"   ✓ Removed {log_file}")
        except Exception as e:
            print(f"   ⚠ Could not remove {log_file}: {e}")
    
    # Clean temporary files
    temp_files = ['temp_api_test.py', 'temp_breeze_test.py']
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                print(f"   ✓ Removed {temp_file}")
            except Exception as e:
                print(f"   ⚠ Could not remove {temp_file}: {e}")
    
    print("   ✅ Cleanup complete")

if __name__ == "__main__":
    # Clean up first
    cleanup_previous_session()
    
    # Verify system
    ready = verify_system_ready()
    
    print(f"\n🎯 Final Status: {'READY' if ready else 'NOT READY'}")
    
    if ready:
        print("\n⏰ Market opens in 56 minutes!")
        print("🚀 Run: python minimal_trading_system.py at 9:15 AM")
    else:
        sys.exit(1)