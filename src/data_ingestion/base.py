"""
Abstract base class for data fetchers.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import datetime
from loguru import logger


class BaseDataFetcher(ABC):
    """Abstract base class for all data fetchers."""
    
    def __init__(self, rate_limit: int = 60):
        """
        Initialize the data fetcher.
        
        Args:
            rate_limit: Maximum requests per minute
        """
        self.rate_limit = rate_limit
        self.logger = logger
    
    @abstractmethod
    def fetch_prices(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Fetch historical price data.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.NS')
            start_date: Start date for data
            end_date: End date for data
            
        Returns:
            List of price dictionaries with keys: timestamp, open, high, low, close, volume
        """
        pass
    
    @abstractmethod
    def fetch_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch fundamental data for a stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary of fundamental data
        """
        pass
    
    @abstractmethod
    def fetch_news(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch news articles.
        
        Args:
            symbol: Stock symbol (optional for general market news)
            start_date: Start date for news
            end_date: End date for news
            
        Returns:
            List of news dictionaries
        """
        pass
    
    def validate_price_data(self, data: List[Dict[str, Any]]) -> bool:
        """Validate price data structure."""
        required_fields = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        
        if not data:
            return False
        
        for record in data:
            if not all(field in record for field in required_fields):
                self.logger.warning(f"Invalid price data record: {record}")
                return False
        
        return True
    
    def sanitize_symbol(self, symbol: str) -> str:
        """Clean and validate symbol format."""
        symbol = symbol.strip().upper()
        if not symbol:
            raise ValueError("Symbol cannot be empty")
        return symbol