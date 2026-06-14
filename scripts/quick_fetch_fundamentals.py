"""
Quick Fundamentals Fetcher
Fetches data for a small set of stocks for testing
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

import yfinance as yf
import logging
from datetime import datetime

from config.database import SessionLocal
from src.database.models import Fundamental
from sqlalchemy.dialects.postgresql import insert

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_fundamentals(symbol):
    try:
        logger.info(f"Fetching {symbol}")
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        fundamentals = {
            'symbol': symbol.replace('.NS', ''),
            'report_date': datetime.now(),
            'period_type': 'quarterly',
            
            'company_name': info.get('longName', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            
            'current_price': info.get('currentPrice') or info.get('regularMarketPrice'),
            'market_cap': info.get('marketCap'),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
            'dividend_yield': (info.get('dividendYield', 0) or 0) * 100,
            'shares_outstanding': info.get('sharesOutstanding'),
            
            'pe_ratio': info.get('trailingPE'),
            'pb_ratio': info.get('priceToBook'),
            'peg_ratio': info.get('pegRatio'),
            'ev_ebitda': info.get('enterpriseToEbitda'),
            'industry_pe': info.get('industryPE'),
            
            'eps': info.get('trailingEps'),
            'roe': (info.get('returnOnEquity') or 0) * 100,
            'roce': (info.get('returnOnCapitalUsed') or 0) * 100,
            'net_profit_margin': (info.get('profitMargins') or 0) * 100,
            'operating_margin': (info.get('operatingMargins') or 0) * 100,
            'ebitda': info.get('ebitda'),
            
            'revenue': info.get('totalRevenue'),
            'revenue_growth_1y': (info.get('revenueGrowth') or 0) * 100,
            'net_profit': info.get('netIncomeToCommon'),
            
            'total_debt': info.get('totalDebt'),
            'debt_to_equity': info.get('debtToEquity'),
            'interest_coverage': info.get('interestCoverage'),
            
            'current_assets': info.get('totalCurrentAssets'),
            'current_liabilities': info.get('totalCurrentLiabilities'),
            'current_ratio': info.get('currentRatio'),
            'cash_and_equivalents': info.get('cashAndCashEquivalents'),
            'free_cash_flow': info.get('freeCashflow'),
            'operating_cash_flow': info.get('operatingCashflow'),
        }
        
        insider_pct = info.get('heldPercentInsiders') or info.get('sharedHeld')
        if insider_pct is not None:
            fundamentals['promoter_holding'] = round(float(insider_pct) * 100, 2)
            fundamentals['public_holding'] = round(100 - float(insider_pct) * 100, 2)
        else:
            fundamentals['promoter_holding'] = None
            fundamentals['public_holding'] = None
        
        inst_pct = info.get('heldPercentInstitutions')
        if inst_pct is not None:
            inst = float(inst_pct) * 100
            fundamentals['fii_holding'] = round(inst * 0.65, 2)
            fundamentals['dii_holding'] = round(inst * 0.35, 2)
        else:
            fundamentals['fii_holding'] = None
            fundamentals['dii_holding'] = None
        
        return fundamentals
        
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {e}")
        return None


def main():
    session = SessionLocal()
    
    test_symbols = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ITC.NS']
    
    logger.info("Fetching test fundamentals data...")
    
    for symbol in test_symbols:
        fundamentals = fetch_fundamentals(symbol)
        
        if fundamentals:
            try:
                stmt = insert(Fundamental).values(**fundamentals)
                stmt = stmt.on_conflict_do_update(
                    constraint='uq_symbol_report_period',
                    set_={k: v for k, v in fundamentals.items() 
                         if k not in ['symbol', 'report_date', 'period_type']}
                )
                session.execute(stmt)
                session.commit()
                logger.info(f"✓ Saved {symbol}")
            except Exception as e:
                session.rollback()
                logger.error(f"Error saving {symbol}: {e}")
        else:
            logger.warning(f"✗ No data for {symbol}")
    
    session.close()
    logger.info("Done!")


if __name__ == "__main__":
    main()