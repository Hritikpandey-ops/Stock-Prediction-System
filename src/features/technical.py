"""
Technical indicator calculations using pandas_ta.
"""
import pandas as pd
import pandas_ta as ta
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
            df: DataFrame with OHLCV data (must have columns: Open, High, Low, Close, Volume)
            
        Returns:
            DataFrame with added technical indicators
        """
        df = df.copy()
        
        # Ensure proper column names for pandas_ta
        df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        }, inplace=True, errors='ignore')
        
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
            
            self.logger.info(f"Calculated {len([c for c in df.columns if c not in ['Open', 'High', 'Low', 'Close', 'Volume']])} technical indicators")
            
        except Exception as e:
            self.logger.error(f"Error calculating technical indicators: {str(e)}")
        
        return df
    
    def _add_trend_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add trend-following indicators."""
        
        # Moving Averages
        for period in [5, 10, 20, 50, 100, 200]:
            df[f'SMA_{period}'] = ta.sma(df['Close'], length=period)
            df[f'EMA_{period}'] = ta.ema(df['Close'], length=period)
        
        # MACD
        macd = ta.macd(df['Close'])
        if macd is not None:
            df['MACD'] = macd['MACD_12_26_9']
            df['MACD_Signal'] = macd['MACDs_12_26_9']
            df['MACD_Hist'] = macd['MACDh_12_26_9']
        
        # ADX (Trend Strength)
        adx = ta.adx(df['High'], df['Low'], df['Close'])
        if adx is not None:
            df['ADX'] = adx['ADX_14']
            df['DI_Plus'] = adx['DMP_14']
            df['DI_Minus'] = adx['DMN_14']
        
        # Parabolic SAR
        psar = ta.psar(df['High'], df['Low'], df['Close'])
        if psar is not None:
            df['PSAR'] = psar['PSARl_0.02_0.2']
        
        # Ichimoku Cloud
        ichimoku = ta.ichimoku(df['High'], df['Low'], df['Close'])
        if ichimoku is not None:
            df['Ichimoku_Conversion'] = ichimoku['IKC_9']
            df['Ichimoku_Base'] = ichimoku['IKS_26']
            df['Ichimoku_A'] = ichimoku['IKS_52']
            df['Ichimoku_B'] = ichimoku['IKD_9']
        
        return df
    
    def _add_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add momentum indicators."""
        
        # RSI
        df['RSI_14'] = ta.rsi(df['Close'], length=14)
        df['RSI_7'] = ta.rsi(df['Close'], length=7)
        df['RSI_21'] = ta.rsi(df['Close'], length=21)
        
        # Stochastic Oscillator
        stoch = ta.stoch(df['High'], df['Low'], df['Close'])
        if stoch is not None:
            df['STOCH_K'] = stoch['STOCHK_14_3_3']
            df['STOCH_D'] = stoch['STOCHD_14_3_3']
        
        # Williams %R
        willr = ta.willr(df['High'], df['Low'], df['Close'])
        if willr is not None:
            df['WILLR'] = willr['WILLR_14']
        
        # CCI (Commodity Channel Index)
        df['CCI_20'] = ta.cci(df['High'], df['Low'], df['Close'], length=20)
        
        # ROC (Rate of Change)
        df['ROC_10'] = ta.roc(df['Close'], length=10)
        df['ROC_20'] = ta.roc(df['Close'], length=20)
        
        # Momentum
        df['MOM_10'] = ta.mom(df['Close'], length=10)
        
        return df
    
    def _add_volatility_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volatility indicators."""
        
        # Bollinger Bands
        bbands = ta.bbands(df['Close'])
        if bbands is not None:
            df['BB_Upper'] = bbands['BBU_5_2.0']
            df['BB_Middle'] = bbands['BBM_5_2.0']
            df['BB_Lower'] = bbands['BBL_5_2.0']
            df['BB_Width'] = bbands['BBW_5_2.0']
            df['BB_Pct'] = bbands['BBP_5_2.0']
        
        # ATR (Average True Range)
        df['ATR_14'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        df['ATR_7'] = ta.atr(df['High'], df['Low'], df['Close'], length=7)
        
        # Standard Deviation
        df['StdDev_20'] = ta.stdev(df['Close'], length=20)
        
        # Historical Volatility
        df['HV_10'] = ta.cvi(df['Close'], length=10)
        df['HV_20'] = ta.cvi(df['Close'], length=20)
        
        # Keltner Channels
        kc = ta.kc(df['High'], df['Low'], df['Close'])
        if kc is not None:
            df['KC_Upper'] = kc['KCU_20_10_2.0']
            df['KC_Middle'] = kc['KCM_20_10_2.0']
            df['KC_Lower'] = kc['KCL_20_10_2.0']
        
        return df
    
    def _add_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based indicators."""
        
        # Volume Moving Average
        df['Volume_SMA_10'] = ta.sma(df['Volume'], length=10)
        df['Volume_SMA_20'] = ta.sma(df['Volume'], length=20)
        
        # OBV (On-Balance Volume)
        df['OBV'] = ta.obv(df['Close'], df['Volume'])
        
        # Volume Price Trend
        vpt = ta.vpt(df['Close'], df['Volume'])
        if vpt is not None:
            df['VPT'] = vpt['VPT']
        
        # Money Flow Index
        mfi = ta.mfi(df['High'], df['Low'], df['Close'], df['Volume'])
        if mfi is not None:
            df['MFI_14'] = mfi['MFI_14']
        
        # Accumulation/Distribution
        ad = ta.ad(df['High'], df['Low'], df['Close'], df['Volume'])
        if ad is not None:
            df['AD'] = ad['AD']
        
        # Chaikin Money Flow
        cmf = ta.cmf(df['High'], df['Low'], df['Close'], df['Volume'])
        if cmf is not None:
            df['CMF_20'] = cmf['CMF_20']
        
        # Volume Ratio
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA_10']
        
        return df
    
    def _add_support_resistance(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add support and resistance levels."""
        
        # Pivot Points
        high = df['High'].rolling(window=5).max()
        low = df['Low'].rolling(window=5).min()
        close = df['Close'].rolling(window=5).mean()
        
        # Classic Pivot Points
        pivot = (high + low + close) / 3
        df['Pivot_Point'] = pivot
        df['Resistance_1'] = (2 * pivot) - low
        df['Support_1'] = (2 * pivot) - high
        df['Resistance_2'] = pivot + (high - low)
        df['Support_2'] = pivot - (high - low)
        
        # Price position relative to moving averages
        df['Price_vs_SMA20'] = (df['Close'] - df['SMA_20']) / df['SMA_20'] * 100
        df['Price_vs_SMA50'] = (df['Close'] - df['SMA_50']) / df['SMA_50'] * 100
        df['Price_vs_SMA200'] = (df['Close'] - df['SMA_200']) / df['SMA_200'] * 100
        
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
                df['Close'].shift(-horizon) > df['Close']
            ).astype(int)
        else:
            # Regression: actual return
            df[f'Target_Return_{horizon}D'] = (
                df['Close'].shift(-horizon) - df['Close']
            ) / df['Close'] * 100
        
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
            'Ichimoku_Conversion', 'Ichimoku_Base', 'Ichimoku_A', 'Ichimoku_B',
            
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
            'StdDev_20',
            'HV_10', 'HV_20',
            'KC_Upper', 'KC_Middle', 'KC_Lower',
            
            # Volume indicators
            'Volume_SMA_10', 'Volume_SMA_20',
            'OBV', 'VPT', 'MFI_14', 'AD', 'CMF_20', 'Volume_Ratio',
            
            # Support/Resistance
            'Pivot_Point', 'Resistance_1', 'Support_1', 'Resistance_2', 'Support_2',
            'Price_vs_SMA20', 'Price_vs_SMA50', 'Price_vs_SMA200',
            'MA_Cross_50_200'
        ]