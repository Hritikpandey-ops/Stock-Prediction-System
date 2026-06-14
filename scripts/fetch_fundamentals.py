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
            'KOTAKBANK.NS', 'HCLTECH.NS', 'AXISBANK.NS', 'ASIANPAINT.NS', 'MARUTI.NS',
            'SUNPHARMA.NS', 'TITAN.NS', 'BAJFINANCE.NS', 'WIPRO.NS', 'ADANIENT.NS',
            'ADANIPORTS.NS', 'APOLLOHOSP.NS', 'BAJAJ-AUTO.NS', 'BAJAJFINSV.NS', 'BPCL.NS',
            'BRITANNIA.NS', 'CIPLA.NS', 'COALINDIA.NS', 'DIVISLAB.NS', 'DRREDDY.NS',
            'EICHERMOT.NS', 'GRASIM.NS', 'HDFCLIFE.NS', 'HEROMOTOCO.NS', 'HINDALCO.NS',
            'INDUSINDBK.NS', 'JSWSTEEL.NS', 'M&M.NS', 'NESTLEIND.NS', 'NTPC.NS',
            'ONGC.NS', 'POWERGRID.NS', 'SBILIFE.NS', 'SHRIRAMFIN.NS', 'TATACONSUM.NS',
            'TATAMOTORS.NS', 'TATASTEEL.NS', 'TECHM.NS', 'TRENT.NS', 'ULTRACEMCO.NS'
        ]
    
    def safe_get(self, ticker, key, default=None):
        try:
            value = ticker.info.get(key)
            return value if value is not None else default
        except:
            return default

    def get_financial_value(self, financials, row_names, col_idx=0):
        try:
            if financials is None or financials.empty:
                return None
            if isinstance(row_names, str):
                row_names = [row_names]
            for name in row_names:
                if name in financials.index:
                    vals = financials.loc[name].values
                    if len(vals) > col_idx and pd.notna(vals[col_idx]):
                        v = float(vals[col_idx])
                        return int(v) if v == v else None
                    break
            return None
        except:
            return None

    def get_any_financial(self, financials, col_idx=0):
        try:
            if financials is None or financials.empty:
                return None
            for col_name in financials.index:
                vals = financials.loc[col_name].values
                if len(vals) > col_idx and pd.notna(vals[col_idx]):
                    v = float(vals[col_idx])
                    if abs(v) > 1e6 and v == v:
                        return int(v)
            return None
        except:
            return None

    def get_cashflow_value(self, cashflow, row_names, col_idx=0):
        try:
            if cashflow is None or cashflow.empty:
                return None
            if isinstance(row_names, str):
                row_names = [row_names]
            for name in row_names:
                if name in cashflow.index:
                    vals = cashflow.loc[name].values
                    if len(vals) > col_idx and pd.notna(vals[col_idx]):
                        v = float(vals[col_idx])
                        return int(v) if v == v else None
                    break
            return None
        except:
            return None

    def get_eps_growth(self, financials):
        try:
            if financials is None or financials.empty:
                return {}
            eps_row = None
            for name in ['Diluted EPS', 'Basic EPS', 'EPS Diluted', 'EPS Basic']:
                if name in financials.index:
                    eps_row = name
                    break
            if eps_row is None:
                return {}
            vals = financials.loc[eps_row].values
            vals = [float(v) for v in vals if pd.notna(v) and abs(float(v)) > 0.001]
            if len(vals) < 2:
                return {}
            result = {}
            result['eps_growth_1y'] = round(((vals[0] - vals[1]) / abs(vals[1])) * 100, 2) if vals[1] != 0 else None
            if len(vals) >= 4:
                cagr = ((vals[0] / abs(vals[3])) ** (1/3) - 1) * 100 if vals[3] != 0 else None
                result['eps_growth_3y'] = round(cagr, 2) if cagr is not None else None
            if len(vals) >= 5:
                cagr = ((vals[0] / abs(vals[4])) ** (1/5) - 1) * 100 if vals[4] != 0 else None
                result['eps_growth_5y'] = round(cagr, 2) if cagr is not None else None
            return result
        except Exception as e:
            logger.warning(f"Could not calculate EPS growth: {e}")
            return {}
    
    def fetch_fundamentals(self, ticker):
        try:
            symbol = ticker.ticker
            logger.info(f"Fetching fundamentals for {symbol}")
            info = ticker.info
            
            report_date = datetime.now()
            
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            cashflow = ticker.cashflow
            
            fundamentals = {
                'symbol': symbol.replace('.NS', ''),
                'report_date': report_date,
                'period_type': 'quarterly',
                
                'company_name': self.safe_get(ticker, 'longName', 'N/A'),
                'sector': self.safe_get(ticker, 'sector', 'N/A'),
                'industry': self.safe_get(ticker, 'industry', 'N/A'),
                
                'current_price': self.safe_get(ticker, 'currentPrice') or self.safe_get(ticker, 'regularMarketPrice'),
                'market_cap': self.safe_get(ticker, 'marketCap'),
                'fifty_two_week_high': self.safe_get(ticker, 'fiftyTwoWeekHigh'),
                'fifty_two_week_low': self.safe_get(ticker, 'fiftyTwoWeekLow'),
                'dividend_yield': (self.safe_get(ticker, 'dividendYield') or 0) * 100 if self.safe_get(ticker, 'dividendYield') is not None else (info.get('dividendYield') or 0) * 100,
                'shares_outstanding': self.safe_get(ticker, 'sharesOutstanding'),
                
                'pe_ratio': self.safe_get(ticker, 'trailingPE') or self.safe_get(ticker, 'forwardPE'),
                'pb_ratio': self.safe_get(ticker, 'priceToBook'),
                'peg_ratio': self.safe_get(ticker, 'pegRatio'),
                'ev_ebitda': self.safe_get(ticker, 'enterpriseToEbitda'),
                'industry_pe': self.safe_get(ticker, 'industryPE'),
                
                'eps': self.safe_get(ticker, 'trailingEps') or self.get_financial_value(financials, 'Diluted EPS') or self.get_financial_value(financials, 'Basic EPS'),
                'roe': (self.safe_get(ticker, 'returnOnEquity') or 0) * 100 if self.safe_get(ticker, 'returnOnEquity') else None,
                'roce': (self.safe_get(ticker, 'returnOnCapitalUsed') or 0) * 100 if self.safe_get(ticker, 'returnOnCapitalUsed') else None,
                'net_profit_margin': (self.safe_get(ticker, 'profitMargins') or 0) * 100 if self.safe_get(ticker, 'profitMargins') else None,
                'operating_margin': (self.safe_get(ticker, 'operatingMargins') or 0) * 100 if self.safe_get(ticker, 'operatingMargins') else None,
                'ebitda': self.safe_get(ticker, 'ebitda') or self.get_financial_value(financials, 'EBITDA'),
                
                'revenue': self.safe_get(ticker, 'totalRevenue') or self.get_financial_value(financials, 'Total Revenue'),
                'revenue_growth_1y': None,
                'net_profit': self.safe_get(ticker, 'netIncomeToCommon') or self.get_financial_value(financials, 'Net Income'),
                
                'total_debt': self.safe_get(ticker, 'totalDebt') or self.get_financial_value(balance_sheet, 'Total Debt') or self.get_financial_value(balance_sheet, 'Long Term Debt'),
                'debt_to_equity': self.safe_get(ticker, 'debtToEquity'),
                'interest_coverage': self.safe_get(ticker, 'interestCoverage'),
                
                'current_assets': self.safe_get(ticker, 'totalCurrentAssets') or self.get_financial_value(balance_sheet, ['Current Assets', 'Total Current Assets', 'Current Assets Total', 'Current Assets (Quarterly)']),
                'current_liabilities': self.safe_get(ticker, 'totalCurrentLiabilities') or self.get_financial_value(balance_sheet, ['Current Liabilities', 'Total Current Liabilities', 'Current Liabilities Total', 'Current Liabilities (Quarterly)']),
                'current_ratio': self.safe_get(ticker, 'currentRatio'),
                'cash_and_equivalents': self.safe_get(ticker, 'cashAndCashEquivalents') or self.get_financial_value(balance_sheet, ['Cash And Cash Equivalents', 'Cash', 'Cash & Equivalents', 'Cash and Equivalents']),
                'free_cash_flow': self.safe_get(ticker, 'freeCashflow') or self.get_cashflow_value(cashflow, ['Free Cash Flow', 'Free Cashflow']),
                'operating_cash_flow': self.safe_get(ticker, 'operatingCashflow') or self.get_cashflow_value(cashflow, ['Operating Cash Flow', 'Total Cash From Operating Activities', 'Cash from Operating Activities']),
                
                'fii_holding': None,
                'dii_holding': None,
                'public_holding': None,
                'promoter_holding': None,
            }
            
            insider_held = info.get('heldPercentInsiders') or info.get('sharedHeld')
            if insider_held is not None:
                fundamentals['promoter_holding'] = round(float(insider_held) * 100, 2)
                fundamentals['public_holding'] = round(100 - float(insider_held) * 100, 2)
            
            inst_held = info.get('heldPercentInstitutions')
            if inst_held is not None:
                inst_pct = float(inst_held) * 100
                fundamentals['fii_holding'] = round(inst_pct * 0.65, 2)
                fundamentals['dii_holding'] = round(inst_pct * 0.35, 2)
            
            try:
                institutional_holders = ticker.institutional_holders
                if institutional_holders is not None and len(institutional_holders) > 0:
                    total_fii = institutional_holders['Shares'].sum() if 'Shares' in institutional_holders.columns else 0
                    if fundamentals.get('shares_outstanding') and total_fii > 0:
                        fii_pct = (total_fii / fundamentals['shares_outstanding']) * 100
                        fundamentals['fii_holding'] = round(fii_pct, 2)
            except Exception as e:
                logger.warning(f"Could not fetch institutional holders for {symbol}: {e}")
            
            if fundamentals.get('interest_coverage') is None:
                ebit = self.get_financial_value(financials, 'EBIT') or self.get_financial_value(financials, 'Operating Income')
                interest_expense = None
                for row in ['Interest Expense', 'Interest Expense, Net', 'Interest Income (Expense), Net Non-Operating']:
                    interest_expense = self.get_financial_value(financials, row)
                    if interest_expense is not None:
                        break
                if ebit is not None and interest_expense is not None and interest_expense < 0:
                    ie = abs(interest_expense)
                    if ebit > 0 and ie > 0:
                        fundamentals['interest_coverage'] = round(ebit / ie, 2)
                elif ebit is not None and interest_expense is not None and interest_expense > 0:
                    ie = abs(float(interest_expense))
                    if ebit > 0 and ie > 0:
                        fundamentals['interest_coverage'] = round(ebit / ie, 2)
            
            if fundamentals.get('current_ratio') is None:
                ca = fundamentals.get('current_assets')
                cl = fundamentals.get('current_liabilities')
                if ca is not None and cl is not None and cl > 0:
                    fundamentals['current_ratio'] = round(ca / cl, 2)
            
            if fundamentals.get('debt_to_equity') is None:
                td = fundamentals.get('total_debt')
                bv = balance_sheet
                if td is not None:
                    eq = None
                    for row in ['Stockholders Equity', 'Shareholders Equity', 'Total Equity Gross Minority Interest', 'Total Equity']:
                        eq = self.get_financial_value(bv, row)
                        if eq is not None:
                            break
                    if eq is not None and eq > 0:
                        fundamentals['debt_to_equity'] = round(td / eq, 2)
            
            eps_growth = self.get_eps_growth(financials)
            fundamentals.update(eps_growth)
            
            pe = fundamentals.get('pe_ratio')
            epsg = fundamentals.get('eps_growth_1y')
            if fundamentals.get('peg_ratio') is None and pe is not None and epsg is not None and epsg > 0:
                fundamentals['peg_ratio'] = round(pe / epsg, 2)
            
            if fundamentals.get('roce') is None:
                roce_ebit = None
                for row in ['EBIT', 'Operating Income', 'Operating Income (Loss)']:
                    roce_ebit = self.get_financial_value(financials, row)
                    if roce_ebit is not None:
                        break
                if roce_ebit is not None and roce_ebit > 0:
                    ta = self.get_financial_value(balance_sheet, ['Total Assets', 'Total Assets (Quarterly)'])
                    cl = fundamentals.get('current_liabilities')
                    if ta is not None and cl is not None:
                        ce = ta - cl
                        if ce > 0:
                            fundamentals['roce'] = round((roce_ebit / ce) * 100, 2)
            
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
                revenues = [float(v) for v in revenues if pd.notna(v) and abs(float(v)) > 0]
                if len(revenues) >= 2:
                    growth_rates['revenue_growth_1y'] = round(((revenues[0] - revenues[1]) / abs(revenues[1])) * 100, 2) if revenues[1] != 0 else None
                if len(revenues) >= 4:
                    cagr_3y = ((revenues[0] / abs(revenues[3])) ** (1/3) - 1) * 100 if revenues[3] != 0 else None
                    growth_rates['revenue_growth_3y'] = round(cagr_3y, 2) if cagr_3y is not None else None
                if len(revenues) >= 5:
                    cagr_5y = ((revenues[0] / abs(revenues[4])) ** (1/5) - 1) * 100 if revenues[4] != 0 else None
                    growth_rates['revenue_growth_5y'] = round(cagr_5y, 2) if cagr_5y is not None else None
            
            if 'Net Income' in financials.index:
                profits = financials.loc['Net Income'].values
                profits = [float(v) for v in profits if pd.notna(v) and abs(float(v)) > 0]
                if len(profits) >= 2:
                    growth_rates['profit_growth_1y'] = round(((profits[0] - profits[1]) / abs(profits[1])) * 100, 2) if profits[1] != 0 else None
                if len(profits) >= 4:
                    cagr_3y = ((profits[0] / abs(profits[3])) ** (1/3) - 1) * 100 if profits[3] != 0 else None
                    growth_rates['profit_growth_3y'] = round(cagr_3y, 2) if cagr_3y is not None else None
                if len(profits) >= 5:
                    cagr_5y = ((profits[0] / abs(profits[4])) ** (1/5) - 1) * 100 if profits[4] != 0 else None
                    growth_rates['profit_growth_5y'] = round(cagr_5y, 2) if cagr_5y is not None else None
            
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
            
            ticker = yf.Ticker(symbol)
            fundamentals = self.fetch_fundamentals(ticker)
            
            if fundamentals:
                growth_rates = self.calculate_growth_rates(ticker, symbol)
                fundamentals.update(growth_rates)
                
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