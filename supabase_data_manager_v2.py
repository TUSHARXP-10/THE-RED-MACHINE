import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseDataManagerV2:
    def __init__(self):
        """Initialize Supabase client with environment variables"""
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
        
    def store_market_data(self, asset: str, data: Dict) -> bool:
        """Store real-time market data"""
        try:
            response = self.supabase.table('market_data').insert({
                'asset': asset,
                'price': float(data.get('price', 0)),
                'volume': int(data.get('volume', 0)),
                'indicators': json.dumps(data.get('technical_indicators', {})),
                'timestamp': data.get('timestamp', datetime.now().isoformat())
            }).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error storing market data: {e}")
            return False
            
    def store_trade_execution(self, trade: Dict) -> bool:
        """Log trade execution with enhanced data"""
        try:
            response = self.supabase.table('trades').insert({
                'asset': trade['asset'],
                'direction': trade['direction'],
                'entry_price': float(trade['entry_price']),
                'quantity': int(trade['quantity']),
                'signal_strength': float(trade.get('signal_strength', 0)),
                'status': trade.get('status', 'OPEN'),
                'pnl': float(trade.get('pnl', 0))
            }).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error storing trade: {e}")
            return False
            
    def update_trade_exit(self, trade_id: str, exit_price: float, pnl: float) -> bool:
        """Update trade with exit details"""
        try:
            response = self.supabase.table('trades').update({
                'exit_price': exit_price,
                'pnl': pnl,
                'status': 'CLOSED'
            }).eq('id', trade_id).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error updating trade: {e}")
            return False
            
    def store_signal(self, signal: Dict) -> bool:
        """Store AI-generated signals"""
        try:
            response = self.supabase.table('signals').insert({
                'asset': signal['asset'],
                'signal_type': signal['type'],
                'strength': float(signal['strength']),
                'price_target': float(signal.get('price_target', 0)),
                'stop_loss': float(signal.get('stop_loss', 0)),
                'confidence': float(signal.get('confidence', 0))
            }).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error storing signal: {e}")
            return False
            
    def get_historical_performance(self, asset: str = None, days: int = 30) -> List[Dict]:
        """Retrieve performance data for analysis"""
        try:
            query = self.supabase.table('trades').select('*')
            
            if asset:
                query = query.eq('asset', asset)
                
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            response = query.gte('timestamp', start_date).execute()
            return response.data or []
        except Exception as e:
            print(f"Error retrieving performance: {e}")
            return []
            
    def get_market_data(self, asset: str, limit: int = 100) -> List[Dict]:
        """Get recent market data for an asset"""
        try:
            response = self.supabase.table('market_data')\
                .select('*')\
                .eq('asset', asset)\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            return response.data or []
        except Exception as e:
            print(f"Error retrieving market data: {e}")
            return []
            
    def update_portfolio(self, asset: str, quantity: int, average_price: float) -> bool:
        """Update portfolio holdings"""
        try:
            # Check if asset exists
            existing = self.supabase.table('portfolio')\
                .select('*')\
                .eq('asset', asset)\
                .execute()
                
            if existing.data:
                response = self.supabase.table('portfolio')\
                    .update({
                        'quantity': quantity,
                        'average_price': average_price,
                        'last_updated': datetime.now().isoformat()
                    })\
                    .eq('asset', asset)\
                    .execute()
            else:
                response = self.supabase.table('portfolio')\
                    .insert({
                        'asset': asset,
                        'quantity': quantity,
                        'average_price': average_price,
                        'total_value': quantity * average_price,
                        'last_updated': datetime.now().isoformat()
                    })\
                    .execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error updating portfolio: {e}")
            return False

# Quick setup script
```python:setup_supabase.py
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def test_supabase_connection():
    """Test Supabase connection"""
    try:
        client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
        
        # Test connection
        result = client.table('trades').select('*').limit(1).execute()
        print("✅ Supabase connection successful!")
        return True
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

if __name__ == "__main__":
    test_supabase_connection()
```

## Setup Instructions

1. **Create new Supabase project** at [supabase.com](https://supabase.com)
2. **Copy these SQL queries** and run them in the SQL Editor
3. **Update your .env file**:
   ```
   SUPABASE_URL=your_project_url
   SUPABASE_KEY=your_anon_key
   ```
4. **Install dependencies**:
   ```bash
   pip install supabase
   ```
5. **Test connection**:
   ```bash
   python setup_supabase.py
   ```

This new schema provides:
- **Complete trading data storage** with all necessary tables
- **Real-time market data capture** 
- **Trade execution logging**
- **Portfolio tracking**
- **AI signal storage**
- **Performance metrics**
- **Model prediction tracking**
- **Optimized indexes for performance**
- **Enhanced Supabase manager with error handling**