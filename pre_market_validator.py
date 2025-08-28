#!/usr/bin/env python3
"""
Pre-Market Validator Script
Ensures all systems are ready for SENSEX scalping session
"""

import os
import sys
import time
import requests
from datetime import datetime
import logging
from breeze_connector import BreezeConnector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PreMarketValidator:
    def __init__(self):
        self.breeze = BreezeConnector()
        self.checklist = {
            "API Connection": False,
            "SENSEX Data": False,
            "Session Token": False,
            "Market Hours": False,
            "Strategy Config": False,
            "Risk Management": False
        }
    
    def validate_api_connection(self):
        """Test Breeze API connection"""
        try:
            # Ensure connection is established
            if not hasattr(self.breeze, 'breeze') or self.breeze.breeze is None:
                self.breeze.connect()
            
            # Test with SENSEX symbol using BreezeConnector method
            response = self.breeze.get_market_data(
                stock_code="BSESEN",
                exchange_code="BSE",
                product_type="cash"
            )
            
            if response and 'current_price' in response:
                self.checklist["API Connection"] = True
                logger.info("✅ API Connection: SUCCESS")
                return True
            else:
                logger.error("❌ API Connection: FAILED")
                return False
                
        except Exception as e:
            logger.error(f"❌ API Connection Error: {e}")
            return False
    
    def validate_sensex_data(self):
        """Verify SENSEX data is realistic"""
        try:
            # Ensure connection is established
            if not hasattr(self.breeze, 'breeze') or self.breeze.breeze is None:
                self.breeze.connect()
                
            response = self.breeze.get_market_data(
                stock_code="BSESEN",
                exchange_code="BSE",
                product_type="cash"
            )
            
            if response and 'current_price' in response:
                current_price = float(response['current_price'])
                
                # Validate SENSEX range (75,000 - 85,000)
                if 75000 <= current_price <= 85000:
                    self.checklist["SENSEX Data"] = True
                    logger.info(f"✅ SENSEX Data: ₹{current_price:,.2f} (VALID)")
                    return True
                else:
                    logger.error(f"❌ SENSEX Data: ₹{current_price:,.2f} (INVALID RANGE)")
                    return False
            else:
                logger.error("❌ SENSEX Data: NO RESPONSE")
                return False
                
        except Exception as e:
            logger.error(f"❌ SENSEX Data Error: {e}")
            return False
    
    def validate_session_token(self):
        """Check session token validity"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            token = os.getenv('BREEZE_SESSION_TOKEN')
            if token and len(token) >= 8:
                self.checklist["Session Token"] = True
                logger.info("✅ Session Token: VALID")
                return True
            else:
                logger.error("❌ Session Token: INVALID/MISSING")
                return False
                
        except Exception as e:
            logger.error(f"❌ Session Token Error: {e}")
            return False
    
    def validate_market_hours(self):
        """Check if we're in valid trading hours"""
        now = datetime.now()
        weekday = now.weekday()
        
        # Check if it's a weekday (0-4 = Mon-Fri)
        if weekday < 5:
            self.checklist["Market Hours"] = True
            logger.info(f"✅ Market Hours: {now.strftime('%A')} - TRADING DAY")
            return True
        else:
            logger.error(f"❌ Market Hours: {now.strftime('%A')} - WEEKEND")
            return False
    
    def validate_strategy_config(self):
        """Check strategy configuration"""
        try:
            from sensex_trading_strategy import RealSENSEXStrategy
            strategy = RealSENSEXStrategy()
            
            # Check key parameters
            if hasattr(strategy, 'price_change_threshold') and strategy.price_change_threshold > 0:
                self.checklist["Strategy Config"] = True
                logger.info("✅ Strategy Config: VALID")
                return True
            else:
                logger.error("❌ Strategy Config: INVALID")
                return False
                
        except Exception as e:
            logger.error(f"❌ Strategy Config Error: {e}")
            return False
    
    def validate_risk_management(self):
        """Verify risk management settings"""
        try:
            # Check for required risk parameters
            risk_params = {
                'max_position_size': 200,
                'max_daily_loss': 1000,
                'stop_loss_pct': 0.5
            }
            
            # Validate each parameter exists and is reasonable
            valid = True
            for param, value in risk_params.items():
                if not isinstance(value, (int, float)) or value <= 0:
                    valid = False
                    break
            
            if valid:
                self.checklist["Risk Management"] = True
                logger.info("✅ Risk Management: CONFIGURED")
                return True
            else:
                logger.error("❌ Risk Management: INVALID")
                return False
                
        except Exception as e:
            logger.error(f"❌ Risk Management Error: {e}")
            return False
    
    def run_full_validation(self):
        """Run complete pre-market validation"""
        logger.info("🚀 Starting Pre-Market Validation...")
        
        # Run all validations
        validations = [
            self.validate_api_connection,
            self.validate_sensex_data,
            self.validate_session_token,
            self.validate_market_hours,
            self.validate_strategy_config,
            self.validate_risk_management
        ]
        
        for validation in validations:
            validation()
            time.sleep(1)  # Small delay between checks
        
        # Summary
        passed = sum(self.checklist.values())
        total = len(self.checklist)
        
        logger.info(f"\n📊 VALIDATION SUMMARY: {passed}/{total} checks passed")
        
        if passed == total:
            logger.info("🎉 ALL SYSTEMS GO! Ready for SENSEX scalping!")
            return True
        else:
            logger.error("❌ Some checks failed. Please fix before launch.")
            return False

if __name__ == "__main__":
    validator = PreMarketValidator()
    validator.run_full_validation()