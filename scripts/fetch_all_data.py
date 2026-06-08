#!/usr/bin/env python3
"""
CLI script to fetch all data for specified symbols.
"""
import argparse
from datetime import datetime, timedelta
from loguru import logger

from src.data_ingestion.scheduler import DataIngestionScheduler
from config.settings import get_settings

settings = get_settings()


def main():
    parser = argparse.ArgumentParser(description='Fetch stock data')
    parser.add_argument(
        '--symbols',
        type=str,
        default='^NSEI,RELIANCE.NS,TCS.NS,HDFCBANK.NS,INFY.NS',
        help='Comma-separated list of symbols (default: Nifty 50 + top stocks)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=365,
        help='Number of days of historical data (default: 365)'
    )
    parser.add_argument(
        '--include-news',
        action='store_true',
        default=True,
        help='Include news sentiment data'
    )
    parser.add_argument(
        '--no-news',
        action='store_true',
        help='Disable news sentiment data'
    )
    
    args = parser.parse_args()
    
    # Parse symbols
    symbols = [s.strip() for s in args.symbols.split(',')]
    
    # Set date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days)
    
    logger.info(f"Fetching data for {len(symbols)} symbols from {start_date.date()} to {end_date.date()}")
    logger.info(f"Symbols: {', '.join(symbols)}")
    
    # Create scheduler
    scheduler = DataIngestionScheduler()
    
    # Run ingestion
    summary = scheduler.full_ingestion(
        symbols=symbols,
        include_news=args.include_news and not args.no_news
    )
    
    # Print summary
    print("\n" + "="*60)
    print("DATA INGESTION SUMMARY")
    print("="*60)
    print(f"Timestamp: {summary['timestamp']}")
    print(f"Symbols processed: {summary['symbols_count']}")
    print(f"\nPrices:")
    print(f"  - Successful: {summary['prices']['successful']}/{summary['prices']['total']}")
    print(f"  - Total records: {summary['prices']['total_records']}")
    if summary['prices']['failed_symbols']:
        print(f"  - Failed: {', '.join(summary['prices']['failed_symbols'])}")
    
    print(f"\nFundamentals:")
    print(f"  - Successful: {summary['fundamentals']['successful']}/{summary['fundamentals']['total']}")
    
    if summary['news']:
        print(f"\nNews:")
        print(f"  - Total articles: {summary['news']['total_articles']}")
    
    print("="*60)
    print("Data ingestion complete!")
    print("="*60)


if __name__ == '__main__':
    main()