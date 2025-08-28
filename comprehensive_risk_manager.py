import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class RiskMetrics:
    daily_pnl: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    avg_win: float
    avg_loss: float
    var_95: float
    var_99: float

@dataclass
class PositionRisk:
    asset: str
    position_size: float
    risk_amount: float
    risk_percentage: float
    stop_loss_distance: float
    correlation_risk: float
    sector_exposure: float

class ComprehensiveRiskManager:
    def __init__(self, total_capital: float = 100000):
        self.total_capital = total_capital
        self.daily_loss_limit = total_capital * 0.05    # 5% daily loss limit
        self.position_risk_limit = total_capital * 0.02  # 2% risk per position
        self.max_correlation_exposure = 0.6            # 60% max correlated positions
        self.max_sector_exposure = 0.4                  # 40% max sector exposure
        self.max_positions = 5                        # Maximum number of positions
        
        self.current_day_pnl = 0.0
        self.max_daily_loss = 0.0
        self.trade_history = []
        self.active_positions = {}
        
        # Initialize Supabase client with error handling
        self.supabase = self._initialize_supabase()
        
        self.logger = logging.getLogger(__name__)
        
    def _initialize_supabase(self):
        """Initialize Supabase client for real-time data storage"""
        try:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")
            
            if not supabase_url or not supabase_key:
                logging.warning("Supabase credentials not found - using offline mode")
                return self._get_mock_client()
                
            from supabase import create_client
            
            # Simple client creation without extra options
            client = create_client(supabase_url, supabase_key)
            
            # Test connection
            try:
                # Simple test query
                test_result = client.table('test').select('*').limit(1).execute()
                logging.info("✅ Supabase client initialized and tested successfully")
                return client
            except Exception as test_error:
                logging.warning(f"Supabase connection test failed: {test_error}")
                logging.info("Falling back to mock client")
                return self._get_mock_client()
                
        except Exception as e:
            logging.error(f"Supabase initialization failed: {e}")
            logging.info("Using mock client for offline operation")
            return self._get_mock_client()
    
    def _get_mock_client(self):
        """Get mock Supabase client"""
        class MockSupabase:
            def table(self, table_name):
                return MockTable(table_name)
                
        class MockTable:
            def __init__(self, name):
                self.name = name
                
            def insert(self, data):
                print(f"Mock DB: Would insert to {self.name}: {data}")
                return MockResponse()
                
            def select(self, *args):
                return MockQuery(self.name)
                
        class MockQuery:
            def __init__(self, table_name):
                self.table_name = table_name
                
            def limit(self, count):
                return self
                
            def execute(self):
                return MockResponse()
                
        class MockResponse:
            def __init__(self):
                self.data = []
                self.error = None
        
        return MockSupabase()
    
    def log_to_supabase(self, data):
        """Log data to Supabase if available, otherwise skip"""
        if self.supabase:
            try:
                return self.supabase.table('risk_logs').insert(data).execute()
            except Exception as e:
                logging.error(f"Failed to log to Supabase: {e}")
        else:
            logging.info(f"Offline mode - would log: {data}")
        
    def validate_trade_risk(self, signal: dict, position_size: float) -> tuple[bool, str]:
        """Comprehensive risk validation for new trades"""
        
        # Check daily loss limit
        if abs(self.current_day_pnl) >= self.daily_loss_limit:
            return False, "Daily loss limit reached"
            
        # Check position concentration
        position_value = position_size * signal['entry_price']
        if position_value > self.total_capital * 0.3:
            return False, "Position too large - exceeds 30% capital limit"
            
        # Check per-position risk limit
        risk_amount = abs(position_value * (signal['entry_price'] - signal['stop_loss']) / signal['entry_price'])
        if risk_amount > self.position_risk_limit:
            return False, f"Risk amount {risk_amount:.2f} exceeds limit {self.position_risk_limit:.2f}"
            
        # Check sector exposure
        sector_exposure = self.calculate_sector_exposure(signal.get('sector', 'Unknown'))
        if sector_exposure > self.max_sector_exposure:
            return False, "Sector exposure limit exceeded"
            
        # Check correlation risk
        correlation_risk = self.calculate_correlation_risk(signal['asset'])
        if correlation_risk > self.max_correlation_exposure:
            return False, "Correlation risk limit exceeded"
            
        # Check volatility-adjusted sizing
        volatility_check = self.validate_volatility_risk(signal)
        if not volatility_check[0]:
            return volatility_check
            
        return True, "Risk validation passed"
        
    def calculate_sector_exposure(self, sector: str) -> float:
        """Calculate current exposure to a specific sector"""
        sector_positions = [
            pos for pos in self.active_positions.values() 
            if pos.get('sector') == sector
        ]
        
        sector_value = sum(pos['current_value'] for pos in sector_positions)
        return sector_value / self.total_capital
        
    def calculate_correlation_risk(self, new_asset: str) -> float:
        """Calculate correlation risk with existing positions"""
        if not self.active_positions:
            return 0.0
            
        # Mock correlation calculation - replace with actual correlation matrix
        correlated_positions = 0
        for asset in self.active_positions.keys():
            if self.is_correlated(new_asset, asset):
                correlated_positions += 1
                
        return correlated_positions / len(self.active_positions)
        
    def is_correlated(self, asset1: str, asset2: str) -> bool:
        """Check if two assets are correlated (mock implementation)"""
        # Replace with actual correlation calculation
        return asset1[:3] == asset2[:3]  # Simple mock correlation
        
    def validate_volatility_risk(self, signal: dict) -> tuple[bool, str]:
        """Validate risk based on asset volatility"""
        # Mock volatility calculation
        volatility = 0.02  # 2% daily volatility
        max_volatility = 0.05  # 5% max acceptable volatility
        
        if volatility > max_volatility:
            return False, "Asset volatility too high"
            
        return True, "Volatility risk acceptable"
        
    def calculate_position_risk_metrics(self, position: dict) -> PositionRisk:
        """Calculate comprehensive risk metrics for a position"""
        position_size = position['quantity'] * position['current_price']
        risk_amount = abs(position_size * (position['current_price'] - position['stop_loss']) / position['current_price'])
        risk_percentage = risk_amount / self.total_capital
        
        return PositionRisk(
            asset=position['asset'],
            position_size=position_size,
            risk_amount=risk_amount,
            risk_percentage=risk_percentage,
            stop_loss_distance=abs(position['current_price'] - position['stop_loss']),
            correlation_risk=self.calculate_correlation_risk(position['asset']),
            sector_exposure=self.calculate_sector_exposure(position.get('sector', 'Unknown'))
        )
        
    def monitor_portfolio_risk(self) -> Dict[str, float]:
        """Monitor overall portfolio risk metrics"""
        total_exposure = sum(
            pos['quantity'] * pos['current_price'] 
            for pos in self.active_positions.values()
        )
        
        # Calculate VaR (Value at Risk)
        var_95 = self.calculate_var(0.05)
        var_99 = self.calculate_var(0.01)
        
        # Calculate Sharpe ratio
        sharpe_ratio = self.calculate_sharpe_ratio()
        
        # Calculate win rate
        win_rate = self.calculate_win_rate()
        
        # Calculate max drawdown
        max_drawdown = self.calculate_max_drawdown()
        
        return {
            'total_exposure': total_exposure,
            'exposure_percentage': total_exposure / self.total_capital,
            'var_95': var_95,
            'var_99': var_99,
            'sharpe_ratio': sharpe_ratio,
            'win_rate': win_rate,
            'max_drawdown': max_drawdown,
            'daily_pnl': self.current_day_pnl,
            'daily_loss_limit': self.daily_loss_limit
        }
        
    def calculate_var(self, confidence_level: float) -> float:
        """Calculate Value at Risk"""
        if not self.trade_history:
            return 0.0
            
        # Mock VaR calculation - replace with actual historical VaR
        returns = [trade.get('return', 0) for trade in self.trade_history[-100:]]
        if not returns:
            return 0.0
            
        var_percentile = np.percentile(returns, confidence_level * 100)
        return abs(var_percentile * self.total_capital)
        
    def calculate_sharpe_ratio(self) -> float:
        """Calculate portfolio Sharpe ratio"""
        if len(self.trade_history) < 2:
            return 0.0
            
        returns = [trade.get('return', 0) for trade in self.trade_history]
        if not returns:
            return 0.0
            
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
            
        return mean_return / std_return
        
    def calculate_win_rate(self) -> float:
        """Calculate trading win rate"""
        if not self.trade_history:
            return 0.0
            
        winning_trades = [trade for trade in self.trade_history if trade.get('pnl', 0) > 0]
        return len(winning_trades) / len(self.trade_history)
        
    def calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        if not self.trade_history:
            return 0.0
            
        # Mock implementation - replace with actual equity curve calculation
        cumulative_returns = [trade.get('cumulative_return', 0) for trade in self.trade_history]
        if not cumulative_returns:
            return 0.0
            
        peak = cumulative_returns[0]
        max_dd = 0.0
        
        for value in cumulative_returns:
            if value > peak:
                peak = value
            else:
                drawdown = (peak - value) / peak
                max_dd = max(max_dd, drawdown)
                
        return max_dd
        
    def adjust_position_sizes(self, market_conditions: dict) -> Dict[str, float]:
        """Dynamically adjust position sizes based on market conditions"""
        adjustments = {}
        
        # Reduce sizes in high volatility
        volatility_factor = min(1.0, 0.5 / market_conditions.get('vix', 20))
        
        # Reduce sizes in high correlation
        correlation_factor = min(1.0, 1.0 / (1 + market_conditions.get('correlation_index', 0)))
        
        # Combine factors
        adjustment_factor = volatility_factor * correlation_factor
        
        for asset, position in self.active_positions.items():
            adjusted_size = position['quantity'] * adjustment_factor
            adjustments[asset] = adjusted_size
            
        return adjustments
        
    def generate_risk_report(self) -> Dict:
        """Generate comprehensive risk report"""
        portfolio_metrics = self.monitor_portfolio_risk()
        
        # Get individual position risks
        position_risks = []
        for asset, position in self.active_positions.items():
            risk_metrics = self.calculate_position_risk_metrics(position)
            position_risks.append({
                'asset': asset,
                'position_size': risk_metrics.position_size,
                'risk_amount': risk_metrics.risk_amount,
                'risk_percentage': risk_metrics.risk_percentage,
                'stop_loss_distance': risk_metrics.stop_loss_distance
            })
            
        # Store in Supabase
        self.store_risk_report(portfolio_metrics, position_risks)
        
        return {
            'timestamp': datetime.datetime.now().isoformat(),
            'portfolio_metrics': portfolio_metrics,
            'position_risks': position_risks,
            'risk_alerts': self.generate_risk_alerts(portfolio_metrics)
        }
        
    def store_risk_report(self, portfolio_metrics: Dict, position_risks: List[Dict]):
        """Store risk report in Supabase"""
        try:
            # Store portfolio-level metrics
            self.supabase.table('portfolio_risk').insert({
                'timestamp': datetime.datetime.now().isoformat(),
                'total_exposure': portfolio_metrics['total_exposure'],
                'var_95': portfolio_metrics['var_95'],
                'var_99': portfolio_metrics['var_99'],
                'sharpe_ratio': portfolio_metrics['sharpe_ratio'],
                'win_rate': portfolio_metrics['win_rate'],
                'max_drawdown': portfolio_metrics['max_drawdown'],
                'daily_pnl': portfolio_metrics['daily_pnl']
            }).execute()
            
            # Store position-level risks
            for risk in position_risks:
                self.supabase.table('position_risk').insert({
                    'timestamp': datetime.datetime.now().isoformat(),
                    'asset': risk['asset'],
                    'position_size': risk['position_size'],
                    'risk_amount': risk['risk_amount'],
                    'risk_percentage': risk['risk_percentage'],
                    'stop_loss_distance': risk['stop_loss_distance']
                }).execute()
                
        except Exception as e:
            self.logger.error(f"Failed to store risk report: {e}")
            
    def generate_risk_alerts(self, portfolio_metrics: Dict) -> List[str]:
        """Generate risk alerts based on current metrics"""
        alerts = []
        
        if portfolio_metrics['daily_pnl'] <= -self.daily_loss_limit * 0.8:
            alerts.append("WARNING: Approaching daily loss limit")
            
        if portfolio_metrics['exposure_percentage'] > 0.8:
            alerts.append("WARNING: High portfolio exposure")
            
        if portfolio_metrics['var_95'] > self.total_capital * 0.05:
            alerts.append("WARNING: High VaR risk")
            
        if portfolio_metrics['max_drawdown'] > 0.15:
            alerts.append("WARNING: Significant drawdown detected")
            
        return alerts
        
    def emergency_stop_check(self) -> bool:
        """Check if emergency stop should be triggered"""
        if abs(self.current_day_pnl) >= self.daily_loss_limit:
            self.logger.critical("EMERGENCY STOP: Daily loss limit exceeded")
            return True
            
        if self.calculate_max_drawdown() > 0.2:  # 20% max drawdown
            self.logger.critical("EMERGENCY STOP: Max drawdown exceeded")
            return True
            
        return False
        
    def get_risk_dashboard_data(self) -> Dict:
        """Get data for risk dashboard"""
        risk_report = self.generate_risk_report()
        
        # Calculate total exposure from active positions
        total_exposure = sum(
            pos['quantity'] * pos['current_price'] 
            for pos in self.active_positions.values()
        )
        
        return {
            'current_metrics': {
                'daily_pnl': self.current_day_pnl,
                'daily_loss_limit': self.daily_loss_limit,
                'available_capital': self.total_capital - total_exposure,
                'total_exposure': total_exposure,  # Added missing key
                'active_positions': len(self.active_positions),
                'position_risk_limit': self.position_risk_limit,
                'max_positions': self.max_positions,
                'risk_utilization': abs(self.current_day_pnl) / self.daily_loss_limit if self.daily_loss_limit > 0 else 0
            },
            'risk_alerts': risk_report['risk_alerts'],
            'portfolio_metrics': risk_report['portfolio_metrics'],
            'position_risks': risk_report['position_risks']
        }

# Example usage
if __name__ == "__main__":
    risk_manager = ComprehensiveRiskManager(total_capital=100000)
    
    # Test risk validation
    test_signal = {
        'asset': 'RELIANCE',
        'entry_price': 2500.0,
        'stop_loss': 2450.0,
        'sector': 'Energy'
    }
    
    test_position = {
        'quantity': 100,
        'current_price': 2520.0,
        'stop_loss': 2450.0,
        'sector': 'Energy'
    }
    
    # Validate trade risk
    is_valid, message = risk_manager.validate_trade_risk(test_signal, 100)
    print(f"Risk validation: {is_valid} - {message}")
    
    # Calculate position risk
    risk_metrics = risk_manager.calculate_position_risk_metrics(test_position)
    print(f"Position risk: {risk_metrics}")
    
    # Generate risk report
    risk_report = risk_manager.generate_risk_report()
    print(f"Risk report: {risk_report}")
    
    print("🛡️ Comprehensive Risk Manager initialized!")