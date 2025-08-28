#!/usr/bin/env python3
"""
Complete Pipeline Verification Script
Checks all components: Streamlit, Kite Connect, Trading System, and Demat Setup
"""

import os
import sys
import json
import subprocess
import requests
from datetime import datetime
import logging

def setup_logging():
    """Setup logging for pipeline verification"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('pipeline_check.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def check_streamlit_dashboard():
    """Check if Streamlit dashboard is running"""
    logger.info("🔍 Checking Streamlit dashboard...")
    try:
        response = requests.get('http://localhost:8501', timeout=5)
        if response.status_code == 200:
            logger.info("✅ Streamlit dashboard is running on http://localhost:8501")
            return True
        else:
            logger.error(f"❌ Streamlit dashboard returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        logger.error("❌ Streamlit dashboard is not accessible")
        return False

def check_kite_connect():
    """Verify Kite Connect API setup"""
    logger.info("🔍 Checking Kite Connect configuration...")
    
    required_env_vars = [
        'KITE_API_KEY',
        'KITE_API_SECRET', 
        'KITE_ACCESS_TOKEN',
        'ZERODHA_CLIENT_ID'
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    logger.info("✅ All Kite Connect environment variables are set")
    
    # Test basic Kite Connect import
    try:
        from kiteconnect import KiteConnect
        kite = KiteConnect(api_key=os.getenv('KITE_API_KEY'))
        kite.set_access_token(os.getenv('KITE_ACCESS_TOKEN'))
        
        # Test API connection
        profile = kite.profile()
        logger.info(f"✅ Kite Connect API working - Profile: {profile.get('user_name', 'Connected')}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Kite Connect API error: {str(e)}")
        return False

def check_trading_system():
    """Verify trading system components"""
    logger.info("🔍 Checking trading system components...")
    
    required_files = [
        'kite_config.json',
        'high_oi_lot_manager.py',
        'live_signal_executor.py',
        'risk_management.py',
        'trade_executor.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"❌ Missing trading system files: {missing_files}")
        return False
    
    logger.info("✅ All trading system files are present")
    
    # Test capital configuration
    try:
        with open('kite_config.json', 'r') as f:
            config = json.load(f)
        
        capital = config.get('trading_parameters', {}).get('initial_capital', 0)
        if capital == 3000:
            logger.info(f"✅ Capital configured correctly: ₹{capital}")
        else:
            logger.warning(f"⚠️ Capital configured as ₹{capital}, expected ₹3000")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error reading capital configuration: {str(e)}")
        return False

def check_demat_setup():
    """Verify demat account integration"""
    logger.info("🔍 Checking demat account setup...")
    
    try:
        from kiteconnect import KiteConnect
        kite = KiteConnect(api_key=os.getenv('KITE_API_KEY'))
        kite.set_access_token(os.getenv('KITE_ACCESS_TOKEN'))
        
        # Check holdings
        holdings = kite.holdings()
        logger.info(f"✅ Demat account connected - Holdings: {len(holdings)} items")
        
        # Check margins
        margins = kite.margins()
        equity_margin = margins.get('equity', {}).get('available', {})
        logger.info(f"✅ Available margin: ₹{equity_margin.get('cash', 0)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Demat account error: {str(e)}")
        return False

def check_otm_system():
    """Verify OTM strike selection system"""
    logger.info("🔍 Checking OTM strike selection...")
    
    try:
        from get_optimal_strikes import get_optimal_strikes
        
        # Test with sample data
        strikes = get_optimal_strikes(75000, "2024-12-19")
        
        if 'strike_selection' in strikes:
            logger.info("✅ OTM strike selection system working")
            logger.info(f"   ATM Strike: {strikes['atm_strike']}")
            logger.info(f"   50 OTM Call: {strikes['strike_selection'].get('otm_50_call', 'N/A')}")
            logger.info(f"   100 OTM Call: {strikes['strike_selection'].get('otm_100_call', 'N/A')}")
            return True
        else:
            logger.error("❌ OTM strike selection returned invalid data")
            return False
            
    except Exception as e:
        logger.error(f"❌ OTM system error: {str(e)}")
        return False

def generate_report(results):
    """Generate pipeline verification report"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'status': 'READY' if all(results.values()) else 'NEEDS_SETUP',
        'next_steps': []
    }
    
    if not results.get('streamlit'):
        report['next_steps'].append("Start Streamlit: streamlit run dashboard.py")
    
    if not results.get('kite_connect'):
        report['next_steps'].append("Update Kite API credentials in .env file")
    
    if not results.get('trading_system'):
        report['next_steps'].append("Verify kite_config.json has ₹3000 capital")
    
    if not results.get('demat'):
        report['next_steps'].append("Check Kite Connect access token validity")
    
    if not results.get('otm_system'):
        report['next_steps'].append("Verify get_optimal_strikes.py is working")
    
    return report

def main():
    """Main pipeline verification"""
    global logger
    logger = setup_logging()
    
    logger.info("🚀 Starting Complete Pipeline Verification...")
    logger.info("=" * 50)
    
    results = {}
    
    # Check all components
    results['streamlit'] = check_streamlit_dashboard()
    results['kite_connect'] = check_kite_connect()
    results['trading_system'] = check_trading_system()
    results['demat'] = check_demat_setup()
    results['otm_system'] = check_otm_system()
    
    # Generate report
    report = generate_report(results)
    
    logger.info("=" * 50)
    logger.info("📋 PIPELINE VERIFICATION COMPLETE")
    logger.info("=" * 50)
    
    for component, status in results.items():
        status_icon = "✅" if status else "❌"
        logger.info(f"{status_icon} {component.upper()}: {'READY' if status else 'NEEDS_SETUP'}")
    
    logger.info(f"\n🎯 OVERALL STATUS: {report['status']}")
    
    if report['next_steps']:
        logger.info("\n📋 NEXT STEPS:")
        for step in report['next_steps']:
            logger.info(f"   • {step}")
    
    # Save report
    with open('pipeline_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    return report

if __name__ == "__main__":
    main()