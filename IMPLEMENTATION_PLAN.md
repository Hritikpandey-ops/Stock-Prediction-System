# Stock Prediction System - Implementation Plan

## 🎯 Project Goal
Build a cost-effective, scalable stock prediction system for the Indian market (Nifty 50) that predicts market direction and individual stock movements using free data sources and open-source tools.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     STOCK PREDICTION SYSTEM                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │  DATA LAYER  │───▶│ FEATURE      │───▶│ ML MODEL     │          │
│  │              │    │ ENGINEERING  │    │ TRAINING     │          │
│  │ • yfinance   │    │              │    │              │          │
│  │ • Finnhub    │    │ • Technical  │    │ • XGBoost    │          │
│  │ • Marketaux  │    │   Indicators │    │ • LSTM       │          │
│  │ • RBI/World  │    │ • Sentiment  │    │ • Ensemble   │          │
│  │   Bank       │    │ • Fundamentals│   │              │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│         │                   │                   │                   │
│         ▼                   ▼                   ▼                   │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    POSTGRESQL (TimescaleDB)                   │  │
│  │  • prices (OHLCV)  • fundamentals  • predictions  • signals   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           │                                         │
│                           ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                 BACKTESTING & EVALUATION ENGINE               │  │
│  │  • Walk-forward validation  • Sharpe ratio  • Max drawdown    │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           │                                         │
│                           ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    FASTAPI PREDICTION SERVICE                 │  │
│  │  • GET /predict/{symbol}  • GET /nifty/outlook               │  │
│  │  • POST /retrain  • GET /historical-signals                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           │                                         │
│                           ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    SCHEDULER (GitHub Actions)                 │  │
│  │  • Daily data fetch  • Model retraining  • Alert generation   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Technology Stack

### Core
- **Language**: Python 3.10+
- **Database**: PostgreSQL 14+ with TimescaleDB extension
- **ORM**: SQLAlchemy 2.0+
- **API Framework**: FastAPI + Uvicorn

### Data & Features
- **Price Data**: `yfinance` (primary), `finnhub` (backup)
- **News/Sentiment**: `marketaux` API, `vaderSentiment`
- **Technical Indicators**: `pandas_ta` (100+ indicators)
- **Fundamentals**: `yfinance` + custom calculations

### Machine Learning
- **Classical ML**: `scikit-learn`, `xgboost`, `lightgbm`
- **Deep Learning**: `pytorch` (LSTM/GRU models)
- **Validation**: Custom walk-forward splitter

### Backtesting
- **Library**: `backtrader` (primary), custom Pandas logic (fallback)
- **Metrics**: `empyrical`, `quantstats`

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Scheduling**: GitHub Actions (free tier)
- **Deployment**: Railway.app or Render (free tier)
- **Monitoring**: Prometheus + Grafana (optional)

---

## 🗄️ Database Schema

### 1. `prices` (Time-series OHLCV data)
```sql
CREATE TABLE prices (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    open DECIMAL(12, 4),
    high DECIMAL(12, 4),
    low DECIMAL(12, 4),
    close DECIMAL(12, 4),
    volume BIGINT,
    vwap DECIMAL(12, 4),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (symbol, timestamp)
);

-- Hypertable for TimescaleDB
SELECT create_hypertable('prices', 'timestamp');
CREATE INDEX idx_prices_symbol_time ON prices (symbol, timestamp DESC);
```

### 2. `fundamentals` (Quarterly/Annual financials)
```sql
CREATE TABLE fundamentals (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    report_date DATE NOT NULL,
    period_type VARCHAR(20) NOT NULL, -- 'QUARTERLY' or 'ANNUAL'
    pe_ratio DECIMAL(10, 2),
    pb_ratio DECIMAL(10, 2),
    eps DECIMAL(10, 2),
    roe DECIMAL(5, 2),
    roce DECIMAL(5, 2),
    debt_to_equity DECIMAL(5, 2),
    current_ratio DECIMAL(5, 2),
    profit_margin DECIMAL(5, 2),
    revenue_growth DECIMAL(5, 2),
    market_cap BIGINT,
    shares_outstanding BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (symbol, report_date, period_type)
);

CREATE INDEX idx_fundamentals_symbol_date ON fundamentals (symbol, report_date DESC);
```

