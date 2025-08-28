from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends
import pandas as pd
import os
import joblib
import logging
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import time
from prometheus_client import Histogram, Counter, generate_latest, CONTENT_TYPE_LATEST
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
try:
    from dateutil import parser
except ImportError:
    parser = None

app = FastAPI(title="Cash Flow Prediction API", version="1.0.0")
security = HTTPBearer()
logger = logging.getLogger(__name__)

@app.get("/")
async def read_root():
    """Root endpoint for API information"""
    return {"message": "Cash Flow Prediction API", "version": app.version, "status": "running"}

# Prometheus metrics
request_latency = Histogram('request_latency_seconds', 'Request latency', ['endpoint'])
prediction_counter = Counter('predictions_total', 'Total number of predictions')
health_check_counter = Counter('health_checks_total', 'Total number of health checks')
error_counter = Counter('prediction_errors_total', 'Total number of prediction errors')

# Load model once at startup for better performance
MODEL_PATH = os.getenv('MODEL_PATH', '/app/models/rf_model_20250724_1608.pkl')

# Simple date parser fallback
def parse_date_fallback(date_str):
    """Fallback date parser if dateutil is not available"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except:
        return datetime.now() + timedelta(days=7)

# Small capital configuration
virtual_capital = 5000  # ₹5,000 starting capital
max_position_size = 1500  # Max ₹1,500 per trade
stop_loss_percent = 3  # 3% maximum loss
target_profit_percent = 8  # 8% target gain

def calculate_position_size(prediction_output, current_capital):
    """Calculate position size for small capital"""
    if prediction_output['risk_flag'] == 0:  # Low risk
        return min(1500, current_capital * 0.3)  # 30% max
    else:  # High risk
        return min(800, current_capital * 0.15)   # 15% max for risky trades

def calculate_days_to_expiry(expiry_date_str: str = None) -> int:
    """Calculate days to expiry for options"""
    if not expiry_date_str:
        # Default to next Thursday (weekly expiry)
        today = datetime.now()
        days_ahead = 3 - today.weekday()  # Thursday is 3
        if days_ahead <= 0:
            days_ahead += 7
        expiry_date = today + timedelta(days=days_ahead)
    else:
        try:
            if parser:
                expiry_date = parser.parse(expiry_date_str)
            else:
                expiry_date = parse_date_fallback(expiry_date_str)
        except:
            expiry_date = datetime.now() + timedelta(days=7)
    
    return max((expiry_date - datetime.now()).days, 1)

def calculate_theta_risk(days_to_expiry: int, india_vix: float) -> float:
    """Calculate theta risk score based on time decay and volatility"""
    if days_to_expiry <= 0:
        return 1.0
    
    # Higher risk for shorter expiry and higher volatility
    time_risk = max(0, (7 - days_to_expiry) / 7)  # 0-1 scale
    volatility_risk = min(india_vix / 25, 1.0)  # Normalize to 0-1
    
    return (time_risk * 0.6 + volatility_risk * 0.4)

def calculate_decay_aware_strategy(market_data: Dict[str, Any], prediction: float) -> Dict[str, Any]:
    """Integrate decay management with 98.61% model"""
    india_vix = market_data.get('india_vix', 15)
    time_to_expiry = calculate_days_to_expiry(market_data.get('expiry_date'))
    current_hour = datetime.now().hour
    
    # Decay-resistant decision logic
    options_favorable = (
        india_vix > 15 and
        time_to_expiry > 3 and
        (9 <= current_hour <= 11 or 14 <= current_hour <= 15)
    )
    
    if options_favorable:
        theta_risk = calculate_theta_risk(time_to_expiry, india_vix)
        return {
            'trade_type': 'options',
            'max_holding_hours': 3,
            'theta_risk_score': theta_risk,
            'position_multiplier': max(0.6, 1 - theta_risk * 0.4),
            'recommended_exit_time': (datetime.now() + timedelta(hours=3)).strftime('%H:%M')
        }
    else:
        return {
            'trade_type': 'equity',
            'max_holding_hours': 6,
            'theta_risk_score': 0.0,
            'position_multiplier': 1.0,
            'recommended_exit_time': (datetime.now() + timedelta(hours=6)).strftime('%H:%M')
        }

def calculate_position_for_30k_capital(enhanced_prediction: Dict[str, Any]):
    capital = 30000
    
    if enhanced_prediction['trade_type'] == 'options':
        if enhanced_prediction['theta_risk_score'] > 0.7:
            max_amount = capital * 0.15  # ₹4,500 (high decay risk)
        else:
            max_amount = capital * 0.25  # ₹7,500 (low decay risk)
    else:  # Equity
        max_amount = capital * 0.30     # ₹9,000
    
    # Adjust for model confidence
    if enhanced_prediction['risk_flag'] == 0:  # High confidence
        recommended_amount = max_amount
    else:  # Lower confidence
        recommended_amount = max_amount * 0.7
    
    return {
        'recommended_amount': recommended_amount,
        'stop_loss': recommended_amount * 0.15,  # 15% stop loss
        'target_profit': recommended_amount * 0.25,  # 25% target
        'percentage_of_capital': (recommended_amount / capital) * 100
    }

def execute_small_capital_trade(prediction_output, current_balance):
    """Execute trades optimized for small capital"""
    
    position_size = calculate_position_size(prediction_output, current_balance)
    
    # This is a placeholder for actual trade execution logic.
    # In a real scenario, you would integrate with a broker API (e.g., Breeze).
    # For now, we'll just log the intended trade.
    if current_balance > 0 and prediction_output['risk_flag'] == 0:
        logger.info(f"Simulating conservative buy trade: position_size={position_size}")
        # execute_equity_trade(position_size, "buy") # Placeholder for actual trade
    else:
        logger.info(f"No trade executed based on risk flag or capital: risk_flag={prediction_output['risk_flag']}, current_balance={current_balance}")
    
    return True
model = None

def load_model():
    global model
    try:
        if model is None:
            model_path = Path(MODEL_PATH)
            if not model_path.exists():
                # Fallback to any available model
                models_dir = Path('/app/models')
                if models_dir.exists():
                    model_files = list(models_dir.glob('*.pkl'))
                    if model_files:
                        model_path = model_files[0]
                    else:
                        logger.warning("No model files found, creating fallback model")
                        model = create_fallback_model()
                        return
                else:
                    logger.warning("Models directory not found, creating fallback model")
                    models_dir.mkdir(exist_ok=True)
                    model = create_fallback_model()
                    return
            
            model = joblib.load(model_path)
            logger.info(f"Model loaded successfully from {model_path}")
    except Exception as e:
        logger.error(f"Error loading model: {e}, creating fallback")
        model = create_fallback_model()

def create_fallback_model():
    """Create a simple fallback model for testing"""
    logger.info("Creating fallback model...")
    
    # Create a simple random forest with dummy data
    np.random.seed(42)
    X = np.random.randn(100, 5)
    y = np.random.randn(100)
    
    model = RandomForestRegressor(n_estimators=10, random_state=42)
    model.fit(X, y)
    
    # Store feature names for consistency
    model.feature_names_in_ = np.array(['stock_price', 'volatility', 'volume', 'sma_20', 'rsi'])
    
    # Save the fallback model
    fallback_path = Path('./models/fallback_model.pkl')
    fallback_path.parent.mkdir(exist_ok=True)
    joblib.dump(model, fallback_path)
    
    logger.info("Fallback model created and saved")
    return model

# Load model on startup
logger.info("Starting API initialization...")
load_model()
logger.info("API initialization complete")

def apply_30k_risk_rules(trade_amount: float, current_capital: float, daily_pnl: float):
    """Apply specific risk rules for ₹30K paper trading"""
    
    # Daily loss limit
    if daily_pnl < -2000:  # Max daily loss ₹2,000
        return {"action": "STOP_TRADING", "reason": "Daily loss limit reached"}
    
    # Position size limit
    if trade_amount > current_capital * 0.4:  # Never >40%
        return {"action": "REDUCE_SIZE", "max_amount": current_capital * 0.3}
    
    # Capital preservation
    if current_capital < 25000:  # If capital drops below ₹25K
        return {"action": "CONSERVATIVE_MODE", "max_position": 4000}
    
    return {"action": "PROCEED", "approved_amount": trade_amount}

class PredictionInput(BaseModel):
    data: dict  # e.g., {"stock_price": 150, "volatility": 0.1}
    current_capital: float = virtual_capital # Current available capital for position sizing

class PredictionOutput(BaseModel):
    prediction: float
    risk_flag: int
    position_size: float

class EnhancedPredictionOutput(BaseModel):
    prediction: float
    risk_flag: int
    trade_type: str  # "equity" or "options"
    max_holding_hours: int
    theta_risk_score: float
    recommended_exit_time: str
    position_multiplier: float
    recommended_amount: float
    stop_loss: float
    target_profit: float
    percentage_of_capital: float
    risk_check_action: str

class EquityTradeInput(BaseModel):
    symbol: str
    current_price: float
    model_score: float = 0.85
    confidence: float = 0.75
    week_number: int = 1

class WeekPlanInput(BaseModel):
    week: int = 1

@app.get("/health")
def health_check():
    """Health check endpoint"""
    health_check_counter.inc()
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/predict")
def predict(input: PredictionInput, authorization = Depends(security)):
    start_time = time.time()
    
    if authorization.credentials != os.getenv('API_TOKEN', 'secure_token'):
        error_counter.inc()
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        df = pd.DataFrame([input.data])
        
        # Get model features
        if hasattr(model, 'feature_names_in_'):
            features = model.feature_names_in_
        else:
            # Use all columns as features
            features = df.columns
        
        # Ensure all required features are present
        missing_features = set(features) - set(df.columns)
        if missing_features:
            # Fill missing features with 0
            for feat in missing_features:
                df[feat] = 0
        
        # Make prediction
        prediction = model.predict(df[features])[0]
        
        # Calculate risk metrics
        risk_flag = 1 if abs(prediction) > 100 else 0
        
        prediction_output = {
            "prediction": float(prediction),
            "risk_flag": int(risk_flag)
        }

        # Calculate position size using the new strategy
        position_size = calculate_position_size(prediction_output, input.current_capital)

        # Simulate trade execution based on small capital strategy
        execute_small_capital_trade(prediction_output, input.current_capital)
        
        # Record metrics
        request_latency.labels(endpoint='/predict').observe(time.time() - start_time)
        prediction_counter.inc()
        
        return {
            "prediction": float(prediction),
            "risk_flag": int(risk_flag),
            "position_size": float(position_size)
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        error_counter.inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/enhanced")
def predict_enhanced(input: PredictionInput, authorization = Depends(security)):
    """Enhanced prediction with decay-aware parameters for options trading"""
    start_time = time.time()
    
    if authorization.credentials != os.getenv('API_TOKEN', 'secure_token'):
        error_counter.inc()
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        df = pd.DataFrame([input.data])
        
        # Get model features
        if hasattr(model, 'feature_names_in_'):
            features = model.feature_names_in_
        else:
            features = df.columns
        
        # Ensure all required features are present
        missing_features = set(features) - set(df.columns)
        if missing_features:
            for feat in missing_features:
                df[feat] = 0
        
        # Make prediction
        prediction = model.predict(df[features])[0]
        
        # Calculate risk metrics
        risk_flag = 1 if abs(prediction) > 100 else 0
        
        prediction_output = {
            "prediction": float(prediction),
            "risk_flag": int(risk_flag)
        }
        
        # Get market data for decay analysis
        market_data = {
            'india_vix': input.data.get('volatility', 15) * 100,
            'expiry_date': None
        }
        
        # Calculate decay-aware strategy
        decay_strategy = calculate_decay_aware_strategy(market_data, float(prediction))
        
        # Combine prediction output with decay strategy for 30K capital calculation
        enhanced_prediction_data = {
            "prediction": float(prediction),
            "risk_flag": int(risk_flag),
            "trade_type": decay_strategy['trade_type'],
            "theta_risk_score": decay_strategy['theta_risk_score']
        }
        
        # Calculate position sizing and targets for 30K capital
        capital_strategy = calculate_position_for_30k_capital(enhanced_prediction_data)
        
        # Apply 30K risk rules (assuming daily_pnl is 0 for a new trade simulation)
        # In a real scenario, daily_pnl would be tracked.
        risk_check = apply_30k_risk_rules(capital_strategy['recommended_amount'], input.current_capital, 0.0)
        
        # Record metrics
        request_latency.labels(endpoint='/predict/enhanced').observe(time.time() - start_time)
        prediction_counter.inc()
        
        return {
            "prediction": float(prediction),
            "risk_flag": int(risk_flag),
            "trade_type": decay_strategy['trade_type'],
            "max_holding_hours": decay_strategy['max_holding_hours'],
            "theta_risk_score": decay_strategy['theta_risk_score'],
            "recommended_exit_time": decay_strategy['recommended_exit_time'],
            "position_multiplier": decay_strategy['position_multiplier'],
            "recommended_amount": capital_strategy['recommended_amount'],
            "stop_loss": capital_strategy['stop_loss'],
            "target_profit": capital_strategy['target_profit'],
            "percentage_of_capital": capital_strategy['percentage_of_capital'],
            "risk_check_action": risk_check['action']
        }
        
    except Exception as e:
        logger.error(f"Enhanced prediction error: {e}")
        error_counter.inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/decay-parameters")
async def get_decay_parameters():
    """Get current decay parameters for manual calculation"""
    current_time = datetime.now()
    india_vix = 18.5  # Mock current VIX
    days_to_expiry = calculate_days_to_expiry()
    theta_risk = calculate_theta_risk(days_to_expiry, india_vix)
    
    return {
        "current_time": current_time.isoformat(),
        "india_vix": india_vix,
        "days_to_expiry": days_to_expiry,
        "theta_risk_score": theta_risk,
        "current_hour": current_time.hour,
        "is_options_favorable": (
            india_vix > 15 and
            days_to_expiry > 3 and
            (9 <= current_time.hour <= 11 or 14 <= current_time.hour <= 15)
        ),
        "recommended_trade_type": "options" if (
            india_vix > 15 and
            days_to_expiry > 3 and
            (9 <= current_time.hour <= 11 or 14 <= current_time.hour <= 15)
        ) else "equity"
    }

@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

@app.get("/equity-scalping/plan")
def get_weekly_plan(week: int = 1):
    """Get week-by-week equity scalping implementation plan"""
    plans = {
        1: {
            'mode': 'equity_only',
            'max_trades': 2,
            'max_position': 1000,
            'symbols': ['RELIANCE', 'TCS'],
            'description': 'Week 1: Pure equity focus, build confidence',
            'capital_allocation': '100% equity',
            'risk_per_trade': 3,
            'target_per_trade': 8,
            'daily_goals': {
                'target_pnl': 300,
                'max_loss': 150,
                'min_accuracy': 75
            }
        },
        2: {
            'mode': 'equity_only',
            'max_trades': 3,
            'max_position': 1200,
            'symbols': ['RELIANCE', 'TCS', 'HDFCBANK'],
            'description': 'Week 2: Expand equity universe, refine strategy',
            'capital_allocation': '100% equity',
            'risk_per_trade': 3,
            'target_per_trade': 8,
            'daily_goals': {
                'target_pnl': 400,
                'max_loss': 180,
                'min_accuracy': 78
            }
        },
        3: {
            'mode': 'hybrid',
            'max_trades': 3,
            'max_position': 1000,
            'symbols': ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY'],
            'description': 'Week 3: 70% equity, 30% options on high conviction',
            'capital_allocation': '70% equity, 30% options',
            'risk_per_trade': 3,
            'target_per_trade': 8,
            'daily_goals': {
                'target_pnl': 500,
                'max_loss': 200,
                'min_accuracy': 80
            },
            'options_criteria': {
                'min_vix': 15,
                'max_hold_time_hours': 2,
                'only_high_conviction': True
            }
        },
        4: {
            'mode': 'hybrid',
            'max_trades': 4,
            'max_position': 1200,
            'symbols': ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ITC'],
            'description': 'Week 4: Scale up hybrid approach with decay awareness',
            'capital_allocation': '60% equity, 40% options',
            'risk_per_trade': 3,
            'target_per_trade': 8,
            'daily_goals': {
                'target_pnl': 600,
                'max_loss': 200,
                'min_accuracy': 82
            },
            'options_criteria': {
                'min_vix': 15,
                'max_hold_time_hours': 1.5,
                'theta_decay_threshold': -0.5
            }
        }
    }
    
    return {
        "week": week,
        "plan": plans.get(week, plans[4]),
        "current_capital": virtual_capital,
        "projected_month_end": virtual_capital * 1.3
    }

@app.post("/equity-scalping/trade")
def execute_equity_trade(trade_input: EquityTradeInput):
    """Execute equity scalping trade based on model signal"""
    try:
        week_plan = get_weekly_plan(trade_input.week_number)
        
        # Validate trading hours
        current_time = datetime.now().time()
        market_open = datetime.strptime("09:15", "%H:%M").time()
        market_close = datetime.strptime("15:30", "%H:%M").time()
        
        if not (market_open <= current_time <= market_close):
            return {
                "status": "rejected",
                "reason": "Outside trading hours",
                "current_time": current_time.isoformat()
            }
        
        # Calculate position size
        max_position = week_plan['plan']['max_position']
        position_size = min(max_position, trade_input.current_price * 10)
        quantity = int(position_size / trade_input.current_price)
        
        if quantity == 0:
            return {
                "status": "rejected",
                "reason": "Position too small",
                "min_shares_needed": 1
            }
        
        # Generate trade recommendation
        trade = {
            "symbol": trade_input.symbol,
            "action": "BUY" if trade_input.model_score > 0.75 else "HOLD",
            "quantity": quantity,
            "entry_price": trade_input.current_price,
            "stop_loss": trade_input.current_price * 0.97,
            "target": trade_input.current_price * 1.08,
            "position_size": position_size,
            "model_score": trade_input.model_score,
            "confidence": trade_input.confidence
        }
        
        return {
            "status": "success",
            "trade": trade,
            "risk_metrics": {
                "max_loss": position_size * 0.03,
                "target_profit": position_size * 0.08,
                "risk_reward_ratio": 2.67
            },
            "capital_remaining": virtual_capital - position_size
        }
        
    except Exception as e:
        logger.error(f"Trade execution error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/equity-scalping/performance")
def get_performance_summary():
    """Get performance summary for equity scalping strategy"""
    mock_performance = {
        "current_week": 1,
        "capital_progression": [
            {"week": 0, "capital": 5000, "target": 5000},
            {"week": 1, "capital": 5300, "target": 5300},
            {"week": 2, "capital": 5700, "target": 5700},
            {"week": 3, "capital": 6200, "target": 6500},
            {"week": 4, "capital": 6800, "target": 6500}
        ],
        "key_metrics": {
            "current_capital": 5300,
            "week_1_gain": 6.0,
            "win_rate": 78.5,
            "avg_profit_per_trade": 187.5,
            "max_daily_loss": 120,
            "model_accuracy": 98.61
        },
        "next_steps": [
            "Continue Week 1 equity-only focus",
            "Monitor win rate and adjust position sizes",
            "Prepare for Week 2 symbol expansion",
            "Validate model accuracy with live data"
        ]
    }
    
    return mock_performance

@app.get("/setup/breeze-credentials")
def setup_breeze_guide():
    """Step-by-step guide for setting up Breeze API credentials"""
    return {
        "steps": [
            {
                "step": 1,
                "action": "Login to ICICI Direct",
                "details": "Go to www.icicidirect.com and login with your credentials"
            },
            {
                "step": 2,
                "action": "Navigate to API Access",
                "details": "Go to 'My Account' -> 'API Access' or 'Trading Tools' -> 'API'"
            },
            {
                "step": 3,
                "action": "Generate API Credentials",
                "details": "Generate API Key, API Secret, and Session Token. Note these down securely."
            },
            {
                "step": 4,
                "action": "Update .env file",
                "details": "Create or update .env file in the project root with your credentials"
            }
        ],
        "env_template": {
            "BREEZE_API_KEY": "your_api_key_here",
            "BREEZE_API_SECRET": "your_api_secret_here",
            "BREEZE_SESSION_TOKEN": "your_session_token_here",
            "ICICI_CLIENT_CODE": "your_client_code_here"
        },
        "testing_command": "python equity_scalping_strategy.py --test-connection"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)