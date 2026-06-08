"""
SQLAlchemy ORM models for the Stock Prediction System.
"""
from sqlalchemy import Column, String, Integer, BigInteger, Numeric, DateTime, Boolean, UniqueConstraint, Index
from sqlalchemy.sql import func
from config.database import Base


class Price(Base):
    """Time-series OHLCV data for stocks and indices."""
    
    __tablename__ = "prices"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True, server_default=func.now())
    
    open = Column(Numeric(12, 4))
    high = Column(Numeric(12, 4))
    low = Column(Numeric(12, 4))
    close = Column(Numeric(12, 4))
    volume = Column(BigInteger)
    vwap = Column(Numeric(12, 4))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('symbol', 'timestamp', name='uq_symbol_timestamp'),
        Index('idx_prices_symbol_time', 'symbol', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<Price(symbol={self.symbol}, timestamp={self.timestamp}, close={self.close})>"


class Fundamental(Base):
    """Quarterly and annual fundamental data for stocks."""
    
    __tablename__ = "fundamentals"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False, index=True)
    report_date = Column(DateTime(timezone=True), nullable=False, index=True)
    period_type = Column(String(20), nullable=False)
    
    pe_ratio = Column(Numeric(10, 2))
    pb_ratio = Column(Numeric(10, 2))
    eps = Column(Numeric(10, 2))
    roe = Column(Numeric(5, 2))
    roce = Column(Numeric(5, 2))
    debt_to_equity = Column(Numeric(5, 2))
    current_ratio = Column(Numeric(5, 2))
    profit_margin = Column(Numeric(5, 2))
    revenue_growth = Column(Numeric(5, 2))
    market_cap = Column(BigInteger)
    shares_outstanding = Column(BigInteger)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('symbol', 'report_date', 'period_type', name='uq_symbol_report_period'),
        Index('idx_fundamentals_symbol_date', 'symbol', 'report_date'),
    )
    
    def __repr__(self):
        return f"<Fundamental(symbol={self.symbol}, report_date={self.report_date}, pe={self.pe_ratio})>"


class NewsSentiment(Base):
    """News articles with sentiment analysis scores."""
    
    __tablename__ = "news_sentiment"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=True, index=True)
    headline = Column(String(1000), nullable=False)
    source = Column(String(100))
    published_at = Column(DateTime(timezone=True), nullable=False, index=True)
    sentiment_score = Column(Numeric(5, 4))
    sentiment_label = Column(String(20))
    url = Column(String(2000), unique=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_news_symbol_time', 'symbol', 'published_at'),
    )
    
    def __repr__(self):
        return f"<NewsSentiment(headline={self.headline[:50]}, score={self.sentiment_score})>"


class ModelPrediction(Base):
    """Stored predictions for audit and performance tracking."""
    
    __tablename__ = "model_predictions"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False, index=True)
    prediction_date = Column(DateTime(timezone=True), nullable=False, index=True)
    horizon = Column(String(20), nullable=False)
    predicted_direction = Column(String(10), nullable=False)
    confidence_score = Column(Numeric(5, 4))
    model_version = Column(String(50), nullable=False)
    features_hash = Column(String(64))
    actual_return = Column(Numeric(10, 4))
    is_correct = Column(Boolean)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('symbol', 'prediction_date', 'horizon', 'model_version', name='uq_prediction'),
        Index('idx_predictions_symbol_date', 'symbol', 'prediction_date'),
    )
    
    def __repr__(self):
        return f"<ModelPrediction(symbol={self.symbol}, direction={self.predicted_direction}, confidence={self.confidence_score})>"


class BacktestResult(Base):
    """Backtesting performance metrics."""
    
    __tablename__ = "backtest_results"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    strategy_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    initial_capital = Column(Numeric(15, 2), nullable=False)
    
    final_capital = Column(Numeric(15, 2))
    total_return = Column(Numeric(10, 4))
    annualized_return = Column(Numeric(10, 4))
    sharpe_ratio = Column(Numeric(10, 4))
    sortino_ratio = Column(Numeric(10, 4))
    max_drawdown = Column(Numeric(10, 4))
    win_rate = Column(Numeric(5, 2))
    profit_factor = Column(Numeric(10, 4))
    total_trades = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<BacktestResult(strategy={self.strategy_name}, sharpe={self.sharpe_ratio}, return={self.total_return}%)>"