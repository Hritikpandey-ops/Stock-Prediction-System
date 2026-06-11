"""
Comprehensive Fundamental Data Fetcher
Fetches detailed fundamental data for Nifty 50 stocks using yfinance
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import logging

from config.database import SessionLocal
from src.database.models import Fundamental
from sqlalchemy.dialects.postgresql import insert

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FundamentalFetcher:
    def __init__(self):
        self.session = SessionLocal()
        
    def get_nifty50_symbols(self):
        return [
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'INFY.NS',
            'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'LT.NS',
            'AXISBANK.NS', 'KOTAKBANK.NS', 'ASIANPAINT.NS', 'HDFC.NS', 'BAJFINANCE.NS',
            'Titan.NS', 'ULTRACEMCO.NS', 'SUNPHARMA.NS', 'LARSEN.NS', 'ONGC.NS',
            'NTPC.NS', 'POWERGRID.NS', 'GAIL.NS', 'COALINDIA.NS', 'IOC.NS',
            'MARUTI.NS', 'TATAMOTORS.NS', 'M&M.NS', 'EicherMOTORS.NS', 'Bajaj_AUTO.NS',
            'HeroMOTCOP.NS', 'TATASTEEL.NS', 'JSWSTEEL.NS', 'HINDALCO.NS', 'SAIL.NS',
            'ADANIPORTS.NS', 'GRASIM.NS', 'INDUSINDBK.NS', 'HDFCLIFE.NS', 'SBILIFE.NS',
            'DivisLAB.NS', 'DRREDDY.NS', 'APOLLOHOSP.NS', 'COFORGE.NS', 'PERSISTENT.NS',
            'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS', 'GENUSPOWER.NS'
        ]
    
    def safe_get(self, ticker, key, default=None):
        try:
            value = ticker.info.get(key)
            return value if value is not None else default
        except:
            return default
    
    def fetch_fundamentals(self, symbol):
        try:
            logger.info(f"Fetching fundamentals for {symbol}")
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            report_date = datetime.now()
            
            fundamentals = {
                'symbol': symbol.replace('.NS', ''),
                'report_date': report_date,
                'period_type': 'quarterly',
                
                'company_name': self.safe_get(ticker, 'longName', 'N/A'),
                'sector': self.safe_get(ticker, 'sector', 'N/A'),
                'industry': self.safe_get(ticker, 'industry', 'N/A'),
                
                'current_price': self.safe_get(ticker, 'currentPrice'),
                'market_cap': self.safe_get(ticker, 'marketCap'),
                'fifty_two_week_high': self.safe_get(ticker, 'fiftyTwoWeekHigh'),
                'fifty_two_week_low': self.safe_get(ticker, 'fiftyTwoWeekLow'),
                'dividend_yield': self.safe_get(ticker, 'dividendYield', 0) * 100 if self.safe_get(ticker, 'dividendYield') else None,
                'shares_outstanding': self.safe_get(ticker, 'sharesOutstanding'),
                
                'pe_ratio': self.safe_get(ticker, 'trailingPE'),
                'pb_ratio': self.safe_get(ticker, 'priceToBook'),
                'peg_ratio': self.safe_get(ticker, 'pegRatio'),
                'ev_ebitda': self.safe_get(ticker, 'enterpriseToEbitda'),
                'industry_pe': self.safe_get(ticker, 'industryPE'),
                
                'eps': self.safe_get(ticker, 'trailingEps'),
                'roe': self.safe_get(ticker, 'returnOnEquity') * 100 if self.safe_get(ticker, 'returnOnEquity') else None,
                'roce': self.safe_get(ticker, 'returnOnCapitalUsed') * 100 if self.safe_get(ticker, 'returnOnCapitalUsed') else None,
                'net_profit_margin': self.safe_get(ticker, 'profitMargins') * 100 if self.safe_get(ticker, 'profitMargins') else None,
                'operating_margin': self.safe_get(ticker, 'operatingMargins') * 100 if self.safe_get(ticker, 'operatingMargins') else None,
                'ebitda': self.safe_get(ticker, 'ebitda'),
                
                'revenue': self.safe_get(ticker, 'totalRevenue'),
                'revenue_growth_1y': self.safe_get(ticker, 'revenueGrowth'),
                'net_profit': self.safe_get(ticker, 'netIncomeToCommon'),
                
                'total_debt': self.safe_get(ticker, 'totalDebt'),
                'debt_to_equity': self.safe_get(ticker, 'debtToEquity'),
                'interest_coverage': self.safe_get(ticker, 'interestCoverage'),
                
                'current_assets': self.safe_get(ticker, 'totalCurrentAssets'),
                'current_liabilities': self.safe_get(ticker, 'totalCurrentLiabilities'),
                'current_ratio': self.safe_get(ticker, 'currentRatio'),
                'cash_and_equivalents': self.safe_get(ticker, 'cashAndCashEquivalents'),
                'free_cash_flow': self.safe_get(ticker, 'freeCashflow'),
                'operating_cash_flow': self.safe_get(ticker, 'operatingCashflow'),
                
                'promoter_holding': self.safe_get(ticker, 'sharedHeld') * 100 if self.safe_get(ticker, 'sharedHeld') else None,
                'public_holding': (1 - self.safe_get(ticker, 'sharedHeld', 1)) * 100 if self.safe_get(ticker, 'sharedHeld') else None,
            }
            
            try:
                major_holders = ticker.major_holders
                if major_holders is not None and len(major_holders) > 0:
                    if len(major_holders) > 0:
                        fundamentals['promoter_holding'] = float(major_holders.iloc[0, 1]) if pd.notna(major_holders.iloc[0, 1]) else fundamentals.get('promoter_holding')
                    if len(major_holders) > 1:
                        fundamentals['institutional_holding'] = float(major_holders.iloc[1, 1]) if pd.notna(major_holders.iloc[1, 1]) else None
            except Exception as e:
                logger.warning(f"Could not fetch major holders for {symbol}: {e}")
            
            try:
                institutional_holders = ticker.institutional_holders
                if institutional_holders is not None and len(institutional_holders) > 0:
                    total_fii = institutional_holders['Shares'].sum() if 'Shares' in institutional_holders.columns else 0
                    if fundamentals.get('shares_outstanding'):
                        fundamentals['fii_holding'] = (total_fii / fundamentals['shares_outstanding']) * 100
            except Exception as e:
                logger.warning(f"Could not fetch institutional holders for {symbol}: {e}")
            
            return fundamentals
            
        except Exception as e:
            logger.error(f"Error fetching fundamentals for {symbol}: {e}")
            return None
    
    def calculate_growth_rates(self, ticker, symbol):
        try:
            financials = ticker.financials
            if financials is None or financials.empty:
                return {}
            
            growth_rates = {}
            
            if 'Total Revenue' in financials.index:
                revenues = financials.loc['Total Revenue'].values
                if len(revenues) >= 4:
                    growth_rates['revenue_growth_1y'] = ((revenues[0] - revenues[1]) / revenues[1] * 100) if revenues[1] != 0 else None
                    if len(revenues) >= 4:
                        cagr_3y = ((revenues[0] / revenues[3]) ** (1/3) - 1) * 100 if revenues[3] != 0 else None
                        growth_rates['revenue_growth_3y'] = cagr_3y
                    if len(revenues) >= 5:
                        cagr_5y = ((revenues[0] / revenues[4]) ** (1/5) - 1) * 100 if revenues[4] != 0 else None
                        growth_rates['revenue_growth_5y'] = cagr_5y
            
            if 'Net Income' in financials.index:
                profits = financials.loc['Net Income'].values
                if len(profits) >= 2:
                    growth_rates['profit_growth_1y'] = ((profits[0] - profits[1]) / profits[1] * 100) if profits[1] != 0 else None
                if len(profits) >= 4:
                    cagr_3y = ((profits[0] / profits[3]) ** (1/3) - 1) * 100 if profits[3] != 0 else None
                    growth_rates['profit_growth_3y'] = cagr_3y
                if len(profits) >= 5:
                    cagr_5y = ((profits[0] / profits[4]) ** (1/5) - 1) * 100 if profits[4] != 0 else None
                    growth_rates['profit_growth_5y'] = cagr_5y
            
            return growth_rates
            
        except Exception as e:
            logger.warning(f"Could not calculate growth rates for {symbol}: {e}")
            return {}
    
    def save_to_database(self, fundamentals):
        if not fundamentals:
            return False
        
        try:
            stmt = insert(Fundamental).values(**fundamentals)
            stmt = stmt.on_conflict_do_update(
                constraint='uq_symbol_report_period',
                set_={k: v for k, v in fundamentals.items() if k not in ['symbol', 'report_date', 'period_type']}
            )
            self.session.execute(stmt)
            self.session.commit()
            logger.info(f"Saved fundamentals for {fundamentals['symbol']}")
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error saving fundamentals for {fundamentals.get('symbol')}: {e}")
            return False
    
    def fetch_all(self, limit=None):
        symbols = self.get_nifty50_symbols()[:limit] if limit else self.get_nifty50_symbols()
        
        logger.info(f"Fetching fundamentals for {len(symbols)} stocks...")
        
        for i, symbol in enumerate(symbols):
            logger.info(f"Processing {i+1}/{len(symbols)}: {symbol}")
            
            fundamentals = self.fetch_fundamentals(symbol)
            
            if fundamentals:
                try:
                    ticker = yf.Ticker(symbol)
                    growth_rates = self.calculate_growth_rates(ticker, symbol)
                    fundamentals.update(growth_rates)
                except Exception as e:
                    logger.warning(f"Could not calculate growth rates: {e}")
                
                self.save_to_database(fundamentals)
            else:
                logger.warning(f"Skipping {symbol} - no data retrieved")
            
            if (i + 1) % 5 == 0:
                logger.info(f"Processed {i+1}/{len(symbols)} stocks")
            
            time.sleep(0.5)
        
        logger.info("Fundamental data fetching complete!")


def main():
    fetcher = FundamentalFetcher()
    fetcher.fetch_all()


if __name__ == "__main__":
    main()