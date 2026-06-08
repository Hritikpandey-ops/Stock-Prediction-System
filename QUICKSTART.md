# 🚀 Stock Prediction System - Quick Start Guide

## What We Have

✅ **Working Database**: PostgreSQL + TimescaleDB on port 5433  
✅ **Data Pipeline**: Yahoo Finance → Database (745 price records)  
✅ **Tech Stack**: Python, FastAPI, XGBoost, Streamlit  
✅ **Frontend**: Interactive dashboard at http://localhost:8501  
📊 **Tech Indicators**: 50+ (SMA, RSI, MACD, Bollinger, etc.)

---

## ⚡ Start Everything in 3 Steps

### Step 1: Start Database
```bash
cd /Users/innovitegrasolutions/Desktop/Stock-Prediction-System
docker-compose up -d db
```

### Step 2: Launch Frontend
```bash
streamlit run src/frontend/app.py
```

### Step 3: Open Browser
```
http://localhost:8501
```

**That's it!** 🎉

---

## 📈 What You'll See

### Dashboard Features
- 📊 **Live Price Charts**: Candlestick with SMA overlays
- 📉 **Technical Indicators**: RSI, MACD, Volume
- 🗄️ **Database Status**: Connection health & record counts
- 📋 **Data Summary**: Available symbols and date ranges

### Available Data
- ^NSEI (Nifty 50): 245 records (Jun 2025 - Jun 2026)
- RELIANCE.NS: 248 records
- TCS.NS: 248 records

---

## 🔧 Common Commands

### Fetch More Data
```bash
python scripts/fetch_all_data.py --symbols "HDFCBANK.NS,INFY.NS" --days 180
```

### Check Database
```bash
docker exec stock_prediction_db psql -U stockuser -d stock_db -c "SELECT COUNT(*) FROM prices;"
```

### View Logs
```bash
docker-compose logs db
```

### Stop Everything
```bash
docker-compose down
```

---

## 🎯 Next: Build ML Models

Once frontend is working:

1. **Phase 3 - ML Models** (Next)
   - Train XGBoost on technical indicators
   - Predict Nifty 50 direction (UP/DOWN)
   - Expected accuracy: 55-70%

2. **Phase 4 - Backtesting**
   - Walk-forward validation
   - Transaction costs (₹20/trade)
   - Sharpe ratio, max drawdown

3. **Phase 5 - API**
   - FastAPI endpoints
   - GET /predict/{symbol}
   - Deploy to Railway.app

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `src/frontend/app.py` | Streamlit dashboard |
| `scripts/fetch_all_data.py` | Data ingestion |
| `config/settings.py` | Configuration |
| `src/database/models.py` | Database schema |
| `PROGRESS_REPORT.md` | Detailed progress |
| `IMPLEMENTATION_PLAN.md` | Full implementation plan |

---

## ⚠️ Current Limitations

1. **No ML Models Yet** - Only data visualization
2. **No News Sentiment** - Needs Marketaux API key
3. **No Predictions** - ML training pending
4. **No Backtesting** - Engine not built yet

---

## 📚 Documentation

- **Quick Start**: This file
- **Progress**: `PROGRESS_REPORT.md`
- **Implementation**: `IMPLEMENTATION_PLAN.md`
- **Frontend Guide**: `src/frontend/README.md`

---

## 🆘 Troubleshooting

### "Connection failed" in frontend
```bash
docker-compose restart db
sleep 5
```

### "No data" in charts
```bash
python scripts/fetch_all_data.py --symbols "^NSEI" --days 30
```

### Database won't start
```bash
docker-compose down -v
docker-compose up -d db
```

---

## 🎉 Success Criteria

When you see:
- ✅ Green "Connected" status in sidebar
- ✅ 3 symbols listed with record counts
- ✅ Candlestick chart with SMA overlays
- ✅ RSI and MACD charts below
- ✅ No red error messages

**Then your system is working!**

---

## 📞 Next Steps

1. **Verify this guide works** (frontend loads)
2. **Read PROGRESS_REPORT.md** for full context
3. **Ask**: "Continue with ML model implementation?"
4. **Goal**: Build prediction model next week

---

**Built with ❤️ using Python, Streamlit, Plotly, and TimescaleDB**  
**For the Indian Stock Market (Nifty 50)**  
**Date**: June 8, 2026