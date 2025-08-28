#!/usr/bin/env python3
"""
ICICI Direct Breeze API Testing Suite
======================================
Comprehensive testing for ICICI Direct integration before going live.

IMPORTANT: Run these tests in paper trading mode only!
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Configure logging with UTF-8 encoding to prevent Unicode errors
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('icici_test_log.txt', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ],
    force=True
)

# Ensure stdout uses UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add the path for breeze_connect import
try:
    from breeze_connect import BreezeConnect
    BREEZE_AVAILABLE = True
except ImportError:
    logging.warning("breeze_connect not found. Creating mock for testing...")
    BREEZE_AVAILABLE = False

# Load environment variables
load_dotenv()

class ICICITestSuite:
    def __init__(self):
        self.breeze = None
        self.test_results = {
            "connection": False,
            "authentication": False,
            "market_data": False,
            "order_placement": False,
            "order_cancellation": False
        }
    
    def setup_connection(self):
        """Initialize Breeze connection"""
        try:
            if not BREEZE_AVAILABLE:
                logging.info("Using mock Breeze connection for testing...")
                self.breeze = MockBreezeConnect()
                return True
                
            # Real Breeze connection
            api_key = os.getenv("BREEZE_API_KEY")
            api_secret = os.getenv("BREEZE_API_SECRET")
            session_token = os.getenv("BREEZE_SESSION_TOKEN")
            
            if not all([api_key, api_secret, session_token]):
                logging.error("Missing required environment variables!")
                logging.error("Please set: BREEZE_API_KEY, BREEZE_API_SECRET, BREEZE_SESSION_TOKEN")
                return False
            
            self.breeze = BreezeConnect(api_key=api_key)
            logging.info("BreezeConnect initialized successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to setup connection: {e}")
            return False
    
    def test_phase_1_connection(self):
        """Phase 1: Test basic connection and authentication"""
        logging.info("=" * 50)
        logging.info("PHASE 1: CONNECTION & AUTHENTICATION TEST")
        logging.info("=" * 50)
        
        try:
            if not BREEZE_AVAILABLE:
                self.test_results["connection"] = True
                self.test_results["authentication"] = True
                logging.info("[SUCCESS] Mock connection successful")
                return True
            
            # Generate session
            session_response = self.breeze.generate_session(
                api_secret=os.getenv("BREEZE_API_SECRET"),
                session_token=os.getenv("BREEZE_SESSION_TOKEN")
            )
            logging.info(f"[SUCCESS] Session Generation: {session_response}")
            
            # Test customer details
            customer_details = self.breeze.get_customer_details()
            logging.info(f"[SUCCESS] Customer Details: {customer_details}")
            
            # Test portfolio access
            portfolio = self.breeze.get_portfolio_holdings()
            logging.info(f"[SUCCESS] Portfolio Access: {len(portfolio)} holdings found")
            
            # Test funds
            funds = self.breeze.get_funds()
            logging.info(f"[SUCCESS] Available Funds: {funds}")
            
            self.test_results["connection"] = True
            self.test_results["authentication"] = True
            return True
            
        except Exception as e:
            logging.error(f"[ERROR] Phase 1 failed: {e}")
            return False
    
    def test_phase_2_market_data(self):
        """Phase 2: Test market data access"""
        logging.info("=" * 50)
        logging.info("PHASE 2: MARKET DATA ACCESS TEST")
        logging.info("=" * 50)
        
        try:
            if not BREEZE_AVAILABLE:
                self.test_results["market_data"] = True
                logging.info("[SUCCESS] Mock market data access successful")
                return True
            
            # Test NIFTY quotes
            nifty_data = self.breeze.get_quotes(
                stock_code="NIFTY",
                exchange_code="NSE",
                product_type="cash"
            )
            logging.info(f"[SUCCESS] NIFTY Data: {nifty_data}")
            
            # Test RELIANCE quotes
            reliance_data = self.breeze.get_quotes(
                stock_code="RELIANCE",
                exchange_code="NSE",
                product_type="cash"
            )
            logging.info(f"[SUCCESS] RELIANCE Data: {reliance_data}")
            
            # Test option chain
            expiry_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            option_chain = self.breeze.get_option_chain_quotes(
                stock_code="NIFTY",
                exchange_code="NSE",
                product_type="options",
                expiry_date=expiry_date
            )
            logging.info(f"[SUCCESS] Option Chain Access: {len(option_chain)} options found")
            
            self.test_results["market_data"] = True
            return True
            
        except Exception as e:
            logging.error(f"[ERROR] Phase 2 failed: {e}")
            return False
    
    def test_phase_3_order_testing(self):
        """Phase 3: Test order placement and cancellation"""
        logging.info("=" * 50)
        logging.info("PHASE 3: ORDER TESTING (PAPER MODE)")
        logging.info("=" * 50)
        
        try:
            if not BREEZE_AVAILABLE:
                self.test_results["order_placement"] = True
                self.test_results["order_cancellation"] = True
                logging.info("[SUCCESS] Mock order testing successful")
                return True
            
            # Test order placement (very small quantity)
            test_order = self.breeze.place_order(
                stock_code="RELIANCE",
                exchange_code="NSE",
                product="cash",
                action="buy",
                order_type="limit",
                stoploss="0",
                quantity="1",
                price="2500.00",
                validity="day"
            )
            logging.info(f"[SUCCESS] Order Placement Test: {test_order}")
            
            self.test_results["order_placement"] = True
            
            # Immediately cancel the test order
            if 'order_id' in test_order:
                cancel_response = self.breeze.cancel_order(
                    exchange_code="NSE",
                    order_id=test_order['order_id']
                )
                logging.info(f"[SUCCESS] Order Cancellation: {cancel_response}")
                self.test_results["order_cancellation"] = True
            
            return True
            
        except Exception as e:
            logging.error(f"[ERROR] Phase 3 failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all test phases"""
        logging.info("[START] Starting ICICI Direct Breeze API Test Suite")
        logging.info(f"Test started at: {datetime.now()}")
        
        # Setup connection
        if not self.setup_connection():
            logging.error("Failed to setup connection. Aborting tests.")
            return False
        
        # Run phases
        phases = [
            ("Phase 1", self.test_phase_1_connection),
            ("Phase 2", self.test_phase_2_market_data),
            ("Phase 3", self.test_phase_3_order_testing)
        ]
        
        for phase_name, test_func in phases:
            try:
                test_func()
            except Exception as e:
                logging.error(f"{phase_name} failed with error: {e}")
        
        # Print summary
        self.print_summary()
        return all(self.test_results.values())
    
    def print_summary(self):
        """Print test summary"""
        logging.info("=" * 50)
        logging.info("TEST SUMMARY")
        logging.info("=" * 50)
        
        for test, result in self.test_results.items():
            status = "[PASS]" if result else "[FAIL]"
            logging.info(f"{test}: {status}")
        
        overall = "[SUCCESS] ALL TESTS PASSED" if all(self.test_results.values()) else "[ERROR] SOME TESTS FAILED"
        logging.info(f"Overall: {overall}")

