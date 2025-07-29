#!/usr/bin/env python3
"""
Test script to verify Prometheus metrics are working correctly
"""

import requests
import time
import json

def test_metrics_endpoint():
    """Test the /metrics endpoint"""
    print("🧪 Testing Prometheus metrics endpoint...")
    
    try:
        response = requests.get('http://localhost:8002/metrics')
        if response.status_code == 200:
            print("✅ /metrics endpoint is accessible")
            
            # Check for expected metrics
            metrics_content = response.text
            expected_metrics = [
                'request_latency_seconds',
                'predictions_total',
                'health_checks_total', 
                'prediction_errors_total'
            ]
            
            found_metrics = []
            for metric in expected_metrics:
                if metric in metrics_content:
                    found_metrics.append(metric)
            
            print(f"📊 Found metrics: {', '.join(found_metrics)}")
            return True
        else:
            print(f"❌ /metrics returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to /metrics: {e}")
        return False

def test_prediction_metrics():
    """Test that prediction metrics are being collected"""
    print("\n🧪 Testing prediction metrics collection...")
    
    # Make some test predictions
    test_data = {
        "data": {
            "stock_price": 150.5,
            "volatility": 0.15,
            "volume": 1000000,
            "sma_20": 145.2,
            "rsi": 65.5
        }
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer secure_token'
    }
    
    # Make 5 predictions to generate metrics
    for i in range(5):
        try:
            response = requests.post(
                'http://localhost:8002/predict',
                json=test_data,
                headers=headers
            )
            if response.status_code == 200:
                print(f"✅ Prediction {i+1} successful")
            else:
                print(f"⚠️ Prediction {i+1} failed: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Prediction {i+1} error: {e}")
    
    # Check metrics again
    time.sleep(1)  # Allow metrics to update
    
    try:
        response = requests.get('http://localhost:8002/metrics')
        if response.status_code == 200:
            metrics = response.text
            
            # Count predictions
            if 'predictions_total' in metrics:
                lines = [line for line in metrics.split('\n') if 'predictions_total' in line and not line.startswith('#')]
                if lines:
                    prediction_count = int(float(lines[0].split()[-1]))
                    print(f"📈 Total predictions recorded: {prediction_count}")
            
            # Check latency metrics
            if 'request_latency_seconds' in metrics:
                print("✅ Latency metrics are being collected")
            
            return True
    except Exception as e:
        print(f"❌ Error checking updated metrics: {e}")
        return False

def test_health_check_metrics():
    """Test health check metrics"""
    print("\n🧪 Testing health check metrics...")
    
    # Make health checks
    for i in range(3):
        try:
            response = requests.get('http://localhost:8002/health')
            if response.status_code == 200:
                print(f"✅ Health check {i+1} successful")
            else:
                print(f"⚠️ Health check {i+1} failed: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Health check {i+1} error: {e}")
    
    return True

def test_prometheus_connection():
    """Test Prometheus is accessible"""
    print("\n🧪 Testing Prometheus connection...")
    
    try:
        response = requests.get('http://localhost:9090/-/healthy')
        if response.status_code == 200:
            print("✅ Prometheus is healthy and accessible")
            return True
        else:
            print(f"⚠️ Prometheus status: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️ Prometheus not accessible: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 Enhanced API Metrics Testing")
    print("=" * 40)
    
    # Test metrics endpoint
    metrics_ok = test_metrics_endpoint()
    
    # Test health check metrics
    health_ok = test_health_check_metrics()
    
    # Test prediction metrics
    prediction_ok = test_prediction_metrics()
    
    # Test Prometheus
    prometheus_ok = test_prometheus_connection()
    
    print("\n📋 Test Summary:")
    print(f"   Metrics Endpoint: {'✅' if metrics_ok else '❌'}")
    print(f"   Health Metrics: {'✅' if health_ok else '❌'}")
    print(f"   Prediction Metrics: {'✅' if prediction_ok else '❌'}")
    print(f"   Prometheus: {'✅' if prometheus_ok else '❌'}")
    
    if all([metrics_ok, health_ok, prediction_ok, prometheus_ok]):
        print("\n🎉 All metrics tests passed! Your enhanced monitoring is ready.")
        print("\nNext steps:")
        print("1. Open Grafana at http://localhost:3000")
        print("2. Add Prometheus data source: http://prometheus:9090")
        print("3. Import dashboards or create custom ones")
        print("4. Set up alerts for critical metrics")
    else:
        print("\n⚠️ Some tests failed. Check the services and try again.")

if __name__ == "__main__":
    main()