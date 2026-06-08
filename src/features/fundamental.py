"""
Fundamental feature engineering.
"""
import pandas as pd
from typing import Dict, Any, List, Optional
from loguru import logger


class FundamentalFeatureEngineer:
    """Engineer features from fundamental data."""
    
    def __init__(self):
        """Initialize fundamental feature engineer."""
        self.logger = logger
    
    def calculate_features(self, fundamentals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate feature set from raw fundamental data.
        
        Args:
            fundamentals: Dictionary of fundamental data
            
        Returns:
            Dictionary of engineered features
        """
        if not fundamentals:
            return {}
        
        features = {}
        
        # Valuation features
        features['pe_ratio'] = fundamentals.get('pe_ratio')
        features['pb_ratio'] = fundamentals.get('pb_ratio')
        features['eps'] = fundamentals.get('eps')
        
        # Profitability features
        features['roe'] = fundamentals.get('roe')
        features['roce'] = fundamentals.get('roce')
        features['profit_margin'] = fundamentals.get('profit_margin')
        features['revenue_growth'] = fundamentals.get('revenue_growth')
        
        # Financial health features
        features['debt_to_equity'] = fundamentals.get('debt_to_equity')
        features['current_ratio'] = fundamentals.get('current_ratio')
        
        # Market features
        features['market_cap'] = fundamentals.get('market_cap')
        features['shares_outstanding'] = fundamentals.get('shares_outstanding')
        
        # Derived features
        if fundamentals.get('pe_ratio') and fundamentals.get('eps'):
            features['implied_price'] = fundamentals['pe_ratio'] * fundamentals['eps']
        
        if fundamentals.get('pb_ratio') and fundamentals.get('roe'):
            features['peg_ratio'] = fundamentals['pe_ratio'] / fundamentals['roe'] if fundamentals['roe'] else None
        
        # Value scoring (0-100 scale)
        features['value_score'] = self._calculate_value_score(features)
        
        # Growth scoring (0-100 scale)
        features['growth_score'] = self._calculate_growth_score(features)
        
        # Quality scoring (0-100 scale)
        features['quality_score'] = self._calculate_quality_score(features)
        
        # Composite score
        features['composite_score'] = (
            features['value_score'] * 0.3 +
            features['growth_score'] * 0.3 +
            features['quality_score'] * 0.4
        )
        
        self.logger.info(f"Calculated {len(features)} fundamental features")
        
        return features
    
    def _calculate_value_score(self, features: Dict[str, Any]) -> float:
        """
        Calculate value score (0-100).
        Lower P/E and P/B are better for value.
        """
        score = 50.0  # Start with neutral score
        
        # P/E scoring (ideal range: 10-20)
        pe = features.get('pe_ratio')
        if pe:
            if pe < 10:
                score += 20
            elif pe < 15:
                score += 15
            elif pe < 20:
                score += 10
            elif pe < 30:
                score -= 5
            elif pe < 50:
                score -= 15
            else:
                score -= 25
        
        # P/B scoring (ideal range: 1-3)
        pb = features.get('pb_ratio')
        if pb:
            if pb < 1:
                score += 20
            elif pb < 2:
                score += 15
            elif pb < 3:
                score += 10
            elif pb < 5:
                score -= 5
            else:
                score -= 15
        
        return max(0, min(100, score))
    
    def _calculate_growth_score(self, features: Dict[str, Any]) -> float:
        """
        Calculate growth score (0-100).
        Higher revenue growth is better.
        """
        score = 50.0  # Start with neutral score
        
        # Revenue growth scoring
        growth = features.get('revenue_growth')
        if growth:
            if growth > 25:
                score += 30
            elif growth > 15:
                score += 20
            elif growth > 10:
                score += 15
            elif growth > 5:
                score += 5
            elif growth < -10:
                score -= 20
            elif growth < 0:
                score -= 10
        
        return max(0, min(100, score))
    
    def _calculate_quality_score(self, features: Dict[str, Any]) -> float:
        """
        Calculate quality score (0-100).
        Higher ROE, profit margin, and lower debt are better.
        """
        score = 50.0  # Start with neutral score
        
        # ROE scoring (ideal: >15%)
        roe = features.get('roe')
        if roe:
            if roe > 20:
                score += 25
            elif roe > 15:
                score += 20
            elif roe > 10:
                score += 10
            elif roe < 5:
                score -= 15
        
        # Profit margin scoring
        margin = features.get('profit_margin')
        if margin:
            if margin > 20:
                score += 15
            elif margin > 10:
                score += 10
            elif margin < 5:
                score -= 10
        
        # Debt to equity scoring (lower is better)
        dte = features.get('debt_to_equity')
        if dte:
            if dte < 0.3:
                score += 15
            elif dte < 0.5:
                score += 10
            elif dte < 1.0:
                score += 5
            elif dte > 2.0:
                score -= 15
            elif dte > 1.0:
                score -= 5
        
        # Current ratio scoring (ideal: >1.5)
        cr = features.get('current_ratio')
        if cr:
            if cr > 2:
                score += 10
            elif cr > 1.5:
                score += 5
            elif cr < 1:
                score -= 15
        
        return max(0, min(100, score))
    
    def merge_with_prices(
        self,
        price_df: pd.DataFrame,
        fundamentals_list: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """
        Merge fundamental data with price data.
        Fundamentals are forward-filled since they change infrequently.
        
        Args:
            price_df: DataFrame with price data
            fundamentals_list: List of fundamental snapshots
            
        Returns:
            DataFrame with merged price and fundamental data
        """
        if not fundamentals_list:
            return price_df
        
        # Convert fundamentals to DataFrame
        fund_df = pd.DataFrame(fundamentals_list)
        
        if fund_df.empty:
            return price_df
        
        # Sort by report date
        fund_df['report_date'] = pd.to_datetime(fund_df['report_date'])
        fund_df = fund_df.sort_values('report_date')
        
        # Create a merged DataFrame
        df = price_df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # For each fundamental metric, forward-fill based on report date
        for _, fund in fund_df.iterrows():
            report_date = fund['report_date']
            
            # Mask for dates after this fundamental report
            mask = df['timestamp'] >= report_date
            
            # Forward fill each metric
            for col in ['pe_ratio', 'pb_ratio', 'roe', 'debt_to_equity', 'profit_margin', 'revenue_growth']:
                if col in fund and fund[col] is not None:
                    df.loc[mask, col] = fund[col]
        
        self.logger.info(f"Merged fundamentals with {len(df)} price records")
        
        return df
    
    def get_feature_names(self) -> List[str]:
        """Get list of all fundamental feature names."""
        return [
            'pe_ratio', 'pb_ratio', 'eps',
            'roe', 'roce', 'profit_margin', 'revenue_growth',
            'debt_to_equity', 'current_ratio',
            'market_cap', 'shares_outstanding',
            'implied_price', 'peg_ratio',
            'value_score', 'growth_score', 'quality_score', 'composite_score'
        ]