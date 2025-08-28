# 🚀 Equity Scalping Strategy - ₹5,000 Capital Implementation

## 📋 Quick Start Checklist

### ✅ Immediate Actions (This Week)

1. **Set up Breeze API credentials** (15 minutes)
   - Go to `/setup/breeze-credentials` endpoint for step-by-step guide
   - Or run: `python equity_scalping_strategy.py` to get interactive setup

2. **Test the system** (5 minutes)
   - Start the API: `uvicorn api:app --host 0.0.0.0 --port 8002 --reload`
   - Test endpoints:
     - `GET http://localhost:8002/equity-scalping/plan?week=1`
     - `POST http://localhost:8002/equity-scalping/trade` with sample data

3. **Paper trading setup** (10 minutes)
   - Review `equity_scalping_config.json` for settings
   - Check `equity_trades_log.csv` will be created automatically

## 🎯 Week-by-Week Implementation Plan

### Week 1: Pure Equity Focus (Build Confidence)
**Goal**: ₹5,000 → ₹5,300 (6% gain)

- **Mode**: 100% equity scalping
- **Symbols**: RELIANCE, TCS (top 2 liquid stocks)
- **Max trades**: 2 per day
- **Max position**: ₹1,000 per trade
- **Risk**: 3% stop loss, 8% target

**Daily Targets**:
- Target P&L: ₹300
- Max loss: ₹150
- Min accuracy: 75%

### Week 2: Expand Universe (Refine Strategy)
**Goal**: ₹5,300 → ₹5,700 (8% gain)

- **Mode**: 100% equity scalping
- **Symbols**: RELIANCE, TCS, HDFCBANK (add 1 more)
- **Max trades**: 3 per day
- **Max position**: ₹1,200 per trade
- **Enhanced monitoring**: Track win rate and model accuracy

### Week 3: Hybrid Introduction (Gradual Options)
**Goal**: ₹5,700 → ₹6,500 (14% gain)

- **Mode**: 70% equity, 30% options
- **Symbols**: All Week 2 + INFY
- **Options criteria**: 
  - India VIX > 15
  - Max hold time: 2 hours
  - Only high-conviction signals

### Week 4: Full Hybrid (Decay Awareness)
**Goal**: ₹6,500 → ₹9,000+ (38% gain)

- **Mode**: 60% equity, 40% options
- **Advanced features**: Theta decay tracking
- **Risk management**: Enhanced position sizing

## 🔧 API Endpoints

### Core Endpoints

#### Get Weekly Plan
```bash
curl "http://localhost:8002/equity-scalping/plan?week=1"
```

#### Execute Trade
```bash
curl -X POST "http://localhost:8002/equity-scalping/trade" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "RELIANCE",
    "current_price": 2800.50,
    "model_score": 0.95,
    "confidence": 0.85,
    "week_number": 1
  }'
```

#### Check Performance
```bash
curl "http://localhost:8002/equity-scalping/performance"
```

#### Setup Guide
```bash
curl "http://localhost:8002/setup/breeze-credentials"
```

## 📊 Performance Tracking

### Key Metrics Dashboard

| Metric | Week 1 | Week 2 | Week 3 | Week 4 |
|--------|--------|--------|--------|--------|
| **Target P&L** | ₹300/day | ₹400/day | ₹500/day | ₹600/day |
| **Win Rate** | >75% | >78% | >80% | >82% |
| **Max Daily Loss** | ₹150 | ₹180 | ₹200 | ₹200 |
| **Model Accuracy** | 98.61% | 98.61% | 98.61% | 98.61% |

### Daily Tracking

```python
# Example daily tracking structure
daily_summary = {
    "date": "2024-01-15",
    "starting_capital": 5000,
    "trades_executed": 2,
    "winning_trades": 2,
    "losing_trades": 0,
    "net_pnl": 320,
    "model_accuracy": 98.61,
    "decay_costs": 0,  # Week 1-2 only
    "capital_end": 5320
}
```

