#!/usr/bin/env python3
"""
Test script to verify API keys for FRED and Alpha Vantage
"""
import os
import requests
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_alpha_vantage():
    """Test Alpha Vantage API key"""
    try:
        api_key = os.getenv('ALPHA_VANTAGE_KEY')
        if not api_key:
            logger.error("ALPHA_VANTAGE_KEY not found in environment")
            return False
            
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AAPL&apikey={api_key}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if "Error Message" in data:
                logger.error(f"Alpha Vantage API Error: {data['Error Message']}")
                return False
            logger.info("✅ Alpha Vantage API key is working")
            return True
        else:
            logger.error(f"❌ Alpha Vantage API failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Alpha Vantage test failed: {str(e)}")
        return False

def test_fred():
    """Test FRED API key"""
    try:
        api_key = os.getenv('FRED_API_KEY')
        if not api_key:
            logger.error("FRED_API_KEY not found in environment")
            return False
            
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id=GDP&api_key={api_key}&file_type=json"
        response = requests.get(url)
        
        if response.status_code == 200:
            logger.info("✅ FRED API key is working")
            return True
        elif response.status_code == 403:
            logger.error("❌ FRED API key invalid or expired")
            return False
        elif response.status_code == 429:
            logger.error("❌ FRED API rate limit exceeded")
            return False
        else:
            logger.error(f"❌ FRED API failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ FRED test failed: {str(e)}")
        return False

if __name__ == "__main__":
    load_dotenv()
    
    print("Testing API Keys...")
    print("=" * 40)
    
    alpha_ok = test_alpha_vantage()
    fred_ok = test_fred()
    
    print("=" * 40)
    if alpha_ok and fred_ok:
        print("✅ All API keys are working!")
    else:
        print("❌ Some API keys need attention")