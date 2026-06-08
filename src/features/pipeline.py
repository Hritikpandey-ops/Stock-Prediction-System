"""
Feature engineering pipeline that orchestrates all feature types.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from loguru import logger

from src.features.technical import TechnicalFeatureEngineer
from src.features.fundamental import FundamentalFeatureEngineer
from src.features.sentiment import SentimentFeatureEngineer
from src.database.repository import PriceRepository, FundamentalRepository, NewsSentimentRepository
from config.database import get_db


class FeaturePipeline:
    """Orchestrates feature engineering from multiple sources."""
    
    def __init__(self):
        """Initialize feature pipeline."""
        self.technical = TechnicalFeatureEngineer()
        self.fundamental = FundamentalFeatureEngineer()
        self.sentiment = SentimentFeatureEngineer()
        self.logger = logger
    
    def build_features(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_fundamentals: bool = True,
        include_sentiment: bool = True,
        target_horizon: int = 1
    ) -> pd.DataFrame:
        """
        Build complete feature set for a symbol.
        
        Args:
            symbol: Stock symbol
            start_date: Start date for data
            end_date: End date for data
            include_fundamentals: Whether to include fundamental features
            include_sentiment: Whether to include sentiment features
            target_horizon: Prediction horizon in days
            
        Returns:
            DataFrame with all features and target variable
        """
        self.logger.info(f"Building features for {symbol}")
        
        # Get price data from database
        with next(get_db()) as db:
            price_repo = PriceRepository(db)
            prices = price_repo.get_by_symbol(symbol, start_date, end_date)
        
        if not prices:
            self.logger.warning(f"No price data found for {symbol}")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'timestamp': p.timestamp,
            'open': float(p.open),
            'high': float(p.high),
            'low': float(p.low),
            'close': float(p.close),
            'volume': int(p.volume) if p.volume else 0
        } for p in prices])
        
        # Sort by timestamp
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Calculate technical indicators
        df = self.technical.calculate_all_indicators(df)
        
        # Add fundamental features if requested
        if include_fundamentals:
            df = self._add_fundamental_features(df, symbol)
        
        # Add sentiment features if requested
        if include_sentiment:
            df = self._add_sentiment_features(df, symbol)
        
        # Add target variable
        df = self.technical.add_target_variable(df, horizon=target_horizon)
        
        # Clean and prepare data
        df = self._clean_data(df)
        
        self.logger.info(f"Built {len(df)} records with {len(df.columns)} features for {symbol}")
        
        return df
    
    def _add_fundamental_features(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Add fundamental features to the DataFrame."""
        try:
            with next(get_db()) as db:
                fund_repo = FundamentalRepository(db)
                fundamentals = fund_repo.get_by_symbol(symbol, limit=10)
            
            if not fundamentals:
                self.logger.warning(f"No fundamental data for {symbol}")
                return df
            
            # Convert to list of dicts
            fund_list = [{
                'report_date': f.report_date,
                'pe_ratio': float(f.pe_ratio) if f.pe_ratio else None,
                'pb_ratio': float(f.pb_ratio) if f.pb_ratio else None,
                'roe': float(f.roe) if f.roe else None,
                'debt_to_equity': float(f.debt_to_equity) if f.debt_to_equity else None,
                'profit_margin': float(f.profit_margin) if f.profit_margin else None,
                'revenue_growth': float(f.revenue_growth) if f.revenue_growth else None,
                'current_ratio': float(f.current_ratio) if f.current_ratio else None,
                'market_cap': int(f.market_cap) if f.market_cap else None
            } for f in fundamentals]
            
            # Merge with price data
            df = self.fundamental.merge_with_prices(df, fund_list)
            
        except Exception as e:
            self.logger.error(f"Error adding fundamental features: {str(e)}")
        
        return df
    
    def _add_sentiment_features(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Add sentiment features to the DataFrame."""
        try:
            with next(get_db()) as db:
                news_repo = NewsSentimentRepository(db)
                articles = news_repo.get_by_symbol(symbol, limit=500)
            
            if not articles:
                self.logger.warning(f"No news data for {symbol}")
                # Add empty sentiment features
                for col in self.sentiment.get_feature_names():
                    df[col] = 0
                return df
            
            # Convert to list of dicts
            article_list = [{
                'headline': a.headline,
                'published_at': a.published_at,
                'sentiment_score': float(a.sentiment_score) if a.sentiment_score else None,
                'sentiment_label': a.sentiment_label
            } for a in articles]
            
            # Aggregate sentiment for each date
            for idx, row in df.iterrows():
                date = row['timestamp']
                
                # Get articles from last 14 days
                cutoff = date - pd.Timedelta(days=14)
                relevant_articles = [
                    a for a in article_list
                    if a['published_at'] and cutoff <= a['published_at'] <= date
                ]
                
                # Calculate aggregate features
                sentiment_features = self.sentiment.aggregate_sentiment(
                    relevant_articles,
                    time_windows=[1, 3, 7, 14]
                )
                
                # Add features to DataFrame
                for col, value in sentiment_features.items():
                    df.at[idx, col] = value
            
            # Fill any missing sentiment features
            for col in self.sentiment.get_feature_names():
                if col not in df.columns:
                    df[col] = 0
            
        except Exception as e:
            self.logger.error(f"Error adding sentiment features: {str(e)}")
        
        return df
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and prepare feature data.
        
        Args:
            df: DataFrame with features
            
        Returns:
            Cleaned DataFrame
        """
        # Reset index
        df = df.reset_index(drop=True)
        
        # Forward fill missing values (common for indicators at start)
        df = df.fillna(method='ffill')
        
        # Backward fill for any remaining NaN at the start
        df = df.fillna(method='bfill')
        
        # Fill any remaining NaN with 0
        df = df.fillna(0)
        
        # Remove rows with infinite values
        df = df.replace([np.inf, -np.inf], 0)
        
        # Drop rows where target is NaN (last few rows due to shift)
        target_cols = [col for col in df.columns if col.startswith('Target_')]
        if target_cols:
            df = df.dropna(subset=target_cols)
        
        self.logger.info(f"Cleaned data: {len(df)} records")
        
        return df
    
    def get_feature_matrix(
        self,
        df: pd.DataFrame,
        exclude_targets: bool = True
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Split DataFrame into features (X) and target (y).
        
        Args:
            df: DataFrame with all features
            exclude_targets: Whether to exclude target columns from X
            
        Returns:
            Tuple of (X, y)
        """
        # Identify target columns
        target_cols = [col for col in df.columns if col.startswith('Target_')]
        
        if exclude_targets and target_cols:
            # Use the first target column as y
            y = df[target_cols[0]]
            X = df.drop(columns=target_cols)
        else:
            X = df
            y = pd.Series(dtype=float)
        
        return X, y
    
    def get_all_feature_names(self) -> List[str]:
        """Get list of all available feature names."""
        return (
            self.technical.get_feature_names() +
            self.fundamental.get_feature_names() +
            self.sentiment.get_feature_names()
        )
    
    def build_features_for_multiple_symbols(
        self,
        symbols: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Build features for multiple symbols.
        
        Args:
            symbols: List of stock symbols
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary mapping symbols to their feature DataFrames
        """
        results = {}
        
        for symbol in symbols:
            try:
                df = self.build_features(symbol, start_date, end_date)
                if not df.empty:
                    results[symbol] = df
                    self.logger.info(f"Built features for {symbol}: {len(df)} records")
                else:
                    self.logger.warning(f"No features built for {symbol}")
            except Exception as e:
                self.logger.error(f"Failed to build features for {symbol}: {str(e)}")
        
        return results