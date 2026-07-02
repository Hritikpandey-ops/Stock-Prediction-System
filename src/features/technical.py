"""
Technical indicator calculations using the ta library.
"""
import pandas as pd
import ta
from typing import Dict, Any, List, Optional
from loguru import logger


class TechnicalFeatureEngineer:
    """Engineer technical indicators from price data."""
    
    def __init__(self):
        """Initialize technical feature engineer."""
        self.logger = logger
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators for a DataFrame.
        
        Args:
            df: DataFrame with OHLCV data (must have columns: open, high, low, close, volume)
            
        Returns:
            DataFrame with added technical indicators
        """
        df = df.copy()
        
        try:
            # Calculate trend indicators
            df = self._add_trend_indicators(df)
            
            # Calculate momentum indicators
            df = self._add_momentum_indicators(df)
            
            # Calculate volatility indicators
            df = self._add_volatility_indicators(df)
            
            # Calculate volume indicators
            df = self._add_volume_indicators(df)
            
            # Calculate support/resistance levels
            df = self._add_support_resistance(df)
            
            self.logger.info(f"Calculated {len([c for c in df.columns if c not in ['open', 'high', 'low', 'close', 'volume']])} technical indicators")
            
        except Exception as e:
            self.logger.error(f"Error calculating technical indicators: {str(e)}")
        
        return df
    
    def _add_trend_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add trend-following indicators."""
        
        # Moving Averages
        for period in [5, 10, 20, 50, 100, 200]:
            df[f'SMA_{period}'] = ta.trend.sma_indicator(df['close'], window=period)
            df[f'EMA_{period}'] = ta.trend.ema_indicator(df['close'], window=period)
        
        # MACD
        macd_obj = ta.trend.MACD(df['close'])
        df['MACD'] = macd_obj.macd()
        df['MACD_Signal'] = macd_obj.macd_signal()
        df['MACD_Hist'] = macd_obj.macd_diff()
        
        # ADX (Trend Strength)
        adx_obj = ta.trend.ADXIndicator(df['high'], df['low'], df['close'])
        df['ADX'] = adx_obj.adx()
        df['DI_Plus'] = adx_obj.adx_pos()
        df['DI_Minus'] = adx_obj.adx_neg()
        
        # Parabolic SAR
        psar_obj = ta.trend.PSARIndicator(df['high'], df['low'], df['close'])
        df['PSAR'] = psar_obj.psar()
        
        return df
    
    def _add_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add momentum indicators."""
        
        # RSI
        df['RSI_14'] = ta.momentum.rsi(df['close'], window=14)
        df['RSI_7'] = ta.momentum.rsi(df['close'], window=7)
        df['RSI_21'] = ta.momentum.rsi(df['close'], window=21)
        
        # Stochastic Oscillator
        stoch_obj = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'])
        df['STOCH_K'] = stoch_obj.stoch()
        df['STOCH_D'] = stoch_obj.stoch_signal()
        
        # Williams %R
        df['WILLR'] = ta.momentum.williams_r(df['high'], df['low'], df['close'])
        
        # CCI (Commodity Channel Index)
        df['CCI_20'] = ta.trend.cci(df['high'], df['low'], df['close'], window=20)
        
        # ROC (Rate of Change)
        df['ROC_10'] = ta.momentum.roc(df['close'], window=10)
        df['ROC_20'] = ta.momentum.roc(df['close'], window=20)
        
        # Momentum
        df['MOM_10'] = ta.momentum.roc(df['close'], window=10)
        
        return df
    
    def _add_volatility_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volatility indicators."""
        
        # Bollinger Bands
        bb_obj = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
        df['BB_Upper'] = bb_obj.bollinger_hband()
        df['BB_Middle'] = bb_obj.bollinger_mavg()
        df['BB_Lower'] = bb_obj.bollinger_lband()
        df['BB_Width'] = bb_obj.bollinger_wband()
        df['BB_Pct'] = bb_obj.bollinger_pband()
        
        # ATR (Average True Range)
        df['ATR_14'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)
        df['ATR_7'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=7)
        
        # Keltner Channels
        kc_obj = ta.volatility.KeltnerChannel(df['high'], df['low'], df['close'])
        df['KC_Upper'] = kc_obj.keltner_channel_hband()
        df['KC_Middle'] = kc_obj.keltner_channel_mband()
        df['KC_Lower'] = kc_obj.keltner_channel_lband()
        
        return df
    
    def _add_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based indicators."""
        
        # Volume Moving Average
        df['Volume_SMA_10'] = ta.trend.sma_indicator(df['volume'], window=10)
        df['Volume_SMA_20'] = ta.trend.sma_indicator(df['volume'], window=20)
        
        # OBV (On-Balance Volume)
        df['OBV'] = ta.volume.on_balance_volume(df['close'], df['volume'])
        
        # Money Flow Index
        df['MFI_14'] = ta.volume.money_flow_index(df['high'], df['low'], df['close'], df['volume'])
        
        # Accumulation/Distribution
        df['AD'] = ta.volume.acc_dist_index(df['high'], df['low'], df['close'], df['volume'])
        
        # Chaikin Money Flow
        df['CMF_20'] = ta.volume.chaikin_money_flow(df['high'], df['low'], df['close'], df['volume'])
        
        # Volume Ratio
        df['Volume_Ratio'] = df['Volume_SMA_10'].apply(lambda x: df['volume'] / x if x and x > 0 else 0)
        
        return df
    
    def _add_support_resistance(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add support and resistance levels."""
        
        # Pivot Points
        high = df['high'].rolling(window=5).max()
        low = df['low'].rolling(window=5).min()
        close = df['close'].rolling(window=5).mean()
        
        # Classic Pivot Points
        pivot = (high + low + close) / 3
        df['Pivot_Point'] = pivot
        df['Resistance_1'] = (2 * pivot) - low
        df['Support_1'] = (2 * pivot) - high
        df['Resistance_2'] = pivot + (high - low)
        df['Support_2'] = pivot - (high - low)
        
        # Price position relative to moving averages
        df['Price_vs_SMA20'] = (df['close'] - df['SMA_20']) / df['SMA_20'] * 100
        df['Price_vs_SMA50'] = (df['close'] - df['SMA_50']) / df['SMA_50'] * 100
        df['Price_vs_SMA200'] = (df['close'] - df['SMA_200']) / df['SMA_200'] * 100
        
        # Golden Cross / Death Cross
        df['MA_Cross_50_200'] = (df['SMA_50'] > df['SMA_200']).astype(int)
        
        return df
    
    def add_target_variable(
        self,
        df: pd.DataFrame,
        horizon: int = 1,
        direction_only: bool = True
    ) -> pd.DataFrame:
        """
        Add target variable for prediction.
        
        Args:
            df: DataFrame with price data
            horizon: Number of days to predict
            direction_only: If True, create binary classification (UP/DOWN)
                          If False, create regression target (actual return)
        
        Returns:
            DataFrame with target variable
        """
        df = df.copy()
        
        if direction_only:
            # Binary classification: 1 if price goes up, 0 if down
            df[f'Target_Dir_{horizon}D'] = (
                df['close'].shift(-horizon) > df['close']
            ).astype(int)
        else:
            # Regression: actual return
            df[f'Target_Return_{horizon}D'] = (
                df['close'].shift(-horizon) - df['close']
            ) / df['close'] * 100
        
        return df
    
    def get_feature_names(self) -> List[str]:
        """Get list of all technical indicator feature names."""
        return [
            # Trend indicators
            'SMA_5', 'SMA_10', 'SMA_20', 'SMA_50', 'SMA_100', 'SMA_200',
            'EMA_5', 'EMA_10', 'EMA_20', 'EMA_50', 'EMA_100', 'EMA_200',
            'MACD', 'MACD_Signal', 'MACD_Hist',
            'ADX', 'DI_Plus', 'DI_Minus',
            'PSAR',
            
            # Momentum indicators
            'RSI_7', 'RSI_14', 'RSI_21',
            'STOCH_K', 'STOCH_D',
            'WILLR',
            'CCI_20',
            'ROC_10', 'ROC_20',
            'MOM_10',
            
            # Volatility indicators
            'BB_Upper', 'BB_Middle', 'BB_Lower', 'BB_Width', 'BB_Pct',
            'ATR_7', 'ATR_14',
            'KC_Upper', 'KC_Middle', 'KC_Lower',
            
            # Volume indicators
            'Volume_SMA_10', 'Volume_SMA_20',
            'OBV', 'MFI_14', 'AD', 'CMF_20', 'Volume_Ratio',
            
            # Support/Resistance
            'Pivot_Point', 'Resistance_1', 'Support_1', 'Resistance_2', 'Support_2',
            'Price_vs_SMA20', 'Price_vs_SMA50', 'Price_vs_SMA200',
            'MA_Cross_50_200'
        ]
