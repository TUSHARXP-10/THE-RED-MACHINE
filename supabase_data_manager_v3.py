import os
import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client, Client
from typing import Dict, List, Optional, Any
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseDataManagerV3:
    """
    Enhanced Supabase Data Manager for THE RED MACHINE trading system
    Handles real-time market data storage, trade execution, and portfolio management
    """
    
    def __init__(self):
        """Initialize Supabase connection using environment variables"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        logger.info("✅ Supabase Data Manager initialized successfully")
    
    def store_market_data(self, symbol: str, data: Dict[str, Any]) -> bool:
        """Store real-time market data"""
        try:
            record = {
                'symbol': symbol,
                'timestamp': datetime.utcnow().isoformat(),
                'open_price': data.get('open'),
                'high_price': data.get('high'),
                'low_price': data.get('low'),
                'close_price': data.get('close'),
                'volume': data.get('volume'),
                'bid': data.get('bid'),
                'ask': data.get('ask'),
                'vwap': data.get('vwap'),
                'turnover': data.get('turnover'),
                'open_interest': data.get('oi'),
                'strike_price': data.get('strike_price'),
                'option_type': data.get('option_type'),
                'expiry_date': data.get('expiry_date')
            }
            
            response = self.client.table('market_data').insert(record).execute()
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Error storing market data: {e}")
            return False
    
    def log_trade(self, trade_data: Dict[str, Any]) -> bool:
        """Log executed trade"""
        try:
            record = {
                'trade_id': trade_data['trade_id'],
                'symbol': trade_data['symbol'],
                'order_type': trade_data['order_type'],
                'quantity': trade_data['quantity'],
                'price': trade_data['price'],
                'value': trade_data['value'],
                'brokerage': trade_data.get('brokerage', 0),
                'net_value': trade_data['net_value'],
                'kite_order_id': trade_data.get('kite_order_id'),
                'strategy_name': trade_data.get('strategy_name'),
                'signal_strength': trade_data.get('signal_strength'),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            response = self.client.table('trades').insert(record).execute()
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Error logging trade: {e}")
            return False
    
    def update_portfolio(self, symbol: str, quantity: int, price: float, 
                        realized_pnl: float = 0) -> bool:
        """Update portfolio position"""
        try:
            # Get existing position
            existing = self.client.table('portfolio').select('*').eq('symbol', symbol).execute()
            
            if existing.data:
                # Update existing position
                current = existing.data[0]
                new_quantity = current['quantity'] + quantity
                
                if new_quantity == 0:
                    # Close position
                    self.client.table('portfolio').delete().eq('symbol', symbol).execute()
                else:
                    # Update position
                    total_value = (current['quantity'] * current['average_price']) + (quantity * price)
                    new_average = total_value / new_quantity
                    
                    update_data = {
                        'quantity': new_quantity,
                        'average_price': new_average,
                        'current_price': price,
                        'total_value': new_quantity * price,
                        'realized_pnl': current['realized_pnl'] + realized_pnl,
                        'last_updated': datetime.utcnow().isoformat()
                    }
                    
                    self.client.table('portfolio').update(update_data).eq('symbol', symbol).execute()
            else:
                # Create new position
                new_position = {
                    'symbol': symbol,
                    'quantity': quantity,
                    'average_price': price,
                    'current_price': price,
                    'total_value': quantity * price,
                    'realized_pnl': realized_pnl,
                    'last_updated': datetime.utcnow().isoformat()
                }
                self.client.table('portfolio').insert(new_position).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating portfolio: {e}")
            return False
    
    def store_signal(self, signal_data: Dict[str, Any]) -> bool:
        """Store trading signal"""
        try:
            record = {
                'symbol': signal_data['symbol'],
                'signal_type': signal_data['signal_type'],
                'confidence': signal_data['confidence'],
                'predicted_price': signal_data.get('predicted_price'),
                'stop_loss': signal_data.get('stop_loss'),
                'target_price': signal_data.get('target_price'),
                'strategy_name': signal_data.get('strategy_name'),
                'model_version': signal_data.get('model_version'),
                'market_condition': signal_data.get('market_condition'),
                'expiry_date': signal_data.get('expiry_date'),
                'executed': False,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            response = self.client.table('signals').insert(record).execute()
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Error storing signal: {e}")
            return False
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get complete portfolio summary"""
        try:
            portfolio = self.client.table('portfolio').select('*').execute()
            trades = self.client.table('trades').select('*').execute()
            
            total_value = sum(pos['total_value'] for pos in portfolio.data)
            total_realized_pnl = sum(pos['realized_pnl'] for pos in portfolio.data)
            
            return {
                'positions': portfolio.data,
                'total_value': total_value,
                'total_realized_pnl': total_realized_pnl,
                'total_trades': len(trades.data)
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            return {}
    
    def get_historical_data(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """Get historical market data for a symbol"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            response = self.client.table('market_data')\
                .select('*')\
                .eq('symbol', symbol)\
                .gte('timestamp', start_date.isoformat())\
                .order('timestamp', desc=True)\
                .execute()
            
            return pd.DataFrame(response.data)
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return pd.DataFrame()
    
    def get_performance_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get performance metrics for specified period"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            trades = self.client.table('trades')\
                .select('*')\
                .gte('timestamp', start_date.isoformat())\
                .execute()
            
            if not trades.data:
                return {}
            
            df = pd.DataFrame(trades.data)
            total_trades = len(df)
            profitable_trades = len(df[df['net_value'] > 0])
            loss_trades = len(df[df['net_value'] < 0])
            
            total_pnl = df['net_value'].sum()
            win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
            
            return {
                'total_trades': total_trades,
                'profitable_trades': profitable_trades,
                'loss_trades': loss_trades,
                'total_pnl': total_pnl,
                'win_rate': win_rate,
                'average_profit': df[df['net_value'] > 0]['net_value'].mean() if profitable_trades > 0 else 0,
                'average_loss': df[df['net_value'] < 0]['net_value'].mean() if loss_trades > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}

# Quick test script
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    manager = SupabaseDataManagerV3()
    
    # Test connection
    print("Testing Supabase connection...")
    portfolio = manager.get_portfolio_summary()
    print(f"✅ Connection successful! Portfolio positions: {len(portfolio.get('positions', []))}")