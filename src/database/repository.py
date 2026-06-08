"""
Repository pattern for database operations.
"""
from typing import List, Optional, TypeVar, Type, Any
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import Session
from decimal import Decimal
import logging

from src.database.models import Price, Fundamental, NewsSentiment, ModelPrediction, BacktestResult

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Price)


class BaseRepository:
    """Base repository with common CRUD operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get(self, model: Type[T], id: int) -> Optional[T]:
        """Get a record by ID."""
        return self.db.query(model).filter(model.id == id).first()
    
    def get_all(self, model: Type[T], limit: int = 100, offset: int = 0) -> List[T]:
        """Get all records with pagination."""
        return self.db.query(model).offset(offset).limit(limit).all()
    
    def create(self, model_kwargs: dict) -> Any:
        """Create a new record."""
        instance = self.model(**model_kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance
    
    def bulk_create(self, model: Type[T], items: List[dict]) -> None:
        """Bulk insert records."""
        if items:
            self.db.bulk_insert_mappings(model, items)
            self.db.commit()
    
    def update(self, model: Type[T], id: int, **kwargs) -> Optional[T]:
        """Update a record."""
        instance = self.get(model, id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            self.db.commit()
            self.db.refresh(instance)
        return instance
    
    def delete(self, model: Type[T], id: int) -> bool:
        """Delete a record."""
        instance = self.get(model, id)
        if instance:
            self.db.delete(instance)
            self.db.commit()
            return True
        return False


class PriceRepository(BaseRepository):
    """Repository for Price operations."""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = Price
    
    def get_by_symbol(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Price]:
        """Get prices for a symbol within a date range."""
        query = self.db.query(self.model).filter(self.model.symbol == symbol)
        
        if start_date:
            query = query.filter(self.model.timestamp >= start_date)
        if end_date:
            query = query.filter(self.model.timestamp <= end_date)
        
        query = query.order_by(desc(self.model.timestamp))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_latest_price(self, symbol: str) -> Optional[Price]:
        """Get the most recent price for a symbol."""
        return self.db.query(self.model).filter(
            self.model.symbol == symbol
        ).order_by(desc(self.model.timestamp)).first()
    
    def get_prices_for_features(
        self,
        symbol: str,
        lookback_days: int = 365
    ) -> List[Price]:
        """Get historical prices for feature engineering."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        return self.get_by_symbol(symbol, start_date, end_date)
    
    def upsert_price(self, symbol: str, timestamp: datetime, **price_data) -> Price:
        """Insert or update a price record."""
        # Check if record exists
        existing = self.db.query(self.model).filter(
            self.model.symbol == symbol,
            self.model.timestamp == timestamp
        ).first()
        
        if existing:
            # Update existing record
            for key, value in price_data.items():
                setattr(existing, key, value)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new record
            price_data['symbol'] = symbol
            price_data['timestamp'] = timestamp
            new_price = self.model(**price_data)
            self.db.add(new_price)
            self.db.commit()
            self.db.refresh(new_price)
            return new_price
    
    def symbol_exists(self, symbol: str) -> bool:
        """Check if any price data exists for a symbol."""
        count = self.db.query(self.model).filter(
            self.model.symbol == symbol
        ).count()
        return count > 0


class FundamentalRepository(BaseRepository):
    """Repository for Fundamental operations."""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = Fundamental
    
    def get_by_symbol(
        self,
        symbol: str,
        period_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Fundamental]:
        """Get fundamentals for a symbol."""
        query = self.db.query(self.model).filter(self.model.symbol == symbol)
        
        if period_type:
            query = query.filter(self.model.period_type == period_type)
        
        return query.order_by(desc(self.model.report_date)).limit(limit).all()
    
    def get_latest_fundamentals(self, symbol: str) -> Optional[Fundamental]:
        """Get the most recent fundamentals for a symbol."""
        return self.db.query(self.model).filter(
            self.model.symbol == symbol
        ).order_by(desc(self.model.report_date)).first()


class NewsSentimentRepository(BaseRepository):
    """Repository for NewsSentiment operations."""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = NewsSentiment
    
    def get_by_symbol(
        self,
        symbol: Optional[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50
    ) -> List[NewsSentiment]:
        """Get news sentiment for a symbol or general market news."""
        query = self.db.query(self.model)
        
        if symbol:
            query = query.filter(self.model.symbol == symbol)
        else:
            query = query.filter(self.model.symbol.is_(None))
        
        if start_date:
            query = query.filter(self.model.published_at >= start_date)
        if end_date:
            query = query.filter(self.model.published_at <= end_date)
        
        return query.order_by(desc(self.model.published_at)).limit(limit).all()
    
    def get_average_sentiment(
        self,
        symbol: Optional[str],
        days: int = 7
    ) -> Optional[Decimal]:
        """Get average sentiment score for a symbol over the last N days."""
        start_date = datetime.now() - timedelta(days=days)
        
        result = self.db.query(func.avg(self.model.sentiment_score)).filter(
            self.model.symbol == symbol if symbol else self.model.symbol.is_(None),
            self.model.published_at >= start_date
        ).first()
        
        return result[0] if result[0] else None


class ModelPredictionRepository(BaseRepository):
    """Repository for ModelPrediction operations."""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = ModelPrediction
    
    def get_predictions(
        self,
        symbol: str,
        model_version: Optional[str] = None,
        limit: int = 100
    ) -> List[ModelPrediction]:
        """Get predictions for a symbol."""
        query = self.db.query(self.model).filter(self.model.symbol == symbol)
        
        if model_version:
            query = query.filter(self.model.model_version == model_version)
        
        return query.order_by(desc(self.model.prediction_date)).limit(limit).all()
    
    def get_accuracy_stats(
        self,
        symbol: str,
        model_version: str,
        days: int = 30
    ) -> dict:
        """Get accuracy statistics for predictions."""
        start_date = datetime.now() - timedelta(days=days)
        
        predictions = self.db.query(self.model).filter(
            self.model.symbol == symbol,
            self.model.model_version == model_version,
            self.model.prediction_date >= start_date,
            self.model.is_correct.isnot(None)
        ).all()
        
        if not predictions:
            return {
                'total_predictions': 0,
                'accuracy': 0.0,
                'avg_confidence': 0.0
            }
        
        correct = sum(1 for p in predictions if p.is_correct)
        total = len(predictions)
        avg_confidence = sum(float(p.confidence_score) for p in predictions) / total
        
        return {
            'total_predictions': total,
            'accuracy': correct / total if total > 0 else 0.0,
            'avg_confidence': avg_confidence
        }


class BacktestResultRepository(BaseRepository):
    """Repository for BacktestResult operations."""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = BacktestResult
    
    def get_all_results(self, limit: int = 100) -> List[BacktestResult]:
        """Get all backtest results."""
        return self.db.query(self.model).order_by(
            desc(self.model.created_at)
        ).limit(limit).all()
    
    def get_best_strategy(self) -> Optional[BacktestResult]:
        """Get the backtest with the highest Sharpe ratio."""
        return self.db.query(self.model).order_by(
            desc(self.model.sharpe_ratio)
        ).first()