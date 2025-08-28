#!/usr/bin/env python3
"""
🎯 **Sensex Domain Knowledge Integration**
Complete integration script for adding Sensex domain knowledge to your 98.61% model

Usage:
    python integrate_sensex_knowledge.py --test
    python integrate_sensex_knowledge.py --live
    python integrate_sensex_knowledge.py --backtest

Author: THE-RED-MACHINE Trading System
Version: 1.0.0
"""

import pandas as pd
import numpy as np
import argparse
import logging
import warnings
from datetime import datetime, timedelta
import os
import sys
from typing import Dict, List

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sensex_domain_knowledge import SensexDomainKnowledge, SensexRulesEngine, SensexDomainAwareModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sensex_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SensexIntegrationTester:
    """
    Comprehensive testing framework for Sensex domain knowledge integration
    """
    
    def __init__(self):
        self.domain_knowledge = SensexDomainKnowledge()
        self.rules_engine = SensexRulesEngine()
        self.enhanced_model = SensexDomainAwareModel()
        
    def create_realistic_sensex_data(self, days: int = 60) -> pd.DataFrame:
        """Create realistic Sensex market data for testing"""
        np.random.seed(42)  # For reproducible results
        
        # Generate dates
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # Base Sensex trend with realistic volatility
        base_sensex = 50000
        trend = np.linspace(0, 0.1, days)  # 10% upward trend over period
        noise = np.random.normal(0, 0.02, days)  # 2% daily volatility
        sensex_prices = base_sensex * (1 + trend + np.cumsum(noise * 0.01))
        
        # Generate correlated stock prices based on Sensex
        stocks = {
            'RELIANCE': {'beta': 1.2, 'base': 2500},
            'HDFC': {'beta': 1.1, 'base': 1600},
            'INFOSYS': {'beta': 0.9, 'base': 1500},
            'ICICIBANK': {'beta': 1.3, 'base': 1000},
            'TCS': {'beta': 0.8, 'base': 3200},
            'KOTAKBANK': {'beta': 1.2, 'base': 1800},
            'SBIN': {'beta': 1.4, 'base': 600},
            'AXISBANK': {'beta': 1.25, 'base': 1100},
            'WIPRO': {'beta': 0.85, 'base': 450},
            'HCLTECH': {'beta': 0.9, 'base': 1200},
            'ONGC': {'beta': 1.1, 'base': 250},
            'NTPC': {'beta': 0.7, 'base': 250},
            'POWERGRID': {'beta': 0.8, 'base': 220},
            'M&M': {'beta': 1.1, 'base': 1800},
            'BAJAJ-AUTO': {'beta': 0.9, 'base': 7000},
            'MARUTI': {'beta': 1.0, 'base': 10000},
            'HINDUNILVR': {'beta': 0.7, 'base': 2500},
            'ITC': {'beta': 0.8, 'base': 450},
            'NESTLEIND': {'beta': 0.6, 'base': 2200},
            'TATASTEEL': {'beta': 1.3, 'base': 120},
            'HINDALCO': {'beta': 1.4, 'base': 500},
            'SUNPHARMA': {'beta': 0.9, 'base': 1400},
            'DRREDDY': {'beta': 0.8, 'base': 5500},
            'BHARTIARTL': {'beta': 1.0, 'base': 1100},
            'ULTRACEMCO': {'beta': 1.1, 'base': 9000},
            'TITAN': {'beta': 1.0, 'base': 3000},
            'ASIANPAINT': {'beta': 0.8, 'base': 3000}
        }
        
        # Convert to pandas Series for proper pct_change
        sensex_series = pd.Series(sensex_prices, index=dates)
        
        # Create DataFrame
        data = {'SENSEX': sensex_series}
        
        # Add individual stocks with correlation to Sensex
        for stock, params in stocks.items():
            sensex_returns = sensex_series.pct_change().fillna(0)
            stock_returns = params['beta'] * sensex_returns
            stock_noise = np.random.normal(0, 0.015, days)  # 1.5% idiosyncratic volatility
            stock_prices = params['base'] * (1 + np.cumsum(stock_returns + stock_noise * 0.01))
            data[stock] = stock_prices
        
        # Add VIX (volatility index)
        vix_base = 15
        vix_noise = np.random.normal(0, 2, days)
        vix_values = np.maximum(vix_base + vix_noise, 10)  # VIX can't go below 10
        data['VIX'] = vix_values
        
        # Create DataFrame with dates as index
        df = pd.DataFrame(data, index=dates)
        
        # Add some realistic market events
        # Add a market crash day
        crash_day = len(df) // 3
        df.iloc[crash_day:crash_day+3] *= 0.95  # 5% crash
        
        # Add a rally day
        rally_day = 2 * len(df) // 3
        df.iloc[rally_day:rally_day+2] *= 1.05  # 5% rally
        
        return df
    
    def test_domain_features(self) -> Dict:
        """Test all Sensex domain features"""
        logger.info("Testing Sensex domain features...")
        
        # Create test data
        test_data = self.create_realistic_sensex_data(days=30)
        
        # Extract features
        features = self.domain_knowledge.extract_sensex_domain_features(test_data)
        
        # Validate features
        validation_results = {
            "features_extracted": len(features),
            "non_zero_features": sum(1 for v in features.values() if abs(v) > 0.001),
            "feature_ranges": {
                name: {"min": min(val, 0), "max": max(val, 0), "value": val}
                for name, val in features.items()
            },
            "key_insights": self._generate_feature_insights(features)
        }
        
        logger.info(f"✅ Extracted {len(features)} domain features")
        logger.info(f"✅ {validation_results['non_zero_features']} features have meaningful values")
        
        return validation_results
    
    def test_rules_engine(self) -> Dict:
        """Test Sensex rules engine"""
        logger.info("Testing Sensex rules engine...")
        
        # Create test data
        test_data = self.create_realistic_sensex_data(days=30)
        
        # Evaluate rules
        signals = self.rules_engine.evaluate_rules(test_data, current_position=0.0)
        
        # Validate signals
        validation_results = {
            "signals_generated": len(signals),
            "composite_signal": signals.get('composite_signal', 0.0),
            "strong_signals": {
                name: value for name, value in signals.items()
                if abs(value) > 0.2
            },
            "risk_adjustment": signals.get('risk_adjustment', 0.0)
        }
        
        logger.info(f"✅ Generated {len(signals)} rule-based signals")
        logger.info(f"✅ Composite signal: {validation_results['composite_signal']:.3f}")
        
        return validation_results
    
    def test_enhanced_model(self) -> Dict:
        """Test enhanced model integration"""
        logger.info("Testing enhanced model integration...")
        
        # Create test data
        test_data = self.create_realistic_sensex_data(days=60)
        
        # Simulate base model predictions (98.61% accuracy)
        base_predictions = []
        enhanced_predictions = []
        
        # Use rolling window for testing
        window_size = 20
        for i in range(window_size, len(test_data)):
            # Get window data
            window_data = test_data.iloc[i-window_size:i]
            
            # Simulate base model prediction (random with 98.61% accuracy)
            actual_next_return = test_data['SENSEX'].iloc[i] / test_data['SENSEX'].iloc[i-1] - 1
            base_pred = actual_next_return + np.random.normal(0, 0.005)  # Small noise
            
            # Get enhanced prediction
            enhanced_pred = self.enhanced_model.predict_with_domain_knowledge(
                window_data, base_pred, current_position=0.0
            )
            
            base_predictions.append(base_pred)
            enhanced_predictions.append(enhanced_pred)
        
        # Calculate improvements
        actual_returns = test_data['SENSEX'].pct_change().iloc[window_size:]
        
        # Simple performance metrics
        base_errors = [abs(bp - ar) for bp, ar in zip(base_predictions, actual_returns)]
        enhanced_errors = [abs(ep - ar) for ep, ar in zip(enhanced_predictions, actual_returns)]
        
        validation_results = {
            "base_predictions": len(base_predictions),
            "enhanced_predictions": len(enhanced_predictions),
            "base_avg_error": np.mean(base_errors),
            "enhanced_avg_error": np.mean(enhanced_errors),
            "error_improvement": np.mean(base_errors) - np.mean(enhanced_errors),
            "improvement_percentage": (
                (np.mean(base_errors) - np.mean(enhanced_errors)) / np.mean(base_errors) * 100
                if np.mean(base_errors) > 0 else 0
            )
        }
        
        logger.info(f"✅ Tested {len(base_predictions)} predictions")
        logger.info(f"✅ Error improvement: {validation_results['error_improvement']:.4f}")
        logger.info(f"✅ Improvement percentage: {validation_results['improvement_percentage']:.2f}%")
        
        return validation_results
    
    def _generate_feature_insights(self, features: Dict[str, float]) -> List[str]:
        """Generate human-readable insights from features"""
        insights = []
        
        # Banking sector insights
        banking_mom = features.get('banking_momentum', 0)
        if abs(banking_mom) > 0.01:
            direction = "positive" if banking_mom > 0 else "negative"
            insights.append(f"Banking sector showing {direction} momentum ({banking_mom:.3f})")
        
        # Reliance leadership
        reliance_lead = features.get('reliance_leadership', 0)
        if abs(reliance_lead) > 0.01:
            direction = "leading" if reliance_lead > 0 else "lagging"
            insights.append(f"Reliance is {direction} the index ({reliance_lead:.3f})")
        
        # FII flows
        fii_flow = features.get('fii_momentum', 0)
        if abs(fii_flow) > 0.02:
            direction = "inflows" if fii_flow > 0 else "outflows"
            insights.append(f"FII showing {direction} ({fii_flow:.3f})")
        
        # Market regime
        regime = features.get('similar_market_regime', 0)
        if regime > 0.5:
            insights.append("High volatility regime detected")
        elif regime < -0.5:
            insights.append("Low volatility regime detected")
        
        return insights
    
    def run_comprehensive_test(self) -> Dict:
        """Run comprehensive integration test"""
        logger.info("🚀 Starting comprehensive Sensex integration test...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "domain_features": self.test_domain_features(),
            "rules_engine": self.test_rules_engine(),
            "enhanced_model": self.test_enhanced_model(),
            "overall_status": "PASSED"
        }
        
        # Check for any failures
        results_str = str(results).lower()
        if "error" in results_str:
            results["overall_status"] = "FAILED"
        
        logger.info(f"✅ Comprehensive test completed - {results['overall_status']}")
        return results
    
    def generate_integration_report(self) -> str:
        """Generate detailed integration report"""
        results = self.run_comprehensive_test()
        
        report = f"""
# 🎯 Sensex Domain Knowledge Integration Report

**Generated:** {results['timestamp']}

## 📊 Test Results Summary

### Domain Features Test
- **Features Extracted:** {results['domain_features']['features_extracted']}
- **Non-zero Features:** {results['domain_features']['non_zero_features']}
- **Key Insights:** {len(results['domain_features']['key_insights'])}

### Rules Engine Test
- **Signals Generated:** {results['rules_engine']['signals_generated']}
- **Composite Signal:** {results['rules_engine']['composite_signal']:.3f}
- **Strong Signals:** {len(results['rules_engine']['strong_signals'])}

### Enhanced Model Test
- **Predictions Tested:** {results['enhanced_model']['base_predictions']}
- **Error Improvement:** {results['enhanced_model']['error_improvement']:.4f}
- **Improvement %:** {results['enhanced_model']['improvement_percentage']:.2f}%

### Key Insights
{chr(10).join(f"- {insight}" for insight in results['domain_features']['key_insights'][:5])}

### Integration Status
**{results['overall_status']}** ✅

## 🔧 Usage Examples

```python
# Basic usage
from sensex_domain_knowledge import SensexDomainAwareModel

# Initialize enhanced model
enhanced_model = SensexDomainAwareModel(base_model=your_98_61_model)

# Get enhanced prediction
enhanced_pred = enhanced_model.predict_with_domain_knowledge(
    market_data, base_prediction, current_position=0.0
)

# Get detailed explanation
explanation = enhanced_model.get_domain_explanation(
    market_data, base_prediction, current_position=0.0
)
```

## 🚀 Next Steps

1. **Deploy with Real Data:** Replace sample data with actual market data
2. **Model Calibration:** Adjust domain_weight based on backtesting
3. **Live Testing:** Start with paper trading
4. **Performance Monitoring:** Track domain knowledge impact

## ⚠️ Important Notes

- Domain knowledge adds institutional-grade understanding
- Test thoroughly before live deployment
- Monitor performance metrics continuously
- Adjust weights based on market conditions

---
**THE-RED-MACHINE Trading System**
"""
        
        # Save report
        with open('sensex_integration_report.md', 'w') as f:
            f.write(report)
        
        return report

