"""
Data ingestion scheduler and orchestrator.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from loguru import logger

from src.data_ingestion.yahoo_finance import YahooFinanceFetcher
from src.data_ingestion.finnhub import FinnhubFetcher
from src.data_ingestion.marketaux import MarketauxFetcher
from src.database.repository import PriceRepository, FundamentalRepository, NewsSentimentRepository
from config.database import get_db


class DataIngestionScheduler:
    """Orchestrates data ingestion from multiple sources."""
    
    def __init__(self):
        """Initialize data fetchers."""
        self.yfinance = YahooFinanceFetcher()
        self.finnhub = FinnhubFetcher()
        self.marketaux = MarketauxFetcher()
        self.logger = logger
    
    def fetch_and_store_prices(
        self,
        symbols: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        use_finnhub: bool = False
    ) -> dict:
        """
        Fetch and store price data for multiple symbols.
        
        Args:
            symbols: List of stock symbols
            start_date: Start date (default: 1 year ago)
            end_date: End date (default: today)
            use_finnhub: Use Finnhub instead of Yahoo Finance
            
        Returns:
            Summary of ingestion results
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=365)
        if not end_date:
            end_date = datetime.now()
        
        self.logger.info(f"Starting price data ingestion for {len(symbols)} symbols")
        
        fetcher = self.finnhub if use_finnhub else self.yfinance
        
        results = {
            'total': len(symbols),
            'successful': 0,
            'failed': 0,
            'total_records': 0,
            'failed_symbols': []
        }
        
        with next(get_db()) as db:
            price_repo = PriceRepository(db)
            
            for symbol in symbols:
                try:
                    # Fetch data
                    data = fetcher.fetch_prices(symbol, start_date, end_date)
                    
                    if not data:
                        results['failed'] += 1
                        results['failed_symbols'].append(symbol)
                        continue
                    
                    # Store in database
                    for record in data:
                        price_repo.upsert_price(
                            symbol=symbol,
                            timestamp=record['timestamp'],
                            open=record['open'],
                            high=record['high'],
                            low=record['low'],
                            close=record['close'],
                            volume=record['volume'],
                            vwap=record.get('vwap')
                        )
                    
                    results['successful'] += 1
                    results['total_records'] += len(data)
                    
                    self.logger.info(f"Stored {len(data)} records for {symbol}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to process {symbol}: {str(e)}")
                    results['failed'] += 1
                    results['failed_symbols'].append(symbol)
        
        self.logger.info(
            f"Price ingestion complete: {results['successful']}/{results['total']} successful, "
            f"{results['total_records']} total records"
        )
        
        return results
    
    def fetch_and_store_fundamentals(self, symbols: List[str]) -> dict:
        """
        Fetch and store fundamental data for multiple symbols.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Summary of ingestion results
        """
        self.logger.info(f"Starting fundamentals ingestion for {len(symbols)} symbols")
        
        results = {
            'total': len(symbols),
            'successful': 0,
            'failed': 0
        }
        
        with next(get_db()) as db:
            fund_repo = FundamentalRepository(db)
            
            for symbol in symbols:
                try:
                    # Fetch data
                    data = self.yfinance.fetch_fundamentals(symbol)
                    
                    if not data:
                        results['failed'] += 1
                        continue
                    
                    # Store in database
                    fund_repo.create({
                        'symbol': data['symbol'],
                        'report_date': datetime.now(),
                        'period_type': 'ANNUAL',
                        'pe_ratio': data.get('pe_ratio'),
                        'pb_ratio': data.get('pb_ratio'),
                        'eps': data.get('eps'),
                        'roe': data.get('roe'),
                        'debt_to_equity': data.get('debt_to_equity'),
                        'current_ratio': data.get('current_ratio'),
                        'profit_margin': data.get('profit_margin'),
                        'market_cap': data.get('market_cap'),
                        'shares_outstanding': data.get('shares_outstanding'),
                        'revenue_growth': data.get('revenue_growth')
                    })
                    
                    results['successful'] += 1
                    
                except Exception as e:
                    self.logger.error(f"Failed to process fundamentals for {symbol}: {str(e)}")
                    results['failed'] += 1
        
        self.logger.info(
            f"Fundamentals ingestion complete: {results['successful']}/{results['total']} successful"
        )
        
        return results
    
    def fetch_and_store_news(
        self,
        symbols: List[str],
        days: int = 7
    ) -> dict:
        """
        Fetch and store news sentiment for multiple symbols.
        
        Args:
            symbols: List of stock symbols
            days: Number of days of news to fetch
            
        Returns:
            Summary of ingestion results
        """
        start_date = datetime.now() - timedelta(days=days)
        
        self.logger.info(f"Starting news ingestion for {len(symbols)} symbols")
        
        results = {
            'total_symbols': len(symbols),
            'total_articles': 0
        }
        
        with next(get_db()) as db:
            news_repo = NewsSentimentRepository(db)
            
            for symbol in symbols:
                try:
                    # Fetch news
                    articles = self.marketaux.fetch_news(symbol=symbol, start_date=start_date)
                    
                    for article in articles:
                        news_repo.create(
                            symbol=symbol,
                            headline=article['headline'],
                            source=article['source'],
                            published_at=article['published_at'],
                            sentiment_score=article.get('sentiment_score'),
                            sentiment_label=article.get('sentiment_label'),
                            url=article['url']
                        )
                    
                    results['total_articles'] += len(articles)
                    self.logger.info(f"Stored {len(articles)} news articles for {symbol}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to process news for {symbol}: {str(e)}")
        
        self.logger.info(f"News ingestion complete: {results['total_articles']} articles stored")
        
        return results
    
    def full_ingestion(
        self,
        symbols: List[str],
        include_news: bool = True
    ) -> dict:
        """
        Run complete data ingestion pipeline.
        
        Args:
            symbols: List of stock symbols
            include_news: Whether to fetch news data
            
        Returns:
            Complete ingestion summary
        """
        self.logger.info("Starting full data ingestion pipeline")
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'symbols_count': len(symbols),
            'prices': None,
            'fundamentals': None,
            'news': None
        }
        
        # Fetch prices
        summary['prices'] = self.fetch_and_store_prices(symbols)
        
        # Fetch fundamentals
        summary['fundamentals'] = self.fetch_and_store_fundamentals(symbols)
        
        # Fetch news if requested
        if include_news:
            summary['news'] = self.fetch_and_store_news(symbols)
        
        self.logger.info("Full data ingestion pipeline complete")
        
        return summary