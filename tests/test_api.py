"""
Basic API endpoint tests for the Stock Prediction System.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client with mocked database."""
    with patch("config.database.get_db") as mock_get_db:
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])

        from src.api.main import app
        client = TestClient(app)
        yield client


class TestHealthEndpoint:
    """Tests for /api/health endpoint."""

    def test_health_returns_ok(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["service"] == "stock-prediction-api"


class TestStocksEndpoint:
    """Tests for /api/stocks endpoint."""

    def test_list_stocks_returns_symbols(self, client):
        response = client.get("/api/stocks")
        assert response.status_code == 200
        data = response.json()
        assert "symbols" in data
        assert isinstance(data["symbols"], list)
        assert len(data["symbols"]) > 0


class TestPriceEndpoint:
    """Tests for /api/stocks/{symbol}/prices endpoint."""

    def test_invalid_symbol_returns_404(self, client):
        response = client.get("/api/stocks/INVALID/prices")
        assert response.status_code == 404

    def test_valid_symbol_returns_prices(self, client):
        # Mock the repository to return sample data
        with patch("src.api.routes.PriceRepository") as mock_repo:
            mock_instance = MagicMock()
            mock_instance.get_by_symbol.return_value = []
            mock_repo.return_value = mock_instance

            response = client.get("/api/stocks/RELIANCE/prices")
            assert response.status_code == 200
            data = response.json()
            assert "prices" in data


class TestFundamentalsEndpoint:
    """Tests for /api/stocks/{symbol}/fundamentals endpoint."""

    def test_invalid_symbol_returns_404(self, client):
        response = client.get("/api/stocks/INVALID/fundamentals")
        assert response.status_code == 404


class TestNewsEndpoint:
    """Tests for /api/stocks/{symbol}/news endpoint."""

    def test_invalid_symbol_returns_404(self, client):
        response = client.get("/api/stocks/INVALID/news")
        assert response.status_code == 404