## 🔐 Breeze API Setup

### 1. Get Credentials from ICICI Direct
1. Login to [ICICI Direct](https://www.icicidirect.com)
2. Navigate to **My Account → API Access**
3. Generate:
   - API Key
   - API Secret  
   - Session Token
   - Client Code

### 2. Update Environment File
Create `.env` file in project root:
```bash
BREEZE_API_KEY=your_api_key_here
BREEZE_API_SECRET=your_api_secret_here
BREEZE_SESSION_TOKEN=your_session_token_here
ICICI_CLIENT_CODE=your_client_code_here
MODE=paper  # Change to 'live' when ready
```

### 3. Test Connection
```bash
python equity_scalping_strategy.py --test-connection
```

## 🎯 Trading Rules & Discipline

### Entry Criteria
- ✅ Model score > 75%
- ✅ Within trading hours (9:30 AM - 3:00 PM)
- ✅ Not during lunch break (12:00-1:30 PM)
- ✅ Below daily trade limit
- ✅ Below daily loss limit

### Exit Rules
- ✅ Stop loss: 3% from entry
- ✅ Target profit: 8% from entry
- ✅ Time-based: Close before 3:00 PM
- ✅ Max hold time: 2 hours for options

### Position Sizing
```python
# Automatic calculation based on:
position_size = min(max_position, capital * risk_factor)
quantity = int(position_size / current_price)
```

## 📈 Expected Results

### Conservative Projections
- **Week 1**: ₹5,000 → ₹5,300 (6% gain)
- **Week 2**: ₹5,300 → ₹5,700 (8% gain)  
- **Week 3**: ₹5,700 → ₹6,500 (14% gain)
- **Week 4**: ₹6,500 → ₹9,000+ (38% gain)

### Success Metrics
- **Win Rate**: 75-82% (matching model accuracy)
- **Average Profit/Trade**: ₹150-300
- **Maximum Daily Loss**: ₹200 (4% of capital)
- **Monthly Consistency**: 15-25% returns

## 🚨 Risk Management

### Daily Limits
- **Max Loss**: ₹200 (4% of capital)
- **Max Exposure**: ₹3,000 (60% of capital)
- **Max Trades**: Week-dependent (2-4 per day)

### Emergency Protocols
- **Circuit Breaker**: Stop trading after 2 consecutive losses
- **Review Trigger**: Win rate drops below 70%
- **Capital Protection**: Never risk more than 3% per trade

## 🔄 Next Steps

### This Week (Immediate)
1. **Set up Breeze credentials** using the API guide
2. **Start paper trading** with Week 1 configuration
3. **Monitor results** daily using the performance endpoint
4. **Adjust settings** based on initial results

### Next Week
1. **Review Week 1 performance**
2. **Expand to Week 2 symbols** if successful
3. **Increase position sizes** gradually
4. **Prepare for hybrid mode** in Week 3

### Month 2+ (If Successful)
1. **Implement full hybrid strategy**
2. **Scale up capital** with profits
3. **Add more sophisticated options strategies**
4. **Consider algorithmic execution**

## 🛠️ Troubleshooting

### Common Issues

**API Connection Failed**
```bash
# Check credentials
cat .env | grep BREEZE

# Test connection
python -c "from breeze_connector import BreezeConnector; print('OK')"
```

**Trade Rejected**
- Check trading hours: 9:15 AM - 3:30 PM IST
- Verify sufficient capital
- Confirm symbol is in approved list

**Performance Below Target**
- Review model accuracy scores
- Check position sizing calculations
- Validate stop loss and target levels

## 📞 Support

For issues or questions:
1. Check logs in `equity_trades_log.csv`
2. Review API responses at `/equity-scalping/performance`
3. Test endpoints individually before live trading
4. Start with paper trading mode always

---

**Ready to start? Begin with Week 1 pure equity focus and build your confidence!** 🚀