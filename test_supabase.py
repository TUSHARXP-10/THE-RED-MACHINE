import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Test connection
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Test inserting sample data
result = supabase.table('market_data').insert({
    'asset': 'SENSEX',
    'price': 72500.00,
    'volume': 1000000,
    'indicators': {'rsi': 65.5, 'macd': 150.2}
}).execute()

print("Connection successful!", result.data)