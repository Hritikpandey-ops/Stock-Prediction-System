# Stock Prediction System - Frontend

A minimal web interface to visualize the stock prediction system's data and functionality.

## 🚀 Features

- **Real-time Dashboard**: View stock prices, technical indicators, and system status
- **Interactive Charts**: Plotly-powered candlestick charts with zoom/pan
- **Technical Analysis**: RSI, MACD, Moving Averages visualization
- **Database Status**: Monitor database connection and data availability
- **Multi-Symbol Support**: View data for Nifty 50 stocks

## 🛠️ Installation

The frontend is already included in the main `requirements.txt`. To install separately:

```bash
pip install streamlit plotly
```

## 🎯 How to Run

1. **Start the Database** (if not already running):
```bash
docker-compose up -d db
```

2. **Populate Data** (optional, for fresh data):
```bash
python scripts/fetch_all_data.py --symbols "^NSEI,RELIANCE.NS,TCS.NS" --days 365
```

3. **Launch Frontend**:
```bash
streamlit run src/frontend/app.py
```

4. **Open Browser**:
Navigate to `http://localhost:8501`

## 📊 Dashboard Sections

### 1. Sidebar Configuration
- Symbol selection (^NSEI, RELIANCE.NS, TCS.NS, etc.)
- Time range slider (7-365 days)
- Refresh button
- System status information

### 2. Database Status
- Connection status (green/red indicator)
- PostgreSQL version
- Total records in database

### 3. Available Data
- Table showing all symbols with record counts
- Date range for each symbol

### 4. Price Summary
- Latest closing price
- Price change (₹ and %)
- Daily OHLC values
- Volume
- RSI indicator value

### 5. Interactive Charts
- **Candlestick Chart**: Price with SMA 20 & SMA 50 overlays
- **Volume Chart**: Daily trading volume
- **RSI Chart**: 14-day RSI with overbought/oversold lines
- **MACD Chart**: MACD line, Signal line, and histogram

## 🔧 Tech Stack

- **Framework**: Streamlit 1.50+
- **Visualization**: Plotly 6.0+
- **Database**: PostgreSQL + TimescaleDB
- **Charts**: Plotly Graph Objects

## 📁 Project Structure

```
src/frontend/
├── __init__.py       # Module initialization
├── app.py            # Main Streamlit application
└── README.md         # This file
```

## ⚠️ Important Notes

1. **Database Required**: The frontend needs the PostgreSQL database running to display data
2. **Data Population**: Run the fetch script before viewing data
3. **Port 8501**: Streamlit defaults to port 8501 (change with `--server.port`)
4. **Browser Access**: Can be accessed from other devices on the network

## 🎨 Customization

### Change Default Port
```bash
streamlit run src/frontend/app.py --server.port 8080
```

### Enable Dark Theme
The app automatically uses Plotly's dark theme. Streamlit theme is light by default.

### Add New Symbols
Edit the `available_symbols` list in `app.py`:
```python
available_symbols = ["^NSEI", "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS"]
```

## 📈 Next Features (Planned)

- [ ] Live prediction display
- [ ] Sentiment analysis visualization
- [ ] Model performance metrics
- [ ] Trading signal alerts
- [ ] Backtesting results display
- [ ] Historical predictions chart

## 🔒 Security

- Frontend is for local/LAN use only
- No authentication implemented (add if exposed publicly)
- Database credentials in `.env` file

## 📝 Troubleshooting

### "Database connection failed"
- Check if Docker container is running: `docker-compose ps`
- Verify database credentials in `.env`
- Ensure database is initialized: `python scripts/init_db.py`

### "No data available"
- Run data fetch script: `python scripts/fetch_all_data.py --symbols "^NSEI" --days 90`
- Check database has tables: `docker exec stock_prediction_db psql -U stockuser -d stock_db -c "\dt"`

### Charts not loading
- Check Plotly is installed: `pip install plotly`
- Try clearing browser cache
- Check browser console for errors

## 🤝 Contributing

This is a minimal frontend for demonstration. For production use, consider:
- Adding authentication (Streamlit-auth or similar)
- Implementing WebSocket for real-time updates
- Adding caching for better performance
- Implementing proper error handling

## 📄 License

Same as main project - MIT License

## 👨‍💻 Author

Built as part of the Stock Prediction System project

---

**⚠️ Disclaimer**: This frontend is for educational and research purposes. Stock market data and predictions should not be used for real trading without proper consultation with financial advisors.