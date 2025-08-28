#!/usr/bin/env python3
"""
Local test script for Hugging Face Space deployment
Tests the API endpoints before pushing to Hugging Face
"""

import requests
import json
import time

def test_local_api():
    """Test the API locally"""
    base_url = "http://localhost:7860"
    
    print("🧪 Testing Hugging Face Space locally...")
    
    try:
        # Test health endpoint
        print("\n1. Testing health endpoint...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
        # Test sample endpoint
        print("\n2. Testing sample endpoint...")
        response = requests.get(f"{base_url}/sample")
        if response.status_code == 200:
            print("✅ Sample endpoint passed")
            sample_data = response.json()
            print(f"   Sample data: {json.dumps(sample_data, indent=2)}")
        else:
            print(f"❌ Sample endpoint failed: {response.status_code}")
            return False
            
        # Test prediction endpoint
        print("\n3. Testing prediction endpoint...")
        sample_input = {
            "data": {
                "stock_price": 150.0,
                "volatility": 0.15,
                "volume": 1000000,
                "sma_20": 145.0,
                "rsi": 65.0
            }
        }
        
        response = requests.post(
            f"{base_url}/predict",
            json=sample_input,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Prediction endpoint passed")
            prediction = response.json()
            print(f"   Prediction: {json.dumps(prediction, indent=2)}")
        else:
            print(f"❌ Prediction endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
        print("\n🎉 All tests passed! Ready for Hugging Face deployment.")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to local API. Make sure it's running on localhost:7860")
        print("   Start with: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting local API tests...")
    
    # Wait a moment for API to be ready
    time.sleep(2)
    
    success = test_local_api()
    
    if success:
        print("\n📋 Next steps for Hugging Face deployment:")
        print("1. Create new Space at https://huggingface.co/spaces")
        print("2. Upload all files from this directory")
        print("3. Wait for automatic build and deployment")
        print("4. Test with the same endpoints at your Hugging Face URL")
    else:
        print("\n🔧 Fix issues above before deploying to Hugging Face")