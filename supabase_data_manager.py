import os
from datetime import datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseDataManager:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
        
    def store_market_data(self, asset, data):
        """Store real-time market data"""
        try:
            response = self.supabase.table('market_data').insert({
                'asset': asset,
                'price': data['price'],
                'volume': data['volume'],
                'timestamp': data['timestamp'],
                'indicators': data['technical_indicators']
            }).execute()
            return response.data
        except Exception as e:
            print(f"Error storing market data: {e}")
            return None
            
    def store_trade_execution(self, trade):
        """Log all trade executions"""
        try:
            response = self.supabase.table('trades').insert({
                'asset': trade['asset'],
                'direction': trade['direction'],
                'entry_price': trade['entry_price'],
                'quantity': trade['quantity'],
                'signal_strength': trade['signal_strength'],
                'timestamp': datetime.now().isoformat()
            }).execute()
            return response.data
        except Exception as e:
            print(f"Error storing trade execution: {e}")
            return None
            
    def get_historical_performance(self, asset, days=30):
        """Retrieve performance data for model training"""
        try:
            response = self.supabase.table('trades').select('*').eq(
                'asset', asset
            ).gte('timestamp',
                (datetime.now() - timedelta(days=days)).isoformat()
            ).execute()
            return response.data
        except Exception as e:
            print(f"Error retrieving historical performance: {e}")
            return []