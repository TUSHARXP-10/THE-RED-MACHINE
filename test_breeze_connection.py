# test_breeze_connection.py - Simple script to test Breeze API connection

import os
import logging
from dotenv import load_dotenv
import time
import json
import requests
from datetime import datetime
from breeze_connect import BreezeConnect

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()
BREEZE_API_KEY = os.getenv("BREEZE_API_KEY")
BREEZE_API_SECRET = os.getenv("BREEZE_API_SECRET")
BREEZE_SESSION_TOKEN = os.getenv("BREEZE_SESSION_TOKEN")
ICICI_CLIENT_CODE = os.getenv("ICICI_CLIENT_CODE")

def test_breeze_connection():
    """Test connection to Breeze API"""
    logging.info("Testing Breeze API connection...")
    
    # Check if environment variables are set
    if not all([BREEZE_API_KEY, BREEZE_API_SECRET, BREEZE_SESSION_TOKEN, ICICI_CLIENT_CODE]):
        logging.error("Missing required environment variables. Please check your .env file.")
        logging.info("Required variables: BREEZE_API_KEY, BREEZE_API_SECRET, BREEZE_SESSION_TOKEN, ICICI_CLIENT_CODE")
        return False
    
    logging.info("Environment variables loaded successfully")
    
    # In a real implementation, you would use the Breeze SDK
    # For this test, we'll just verify the credentials are available
    
    # Print masked credentials for verification
    logging.info(f"API Key: {BREEZE_API_KEY[:4]}...{BREEZE_API_KEY[-4:]}")
    logging.info(f"API Secret: {BREEZE_API_SECRET[:4]}...{BREEZE_API_SECRET[-4:] if len(BREEZE_API_SECRET) > 8 else '****'}")
    logging.info(f"Session Token: {BREEZE_SESSION_TOKEN[:4]}...{BREEZE_SESSION_TOKEN[-4:] if len(BREEZE_SESSION_TOKEN) > 8 else '****'}")
    logging.info(f"Client Code: {ICICI_CLIENT_CODE}")
    
    # Simulate API connection
    logging.info("Simulating API connection...")
    time.sleep(2)  # Simulate network delay
    
    # In a real implementation, you would make an actual API call here
    # For example:
    try:
        # Initialize Breeze API
        breeze = BreezeConnect(api_key=BREEZE_API_KEY)
        breeze.generate_session(api_secret=BREEZE_API_SECRET, session_token=BREEZE_SESSION_TOKEN)

        # Make a simple API call, e.g., get historical data for a dummy stock
        # This requires a valid stock code and date range
        # For a simple connection test, we can try to get holdings or account balance if available
        # As a fallback, we can use a known public endpoint or a simple data request
        
        # Attempt to get holdings as a robust test of authentication and connection
        logging.info("Attempting to fetch demat holdings...")
        holdings = breeze.get_demat_holdings()
        
        if holdings and holdings['Status'] == 200:
            logging.info("API connection successful! Holdings fetched.")
            # logging.info(f"Holdings: {holdings['Success']}") # Uncomment to see actual holdings
            return True
        elif holdings and holdings['Status'] == 500 and holdings.get('Error') == 'No Data Found':
            logging.info("API connection successful! No holdings found (expected for new accounts or no positions).")
            return True
        else:
            logging.error(f"API connection failed. Holdings response: {holdings}")
            return False
    except Exception as e:
        logging.error(f"API connection failed with error: {e}")
        return False
    
    # For now, just return success if we have all the credentials
    # logging.info("Credentials verification complete. In a real implementation, this would test the actual API connection.")
    # logging.info("To implement actual API connection, uncomment the API call code in this script.")
    # return True

if __name__ == "__main__":
    print("\n===== Breeze API Connection Test =====\n")
    result = test_breeze_connection()
    print("\n===== Test Results =====")
    if result:
        print("✅ Credentials verification successful!")
        print("NOTE: This only verifies that credentials are present in your .env file.")
        print("To test actual API connectivity, modify this script to make a real API call.")
    else:
        print("❌ Credentials verification failed!")
        print("Please check your .env file and ensure all required variables are set correctly.")
    print("\n=================================")