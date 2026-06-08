"""
Configuration management for the Stock Prediction System.
"""
import os
from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    db_user: str = "stockuser"
    db_password: str = "stockpass"
    db_name: str = "stock_db"
    db_host: str = "127.0.0.1"
    db_port: int = 5433
    
    @property
    def database_url(self) -> str:
        """Construct database URL from individual components."""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    environment: str = "development"
    
    # YFinance Configuration
    yfinance_rate_limit: int = 60
    
    # Finnhub Configuration
    finnhub_api_key: Optional[str] = None
    
    # Marketaux Configuration
    marketaux_api_key: Optional[str] = None
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    # Backtesting
    initial_capital: float = 1000000.0
    transaction_cost_per_trade: float = 20.0
    slippage_percent: float = 0.05
    
    # Model
    model_version: str = "1.0.0"
    train_test_split: float = 0.2
    walk_forward_window_months: int = 12
    walk_forward_test_months: int = 3
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Nifty 50 Constituents (simplified list - can be extended)
    nifty50_symbols: List[str] = [
        "^NSEI",  # Nifty 50 Index
        "RELIANCE.NS",
        "TCS.NS",
        "HDFCBANK.NS",
        "INFY.NS",
        "ICICIBANK.NS",
        "HINDUNILVR.NS",
        "SBIN.NS",
        "BHARTIARTL.NS",
        "ITC.NS",
        "KOTAKBANK.NS",
        "LT.NS",
        "HCLTECH.NS",
        "AXISBANK.NS",
        "ASIANPAINT.NS",
        "MARUTI.NS",
        "SUNPHARMA.NS",
        "TITAN.NS",
        "BAJFINANCE.NS",
        "WIPRO.NS",
    ]
    
    @field_validator('train_test_split')
    @classmethod
    def validate_split(cls, v: float) -> float:
        if not 0.0 < v < 1.0:
            raise ValueError('train_test_split must be between 0 and 1')
        return v
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        return v.upper() if v.upper() in valid_levels else 'INFO'
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()