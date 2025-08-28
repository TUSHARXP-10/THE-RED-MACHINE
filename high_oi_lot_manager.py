import json
import numpy as np
from datetime import datetime
import logging

class HighOILotManager:
    """
    Advanced lot management system for 3000 capital with high OI detection
    """
    
    def __init__(self, config_file='kite_config.json'):
        self.config = self.load_config(config_file)
        self.capital = self.config['trading_parameters']['initial_capital']
        self.logger = self.setup_logger()
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.get_default_config()
    
    def get_default_config(self):
        """Default configuration for 3000 capital"""
        return {
            "trading_parameters": {
                "initial_capital": 3000,
                "max_position_size": 0.15,
                "risk_per_trade": 0.02,
                "oi_management": {
                    "min_oi_threshold": 100000,
                    "max_oi_threshold": 5000000,
                    "oi_percentile": 90,
                    "auto_lot_calculation": True,
                    "max_lots_per_trade": 2
                }
            }
        }
    
    def setup_logger(self):
        """Setup logging for OI management"""
        logger = logging.getLogger('HighOIManager')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def calculate_lots_by_oi(self, oi_data, current_price):
        """
        Calculate optimal lots based on OI levels and 3000 capital
        
        Args:
            oi_data: Dictionary with strike OI information
            current_price: Current market price
        
        Returns:
            dict: Lot sizing recommendations
        """
        try:
            # Extract OI values
            strikes = list(oi_data.keys())
            oi_values = [oi_data[strike]['total_oi'] for strike in strikes]
            
            # Calculate OI statistics
            high_oi_threshold = np.percentile(oi_values, 90)
            medium_oi_threshold = np.percentile(oi_values, 75)
            
            # Filter high OI strikes
            high_oi_strikes = {
                strike: data for strike, data in oi_data.items()
                if data['total_oi'] >= high_oi_threshold
            }
            
            medium_oi_strikes = {
                strike: data for strike, data in oi_data.items()
                if medium_oi_threshold <= data['total_oi'] < high_oi_threshold
            }
            
            # Calculate position sizing
            max_risk_amount = self.capital * 0.02  # 2% risk per trade = 60
            
            lot_recommendations = {
                'high_oi_strikes': {},
                'medium_oi_strikes': {},
                'risk_management': {
                    'max_risk_per_trade': max_risk_amount,
                    'max_lots_per_trade': 2,
                    'capital_utilization': 0.15  # 15% max per trade
                }
            }
            
            # High OI strikes - prefer these
            for strike, data in high_oi_strikes.items():
                distance_from_price = abs(strike - current_price)
                
                # Calculate lots based on OI strength and distance
                oi_strength = data['total_oi'] / high_oi_threshold
                distance_factor = max(0.1, 1 - (distance_from_price / current_price))
                
                # Conservative lot calculation for 3000 capital
                max_lots = min(2, int(max_risk_amount / 50))  # Assuming 50 per lot
                recommended_lots = max(1, int(max_lots * oi_strength * distance_factor))
                
                lot_recommendations['high_oi_strikes'][strike] = {
                    'oi': data['total_oi'],
                    'lots': recommended_lots,
                    'position_size': recommended_lots * 50,
                    'risk_amount': recommended_lots * 50,
                    'distance_from_price': distance_from_price,
                    'confidence': min(95, 80 + (oi_strength * 10))
                }
            
            # Medium OI strikes - secondary options
            for strike, data in medium_oi_strikes.items():
                distance_from_price = abs(strike - current_price)
                
                oi_strength = data['total_oi'] / medium_oi_threshold
                distance_factor = max(0.1, 1 - (distance_from_price / current_price))
                
                max_lots = min(1, int(max_risk_amount / 75))  # More conservative for medium OI
                recommended_lots = max(1, int(max_lots * oi_strength * distance_factor * 0.7))
                
                lot_recommendations['medium_oi_strikes'][strike] = {
                    'oi': data['total_oi'],
                    'lots': recommended_lots,
                    'position_size': recommended_lots * 75,
                    'risk_amount': recommended_lots * 75,
                    'distance_from_price': distance_from_price,
                    'confidence': min(85, 70 + (oi_strength * 8))
                }
            
            self.logger.info(f"Lot recommendations calculated for {len(high_oi_strikes)} high OI strikes and {len(medium_oi_strikes)} medium OI strikes")
            
            return lot_recommendations
            
        except Exception as e:
            self.logger.error(f"Error calculating lots by OI: {e}")
            return {'error': str(e)}
    
    def get_optimal_strikes(self, current_price, expiry_date):
        """
        Get optimal strike selection for 3000 capital with 50-100 OTM range
        
        Args:
            current_price: Current market price
            expiry_date: Options expiry date
        
        Returns:
            dict: Strike selection recommendations with 50-100 OTM focus
        """
        try:
            # Calculate strike ranges based on current price
            atm_strike = int(round(current_price / 50) * 50)
            
            # Focus on 50-100 OTM range for optimal 3000 capital utilization
            strikes = {
                'atm_call': atm_strike,
                'atm_put': atm_strike,
                'otm_50_call': atm_strike + 50,
                'otm_100_call': atm_strike + 100,
                'otm_50_put': atm_strike - 50,
                'otm_100_put': atm_strike - 100,
                'otm_75_call': atm_strike + 75,  # Mid-range OTM
                'otm_75_put': atm_strike - 75
            }
            
            # Risk allocation optimized for 50-100 OTM range
            risk_allocation = {
                'atm': 0.4,      # 40% for ATM (conservative)
                'otm_50': 0.35,  # 35% for 50 OTM (primary target)
                'otm_75': 0.20,  # 20% for 75 OTM (mid-range)
                'otm_100': 0.15  # 15% for 100 OTM (aggressive)
            }
            
            max_risk = self.capital * 0.02  # 60 max risk
            
            recommendations = {
                'current_price': current_price,
                'atm_strike': atm_strike,
                'strike_selection': {},
                'risk_budget': max_risk,
                'capital_utilization': {}
            }
            
            for strike_name, strike_price in strikes.items():
                distance = abs(strike_price - current_price)
                
                # Determine risk allocation based on OTM distance
                if 'atm' in strike_name:
                    risk_pct = risk_allocation['atm']
                    strike_type = 'ATM'
                elif 'otm_50' in strike_name:
                    risk_pct = risk_allocation['otm_50']
                    strike_type = '50 OTM'
                elif 'otm_75' in strike_name:
                    risk_pct = risk_allocation['otm_75']
                    strike_type = '75 OTM'
                elif 'otm_100' in strike_name:
                    risk_pct = risk_allocation['otm_100']
                    strike_type = '100 OTM'
                
                risk_amount = max_risk * risk_pct
                
                # Calculate lots based on distance - 50-100 range optimized
                if distance <= 50:  # ATM and 50 OTM
                    lot_price = 40    # Lower price for closer strikes
                    max_lots = min(2, int(risk_amount / lot_price))
                elif distance <= 75:  # 75 OTM
                    lot_price = 35    # Mid-range pricing
                    max_lots = min(2, int(risk_amount / lot_price))
                else:  # 100 OTM
                    lot_price = 30    # Lower price for far OTM
                    max_lots = min(2, int(risk_amount / lot_price))
                
                recommendations['strike_selection'][strike_name] = {
                    'strike_price': strike_price,
                    'distance_from_price': distance,
                    'strike_type': strike_type,
                    'lot_price': lot_price,
                    'max_lots': max_lots,
                    'max_position_size': max_lots * lot_price,
                    'risk_amount': risk_amount,
                    'priority': 'high' if distance <= 50 else 'medium' if distance <= 75 else 'low',
                    'oi_target_range': '50-100 OTM' if distance >= 50 else 'ATM'
                }
                
                # Track capital utilization
                recommendations['capital_utilization'][strike_name] = max_lots * 50
            
            total_utilization = sum(recommendations['capital_utilization'].values())
            recommendations['total_capital_utilization'] = total_utilization
            recommendations['remaining_capital'] = self.capital - total_utilization
            
            self.logger.info(f"Strike recommendations generated for {current_price} with {total_utilization} capital utilization")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting optimal strikes: {e}")
            return {'error': str(e)}
    
    def validate_position_size(self, position_size):
        """
        Validate position size against 3000 capital limits
        
        Args:
            position_size: Proposed position size
        
        Returns:
            dict: Validation result
        """
        max_allowed = self.capital * 0.15  # 15% max per position = 450
        
        validation = {
            'position_size': position_size,
            'max_allowed': max_allowed,
            'is_valid': position_size <= max_allowed,
            'utilization_percent': (position_size / self.capital) * 100,
            'remaining_capital': self.capital - position_size
        }
        
        if not validation['is_valid']:
            validation['suggested_size'] = max_allowed
            validation['warning'] = f"Position size exceeds 15% limit. Suggested: {max_allowed}"
        
        return validation
    
    def get_daily_summary(self):
        """Get daily trading summary for 3000 capital"""
        return {
            'capital': self.capital,
            'max_risk_per_trade': self.capital * 0.02,  # 60
            'max_position_size': self.capital * 0.15,   # 450
            'daily_trades_limit': 5,
            'capital_utilization_target': 0.8,  # Use 80% max
            'risk_management': {
                'stop_loss_pct': 0.01,
                'profit_target_pct': 0.02,
                'max_drawdown': 0.05  # 5% max daily loss
            }
        }

