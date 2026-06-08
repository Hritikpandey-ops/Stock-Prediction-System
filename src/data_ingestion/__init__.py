"""
Data ingestion module initialization.
"""
from src.data_ingestion.base import BaseDataFetcher
from src.data_ingestion.yahoo_finance import YahooFinanceFetcher
from src.data_ingestion.finnhub import FinnhubFetcher
from src.data_ingestion.marketaux import MarketauxFetcher

__all__ = [
    "BaseDataFetcher",
    "YahooFinanceFetcher",
    "FinnhubFetcher",
    "MarketauxFetcher",
]