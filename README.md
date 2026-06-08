# Stock Prediction System

A cost-effective, scalable stock prediction system for the Indian market (Nifty 50) built with modern ML techniques and open-source tools.

## 🚀 Features

- **Multi-source Data Ingestion**: yfinance, Finnhub, Marketaux news API
- **Advanced Feature Engineering**: 100+ technical indicators, fundamental analysis, sentiment scoring
- **ML Models**: XGBoost, LSTM, and ensemble methods
- **Walk-forward Validation**: Robust backtesting with time-series cross-validation
- **Real-time API**: FastAPI endpoints for predictions and market outlook
- **Dockerized**: Easy deployment with PostgreSQL + TimescaleDB

## 📋 Prerequisites

- Docker & Docker Compose
- Python 3.10+ (for local development)
- API keys (optional): Finnhub, Marketaux

## 🛠️ Installation

### Quick Start (Docker)

```bash
# Clone the repository
git clone <repository-url>
cd stock-prediction-system

# Copy environment file
cp .env.example .env

# Start the stack
docker-compose up -d

# Access the API
open http://localhost:8000/docs
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Start PostgreSQL (using Docker only for DB)
docker-compose up -d db

# Run database migrations
alembic upgrade head

# Run the API
uvicorn src.api.main:app --reload
```

## 📁 Project Structure

```
stock-prediction-system/
├── config/              # Configuration and settings
├── src/
│   ├── data_ingestion/  # Data fetchers (yfinance, Finnhub, etc.)
│   ├── database/        # SQLAlchemy models and repositories
│   ├── features/        # Technical indicators, sentiment analysis
│   ├── models/          # ML models (XGBoost, LSTM)
│   ├── backtesting/     # Strategy backtesting engine
│   └── api/             # FastAPI endpoints
├── tests/               # Unit and integration tests
├── notebooks/           # Jupyter notebooks for exploration
├── scripts/             # CLI scripts for automation
└── docker-compose.yml   # Docker orchestration
```

## 🎯 Quick Usage

### Fetch Data

```bash
python scripts/fetch_all_data.py --symbols "RELIANCE.NS,TCS.NS,HDFCBANK.NS"
```

### Train Model

```bash
python scripts/train_model.py --symbol "^NSEI" --horizon 1D
```

### Run Backtest

```bash
python scripts/run_backtest.py --strategy xgboost --start-date 2023-01-01
```

### Get Prediction

```bash
# API endpoint
curl http://localhost:8000/predict/RELIANCE.NS

# Or via Python
import requests
response = requests.get("http://localhost:8000/predict/RELIANCE.NS")
print(response.json())
```

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/predict/{symbol}` | GET | Get prediction for a stock |
| `/nifty/outlook` | GET | Get Nifty 50 market direction |
| `/backtest/run` | POST | Run backtest for a strategy |
| `/retrain` | POST | Trigger model retraining |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger UI documentation |

## 🔧 Configuration

Copy `.env.example` to `.env` and configure:

```env
DATABASE_URL=postgresql://stockuser:stockpass@localhost:5432/stock_db
FINNHUB_API_KEY=your_finnhub_key
MARKETAUX_API_KEY=your_marketaux_key
INITIAL_CAPITAL=1000000
MODEL_VERSION=1.0.0
```

## 📈 Development Roadmap

- [x] Phase 1: Database & Data Ingestion
- [x] Phase 2: Feature Engineering
- [ ] Phase 3: ML Models & Training
- [ ] Phase 4: Backtesting Engine
- [ ] Phase 5: API & Deployment
- [ ] Phase 6: Paper Trading & Alerts

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 📝 License

MIT License - See [LICENSE](LICENSE) for details

## ⚠️ Disclaimer

This system is for **educational and research purposes only**. It is not financial advice. Past performance does not guarantee future results. Always do your own research and consult with a licensed financial advisor before making investment decisions.

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

Built with ❤️ using Python, FastAPI, XGBoost, and TimescaleDB