### 3. `news_sentiment` (News articles with sentiment)
```sql
CREATE TABLE news_sentiment (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10), -- NULL for general market news
    headline TEXT NOT NULL,
    source VARCHAR(100),
    published_at TIMESTAMPTZ NOT NULL,
    sentiment_score DECIMAL(5, 4), -- -1 to +1
    sentiment_label VARCHAR(20), -- 'NEGATIVE', 'NEUTRAL', 'POSITIVE'
    url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (url)
);

CREATE INDEX idx_news_symbol_time ON news_sentiment (symbol, published_at DESC);
```

### 4. `model_predictions` (Stored predictions for audit)
```sql
CREATE TABLE model_predictions (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    prediction_date TIMESTAMPTZ NOT NULL,
    horizon VARCHAR(20) NOT NULL, -- '1D', '1W', '1M'
    predicted_direction VARCHAR(10) NOT NULL, -- 'UP', 'DOWN', 'NEUTRAL'
    confidence_score DECIMAL(5, 4),
    model_version VARCHAR(50) NOT NULL,
    features_hash VARCHAR(64), -- For reproducibility
    actual_return DECIMAL(10, 4), -- Populated after fact
    is_correct BOOLEAN, -- Populated after fact
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (symbol, prediction_date, horizon, model_version)
);

CREATE INDEX idx_predictions_symbol_date ON model_predictions (symbol, prediction_date DESC);
```

### 5. `backtest_results` (Performance metrics)
```sql
CREATE TABLE backtest_results (
    id BIGSERIAL PRIMARY KEY,
    strategy_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(15, 2) NOT NULL,
    final_capital DECIMAL(15, 2),
    total_return DECIMAL(10, 4),
    annualized_return DECIMAL(10, 4),
    sharpe_ratio DECIMAL(10, 4),
    sortino_ratio DECIMAL(10, 4),
    max_drawdown DECIMAL(10, 4),
    win_rate DECIMAL(5, 2),
    profit_factor DECIMAL(10, 4),
    total_trades INTEGER,
    avg_trade_duration INTERVAL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 📂 Project Structure

```
stock-prediction-system/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
├── IMPLEMENTATION_PLAN.md (this file)
│
├── config/
│   ├── settings.py          # Environment variables, API keys
│   ├── database.py          # SQLAlchemy engine, session
│   └── logging_config.py
│
├── src/
│   ├── data_ingestion/
│   │   ├── __init__.py
│   │   ├── base.py          # Abstract base class for data fetchers
│   │   ├── yahoo_finance.py # yfinance wrapper
│   │   ├── finnhub.py       # Finnhub wrapper
│   │   ├── marketaux.py     # News API wrapper
│   │   └── scheduler.py     # Data fetch orchestration
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py        # SQLAlchemy ORM models
│   │   ├── repository.py    # CRUD operations
│   │   └── migrations/      # Alembic migrations
│   │
│   ├── features/
│   │   ├── __init__.py
│   │   ├── technical.py     # pandas_ta indicators
│   │   ├── fundamental.py   # Ratio calculations
│   │   ├── sentiment.py     # VADER/NLP processing
│   │   └── pipeline.py      # Feature engineering orchestration
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py          # Abstract ML model interface
│   │   ├── xgboost_model.py # XGBoost classifier
│   │   ├── lstm_model.py    # PyTorch LSTM model
│   │   ├── ensemble.py      # Model stacking
│   │   └── trainer.py       # Training logic with walk-forward
│   │
│   ├── backtesting/
│   │   ├── __init__.py
│   │   ├── engine.py        # Backtest execution
│   │   ├── strategies.py    # Trading strategies
│   │   ├── metrics.py       # Sharpe, drawdown, etc.
│   │   └── visualizer.py    # Plotting results
│   │
│   └── api/
│       ├── __init__.py
│       ├── main.py          # FastAPI application
│       ├── endpoints/
│       │   ├── predictions.py
│       │   ├── nifty.py
│       │   ├── backtest.py
│       │   └── health.py
│       ├── schemas.py       # Pydantic models
│       └── dependencies.py
│
├── tests/
│   ├── __init__.py
│   ├── test_data_ingestion.py
│   ├── test_features.py
│   ├── test_models.py
│   └── test_api.py
│
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_feature_analysis.ipynb
│   └── 03_model_experiments.ipynb
│
├── scripts/
│   ├── fetch_all_data.py
│   ├── train_model.py
│   ├── run_backtest.py
│   └── generate_alerts.py
│
└── .github/
    └── workflows/
        ├── daily_data_fetch.yml
        ├── model_retrain.yml
        └── deploy.yml
