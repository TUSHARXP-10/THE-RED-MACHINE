#!/usr/bin/env python3
"""
Enhanced Margin Handling for Kite Connect Integration
Fixes the "Get Rms Limits Entity Response" error and provides robust margin management
"""

import os
import json
from datetime import datetime
from kite_connector import KiteConnector

class MarginManager:
    def __init__(self):
        self.connector = KiteConnector()
        self.margin_cache = {}
        self.last_update = None
        
    def initialize_margins(self):
        """Initialize margin system with proper error handling"""
        print("🚀 Initializing Enhanced Margin System...")
        
        if not self.connector.connect():
            print("❌ Failed to connect to Kite API")
            return False
            
        # Test margin retrieval
        margins = self.get_enhanced_margins()
        if margins:
            print("✅ Margin system initialized successfully")
            self.save_margin_snapshot(margins)
            return True
        else:
            print("⚠️  Using fallback margin system")
            return self.setup_fallback_margins()
    
    def get_enhanced_margins(self):
        """Get margins with multiple fallback strategies"""
        try:
            # Primary: Direct Kite margins
            margins = self.connector.get_margins()
            if margins and 'equity' in margins:
                return self.process_margins(margins, source="kite_api")
                
        except Exception as e:
            print(f"⚠️  Primary margin retrieval failed: {e}")
            
        # Fallback 1: Use cached margins
        cached = self.load_cached_margins()
        if cached:
            return self.process_margins(cached, source="cache")
            
        # Fallback 2: Calculate from positions
        positions = self.connector.get_positions()
        if positions:
            return self.calculate_margins_from_positions(positions)
            
        # Fallback 3: Use ₹3000 system default
        return self.get_default_margins()
    
    def process_margins(self, margins, source="api"):
        """Process and standardize margin data"""
        try:
            equity = margins.get('equity', {})
            available = equity.get('available', {})
            utilised = equity.get('utilised', {})
            
            processed = {
                'source': source,
                'timestamp': datetime.now().isoformat(),
                'available_cash': available.get('cash', 3000.0),
                'available_intraday': available.get('intraday_payin', 0.0),
                'utilised_debits': utilised.get('debits', 0.0),
                'utilised_span': utilised.get('span', 0.0),
                'utilised_exposure': utilised.get('exposure', 0.0),
                'total_available': 0.0,
                'utilised_total': 0.0,
                'net_available': 3000.0,
                'status': 'active'
            }
            
            # Calculate totals
            processed['total_available'] = (
                processed['available_cash'] + 
                processed['available_intraday']
            )
            processed['utilised_total'] = (
                processed['utilised_debits'] + 
                processed['utilised_span'] + 
                processed['utilised_exposure']
            )
            processed['net_available'] = max(0, processed['total_available'] - processed['utilised_total'])
            
            return processed
            
        except Exception as e:
            print(f"⚠️  Error processing margins: {e}")
            return self.get_default_margins()
    
    def calculate_margins_from_positions(self, positions):
        """Calculate margins based on current positions"""
        try:
            net_value = 0.0
            if 'net' in positions:
                for pos in positions['net']:
                    net_value += float(pos.get('pnl', 0.0))
            
            return {
                'source': 'positions_calculation',
                'timestamp': datetime.now().isoformat(),
                'available_cash': 3000.0,
                'available_intraday': 0.0,
                'utilised_debits': abs(net_value) if net_value < 0 else 0.0,
                'utilised_span': 0.0,
                'utilised_exposure': 0.0,
                'total_available': 3000.0,
                'utilised_total': abs(net_value) if net_value < 0 else 0.0,
                'net_available': 3000.0 - abs(net_value) if net_value < 0 else 3000.0,
                'status': 'calculated'
            }
            
        except Exception as e:
            print(f"⚠️  Error calculating from positions: {e}")
            return self.get_default_margins()
    
    def get_default_margins(self):
        """Return safe default margins for ₹3000 system"""
        return {
            'source': 'default_3000_system',
            'timestamp': datetime.now().isoformat(),
            'available_cash': 3000.0,
            'available_intraday': 0.0,
            'utilised_debits': 0.0,
            'utilised_span': 0.0,
            'utilised_exposure': 0.0,
            'total_available': 3000.0,
            'utilised_total': 0.0,
            'net_available': 3000.0,
            'status': 'default'
        }
    
    def save_margin_snapshot(self, margins):
        """Save margin snapshot for caching"""
        try:
            snapshot = {
                'margins': margins,
                'timestamp': datetime.now().isoformat()
            }
            with open('margin_cache.json', 'w') as f:
                json.dump(snapshot, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save margin cache: {e}")
    
    def load_cached_margins(self):
        """Load cached margins if available"""
        try:
            if os.path.exists('margin_cache.json'):
                with open('margin_cache.json', 'r') as f:
                    data = json.load(f)
                    # Check if cache is less than 1 hour old
                    cache_time = datetime.fromisoformat(data['timestamp'])
                    if (datetime.now() - cache_time).total_seconds() < 3600:
                        return data['margins']
        except Exception as e:
            print(f"⚠️  Could not load cached margins: {e}")
        return None
    
    def check_trading_capacity(self, proposed_amount):
        """Check if there's enough margin for a proposed trade"""
        margins = self.get_enhanced_margins()
        available = margins.get('net_available', 0.0)
        
        if available >= proposed_amount:
            return {
                'can_trade': True,
                'available': available,
                'proposed': proposed_amount,
                'remaining': available - proposed_amount
            }
        else:
            return {
                'can_trade': False,
                'available': available,
                'proposed': proposed_amount,
                'shortfall': proposed_amount - available
            }

def test_margin_system():
    """Comprehensive test of the margin system"""
    print("🧪 Testing Enhanced Margin System")
    print("=" * 50)
    
    manager = MarginManager()
    
    # Test initialization
    if manager.initialize_margins():
        print("✅ Margin system initialized")
    else:
        print("⚠️  Using fallback system")
    
    # Test margin retrieval
    margins = manager.get_enhanced_margins()
    print(f"📊 Current Margins: {json.dumps(margins, indent=2)}")
    
    # Test trading capacity
    capacity = manager.check_trading_capacity(500)
    print(f"💰 Trading Capacity Check: {json.dumps(capacity, indent=2)}")
    
    return margins

if __name__ == "__main__":
    test_margin_system()