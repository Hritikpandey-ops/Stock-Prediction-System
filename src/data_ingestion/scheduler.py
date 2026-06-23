"""
Data ingestion scheduler and orchestrator.
"""
from typing import List, Optional, Set
from datetime import datetime, timedelta
from loguru import logger

from src.data_ingestion.yahoo_finance import YahooFinanceFetcher
from src.data_ingestion.finnhub import FinnhubFetcher
from src.data_ingestion.marketaux import MarketauxFetcher
from src.database.repository import PriceRepository, FundamentalRepository, NewsSentimentRepository
from src.features.sentiment import SentimentFeatureEngineer
from config.database import get_db


class DataIngestionScheduler:
    """Orchestrates data ingestion from multiple sources."""
    
    def __init__(self):
        """Initialize data fetchers."""
        self.yfinance = YahooFinanceFetcher()
        self.finnhub = FinnhubFetcher()
        self.marketaux = MarketauxFetcher()
        self.sentiment_engineer = SentimentFeatureEngineer()
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
                        'net_profit_margin': data.get('profit_margin'),
                        'market_cap': data.get('market_cap'),
                        'shares_outstanding': data.get('shares_outstanding'),
                        'revenue_growth_1y': data.get('revenue_growth')
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
        Uses Marketaux first (built-in sentiment), falls back to Finnhub + VADER.

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
            'total_articles': 0,
            'by_source': {'marketaux': 0, 'finnhub': 0}
        }

        seen_urls: Set[str] = set()

        with next(get_db()) as db:
            news_repo = NewsSentimentRepository(db)

            for symbol in symbols:
                # Clean symbol for different APIs
                clean_symbol = symbol.replace('.NS', '').replace('.BSE', '').upper()
                finnhub_symbol = f"NSE:{clean_symbol}" if not symbol.startswith(('NSE:', 'BSE:')) else symbol
                
                self.logger.info(f"Processing news for {symbol} (clean: {clean_symbol}, finnhub: {finnhub_symbol})")
                
                articles = []

                # Try Marketaux first
                marketaux_articles = self.marketaux.fetch_news(
                    symbol=clean_symbol, start_date=start_date
                )
                if marketaux_articles:
                    articles.extend(marketaux_articles)
                    results['by_source']['marketaux'] += len(marketaux_articles)
                    self.logger.debug(f"Marketaux returned {len(marketaux_articles)} articles for {clean_symbol}")

                if not articles:
                    # Try Finnhub company-specific news first
                    finnhub_articles = self.finnhub.fetch_news(
                        symbol=finnhub_symbol, start_date=start_date
                    )
                    if finnhub_articles:
                        for art in finnhub_articles:
                            if art.get('sentiment_score') is None:
                                sentiment = self.sentiment_engineer.calculate_sentiment_score(art['headline'])
                                art['sentiment_score'] = sentiment['compound']
                                if sentiment['compound'] >= 0.05:
                                    art['sentiment_label'] = 'POSITIVE'
                                elif sentiment['compound'] <= -0.05:
                                    art['sentiment_label'] = 'NEGATIVE'
                                else:
                                    art['sentiment_label'] = 'NEUTRAL'
                            art['symbol'] = clean_symbol  # Assign symbol to article
                        articles.extend(finnhub_articles)
                        results['by_source']['finnhub'] += len(finnhub_articles)
                        self.logger.debug(f"Finnhub returned {len(finnhub_articles)} articles for {clean_symbol}")
                    
                    # Fall back to general news if no company-specific news
                    if not articles:
                        general_news = self.finnhub.fetch_news(symbol=None, start_date=start_date)
                        if general_news:
                            # Assign general news to this symbol
                            for art in general_news:
                                sentiment = self.sentiment_engineer.calculate_sentiment_score(art['headline'])
                                art['sentiment_score'] = sentiment['compound']
                                if sentiment['compound'] >= 0.05:
                                    art['sentiment_label'] = 'POSITIVE'
                                elif sentiment['compound'] <= -0.05:
                                    art['sentiment_label'] = 'NEGATIVE'
                                else:
                                    art['sentiment_label'] = 'NEUTRAL'
                                art['symbol'] = clean_symbol  # Assign symbol to article
                            
                            # Distribute general news across all symbols to avoid duplication
                            articles_to_assign = []
                            for i, art in enumerate(general_news):
                                # Assign each article to a different symbol in round-robin fashion
                                assigned_symbol = symbols[i % len(symbols)].replace('.NS', '').replace('.BSE', '').upper()
                                art_copy = art.copy()
                                art_copy['symbol'] = assigned_symbol
                                articles_to_assign.append(art_copy)
                            
                            articles.extend(articles_to_assign)
                            results['by_source']['finnhub'] += len(articles_to_assign)
                            self.logger.debug(f"Finnhub general returned {len(articles_to_assign)} articles distributed across symbols")

                stored = 0
                for article in articles:
                    if not article.get('url') or article.get('url') in seen_urls:
                        continue
                    seen_urls.add(article.get('url'))
                    try:
                        news_repo.create({
                            'symbol': clean_symbol,
                            'headline': article['headline'][:500],  # Limit headline length
                            'source': article['source'][:100],     # Limit source length
                            'published_at': article['published_at'],
                            'sentiment_score': article.get('sentiment_score'),
                            'sentiment_label': article.get('sentiment_label'),
                            'url': article['url'][:500]           # Limit URL length
                        })
                        stored += 1
                    except Exception as e:
                        self.logger.warning(f"Skipping article due to error: {e}")
                        self.logger.debug(f"Article data: {article}")

                results['total_articles'] += stored
                self.logger.info(f"Stored {stored} news articles for {clean_symbol}")

        self.logger.info(
            f"News ingestion complete: {results['total_articles']} articles stored "
            f"(Marketaux: {results['by_source']['marketaux']}, Finnhub: {results['by_source']['finnhub']})"
        )

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
    
    def fetch_and_store_prices_for_today(
        self,
        symbols: List[str]
    ) -> dict:
        """
        Fetch and store today's price data for multiple symbols.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Summary of ingestion results
        """
        from datetime import datetime, timedelta
        
        # Get today's date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)  # Last 1 day
        
        return self.fetch_and_store_prices(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            use_finnhub=False
        )
    
    def fetch_and_store_fundamentals_for_all(
        self,
        symbols: List[str]
    ) -> dict:
        """
        Fetch and store fundamental data for all symbols.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Summary of ingestion results
        """
        return self.fetch_and_store_fundamentals(symbols)