```

---

## 🚀 Implementation Phases

### Phase 1: Foundation (Week 1)
**Goal**: Set up project structure, database, and basic data ingestion.

**Tasks**:
- [ ] Create project directory structure
- [ ] Set up Docker Compose with PostgreSQL + TimescaleDB
- [ ] Implement SQLAlchemy models (`prices`, `fundamentals`)
- [ ] Build `yfinance` data fetcher with database persistence
- [ ] Create basic CLI scripts for data ingestion
- [ ] Write unit tests for data layer

**Deliverables**:
- Working Docker environment
- Database schema populated with Nifty 50 historical data
- `scripts/fetch_all_data.py` script

---

### Phase 2: Feature Engineering (Week 2-3)
**Goal**: Build robust feature pipeline for technical, fundamental, and sentiment data.

**Tasks**:
- [ ] Implement technical indicator calculations (SMA, EMA, RSI, MACD, Bollinger, ATR)
- [ ] Build fundamental ratio calculators (P/E, P/B, ROE, debt/equity)
- [ ] Integrate Marketaux news API and sentiment scoring
- [ ] Create feature alignment logic (handle different frequencies)
- [ ] Implement feature storage in database or Parquet files
- [ ] Add feature validation and outlier detection

**Deliverables**:
- `src/features/pipeline.py` with full feature generation
- 50+ technical indicators ready
- Sentiment scores for Nifty 50 stocks
- Feature importance analysis notebook

---

### Phase 3: ML Models & Training (Week 4-5)
**Goal**: Train and validate prediction models with walk-forward validation.

**Tasks**:
- [ ] Implement XGBoost baseline model
- [ ] Build LSTM/GRU deep learning model
- [ ] Create walk-forward validation splitter
- [ ] Implement hyperparameter tuning (Optuna)
- [ ] Add model versioning and experiment tracking (MLflow optional)
- [ ] Build model persistence (pickle/joblib)

**Deliverables**:
- Trained XGBoost and LSTM models
- Walk-forward validation results
- Model performance comparison report
- `scripts/train_model.py` for automated training

---

### Phase 4: Backtesting Engine (Week 6)
**Goal**: Evaluate strategies with realistic transaction costs and slippage.

**Tasks**:
- [ ] Integrate Backtrader or build custom backtester
- [ ] Implement transaction cost model (₹20/trade + 0.05% slippage)
- [ ] Calculate financial metrics (Sharpe, Sortino, max drawdown)
- [ ] Build equity curve visualization
- [ ] Add risk management rules (position sizing, stop-loss)
- [ ] Compare vs. buy-and-hold benchmark

**Deliverables**:
- Backtest execution engine
- Performance reports for each strategy
- Equity curve charts
- `scripts/run_backtest.py`

---

### Phase 5: API & Deployment (Week 7-8)
**Goal**: Expose predictions via REST API and automate daily operations.

**Tasks**:
- [ ] Build FastAPI application with endpoints:
  - `GET /predict/{symbol}` - Get prediction for a stock
  - `GET /nifty/outlook` - Get Nifty 50 market direction
  - `POST /retrain` - Trigger model retraining
  - `GET /historical-signals` - View past predictions
- [ ] Implement async database sessions
- [ ] Add authentication (API keys)
- [ ] Create Dockerfile for production deployment
- [ ] Set up GitHub Actions for daily data fetch
- [ ] Deploy to Railway.app or Render (free tier)
- [ ] Add monitoring and logging

**Deliverables**:
- Live API endpoint
- Automated daily data pipeline
- Production deployment
- API documentation (Swagger UI)

---

### Phase 6: Enhancement & Paper Trading (Week 9-10)
**Goal**: Add advanced features and simulate live trading.

**Tasks**:
- [ ] Add ensemble model (combine XGBoost + LSTM + Sentiment)
- [ ] Implement real-time alert system (Telegram/Email)
- [ ] Build paper trading simulator
- [ ] Add model drift detection
- [ ] Optimize inference speed
- [ ] Write comprehensive documentation

**Deliverables**:
- Ensemble model with improved accuracy
- Live alert system
- Paper trading dashboard
- Complete documentation

---

## 🧪 Testing Strategy

### Unit Tests
- Data fetchers (mock API responses)
- Feature calculations (verify against known values)
- Database CRUD operations
- Model training (small dataset)

### Integration Tests
- End-to-end data pipeline
- API endpoint responses
- Backtest execution

### Performance Tests
- Database query optimization
- Model inference latency
- Concurrent API requests

---

## 🔐 Security & Compliance

### Data Licensing
- Verify API terms for yfinance, Finnhub, Marketaux
- Include attribution in documentation
- Respect rate limits

### SEBI Compliance (Future)
- Add disclaimer: "For educational/research purposes only"
- No real-money execution without SEBI registration
- Log all predictions for audit trail

### API Security
- Environment variables for API keys (`.env` file)
- API key authentication for endpoints
- Rate limiting on public endpoints

---

## 📊 Success Metrics

### Technical
- Data ingestion: 100% of Nifty 50 stocks updated daily
- Model accuracy: >55% directional accuracy (better than random)
- API response time: <200ms for predictions
- System uptime: >95%

### Financial (Backtest)
- Sharpe ratio: >1.0
- Max drawdown: <20%
- Win rate: >50%
- Profit factor: >1.2

---

## 🛠️ Code Generation Approach

I will generate code in the following order:

1. **Configuration & Infrastructure**
   - `docker-compose.yml`, `Dockerfile`, `requirements.txt`
   - `config/settings.py`, `config/database.py`

2. **Database Layer**
   - `src/database/models.py` (SQLAlchemy ORM)
   - `src/database/repository.py` (CRUD operations)

3. **Data Ingestion**
   - `src/data_ingestion/base.py`, `yahoo_finance.py`
   - `src/data_ingestion/scheduler.py`

4. **Feature Engineering**
   - `src/features/technical.py`, `fundamental.py`, `sentiment.py`
   - `src/features/pipeline.py`

5. **Machine Learning**
   - `src/models/base.py`, `xgboost_model.py`, `lstm_model.py`
   - `src/models/trainer.py`

6. **Backtesting**
   - `src/backtesting/engine.py`, `metrics.py`
   - `scripts/run_backtest.py`

7. **API**
   - `src/api/main.py`, `endpoints/predictions.py`
   - `src/api/schemas.py`

8. **Testing & Scripts**
   - Unit tests for each module
   - CLI scripts for automation

**Each file will include**:
- Type hints
- Docstrings
- Error handling
- Logging
- Unit tests

---

## 📝 Next Steps

1. **Review this plan** and provide feedback on:
   - Technology stack choices
   - Database schema
   - Feature priorities
   - Any additional requirements

2. **Upon approval**, I will start generating the code files in this order:
   - Infrastructure setup (Docker, requirements)
   - Database models and connection
   - Data ingestion pipeline
   - Feature engineering
   - ML models
   - Backtesting
   - API

3. **Iterate** based on testing results and feedback.

---

## 🎓 Learning Resources

- **TimescaleDB**: https://docs.timescale.com/
- **FastAPI**: https://fastapi.tiangolo.com/
- **pandas_ta**: https://github.com/dgtlmoon/pandas_ta
- **XGBoost**: https://xgboost.readthedocs.io/
- **Backtrader**: https://www.backtrader.com/
- **Walk-forward validation**: https://www.investopedia.com/terms/w/walk-forward.asp

---

*Last Updated: 2026-06-08*
*Version: 1.0*