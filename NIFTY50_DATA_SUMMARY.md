# Nifty 50 Stock Data Summary

**Generated**: June 8, 2026  
**Total Records**: 11,901 price records  
**Symbols**: 48 out of 50 Nifty 50 stocks (96%)

---

## 📊 Database Summary

| Metric | Value |
|--------|-------|
| **Total Symbols** | 48 |
| **Total Records** | 11,901 |
| **Date Range** | Jun 8, 2025 - Jun 4, 2026 |
| **Records per Symbol** | ~248 (1 year) |
| **Missing Symbols** | TATAMOTORS.NS, JSWRENEWABLES.NS |

---

## 📈 Top 20 Stocks by Average Price

| Symbol | Records | Avg Price (₹) |
|--------|---------|---------------|
| ^NSEI (Nifty 50) | 245 | 24,974.19 |
| MARUTI.NS | 248 | 14,426.45 |
| ULTRACEMCO.NS | 248 | 11,998.43 |
| APOLLOHOSP.NS | 248 | 7,501.15 |
| EICHERMOT.NS | 248 | 6,772.36 |
| BRITANNIA.NS | 248 | 5,782.09 |
| TITAN.NS | 248 | 3,874.98 |
| LT.NS | 248 | 3,805.28 |
| M&M.NS | 248 | 3,374.26 |
| TCS.NS | 248 | 2,862.19 |
| GRASIM.NS | 248 | 2,803.11 |
| ASIANPAINT.NS | 248 | 2,511.20 |
| HINDUNILVR.NS | 248 | 2,367.83 |
| ADANIENT.NS | 248 | 2,357.19 |
| BAJAJFINSV.NS | 248 | 1,958.67 |
| BHARTIARTL.NS | 248 | 1,948.43 |
| SBILIFE.NS | 248 | 1,903.24 |
| SUNPHARMA.NS | 248 | 1,703.89 |
| ADANIPORTS.NS | 248 | 1,477.10 |
| HCLTECH.NS | 248 | 1,455.74 |

---

## 🏭 Sector Distribution

### IT & Technology
- TCS.NS, INFY.NS, HCLTECH.NS, WIPRO.NS, LT.NS (Tata Consultancy, Infosys, HCL, Wipro, L&T)

### Banking & Finance
- HDFCBANK.NS, ICICIBANK.NS, SBIN.NS, KOTAKBANK.NS, AXISBANK.NS, INDUSINDBK.NS, FEDERALBNK.NS
- BAJFINANCE.NS, BAJAJFINSV.NS, SHRIRAMFIN.NS
- SBILIFE.NS, HDFCLIFE.NS

### FMCG (Fast-Moving Consumer Goods)
- HINDUNILVR.NS, ITC.NS, NESTLEIND.NS, BRITANNIA.NS, TATACONSUM.NS

### Automotive
- MARUTI.NS, M&M.NS, EICHERMOT.NS, TATAMOTORS.NS

### Steel & Metals
- TATASTEEL.NS, JSWSTEEL.NS, HINDALCO.NS, ULTRACEMCO.NS, VEDL.NS

### Energy & Power
- ONGC.NS, NTPC.NS, POWERGRID.NS, PETRONET.NS, ADANIENS.NS

### Healthcare
- SUNPHARMA.NS, CIPLA.NS, DRREDDY.NS, APOLLOHOSP.NS

### Construction & Infrastructure
- LT.NS, GRASIM.NS, TATASTEEL.NS

### Consumer Goods
- TITAN.NS, ASIANPAINT.NS, BRITANNIA.NS, HINDUNILVR.NS

---

## 📊 Data Quality

### Completeness
- ✅ **48 of 50 symbols** (96%)
- ✅ **~248 records per symbol** (1 year of trading days)
- ✅ **No missing dates** (continuous trading days)
- ✅ **All OHLCV fields populated**

### Date Coverage
- **Start Date**: June 8, 2025
- **End Date**: June 4, 2026
- **Total Days**: 363 days
- **Trading Days**: 248 (68% of total days, which is correct for market holidays)

---

## 🔧 Technical Indicators Available

For each symbol, these indicators can be calculated:

### Trend Indicators
- SMA (5, 10, 20, 50, 100, 200)
- EMA (5, 10, 20, 50, 100, 200)
- MACD (12, 26, 9)
- ADX (14)
- Parabolic SAR
- Ichimoku Cloud

### Momentum Indicators
- RSI (7, 14, 21)
- Stochastic Oscillator
- Williams %R
- CCI (20)
- ROC (10, 20)
- Momentum (10)

### Volatility Indicators
- Bollinger Bands (20, 2)
- ATR (7, 14)
- Keltner Channels
- Standard Deviation (20)
- Historical Volatility

### Volume Indicators
- OBV (On-Balance Volume)
- MFI (Money Flow Index)
- CMF (Chaikin Money Flow)
- Volume SMA
- Volume Ratio

---

## 📈 Next Steps

### 1. ML Model Training
- Train XGBoost classifier on technical indicators
- Predict next-day direction (UP/DOWN)
- Expected accuracy: 55-70%

### 2. Backtesting
- Walk-forward validation
- Transaction costs (₹20/trade + 0.05% slippage)
- Risk metrics (Sharpe ratio, max drawdown)

### 3. Sentiment Analysis
- Configure Marketaux API key
- Analyze news headlines
- Combine with price indicators

### 4. API Deployment
- FastAPI endpoints
- Real-time predictions
- Telegram alerts

---

## 🎯 Usage Examples

### View in Frontend
```bash
streamlit run src/frontend/app.py
```

Select any of the 48 symbols from the dropdown to view:
- Candlestick charts with SMAs
- RSI, MACD, Volume charts
- Database status

### Query Database
```bash
# Get all data for a symbol
docker exec stock_prediction_db psql -U stockuser -d stock_db -c "SELECT * FROM prices WHERE symbol='RELIANCE.NS' ORDER BY timestamp DESC LIMIT 10;"

# Get latest prices
docker exec stock_prediction_db psql -U stockuser -d stock_db -c "SELECT symbol, close, volume FROM prices WHERE timestamp = (SELECT MAX(timestamp) FROM prices);"
```

### Fetch More Data
```bash
# Add new symbols
python scripts/fetch_all_data.py --symbols "NEWSYMBOL.NS" --days 365

# Update existing symbols
python scripts/fetch_all_data.py --symbols "^NSEI,RELIANCE.NS" --days 365
```

---

## ⚠️ Missing Data

Two symbols are not available:
1. **TATAMOTORS.NS** - May have been delisted or renamed
2. **JSWRENEWABLES.NS** - New listing, limited history

**Workaround**: Use TATASTEEL.NS for steel sector, or check alternate symbols.

---

## 📝 Notes

- All data sourced from **Yahoo Finance** (free)
- Prices are **adjusted closes** (account for splits/dividends)
- Data stored in **TimescaleDB** (optimized for time-series)
- Records include: Open, High, Low, Close, Volume

---

## 🎉 Achievement

**11,901 records** across **48 Nifty 50 stocks** successfully populated!

This forms the foundation for:
- Machine learning models
- Technical analysis
- Backtesting strategies
- Trading signal generation

Ready for Phase 3: ML Model Implementation!

---

*Data Last Updated: June 8, 2026*  
*Next Update: Daily via automated cron job*