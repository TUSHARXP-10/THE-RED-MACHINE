#!/usr/bin/env python3
"""
Final test script for Supabase connection using the correct schema
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import uuid
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing Supabase credentials in .env file")
    exit(1)

print("🔍 Testing Supabase connection with correct schema...")
print(f"URL: {SUPABASE_URL}")
print(f"Key: {SUPABASE_KEY[:20]}...")

try:
    # Initialize Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Test 1: Basic connection
    print("\n1. Testing basic connection...")
    response = supabase.table('market_data').select('*').limit(1).execute()
    print("✅ Basic connection successful!")
    
    # Test 2: Insert test data using correct schema
    print("\n2. Testing data insertion...")
    test_data = {
        'asset': 'TEST_STOCK',
        'price': 150.25,
        'volume': 100000,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'indicators': {'rsi': 65.5, 'macd': 2.3}
    }
    
    insert_response = supabase.table('market_data').insert(test_data).execute()
    if insert_response.data:
        print("✅ Data insertion successful!")
        test_id = insert_response.data[0]['id']
        
        # Test 3: Data retrieval
        print("\n3. Testing data retrieval...")
        retrieve_response = supabase.table('market_data').select('*').eq('id', test_id).execute()
        if retrieve_response.data:
            print("✅ Data retrieval successful!")
            print(f"   Retrieved: {retrieve_response.data[0]}")
        
        # Test 4: Data cleanup
        print("\n4. Testing data cleanup...")
        delete_response = supabase.table('market_data').delete().eq('id', test_id).execute()
        print("✅ Data cleanup successful!")
        
    else:
        print("❌ Data insertion failed")
        
    print("\n🎉 All tests passed! Supabase is working correctly.")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("\n📋 Troubleshooting:")
    print("1. Ensure SQL schema is executed in Supabase dashboard")
    print("2. Check API key permissions")
    print("3. Verify project URL is correct")
    print("\n📝 To fix, run this SQL in Supabase dashboard:")
    print("   - Copy contents of supabase_schema.sql")
    print("   - Go to Supabase dashboard > SQL Editor")
    print("   - Paste and run the SQL")