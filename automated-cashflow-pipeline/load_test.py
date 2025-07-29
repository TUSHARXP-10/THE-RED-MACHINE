#!/usr/bin/env python3
"""
Simple load testing script for the financial API
"""
import requests
import time
import concurrent.futures
import statistics
import argparse

def test_api(url, token, request_id):
    """Test a single API request"""
    headers = {
        "Authorization": f"Bearer {token}",
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
    
    start_time = time.time()
    try:
        response = requests.post(f"{url}/predict", json=test_data, headers=headers, timeout=10)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "duration": (end_time - start_time) * 1000,
                "request_id": request_id,
                "prediction": result.get("prediction"),
                "risk_flag": result.get("risk_flag"),
                "position_size": result.get("position_size")
            }
        else:
            return {
                "success": False,
                "duration": (end_time - start_time) * 1000,
                "request_id": request_id,
                "error": f"HTTP {response.status_code}"
            }
    except Exception as e:
        end_time = time.time()
        return {
            "success": False,
            "duration": (end_time - start_time) * 1000,
            "request_id": request_id,
            "error": str(e)
        }

def main():
    parser = argparse.ArgumentParser(description="Load test the financial API")
    parser.add_argument("-r", "--requests", type=int, default=50, help="Number of requests")
    parser.add_argument("-c", "--concurrent", type=int, default=5, help="Concurrent requests")
    parser.add_argument("-u", "--url", default="http://localhost:8002", help="API base URL")
    parser.add_argument("-t", "--token", default="secure_token", help="API token")
    
    args = parser.parse_args()
    
    print(f"🚀 Starting load test: {args.requests} requests with {args.concurrent} concurrent users")
    print(f"🎯 Target: {args.url}")
    
    start_time = time.time()
    
    # Run concurrent requests
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrent) as executor:
        futures = [executor.submit(test_api, args.url, args.token, i) for i in range(1, args.requests + 1)]
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            
            if result["success"]:
                print(f"✓ Request {result['request_id']} completed in {result['duration']:.2f}ms")
            else:
                print(f"✗ Request {result['request_id']} failed: {result['error']}")
    
    end_time = time.time()
    
    # Calculate statistics
    successful_requests = [r for r in results if r["success"]]
    failed_requests = [r for r in results if not r["success"]]
    
    total_duration = end_time - start_time
    success_rate = len(successful_requests) / len(results) * 100
    
    if successful_requests:
        response_times = [r["duration"] for r in successful_requests]
        avg_response_time = statistics.mean(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
    else:
        avg_response_time = min_response_time = max_response_time = 0
    
    print("\n" + "="*50)
    print("📊 LOAD TEST RESULTS")
    print("="*50)
    print(f"Total Requests: {args.requests}")
    print(f"Successful: {len(successful_requests)}")
    print(f"Failed: {len(failed_requests)}")
    print(f"Success Rate: {success_rate:.2f}%")
    print(f"Total Time: {total_duration:.2f}s")
    print(f"Requests/Second: {args.requests/total_duration:.2f}")
    print(f"Average Response Time: {avg_response_time:.2f}ms")
    print(f"Min Response Time: {min_response_time:.2f}ms")
    print(f"Max Response Time: {max_response_time:.2f}ms")
    
    # Performance recommendations
    print("\n" + "="*50)
    print("🔍 PERFORMANCE ANALYSIS")
    print("="*50)
    
    if avg_response_time > 1000:
        print("⚠️  Average response time is high (>1s)")
        print("   Consider: Increasing CPU/memory limits")
        print("   Consider: Optimizing model inference")
        print("   Consider: Using a more powerful instance")
    
    if success_rate < 95:
        print("⚠️  Success rate is low (<95%)")
        print("   Check: API health endpoints")
        print("   Check: Docker resource limits")
        print("   Check: Network connectivity")
    
    if success_rate >= 95 and avg_response_time <= 1000:
        print("✅ Performance looks good!")
        print("   The API is responding within acceptable limits")

if __name__ == "__main__":
    main()