# 📈 Stock Prediction System - Nifty 50 (India)

A cost-effective, scalable stock prediction system for the Indian market using machine learning and free data sources.

## 🎯 Current Status

### ✅ Working Features
- **Database**: PostgreSQL + TimescaleDB (745 price records)
- **Data Pipeline**: Yahoo Finance → Database
- **Technical Analysis**: 50+ indicators (SMA, RSI, MACD, Bollinger, etc.)
- **Frontend Dashboard**: Streamlit app at `http://localhost:8501`

### 📊 Available Data
- ^NSEI (Nifty 50 Index): 245 records
- RELIANCE.NS: 248 records
- TCS.NS: 248 records
- Date Range: Jun 2025 - Jun 2026

---

## 🚀 Quick Start

### 1. Start Database
```bash
docker-compose up -d db
```

### 2. Launch Frontend
```bash
streamlit run src/frontend/app.py
```

### 3. Open Browser
Navigate to: `http://localhost:8501`

**That's it!** You should see the dashboard with price charts and technical indicators.

---

## 📁 Project Structure

```
stock-prediction-system/
├── config/                 # Configuration
│   ├── settings.py         # Environment variables
│   ├── database.py        # SQLAlchemy setup
│   └── logging_config.py   # Logging
│
├── src/
│   ├── data_ingestion/     # Data fetching (yfinance, Finnhub)
│   ├── database/           # ORM models & CRUD
│   ├── features/           # Technical & sentiment analysis
│   ├── models/             # ML models (pending)
│   ├── backtesting/        # Backtesting engine (pending)
│   ├── api/                # FastAPI endpoints (pending)
│   └── frontend/           # Streamlit dashboard ✅
│
├── scripts/                # CLI tools
│   ├── fetch_all_data.py  # Data ingestion ✅
│   ├── init_db.py         # Database setup ✅
│   └── train_model.py     # ML training (pending)
│
├── docker-compose.yml      # Docker setup
├── requirements.txt        # Python dependencies
├── QUICKSTART.md          # Quick start guide
├── PROGRESS_REPORT.md     # Detailed progress
└── IMPLEMENTATION_PLAN.md # Full roadmap
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.9+ |
| Database | PostgreSQL + TimescaleDB |
| ML | scikit-learn, XGBoost, PyTorch |
| API | FastAPI + Uvicorn |
| Frontend | Streamlit + Plotly |
| Container | Docker + Docker Compose |

---

## 📈 Features

### Data Ingestion ✅
- Yahoo Finance (free OHLCV data)
- Finnhub API (fundamentals & news)
- Marketaux (sentiment analysis - needs API key)
- Automatic database storage

### Feature Engineering ✅
- **Technical Indicators**: 50+ (SMA, EMA, RSI, MACD, Bollinger, ATR, etc.)
- **Fundamental Ratios**: P/E, P/B, ROE, debt/equity
- **Sentiment Analysis**: VADER for news headlines

### Machine Learning 🚧 (Next Phase)
- XGBoost classifier for direction prediction
- LSTM for sequential patterns
- Walk-forward validation
- Expected accuracy: 55-70%

### Backtesting 🚧 (Later)
- Transaction costs (₹20/trade)
- Slippage modeling
- Sharpe ratio, max drawdown
- Risk metrics

---

## 🎯 Usage

### Fetch Stock Data
```bash
python scripts/fetch_all_data.py --symbols "^NSEI,RELIANCE.NS" --days 365
```

### View Dashboard
```bash
streamlit run src/frontend/app.py
```

### Check Database
```bash
docker exec stock_prediction_db psql -U stockuser -d stock_db -c "\dt"
```

---

## 📊 Dashboard Preview

The Streamlit frontend provides:

- **Price Charts**: Interactive candlestick with moving averages
- **Technical Indicators**: RSI, MACD, Bollinger Bands
- **Volume Analysis**: Trading volume visualization
- **Database Status**: Connection health monitoring
- **Data Summary**: Available symbols and record counts

Access at: `http://localhost:8501`

---

## 🔑 API Keys (Optional)

For full functionality, configure free API keys in `.env`:

```env
FINNHUB_API_KEY=your_finnhub_key      # https://finnhub.io/
MARKETAUX_API_KEY=your_marketaux_key  # https://marketaux.com/
```

---

## 📚 Documentation

- [QUICKSTART.md](QUICKSTART.md) - Get started in 3 steps
- [PROGRESS_REPORT.md](PROGRESS_REPORT.md) - Detailed progress report
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Full implementation plan
- [src/frontend/README.md](src/frontend/README.md) - Frontend guide

---

## 🎓 Next Steps

1. **Week 1**: Build ML models (XGBoost, LSTM)
2. **Week 2**: Implement backtesting engine
3. **Week 3**: Deploy FastAPI + predictions endpoint
4. **Week 4**: Paper trading simulation

---

## ⚠️ Disclaimer

**This system is for educational and research purposes only.**

- Not financial advice
- Past performance doesn't guarantee future results
- Stock investments involve risk
- Always consult a licensed financial advisor

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests
4. Submit a pull request

---

## 📞 Support

- Open an issue for bugs
- Discussions for questions
- Check PROGRESS_REPORT.md for context

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

**Built with ❤️ using Python, FastAPI, XGBoost, Streamlit, and TimescaleDB**  
**For the Indian Stock Market (Nifty 50)**  
**Version**: 1.0.0  
**Date**: June 8, 2026