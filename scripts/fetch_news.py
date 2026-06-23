#!/usr/bin/env python3
"""
CLI script to fetch news for Nifty 50 symbols.
Usage: python scripts/fetch_news.py [--symbols RELIANCE,TCS] [--days 7]
"""
import argparse
from loguru import logger

from src.data_ingestion.scheduler import DataIngestionScheduler

NIFTY50_SYMBOLS = [
    'RELIANCE', 'TCS', 'HDFCBANK', 'ICICIBANK', 'INFY', 'HINDUNILVR', 'ITC', 'SBIN',
    'BHARTIARTL', 'LT', 'KOTAKBANK', 'HCLTECH', 'AXISBANK', 'ASIANPAINT', 'MARUTI',
    'SUNPHARMA', 'TITAN', 'BAJFINANCE', 'WIPRO', 'ADANIENT', 'ADANIPORTS', 'APOLLOHOSP',
    'BAJAJ-AUTO', 'BAJAJFINSV', 'BPCL', 'BRITANNIA', 'CIPLA', 'COALINDIA', 'DIVISLAB',
    'DRREDDY', 'EICHERMOT', 'GRASIM', 'HDFCLIFE', 'HEROMOTOCO', 'HINDALCO', 'INDUSINDBK',
    'JSWSTEEL', 'M&M', 'NESTLEIND', 'NTPC', 'ONGC', 'POWERGRID', 'SBILIFE', 'SHRIRAMFIN',
    'TATACONSUM', 'TATAMOTORS', 'TATASTEEL', 'TECHM', 'TRENT', 'ULTRACEMCO'
]


def main():
    parser = argparse.ArgumentParser(description='Fetch news for Nifty 50 symbols')
    parser.add_argument(
        '--symbols',
        type=str,
        default=None,
        help='Comma-separated symbols (default: all Nifty 50)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days of news to fetch (default: 7)'
    )
    args = parser.parse_args()

    symbols = NIFTY50_SYMBOLS
    if args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(',')]

    logger.info(f"Fetching news for {len(symbols)} symbols (last {args.days} days)")

    scheduler = DataIngestionScheduler()
    results = scheduler.fetch_and_store_news(symbols, days=args.days)

    logger.info(f"Done: {results['total_articles']} articles stored")
    logger.info(f"  Marketaux: {results['by_source']['marketaux']}")
    logger.info(f"  Finnhub:   {results['by_source']['finnhub']}")


if __name__ == '__main__':
    main()