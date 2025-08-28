# 🧪 ICICI Direct Breeze API Testing Guide

## ⚡ Quick Start - Run Tests Now

### 1. Run All Tests (Safe)
```bash
python test_icici_connection.py
```

### 2. Run Individual Test Phases
```bash
# Phase 1: Connection only
python -c "from test_icici_connection import ICICITestSuite; t=ICICITestSuite(); t.test_phase_1_connection()"

# Phase 2: Market data only
python -c "from test_icici_connection import ICICITestSuite; t=ICICITestSuite(); t.test_phase_2_market_data()"

# Phase 3: Order testing only
python -c "from test_icici_connection import ICICITestSuite; t=ICICITestSuite(); t.test_phase_3_order_testing()"
```

## 🔐 Environment Setup

### Required Environment Variables
Create a `.env` file in your project root:

```bash
# ICICI Direct Credentials
BREEZE_API_KEY=your_api_key_here
BREEZE_API_SECRET=your_api_secret_here
BREEZE_SESSION_TOKEN=your_session_token_here

# Optional: Paper trading mode
PAPER_TRADING=true
```

### Get Your Credentials
1. **API Key**: From ICICI Direct Developer Portal
2. **API Secret**: Generated during app creation
3. **Session Token**: Generated via login flow

## 📋 Test Phases Explained

### Phase 1: Connection & Authentication ✅
**Purpose**: Verify API connectivity and session management
**Tests**:
- Session generation
- Customer details retrieval
- Portfolio holdings access
- Fund balance check

**Expected Output**:
```
✅ Session Generation: {'status': 'success', ...}
✅ Customer Details: {'client_code': 'ABC123', ...}
✅ Portfolio Access: 5 holdings found
✅ Available Funds: {'available_margin': 50000, ...}
```

### Phase 2: Market Data Access ✅
**Purpose**: Ensure live market data feeds work
**Tests**:
- NIFTY index quotes
- Individual stock quotes
- Options chain data
- Futures data

**Expected Output**:
```
✅ NIFTY Data: {'ltp': 25000.5, 'volume': 1000000, ...}
✅ RELIANCE Data: {'ltp': 2500.5, 'volume': 500000, ...}
✅ Option Chain Access: 200 options found
```

### Phase 3: Order Testing ✅
**Purpose**: Test order placement/cancellation safely
**Tests**:
- Place limit order (1 share, low price)
- Immediate cancellation
- Order status verification

**Expected Output**:
```
✅ Order Placement Test: {'order_id': 'ORD123', 'status': 'placed'}
✅ Order Cancellation: {'order_id': 'ORD123', 'status': 'cancelled'}
```

## 🛡️ Safety Features

### Built-in Protections
- **Minimum quantity**: 1 share only
- **Limit orders**: Set far from market price
- **Immediate cancellation**: Orders cancelled within 1 second
- **Paper mode**: Uses mock data when credentials not provided

### Manual Safety Checks
Before running live:
1. ✅ Verify `.env` file has correct credentials
2. ✅ Check account balance (should show actual funds)
3. ✅ Confirm paper trading mode is OFF for live
4. ✅ Test with 1 share orders first
5. ✅ Monitor order book in ICICI Direct app

## 🚨 Troubleshooting

### Common Issues

#### 1. "breeze_connect not found"
```bash
pip install breeze-connect
```

#### 2. "Session expired"
- Generate new session token via ICICI login
- Update BREEZE_SESSION_TOKEN in .env

#### 3. "Insufficient funds"
- Switch to paper trading mode: `PAPER_TRADING=true`
- Or deposit funds in ICICI account

#### 4. "Market data unavailable"
- Check if market hours (9:15 AM - 3:30 PM IST)
- Verify exchange code is "NSE" or "BSE"

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Test Results Analysis

### Successful Test Output
```
🚀 Starting ICICI Direct Breeze API Test Suite
✅ ALL TESTS PASSED
🎉 Ready for live trading!
```

### Failed Test Output
```
❌ SOME TESTS FAILED
⚠️ Fix issues before going live
```

Check `icici_test_log.txt` for detailed error logs.

## 🔄 Live Trading Checklist

Before switching from test to live:

- [ ] All 3 test phases pass
- [ ] Environment variables verified
- [ ] Paper trading mode disabled
- [ ] Real account balance confirmed
- [ ] Small position sizes configured
- [ ] Stop-loss levels set
- [ ] Emergency contact info updated

## 📞 Support

If tests fail:
1. Check `icici_test_log.txt` for detailed errors
2. Verify credentials with ICICI support
3. Ensure API permissions are enabled
4. Check network/firewall settings

## 🎯 Next Steps After Testing

1. **If tests pass**: Update `minimal_trading_system.py` to use real credentials
2. **Start small**: Begin with 1-2 shares per trade
3. **Monitor closely**: Watch first few trades manually
4. **Scale gradually**: Increase position sizes after confidence

## 🔍 Additional Test Scripts

### Test Specific Symbols
```python
# Test specific stock
test_symbol = "HDFC"
data = breeze.get_quotes(stock_code=test_symbol, exchange_code="NSE", product_type="cash")
```

### Test Options
```python
# Test options chain
expiry = "2024-12-26"
chain = breeze.get_option_chain_quotes(
    stock_code="BANKNIFTY",
    exchange_code="NSE",
    product_type="options",
    expiry_date=expiry
)
```

---

**Remember**: Never risk more than you can afford to lose. Start small and scale gradually! 🚀