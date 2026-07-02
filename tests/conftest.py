"""
Shared test fixtures for the Stock Prediction System test suite.
"""
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_db_session():
    """Mock SQLAlchemy database session."""
    session = MagicMock()
    session.query.return_value = MagicMock()
    session.add = MagicMock()
    session.commit = MagicMock()
    session.close = MagicMock()
    return session


@pytest.fixture
def sample_price_data():
    """Sample OHLCV price data for testing."""
    return [
        {"timestamp": "2024-01-01", "open": 100, "high": 105, "low": 98, "close": 103, "volume": 1000000},
        {"timestamp": "2024-01-02", "open": 103, "high": 108, "low": 101, "close": 106, "volume": 1200000},
        {"timestamp": "2024-01-03", "open": 106, "high": 110, "low": 104, "close": 109, "volume": 1100000},
        {"timestamp": "2024-01-04", "open": 109, "high": 112, "low": 107, "close": 108, "volume": 900000},
        {"timestamp": "2024-01-05", "open": 108, "high": 111, "low": 106, "close": 110, "volume": 1050000},
    ]


@pytest.fixture
def sample_fundamentals():
    """Sample fundamental data for testing."""
    return {
        "symbol": "RELIANCE",
        "company_name": "Reliance Industries Ltd",
        "sector": "Oil & Gas",
        "industry": "Refineries",
        "pe_ratio": 25.5,
        "pb_ratio": 2.1,
        "roe": 18.5,
        "roce": 22.3,
        "debt_to_equity": 0.45,
        "net_profit_margin": 12.8,
        "market_cap": 1800000000000,
        "current_price": 2650.0,
        "eps": 103.9,
    }


@pytest.fixture
def sample_news():
    """Sample news data for testing."""
    return [
        {
            "id": 1,
            "symbol": "RELIANCE",
            "headline": "Reliance Industries reports strong Q3 results",
            "source": "Economic Times",
            "published_at": "2024-01-15T10:30:00",
            "sentiment_score": 0.75,
            "sentiment_label": "POSITIVE",
            "url": "https://example.com/news/1",
        },
        {
            "id": 2,
            "symbol": "RELIANCE",
            "headline": "Reliance to invest in green energy",
            "source": "Moneycontrol",
            "published_at": "2024-01-14T14:20:00",
            "sentiment_score": 0.45,
            "sentiment_label": "POSITIVE",
            "url": "https://example.com/news/2",
        },
    ]
