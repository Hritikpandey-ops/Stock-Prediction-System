"""
Sentiment feature engineering from news data.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from loguru import logger


class SentimentFeatureEngineer:
    """Engineer features from news sentiment data."""
    
    def __init__(self):
        """Initialize sentiment feature engineer."""
        self.logger = logger
        self.analyzer = SentimentIntensityAnalyzer()
    
    def calculate_sentiment_score(self, text: str) -> Dict[str, float]:
        """
        Calculate sentiment scores for a text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment scores
        """
        scores = self.analyzer.polarity_scores(text)
        
        return {
            'compound': scores['compound'],
            'positive': scores['pos'],
            'neutral': scores['neu'],
            'negative': scores['neg']
        }
    
    def process_news_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process news articles and add sentiment scores.
        
        Args:
            articles: List of news articles with headlines
            
        Returns:
            List of articles with sentiment scores
        """
        if not articles:
            return []
        
        processed = []
        
        for article in articles:
            headline = article.get('headline', '')
            
            # Calculate sentiment if not already provided
            if 'sentiment_score' not in article or article['sentiment_score'] is None:
                sentiment = self.calculate_sentiment_score(headline)
                article['sentiment_score'] = sentiment['compound']
                article['sentiment_positive'] = sentiment['positive']
                article['sentiment_negative'] = sentiment['negative']
                article['sentiment_neutral'] = sentiment['neutral']
                
                # Assign label
                if sentiment['compound'] >= 0.1:
                    article['sentiment_label'] = 'POSITIVE'
                elif sentiment['compound'] <= -0.1:
                    article['sentiment_label'] = 'NEGATIVE'
                else:
                    article['sentiment_label'] = 'NEUTRAL'
            
            processed.append(article)
        
        self.logger.info(f"Processed {len(processed)} articles with sentiment analysis")
        
        return processed
    
    def aggregate_sentiment(
        self,
        articles: List[Dict[str, Any]],
        time_windows: List[int] = [1, 3, 7, 14]
    ) -> Dict[str, Any]:
        """
        Aggregate sentiment scores over different time windows.
        
        Args:
            articles: List of news articles with sentiment scores
            time_windows: List of time windows in days
            
        Returns:
            Dictionary with aggregated sentiment features
        """
        if not articles:
            return self._empty_sentiment_features()
        
        features = {}
        now = datetime.now()
        
        for window in time_windows:
            # Filter articles within time window
            cutoff_date = now - timedelta(days=window)
            window_articles = [
                a for a in articles
                if a.get('published_at') and a['published_at'] >= cutoff_date
            ]
            
            if not window_articles:
                features[f'sentiment_avg_{window}d'] = 0
                features[f'sentiment_std_{window}d'] = 0
                features[f'sentiment_count_{window}d'] = 0
                features[f'sentiment_positive_ratio_{window}d'] = 0
                features[f'sentiment_negative_ratio_{window}d'] = 0
                continue
            
            # Calculate aggregate metrics
            scores = [a.get('sentiment_score', 0) for a in window_articles if a.get('sentiment_score') is not None]
            
            if scores:
                features[f'sentiment_avg_{window}d'] = np.mean(scores)
                features[f'sentiment_std_{window}d'] = np.std(scores)
                features[f'sentiment_min_{window}d'] = np.min(scores)
                features[f'sentiment_max_{window}d'] = np.max(scores)
            else:
                features[f'sentiment_avg_{window}d'] = 0
                features[f'sentiment_std_{window}d'] = 0
                features[f'sentiment_min_{window}d'] = 0
                features[f'sentiment_max_{window}d'] = 0
            
            features[f'sentiment_count_{window}d'] = len(window_articles)
            
            # Calculate positive/negative ratios
            positive_count = sum(1 for a in window_articles if a.get('sentiment_label') == 'POSITIVE')
            negative_count = sum(1 for a in window_articles if a.get('sentiment_label') == 'NEGATIVE')
            
            features[f'sentiment_positive_ratio_{window}d'] = positive_count / len(window_articles) if window_articles else 0
            features[f'sentiment_negative_ratio_{window}d'] = negative_count / len(window_articles) if window_articles else 0
        
        # Sentiment momentum (change in sentiment)
        if len(time_windows) >= 2:
            short_window = min(time_windows)
            long_window = max(time_windows)
            
            short_sentiment = features.get(f'sentiment_avg_{short_window}d', 0)
            long_sentiment = features.get(f'sentiment_avg_{long_window}d', 0)
            
            features['sentiment_momentum'] = short_sentiment - long_sentiment
        
        # News volume features
        features['news_volume_7d'] = features.get('sentiment_count_7d', 0)
        features['news_volume_14d'] = features.get('sentiment_count_14d', 0)
        
        # Sentiment volatility
        if features.get('sentiment_std_7d') and features.get('sentiment_avg_7d'):
            features['sentiment_volatility'] = features['sentiment_std_7d'] / abs(features['sentiment_avg_7d']) if features['sentiment_avg_7d'] != 0 else 0
        else:
            features['sentiment_volatility'] = 0
        
        self.logger.info(f"Calculated sentiment features for {len(articles)} articles")
        
        return features
    
    def create_sentiment_signal(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create trading signal from sentiment features.
        
        Args:
            features: Dictionary of sentiment features
            
        Returns:
            Dictionary with sentiment signals
        """
        # Get recent sentiment
        recent_sentiment = features.get('sentiment_avg_7d', 0)
        sentiment_momentum = features.get('sentiment_momentum', 0)
        news_volume = features.get('news_volume_7d', 0)
        
        # Calculate signal strength
        signal_strength = 0
        
        # Base signal from sentiment
        if recent_sentiment > 0.2:
            signal_strength += 2
        elif recent_sentiment > 0.1:
            signal_strength += 1
        elif recent_sentiment < -0.2:
            signal_strength -= 2
        elif recent_sentiment < -0.1:
            signal_strength -= 1
        
        # Adjust for momentum
        if sentiment_momentum > 0.1:
            signal_strength += 1
        elif sentiment_momentum < -0.1:
            signal_strength -= 1
        
        # Adjust for news volume (more news = more confidence)
        if news_volume > 10:
            signal_strength *= 1.2
        elif news_volume > 5:
            signal_strength *= 1.1
        
        # Determine signal direction
        if signal_strength >= 2:
            signal = 'STRONG_BUY'
        elif signal_strength >= 1:
            signal = 'BUY'
        elif signal_strength <= -2:
            signal = 'STRONG_SELL'
        elif signal_strength <= -1:
            signal = 'SELL'
        else:
            signal = 'NEUTRAL'
        
        return {
            'sentiment_signal': signal,
            'sentiment_signal_strength': signal_strength,
            'recent_sentiment': recent_sentiment,
            'sentiment_momentum': sentiment_momentum,
            'news_volume': news_volume
        }
    
    def _empty_sentiment_features(self) -> Dict[str, Any]:
        """Return empty sentiment features."""
        return {
            'sentiment_avg_1d': 0,
            'sentiment_avg_3d': 0,
            'sentiment_avg_7d': 0,
            'sentiment_avg_14d': 0,
            'sentiment_std_7d': 0,
            'sentiment_min_7d': 0,
            'sentiment_max_7d': 0,
            'sentiment_count_1d': 0,
            'sentiment_count_3d': 0,
            'sentiment_count_7d': 0,
            'sentiment_count_14d': 0,
            'sentiment_positive_ratio_7d': 0,
            'sentiment_negative_ratio_7d': 0,
            'sentiment_momentum': 0,
            'news_volume_7d': 0,
            'news_volume_14d': 0,
            'sentiment_volatility': 0
        }
    
    def get_feature_names(self) -> List[str]:
        """Get list of all sentiment feature names."""
        time_windows = [1, 3, 7, 14]
        features = []
        
        for window in time_windows:
            features.extend([
                f'sentiment_avg_{window}d',
                f'sentiment_std_{window}d',
                f'sentiment_count_{window}d',
                f'sentiment_positive_ratio_{window}d',
                f'sentiment_negative_ratio_{window}d'
            ])
        
        features.extend([
            'sentiment_min_7d',
            'sentiment_max_7d',
            'sentiment_momentum',
            'news_volume_7d',
            'news_volume_14d',
            'sentiment_volatility'
        ])
        
        return features