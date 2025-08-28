# 🛡️ ICICI Direct Testing Safety Checklist

## ⚠️ CRITICAL SAFETY PRECAUTIONS

### Before Testing Order Placement
- [ ] **Minimal funds only** - Keep ₹1000 max in ICICI account for testing
- [ ] **Limit orders only** - Use prices that won't execute immediately  
- [ ] **Market hours only** - Test between 9:15 AM - 3:30 PM IST only
- [ ] **Immediate cancellation** - Cancel test orders within 1 second
- [ ] **Liquid stocks only** - Use RELIANCE, TCS, INFY for testing

### Common ICICI Direct Issues to Check
- [ ] **Session token expiry** - Needs daily refresh via login
- [ ] **API rate limits** - Too many calls can cause temporary blocks
- [ ] **Insufficient funds** - Orders will be rejected if balance low
- [ ] **Wrong exchange codes** - Verify NSE vs BSE vs NFO codes
- [ ] **Invalid symbols** - Option symbols must be exact match

## 🔧 Quick Setup Guide

### 1. Get Your Credentials
1. Login to [ICICI Direct Developer Portal](https://api.icicidirect.com)
2. Generate API Key, Secret, and Session Token
3. Save these securely - you'll need them daily

### 2. Configure Environment
```bash
# Copy template
copy .env.template .env

# Edit .env file with your credentials
notepad .env
```

### 3. Test During Market Hours
```bash
# Run comprehensive test
python comprehensive_icici_test.py

# Check results
type comprehensive_icici_test.log
```

## 📋 Pre-Trading Checklist

### Before Your First Real Trade
- [ ] Connection test passes
- [ ] Market data retrieval works  
- [ ] Portfolio access confirmed
- [ ] Available funds verified
- [ ] Test order placement successful (and cancelled)
- [ ] Session token refresh working
- [ ] Error handling tested
- [ ] Market hours validation implemented

### Emergency Stop Commands
```bash
# Stop any running trading system
Ctrl+C in terminal

# Check for active orders
python -c "from breeze_connect import BreezeConnect; print('Check ICICI Direct app for active orders')"
```

## 💡 Testing Schedule

### Right Now (Market Closed)
- [ ] Verify credentials work
- [ ] Test session generation
- [ ] Confirm data access

### Tomorrow 9:15 AM - 3:30 PM
- [ ] Test live market data
- [ ] Place and cancel test order
- [ ] Verify market hours restriction

## 🚨 Emergency Contacts

If tests fail:
1. Check `comprehensive_icici_test.log` for errors
2. Verify credentials with ICICI support
3. Ensure API permissions are enabled
4. Check network/firewall settings

## 🎯 Final Reminder

**DO NOT** risk real money until you've verified:
- ✅ Connection works reliably
- ✅ Orders can be placed and cancelled  
- ✅ Market data flows correctly
- ✅ Your system respects market hours

**Better safe than sorry** - test thoroughly before going live!