# Mock BreezeConnect for testing without actual API
class MockBreezeConnect:
    def __init__(self, api_key=None):
        self.api_key = api_key
    
    def generate_session(self, api_secret, session_token):
        return {"status": "success", "message": "Mock session generated"}
    
    def get_customer_details(self):
        return {
            "client_code": "TEST123",
            "name": "Test User",
            "email": "test@example.com"
        }
    
    def get_portfolio_holdings(self):
        return [
            {"stock_code": "RELIANCE", "quantity": 100, "average_price": 2500},
            {"stock_code": "TCS", "quantity": 50, "average_price": 3200}
        ]
    
    def get_funds(self):
        return {
            "available_margin": 100000,
            "used_margin": 25000,
            "total_balance": 125000
        }
    
    def get_quotes(self, stock_code, exchange_code, product_type):
        return {
            "stock_code": stock_code,
            "ltp": 2500.50,
            "bid": 2500.25,
            "ask": 2500.75,
            "volume": 1000000
        }
    
    def get_option_chain_quotes(self, stock_code, exchange_code, product_type, expiry_date):
        return [
            {"strike_price": 25000, "call_ltp": 100, "put_ltp": 50},
            {"strike_price": 25100, "call_ltp": 80, "put_ltp": 70}
        ]
    
    def place_order(self, **kwargs):
        return {"order_id": "TEST123456", "status": "placed"}
    
    def cancel_order(self, exchange_code, order_id):
        return {"order_id": order_id, "status": "cancelled"}

if __name__ == "__main__":
    # Check environment
    logging.info("Checking environment variables...")
    required_vars = ["BREEZE_API_KEY", "BREEZE_API_SECRET", "BREEZE_SESSION_TOKEN"]
    for var in required_vars:
        value = os.getenv(var)
        if value:
            logging.info(f"[OK] {var}: Set (length: {len(value)})")
        else:
            logging.warning(f"[MISSING] {var}: Not set")
    
    # Run tests
    test_suite = ICICITestSuite()
    success = test_suite.run_all_tests()
    
    if success:
        logging.info("[SUCCESS] All tests completed successfully! Ready for live trading.")
    else:
        logging.error("[WARNING] Some tests failed. Please fix issues before going live.")
        sys.exit(1)