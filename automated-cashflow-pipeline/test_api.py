#!/usr/bin/env python3
"""
Quick test script to verify the financial API is working correctly
"""
import requests
import json
import time

def test_api():
    """Test the API endpoints"""
    base_url = "http://localhost:8002"
    headers = {
        "Authorization": "Bearer secure_token",
        "Content-Type": "application/json"
    }
    
    test_data = {
        "data": {
            "stock_price": 150.25,
            "volatility": 0.12,
            "volume": 1000000,
            "sma_20": 145.50,
            "sma_50": 142.30,
            "rsi": 65.5,
            "macd": 2.1,
            "bollinger_upper": 155.80,
            "bollinger_lower": 144.70,
            "vix": 18.5,
            "treasury_10y": 3.45,
            "dollar_index": 102.3
        }
    }
    
    print("🚀 Testing Financial API...")
    
    # Test health endpoint
    try:
        print("📊 Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test prediction endpoint
    try:
        print("🔮 Testing prediction endpoint...")
        start_time = time.time()
        response = requests.post(
            f"{base_url}/predict",
            headers=headers,
            json=test_data,
            timeout=30
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            duration = (end_time - start_time) * 1000
            print(f"✅ Prediction successful!")
            print(f"📈 Prediction: {result['prediction']}")
            print(f"⚠️  Risk Flag: {result['risk_flag']}")
            print(f"📊 Position Size: {result['position_size']}")
            print(f"⏱️  Response Time: {duration:.2f}ms")
            return True
        else:
            print(f"❌ Prediction failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return False

if __name__ == "__main__":
    success = test_api()
    if success:
        print("\n🎉 All tests passed! The API is working correctly.")
    else:
        print("\n💥 Some tests failed. Check the logs above.")