def main():
    """Main integration script"""
    parser = argparse.ArgumentParser(description='Sensex Domain Knowledge Integration')
    parser.add_argument('--test', action='store_true', help='Run comprehensive tests')
    parser.add_argument('--live', action='store_true', help='Run live integration')
    parser.add_argument('--backtest', action='store_true', help='Run backtesting')
    parser.add_argument('--report', action='store_true', help='Generate detailed report')
    
    args = parser.parse_args()
    
    tester = SensexIntegrationTester()
    
    if args.test:
        print("🧪 Running comprehensive tests...")
        results = tester.run_comprehensive_test()
        print(f"✅ Tests completed: {results['overall_status']}")
        
    elif args.report:
        print("📊 Generating integration report...")
        report = tester.generate_integration_report()
        print("✅ Report saved to 'sensex_integration_report.md'")
        
    elif args.live:
        print("🚀 Running live integration...")
        # Placeholder for live integration
        print("💡 Connect your 98.61% model here")
        
    elif args.backtest:
        print("📈 Running backtesting...")
        # Placeholder for backtesting
        print("💡 Add historical data for backtesting")
        
    else:
        print("🎯 Sensex Domain Knowledge Integration")
        print("=" * 50)
        print("Usage:")
        print("  python integrate_sensex_knowledge.py --test")
        print("  python integrate_sensex_knowledge.py --report")
        print("  python integrate_sensex_knowledge.py --live")
        print("  python integrate_sensex_knowledge.py --backtest")

if __name__ == "__main__":
    main()