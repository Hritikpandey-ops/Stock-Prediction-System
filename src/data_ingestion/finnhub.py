"""
Finnhub data fetcher for price and news data.
"""
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import requests
from loguru import logger

from src.data_ingestion.base import BaseDataFetcher
from config.settings import get_settings

settings = get_settings()


class FinnhubFetcher(BaseDataFetcher):
    """Fetcher for price and news data from Finnhub API."""
    
    def __init__(self, api_key: Optional[str] = None, rate_limit: int = 60):
        """
        Initialize Finnhub fetcher.
        
        Args:
            api_key: Finnhub API key
            rate_limit: Requests per minute limit
        """
        super().__init__(rate_limit=rate_limit)
        self.api_key = api_key or settings.finnhub_api_key
        self.base_url = "https://finnhub.io/api/v1"
        self.logger = logger
        
        if not self.api_key:
            self.logger.warning("Finnhub API key not set. Some features may not work.")
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
        """Make API request with error handling."""
        if not self.api_key:
            self.logger.warning("Finnhub API key not configured")
            return None
        
        params['token'] = self.api_key
        
        try:
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            return None
    
    def fetch_prices(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Fetch historical candlestick data from Finnhub.
        
        Args:
            symbol: Stock symbol (e.g., 'NSE:RELIANCE')
            start_date: Start date
            end_date: End date
            
        Returns:
            List of price records
        """
        try:
            # Convert symbol to Finnhub format (remove .NS suffix)
            finnhub_symbol = symbol.replace('.NS', '').replace('.BSE', '')
            if not symbol.startswith('NSE:') and not symbol.startswith('BSE:'):
                finnhub_symbol = f"NSE:{finnhub_symbol}"
            
            self.logger.info(f"Fetching prices for {finnhub_symbol}")
            
            # Convert dates to Unix timestamp
            start_ts = int(start_date.timestamp())
            end_ts = int(end_date.timestamp())
            
            data = self._make_request('stock/candle', {
                'symbol': finnhub_symbol,
                'resolution': 'D',
                'from': start_ts,
                'to': end_ts
            })
            
            if not data or data.get('s') != 'ok':
                self.logger.warning(f"No data found for {symbol}")
                return []
            
            # Parse candlestick data
            records = []
            timestamps = data.get('t', [])
            opens = data.get('o', [])
            highs = data.get('h', [])
            lows = data.get('l', [])
            closes = data.get('c', [])
            volumes = data.get('v', [])
            
            for i in range(len(timestamps)):
                record = {
                    'timestamp': datetime.fromtimestamp(timestamps[i]),
                    'open': float(opens[i]) if opens[i] else None,
                    'high': float(highs[i]) if highs[i] else None,
                    'low': float(lows[i]) if lows[i] else None,
                    'close': float(closes[i]) if closes[i] else None,
                    'volume': int(volumes[i]) if volumes[i] else 0,
                    'vwap': None
                }
                records.append(record)
            
            self.logger.info(f"Fetched {len(records)} records for {symbol}")
            return records
            
        except Exception as e:
            self.logger.error(f"Error fetching prices for {symbol}: {str(e)}")
            return []
    
    def fetch_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch fundamental data from Finnhub.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary of fundamental data
        """
        try:
            finnhub_symbol = symbol.replace('.NS', '').replace('.BSE', '')
            if not symbol.startswith('NSE:') and not symbol.startswith('BSE:'):
                finnhub_symbol = f"NSE:{finnhub_symbol}"
            
            self.logger.info(f"Fetching fundamentals for {finnhub_symbol}")
            
            data = self._make_request('stock/metric', {
                'symbol': finnhub_symbol,
                'metric': 'all'
            })
            
            if not data:
                return {}
            
            metrics = data.get('metric', {})
            
            fundamentals = {
                'symbol': symbol,
                'pe_ratio': metrics.get('PE'),
                'pb_ratio': metrics.get('PBT'),
                'eps': metrics.get('EPS', {}).get('TTM'),
                'roe': metrics.get('ROE'),
                'debt_to_equity': metrics.get('Debt/Equity'),
                'current_ratio': metrics.get('Current'),
                'profit_margin': metrics.get('Net Margin'),
                'market_cap': metrics.get('Market Capitalization'),
                'shares_outstanding': metrics.get('Shares Outstanding'),
                'revenue_growth': metrics.get('Revenue Growth YoY')
            }
            
            self.logger.info(f"Fetched fundamentals for {symbol}")
            return fundamentals
            
        except Exception as e:
            self.logger.error(f"Error fetching fundamentals for {symbol}: {str(e)}")
            return {}
    
    def fetch_news(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch news articles from Finnhub.
        
        Args:
            symbol: Stock symbol (optional)
            start_date: Start date
            end_date: End date
            
        Returns:
            List of news articles
        """
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=7)
            if not end_date:
                end_date = datetime.now()
            
            # Convert dates to Unix timestamp
            start_ts = int(start_date.timestamp())
            end_ts = int(end_date.timestamp())
            
            news_list = []
            
            if symbol:
                # Fetch company-specific news
                finnhub_symbol = symbol.replace('.NS', '').replace('.BSE', '')
                if not symbol.startswith('NSE:') and not symbol.startswith('BSE:'):
                    finnhub_symbol = f"NSE:{finnhub_symbol}"
                
                data = self._make_request('company-news', {
                    'symbol': finnhub_symbol,
                    'from': start_date.strftime('%Y-%m-%d'),
                    'to': end_date.strftime('%Y-%m-%d')
                })
                
                if data:
                    for article in data:
                        publication_date = article.get('publicationDate')
                        if isinstance(publication_date, (int, float)):
                            published_at = datetime.fromtimestamp(publication_date)
                            if published_at.year == 1970:  # Handle invalid timestamp
                                published_at = datetime.now()
                        elif isinstance(publication_date, str):
                            try:
                                published_at = datetime.strptime(publication_date, '%Y-%m-%d %H:%M:%S')
                            except ValueError:
                                published_at = datetime.now()
                        else:
                            published_at = datetime.now()
                        
                        news_list.append({
                            'headline': article.get('headline', ''),
                            'source': article.get('source', ''),
                            'published_at': published_at,
                            'sentiment_score': None,  # Finnhub doesn't provide sentiment
                            'sentiment_label': None,
                            'url': article.get('url', ''),
                            'symbol': symbol
                        })
            else:
                # Fetch general market news
                data = self._make_request('news', {
                    'category': 'general',
                    'from': start_date.strftime('%Y-%m-%d'),
                    'to': end_date.strftime('%Y-%m-%d')
                })
                
                if data:
                    for article in data[:20]:  # Limit to 20 articles
                        published_at = datetime.fromtimestamp(article.get('publishedAt', 0))
                        if published_at.year == 1970:  # Handle invalid timestamp
                            published_at = datetime.now()
                        
                        news_list.append({
                            'headline': article.get('headline', ''),
                            'source': article.get('source', ''),
                            'published_at': published_at,
                            'sentiment_score': None,
                            'sentiment_label': None,
                            'url': article.get('url', ''),
                            'symbol': None
                        })
            
            self.logger.info(f"Fetched {len(news_list)} news articles")
            return news_list
        
        except Exception as e:
            self.logger.error(f"Error fetching news: {str(e)}")
            return []
    
    def fetch_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch current quote for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Current quote data
        """
        try:
            finnhub_symbol = symbol.replace('.NS', '').replace('.BSE', '')
            if not symbol.startswith('NSE:') and not symbol.startswith('BSE:'):
                finnhub_symbol = f"NSE:{finnhub_symbol}"
            
            data = self._make_request('quote', {'symbol': finnhub_symbol})
            
            if data and data.get('c'):
                return {
                    'current_price': data.get('c'),
                    'change': data.get('d'),
                    'change_percent': data.get('dp'),
                    'high': data.get('h'),
                    'low': data.get('l'),
                    'open': data.get('o'),
                    'previous_close': data.get('pc')
                }
            
            return None
        
        except Exception as e:
            self.logger.error(f"Error fetching quote for {symbol}: {str(e)}")
            return None