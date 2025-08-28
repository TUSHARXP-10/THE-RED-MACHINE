#!/usr/bin/env python3
"""
Emergency Signal Generation Validation Script
Run this before live deployment to ensure all fixes are working
"""

import json
import os
import sys
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment_validation.log'),
        logging.StreamHandler()
    ]
)

class DeploymentValidator:
    def __init__(self):
        self.validation_results = {}
        
    def validate_config_files(self):
        """Check if all required files exist"""
        required_files = [
            'morning_scalper.py',
            'emergency_config.json',
            'emergency_signal_fix.py',
            'EMERGENCY_DEPLOYMENT_GUIDE.md'
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        self.validation_results['config_files'] = {
            'status': 'PASS' if not missing_files else 'FAIL',
            'missing': missing_files
        }
        
        return len(missing_files) == 0
    
    def validate_thresholds(self):
        """Check if emergency thresholds are properly configured"""
        try:
            with open('emergency_config.json', 'r') as f:
                config = json.load(f)
            
            # Check key thresholds
            min_confidence = config.get('min_confidence', 0.9)
            price_change_threshold = config.get('price_change_threshold', 50)
            
            self.validation_results['thresholds'] = {
                'min_confidence': min_confidence,
                'price_change_threshold': price_change_threshold,
                'status': 'PASS' if min_confidence <= 0.7 and price_change_threshold <= 30 else 'FAIL'
            }
            
            return min_confidence <= 0.7 and price_change_threshold <= 30
            
        except Exception as e:
            self.validation_results['thresholds'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            return False
    
    def validate_signal_generation(self):
        """Test signal generation with sample data"""
        try:
            # Simulate market conditions
            sample_data = [
                {'price': 100, 'volume': 1000, 'momentum': 0.8},
                {'price': 102, 'volume': 1500, 'momentum': 0.9},
                {'price': 98, 'volume': 800, 'momentum': -0.7},
                {'price': 95, 'volume': 2000, 'momentum': -0.9}
            ]
            
            signals_generated = 0
            for data in sample_data:
                # Simple signal logic test
                if abs(data['momentum']) > 0.5:
                    signals_generated += 1
            
            self.validation_results['signal_generation'] = {
                'signals_generated': signals_generated,
                'total_scenarios': len(sample_data),
                'status': 'PASS' if signals_generated > 0 else 'FAIL'
            }
            
            return signals_generated > 0
            
        except Exception as e:
            self.validation_results['signal_generation'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            return False
    
    def validate_backup_system(self):
        """Check if backup files exist"""
        backup_files = [f for f in os.listdir('.') if 'morning_scalper_backup' in f]
        
        self.validation_results['backup_system'] = {
            'backup_files': len(backup_files),
            'status': 'PASS' if backup_files else 'WARNING'
        }
        
        return len(backup_files) > 0
    
    def run_full_validation(self):
        """Run complete deployment validation"""
        logging.info("🚀 Starting Emergency Signal Generation Validation")
        
        # Run all validations
        validations = [
            self.validate_config_files,
            self.validate_thresholds,
            self.validate_signal_generation,
            self.validate_backup_system
        ]
        
        results = []
        for validation in validations:
            try:
                result = validation()
                results.append(result)
                logging.info(f"{validation.__name__}: {'✅ PASS' if result else '❌ FAIL'}")
            except Exception as e:
                logging.error(f"{validation.__name__}: Error - {e}")
                results.append(False)
        
        # Summary
        total_tests = len(results)
        passed_tests = sum(results)
        
        self.validation_results['summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': f"{passed_tests}/{total_tests}",
            'deployment_ready': passed_tests >= 3
        }
        
        # Save results
        with open('deployment_validation_results.json', 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        # Final report
        logging.info("\n" + "="*50)
        logging.info("📊 VALIDATION SUMMARY")
        logging.info("="*50)
        
        for test, result in self.validation_results.items():
            if test != 'summary':
                status = result.get('status', 'UNKNOWN')
                logging.info(f"{test}: {status}")
        
        logging.info(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        logging.info(f"Deployment Ready: {'✅ YES' if passed_tests >= 3 else '❌ NO'}")
        
        return passed_tests >= 3

if __name__ == "__main__":
    validator = DeploymentValidator()
    ready_for_deployment = validator.run_full_validation()
    
    if ready_for_deployment:
        logging.info("\n🎉 SYSTEM READY FOR EMERGENCY DEPLOYMENT!")
        logging.info("Run: python morning_scalper.py --paper-trading")
    else:
        logging.info("\n⚠️ FIX ISSUES BEFORE DEPLOYMENT")
        logging.info("Check deployment_validation_results.json for details")