# Example usage and testing
if __name__ == "__main__":
    manager = HighOILotManager()
    
    # Sample OI data
    sample_oi = {
        50000: {'total_oi': 150000, 'call_oi': 80000, 'put_oi': 70000},
        50100: {'total_oi': 200000, 'call_oi': 120000, 'put_oi': 80000},
        50200: {'total_oi': 300000, 'call_oi': 180000, 'put_oi': 120000},
        50300: {'total_oi': 250000, 'call_oi': 140000, 'put_oi': 110000},
        50400: {'total_oi': 180000, 'call_oi': 100000, 'put_oi': 80000}
    }
    
    # Test lot calculation
    recommendations = manager.calculate_lots_by_oi(sample_oi, 50250)
    print("\n=== High OI Lot Recommendations ===")
    print(json.dumps(recommendations, indent=2))
    
    # Test strike selection
    strikes = manager.get_optimal_strikes(50250, "2024-07-25")
    print("\n=== Strike Selection ===")
    print(json.dumps(strikes, indent=2))
    
    # Test validation
    validation = manager.validate_position_size(400)
    print("\n=== Position Validation ===")
    print(json.dumps(validation, indent=2))
    
    # Daily summary
    summary = manager.get_daily_summary()
    print("\n=== Daily Summary ===")
    print(json.dumps(summary, indent=2))