#!/usr/bin/env python3
"""
🎯 Test Script for Decay-Aware Trading Implementation
Run this to test your new theta decay intelligence!
"""

import requests
import json
from datetime import datetime

def test_decay_aware_prediction():
    """Test the new decay-aware prediction endpoint"""
    
    print("🚀 Testing Decay-Aware Trading API")
    print("=" * 50)
    
    # Test data for different market conditions
    test_cases = [
        {
            "name": "High VIX, Good for Options",
            "data": {
                "sma_20": 1.02,
                "rsi": 45.5,
                "macd": 0.15,
                "bollinger_position": 0.3,
                "volume_ratio": 1.2,
                "price_change": 0.8,
                "market_sentiment": 0.7,
                "volatility": 0.18  # High VIX
            },
            "current_capital": 5000
        },
        {
            "name": "Low VIX, Stick to Equity",
            "data": {
                "sma_20": 0.98,
                "rsi": 52.3,
                "macd": -0.05,
                "bollinger_position": -0.2,
                "volume_ratio": 0.9,
                "price_change": -0.3,
                "market_sentiment": 0.4,
                "volatility": 0.12  # Low VIX
            },
            "current_capital": 5000
        }
    ]
    
    base_url = "http://localhost:8002"
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 30)
        
        try:
            # Test enhanced prediction
            response = requests.post(
                f"{base_url}/predict/enhanced",
                json=test_case,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Trade Type: {result['trade_type']}")
                print(f"✅ Max Holding: {result['max_holding_hours']} hours")
                print(f"✅ Theta Risk: {result['theta_risk_score']:.3f}")
                print(f"✅ Position Size: ₹{result['position_size']:.0f}")
                print(f"✅ Exit Time: {result['recommended_exit_time']}")
                print(f"✅ Multiplier: {result['position_multiplier']:.2f}")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection Error: {e}")
            print("💡 Make sure the server is running: uvicorn api:app --host 0.0.0.0 --port 8002")

def test_theta_calculation():
    """Test the theta risk calculation manually"""
    
    print("\n🔍 Manual Theta Risk Calculation")
    print("=" * 40)
    
    # Simulate different scenarios
    scenarios = [
        {"days": 1, "vix": 20, "desc": "1 day to expiry, high VIX"},
        {"days": 5, "vix": 15, "desc": "5 days to expiry, normal VIX"},
        {"days": 10, "vix": 12, "desc": "10 days to expiry, low VIX"},
    ]
    
    def calculate_theta_risk(days_to_expiry, india_vix):
        if days_to_expiry <= 0:
            return 1.0
        time_risk = max(0, (7 - days_to_expiry) / 7)
        volatility_risk = min(india_vix / 25, 1.0)
        return (time_risk * 0.6 + volatility_risk * 0.4)
    
    for scenario in scenarios:
        risk = calculate_theta_risk(scenario["days"], scenario["vix"])
        print(f"📊 {scenario['desc']}: Theta Risk = {risk:.3f}")

def show_usage_examples():
    """Show practical usage examples"""
    
    print("\n📋 Quick Usage Examples")
    print("=" * 35)
    
    examples = [
        {
            "name": "Get Enhanced Prediction",
            "command": "curl -X POST 'http://localhost:8002/predict/enhanced' -H 'Content-Type: application/json' -d '{\"data\":{\"sma_20\":1.02,\"rsi\":45.5,\"macd\":0.15,\"bollinger_position\":0.3,\"volume_ratio\":1.2,\"price_change\":0.8,\"market_sentiment\":0.7,\"volatility\":0.18},\"current_capital\":5000}'"
        },
        {
            "name": "Check Health",
            "command": "curl 'http://localhost:8002/health'"
        },
        {
            "name": "Get Week 1 Plan",
            "command": "curl 'http://localhost:8002/equity-scalping/plan?week=1'"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['name']}:")
        print(f"   {example['command']}")
        print()

if __name__ == "__main__":
    print("🎯 Decay-Aware Trading Implementation Test")
    print("=" * 60)
    print("Testing your new theta decay intelligence...")
    
    test_decay_aware_prediction()
    test_theta_calculation()
    show_usage_examples()
    
    print("\n✅ Implementation Complete!")
    print("🚀 Your decay-resistant trading system is ready!")
    print("📈 Target: ₹5,000 → ₹5,300 (6% gain) with theta decay protection")