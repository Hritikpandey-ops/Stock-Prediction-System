"""
Yahoo Finance data fetcher using yfinance library.
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
import yfinance as yf
import pandas as pd
from loguru import logger

from src.data_ingestion.base import BaseDataFetcher


class YahooFinanceFetcher(BaseDataFetcher):
    """Fetcher for price and fundamental data from Yahoo Finance."""
    
    def __init__(self, rate_limit: int = 60):
        """Initialize Yahoo Finance fetcher."""
        super().__init__(rate_limit=rate_limit)
        self.logger = logger
    
    def fetch_prices(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Fetch historical OHLCV data from Yahoo Finance.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.NS', '^NSEI')
            start_date: Start date
            end_date: End date
            
        Returns:
            List of price records
        """
        try:
            symbol = self.sanitize_symbol(symbol)
            self.logger.info(f"Fetching prices for {symbol} from {start_date} to {end_date}")
            
            # Download data
            ticker = yf.Ticker(symbol)
            df = ticker.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1d'
            )
            
            if df.empty:
                self.logger.warning(f"No data found for {symbol}")
                return []
            
            # Reset index to get timestamp as column
            df = df.reset_index()
            
            # Convert to list of dictionaries
            records = []
            for _, row in df.iterrows():
                record = {
                    'timestamp': row['Date'],
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume']),
                    'vwap': float(row.get('Close', row['Close']))  # Yahoo doesn't provide VWAP directly
                }
                records.append(record)
            
            self.logger.info(f"Fetched {len(records)} records for {symbol}")
            return records
            
        except Exception as e:
            self.logger.error(f"Error fetching prices for {symbol}: {str(e)}")
            return []
    
    def fetch_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch fundamental data from Yahoo Finance.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary of fundamental data
        """
        try:
            symbol = self.sanitize_symbol(symbol)
            self.logger.info(f"Fetching fundamentals for {symbol}")
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Extract key fundamentals
            fundamentals = {
                'symbol': symbol,
                'pe_ratio': info.get('trailingPE'),
                'pb_ratio': info.get('priceToBook'),
                'eps': info.get('trailingEps'),
                'roe': info.get('returnOnEquity') * 100 if info.get('returnOnEquity') else None,
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'profit_margin': info.get('profitMargins') * 100 if info.get('profitMargins') else None,
                'market_cap': info.get('marketCap'),
                'shares_outstanding': info.get('sharesOutstanding'),
                'revenue_growth': info.get('revenueGrowth') * 100 if info.get('revenueGrowth') else None
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
        Yahoo Finance doesn't provide news API, return empty list.
        Use Marketaux or Finnhub for news data.
        """
        self.logger.info("Yahoo Finance doesn't provide news data. Use Marketaux or Finnhub.")
        return []
    
    def get_available_symbols(self) -> List[str]:
        """
        Get a list of popular Indian stock symbols.
        
        Returns:
            List of NSE/BSE symbols
        """
        nifty50_symbols = [
            "^NSEI",
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
            "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS",
            "LT.NS", "HCLTECH.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS",
            "SUNPHARMA.NS", "TITAN.NS", "BAJFINANCE.NS", "WIPRO.NS", "ULTRACEMCO.NS",
            "TATAMOTORS.NS", "TATASTEEL.NS", "ADANIENT.NS", "ADANIPORTS.NS", "NESTLEIND.NS",
            "BAJAJFINSV.NS", "TATACONSUM.NS", "DRREDDY.NS", "CIPLA.NS", "ONGC.NS",
            "NTPC.NS", "POWERGRID.NS", "JSWSTEEL.NS", "COALINDIA.NS", "M&M.NS",
            "EICHERMOT.NS", "GRASIM.NS", "BRITANNIA.NS", "APOLLOHOSP.NS", "SHRIRAMFIN.NS",
            "HINDALCO.NS", "SBILIFE.NS", "HDFCLIFE.NS", "AXISBANK.NS", "INDUSINDBK.NS",
            "ITC.NS", "TCS.NS", "RELIANCE.NS", "HDFCBANK.NS"
        ]
        return nifty50_symbols
    
    def download_multiple_symbols(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Download data for multiple symbols efficiently.
        
        Args:
            symbols: List of stock symbols
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary mapping symbols to their price data
        """
        results = {}
        
        for symbol in symbols:
            try:
                data = self.fetch_prices(symbol, start_date, end_date)
                results[symbol] = data
            except Exception as e:
                self.logger.error(f"Failed to fetch {symbol}: {e}")
                results[symbol] = []
        
        return results