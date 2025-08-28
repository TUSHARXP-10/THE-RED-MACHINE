import requests
import json
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
API_URL = "http://localhost:8002/predict"
TOTAL_REQUESTS = 200
CONCURRENT_THREADS = 20
AUTH_TOKEN = "secure_token"

def generate_payload():
    """Generate random payload for API testing"""
    import random
    return {
        "data": {
            "stock_price": random.uniform(100, 200),
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

def make_request(request_id):
    """Make a single API request and return metrics"""
    headers = {
        'Authorization': f'Bearer {AUTH_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    payload = generate_payload()
    start_time = time.time()
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        end_time = time.time()
        
        return {
            'request_id': request_id,
            'status_code': response.status_code,
            'response_time': (end_time - start_time) * 1000,  # Convert to ms
            'success': response.status_code == 200,
            'error': None,
            'response_size': len(response.content) if response.status_code == 200 else 0
        }
    except Exception as e:
        end_time = time.time()
        return {
            'request_id': request_id,
            'status_code': None,
            'response_time': (end_time - start_time) * 1000,
            'success': False,
            'error': str(e),
            'response_size': 0
        }

def run_load_test():
    """Run the comprehensive load test"""
    print("🚀 Starting Comprehensive Load Test...")
    print(f"Target: {API_URL}")
    print(f"Total Requests: {TOTAL_REQUESTS}")
    print(f"Concurrent Threads: {CONCURRENT_THREADS}")
    print("-" * 50)
    
    start_time = time.time()
    results = []
    
    # Execute requests with thread pool
    with ThreadPoolExecutor(max_workers=CONCURRENT_THREADS) as executor:
        future_to_id = {executor.submit(make_request, i): i for i in range(TOTAL_REQUESTS)}
        
        for future in as_completed(future_to_id):
            result = future.result()
            results.append(result)
            
            if result['success']:
                print(f"✅ Request {result['request_id']}: {result['status_code']} ({result['response_time']:.2f}ms)")
            else:
                print(f"❌ Request {result['request_id']}: {result['error']}")
    
    end_time = time.time()
    total_duration = end_time - start_time
    
    # Calculate metrics
    successful_requests = [r for r in results if r['success']]
    failed_requests = [r for r in results if not r['success']]
    
    success_rate = len(successful_requests) / TOTAL_REQUESTS * 100
    avg_response_time = statistics.mean([r['response_time'] for r in successful_requests]) if successful_requests else 0
    min_response_time = min([r['response_time'] for r in successful_requests]) if successful_requests else 0
    max_response_time = max([r['response_time'] for r in successful_requests]) if successful_requests else 0
    
    # Print results
    print("\n" + "=" * 50)
    print("📊 LOAD TEST RESULTS")
    print("=" * 50)
    print(f"Total Duration: {total_duration:.2f} seconds")
    print(f"Total Requests: {TOTAL_REQUESTS}")
    print(f"Successful Requests: {len(successful_requests)}")
    print(f"Failed Requests: {len(failed_requests)}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Average Response Time: {avg_response_time:.2f}ms")
    print(f"Min Response Time: {min_response_time:.2f}ms")
    print(f"Max Response Time: {max_response_time:.2f}ms")
    print(f"Requests Per Second: {TOTAL_REQUESTS/total_duration:.2f}")
    
    if failed_requests:
        print("\n❌ FAILED REQUESTS:")
        for fail in failed_requests[:5]:  # Show first 5 failures
            print(f"  - Request {fail['request_id']}: {fail['error']}")
    
    return {
        'total_requests': TOTAL_REQUESTS,
        'successful_requests': len(successful_requests),
        'failed_requests': len(failed_requests),
        'success_rate': success_rate,
        'total_duration': total_duration,
        'avg_response_time': avg_response_time,
        'min_response_time': min_response_time,
        'max_response_time': max_response_time,
        'requests_per_second': TOTAL_REQUESTS/total_duration,
        'results': results
    }

if __name__ == "__main__":
    results = run_load_test()
    
    # Save detailed results
    with open('load_test_detailed_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: load_test_detailed_results.json")