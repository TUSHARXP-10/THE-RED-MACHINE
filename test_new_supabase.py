import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Test connection with your new credentials
SUPABASE_URL = "https://dgenfxqyrtmnbpzdvgrd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRnZW5meHF5cnRtbmJwemR2Z3JkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYyMjMzMzQsImV4cCI6MjA3MTc5OTMzNH0.T5sTomT6M5Wlzjb5ckgyI_o5gN_KoGX7JVO315mHH-M"

print("🔍 Testing new Supabase connection...")
print(f"URL: {SUPABASE_URL}")
print(f"Key: {SUPABASE_KEY[:20]}...")

try:
    # Create client
    client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Test basic connection
    response = client.table('market_data').select("*").limit(1).execute()
    print("✅ Supabase connection successful!")
    print(f"✅ Tables accessible: {len(response.data) if response.data else 0}")
    
    # Test inserting sample data
    test_data = {
        'symbol': 'TEST',
        'close_price': 100.00,
        'volume': 1000
    }
    
    insert_response = client.table('market_data').insert(test_data).execute()
    print("✅ Data insertion successful!")
    
    # Clean up test data
    client.table('market_data').delete().eq('symbol', 'TEST').execute()
    print("✅ Test cleanup completed!")
    
    print("\n🎉 All tests passed! Your Supabase setup is ready.")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\n📋 Troubleshooting:")
    print("1. Ensure your Supabase project is active")
    print("2. Check if tables are created in Supabase dashboard")
    print("3. Verify API key permissions")