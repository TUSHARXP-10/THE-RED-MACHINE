#!/usr/bin/env python3
"""
Simple test script for Sensex domain knowledge layer
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sensex_domain_knowledge import SensexDomainKnowledge, SensexRulesEngine, SensexDomainAwareModel

def simple_test():
    """Simple test of Sensex domain knowledge"""
    print("🎯 Testing Sensex Domain Knowledge Layer")
    print("=" * 50)
    
    # Create simple test data
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    
    data = pd.DataFrame({
        'RELIANCE': np.random.normal(2500, 50, 30),
        'HDFC': np.random.normal(1600, 30, 30),
        'INFOSYS': np.random.normal(1500, 25, 30),
        'ICICIBANK': np.random.normal(1000, 20, 30),
        'TCS': np.random.normal(3200, 40, 30),
        'SENSEX': np.random.normal(50000, 500, 30)
    }, index=dates)
    
    # Test 1: Domain Knowledge
    print("\n1. Testing Domain Knowledge...")
    dk = SensexDomainKnowledge()
    features = dk.extract_sensex_domain_features(data)
    print(f"   Features extracted: {len(features)}")
    print(f"   Sample features:")
    for name, value in list(features.items())[:5]:
        print(f"     {name}: {value:.4f}")
    
    # Test 2: Rules Engine
    print("\n2. Testing Rules Engine...")
    engine = SensexRulesEngine()
    signals = engine.evaluate_rules(data, 0.0)
    print(f"   Signals generated: {len(signals)}")
    print(f"   Composite signal: {signals.get('composite_signal', 0.0):.3f}")
    
    # Test 3: Enhanced Model
    print("\n3. Testing Enhanced Model...")
    enhanced = SensexDomainAwareModel()
    base_pred = 0.75  # Simulate 98.61% model output
    enhanced_pred = enhanced.predict_with_domain_knowledge(data, base_pred, 0.0)
    explanation = enhanced.get_domain_explanation(data, base_pred, 0.0)
    
    print(f"   Base prediction: {base_pred:.3f}")
    print(f"   Enhanced prediction: {enhanced_pred:.3f}")
    print(f"   Domain adjustment: {explanation.get('domain_adjustment', 0.0):.3f}")
    
    # Test 4: Key insights
    print("\n4. Key Insights:")
    banking_momentum = features.get('banking_momentum', 0.0)
    reliance_lead = features.get('reliance_leadership', 0.0)
    print(f"   Banking momentum: {banking_momentum:.4f}")
    print(f"   Reliance leadership: {reliance_lead:.4f}")
    
    print("\n✅ All tests completed successfully!")
    print("\n🚀 Ready to integrate with your 98.61% model!")
    
    return {
        'features': len(features),
        'signals': len(signals),
        'enhanced_prediction': enhanced_pred,
        'domain_adjustment': explanation.get('domain_adjustment', 0.0)
    }

if __name__ == "__main__":
    results = simple_test()
    print(f"\n📊 Summary:")
    print(f"   Features: {results['features']}")
    print(f"   Signals: {results['signals']}")
    print(f"   Enhancement: {results['enhanced_prediction']:.3f}")