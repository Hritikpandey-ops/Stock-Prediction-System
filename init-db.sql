-- Create base tables first, then convert to hypertables
-- This order is important for TimescaleDB

-- Create prices table
CREATE TABLE IF NOT EXISTS prices (
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

CREATE INDEX IF NOT EXISTS idx_prices_symbol_time ON prices (symbol, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_prices_timestamp ON prices (timestamp DESC);

-- Convert to TimescaleDB hypertable (ignore error if already a hypertable)
SELECT create_hypertable('prices', 'timestamp', if_not_exists := TRUE);

-- Create fundamentals table
CREATE TABLE IF NOT EXISTS fundamentals (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    report_date DATE NOT NULL,
    period_type VARCHAR(20) NOT NULL,
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

CREATE INDEX IF NOT EXISTS idx_fundamentals_symbol_date ON fundamentals (symbol, report_date DESC);

-- Create news sentiment table
CREATE TABLE IF NOT EXISTS news_sentiment (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10),
    headline TEXT NOT NULL,
    source VARCHAR(100),
    published_at TIMESTAMPTZ NOT NULL,
    sentiment_score DECIMAL(5, 4),
    sentiment_label VARCHAR(20),
    url TEXT UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_news_symbol_time ON news_sentiment (symbol, published_at DESC);

-- Create model predictions table
CREATE TABLE IF NOT EXISTS model_predictions (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    prediction_date TIMESTAMPTZ NOT NULL,
    horizon VARCHAR(20) NOT NULL,
    predicted_direction VARCHAR(10) NOT NULL,
    confidence_score DECIMAL(5, 4),
    model_version VARCHAR(50) NOT NULL,
    features_hash VARCHAR(64),
    actual_return DECIMAL(10, 4),
    is_correct BOOLEAN,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (symbol, prediction_date, horizon, model_version)
);

CREATE INDEX IF NOT EXISTS idx_predictions_symbol_date ON model_predictions (symbol, prediction_date DESC);

-- Create backtest results table
CREATE TABLE IF NOT EXISTS backtest_results (
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

CREATE INDEX IF NOT EXISTS idx_backtest_strategy ON backtest_results (strategy_name);
CREATE INDEX IF NOT EXISTS idx_backtest_dates ON backtest_results (start_date, end_date);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO stockuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO stockuser;