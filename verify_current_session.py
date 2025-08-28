#!/usr/bin/env python3
"""
Quick verification of current Breeze API session and connection
"""

import os
import sys
import json

# Add current directory to path to import breeze_connector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from breeze_connector import BreezeConnector
    
    print("🔍 Current Session Verification")
    print("="*50)
    
    # Initialize connector
    connector = BreezeConnector()
    
    print("📋 Environment Variables:")
    print(f"API Key: {connector.api_key[:10]}..." if connector.api_key else "❌ Missing")
    print(f"Session Token: {connector.session_token[:10]}..." if connector.session_token else "❌ Missing")
    print(f"Client Code: {connector.client_code}" if connector.client_code else "❌ Missing")
    
    # Test connection
    print("\n🔗 Testing Connection...")
    if connector.connect():
        print("✅ Successfully connected to Breeze API")
        
        # Test customer details
        try:
            customer_details = connector.breeze.get_customer_details()
            print("\n📊 Customer Details:")
            print(json.dumps(customer_details, indent=2))
            
            # Check segments allowed
            if 'Success' in customer_details:
                segments = customer_details['Success'].get('segments_allowed', {})
                print(f"\n✅ Trading: {segments.get('Trading', 'N/A')}")
                print(f"✅ Equity: {segments.get('Equity', 'N/A')}")
                print(f"✅ Derivatives: {segments.get('Derivatives', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Customer details failed: {e}")
    else:
        print("❌ Failed to connect to Breeze API")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*50)
print("Session verification complete!")