import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Test connection
try:
    response = supabase.table('market_data').select("*").limit(1).execute()
    print("✅ Supabase connection successful!")
    print("Tables created:", len(response.data))
except Exception as e:
    print("❌ Connection failed:", str(e))