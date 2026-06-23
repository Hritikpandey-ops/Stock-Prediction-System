"""
Marketaux news API fetcher with sentiment analysis.
"""
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import requests
from loguru import logger

from src.data_ingestion.base import BaseDataFetcher
from config.settings import get_settings

settings = get_settings()


class MarketauxFetcher(BaseDataFetcher):
    """Fetcher for news and sentiment data from Marketaux API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Marketaux fetcher.
        
        Args:
            api_key: Marketaux API key
        """
        super().__init__(rate_limit=60)
        self.api_key = api_key or settings.marketaux_api_key
        self.base_url = "https://api.marketaux.com/v1"
        self.logger = logger
        
        if not self.api_key:
            self.logger.warning("Marketaux API key not set. Some features may not work.")
    
    def fetch_prices(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Marketaux doesn't provide price data.
        Use Yahoo Finance or Finnhub for prices.
        """
        self.logger.info("Marketaux doesn't provide price data. Use Yahoo Finance or Finnhub.")
        return []
    
    def fetch_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """
        Marketaux doesn't provide fundamental data.
        Use Yahoo Finance or Finnhub for fundamentals.
        """
        self.logger.info("Marketaux doesn't provide fundamental data. Use Yahoo Finance or Finnhub.")
        return {}
    
    def fetch_news(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Fetch news articles with sentiment from Marketaux.
        
        Args:
            symbol: Stock symbol (optional)
            start_date: Start date
            end_date: End date
            limit: Maximum number of articles
            
        Returns:
            List of news articles with sentiment scores
        """
        try:
            if not self.api_key:
                self.logger.warning("Marketaux API key not configured")
                return []
            
            if not start_date:
                start_date = datetime.now() - timedelta(days=7)
            if not end_date:
                end_date = datetime.now()
            
            self.logger.info(f"Fetching news from {start_date} to {end_date}")
            
            # Build query parameters
            params = {
                'api_token': self.api_key,
                'published_after': start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'published_before': end_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'limit': limit,
                'language': 'en'
            }
            
            # Add symbol filter if provided
            if symbol:
                # Map Indian symbols to Marketaux format
                # Marketaux uses ticker symbols without exchange suffix
                clean_symbol = symbol.replace('.NS', '').replace('.BSE', '').upper()
                params['symbols_in'] = clean_symbol
            
            response = requests.get(
                f"{self.base_url}/news/all",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('data', [])
            
            news_list = []
            for article in articles:
                # Extract sentiment data
                sentiment_score = article.get('sentiment_score')
                
                # Convert sentiment score to label
                if sentiment_score is not None:
                    if sentiment_score >= 0.1:
                        sentiment_label = 'POSITIVE'
                    elif sentiment_score <= -0.1:
                        sentiment_label = 'NEGATIVE'
                    else:
                        sentiment_label = 'NEUTRAL'
                else:
                    sentiment_label = None
                
                published_at_str = article.get('published_at', '')
                try:
                    if published_at_str.endswith('Z'):
                        published_at = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
                    else:
                        published_at = datetime.strptime(published_at_str, '%Y-%m-%dT%H:%M:%S.%f')
                except (ValueError, TypeError):
                    published_at = datetime.now()
                
                news_list.append({
                    'headline': article.get('title', ''),
                    'source': article.get('author', article.get('source', '')),
                    'published_at': published_at,
                    'sentiment_score': float(sentiment_score) if sentiment_score is not None else None,
                    'sentiment_label': sentiment_label,
                    'url': article.get('url', ''),
                    'symbol': symbol  # Marketaux returns general news, symbol is filtered client-side
                })
            
            self.logger.info(f"Fetched {len(news_list)} news articles with sentiment")
            return news_list
            
        except Exception as e:
            self.logger.error(f"Error fetching news from Marketaux: {str(e)}")
            return []
    
    def fetch_sentiment_summary(
        self,
        symbol: str,
        days: int = 7
    ) -> Optional[Dict[str, Any]]:
        """
        Get sentiment summary for a symbol over the last N days.
        
        Args:
            symbol: Stock symbol
            days: Number of days to look back
            
        Returns:
            Sentiment summary statistics
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            articles = self.fetch_news(symbol=symbol, start_date=start_date, limit=100)
            
            if not articles:
                return None
            
            # Calculate sentiment statistics
            scores = [a['sentiment_score'] for a in articles if a['sentiment_score'] is not None]
            
            if not scores:
                return {
                    'symbol': symbol,
                    'days': days,
                    'article_count': len(articles),
                    'avg_sentiment': None,
                    'positive_count': 0,
                    'negative_count': 0,
                    'neutral_count': 0
                }
            
            return {
                'symbol': symbol,
                'days': days,
                'article_count': len(articles),
                'avg_sentiment': sum(scores) / len(scores),
                'min_sentiment': min(scores),
                'max_sentiment': max(scores),
                'positive_count': sum(1 for s in scores if s > 0.1),
                'negative_count': sum(1 for s in scores if s < -0.1),
                'neutral_count': sum(1 for s in scores if -0.1 <= s <= 0.1)
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching sentiment summary: {str(e)}")
            return None