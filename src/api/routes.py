from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
import pandas as pd
import ta

from config.database import SessionLocal
from config.settings import get_settings
from src.database.repository import PriceRepository, FundamentalRepository, NewsSentimentRepository
from src.database.models import NewsSentiment
from src.analysis.fundamental_scorer import FundamentalScorer

router = APIRouter(prefix="/api/stocks", tags=["stocks"])

settings = get_settings()
SYMBOLS = settings.nifty50_symbols_clean

PERIOD_MAP = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365, "2Y": 730}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def compute_indicators(opens, highs, lows, closes, volumes):
    """Compute all technical indicators using the ta library."""
    import math
    n = len(closes)
    df = pd.DataFrame({
        'Open': opens, 'High': highs, 'Low': lows,
        'Close': closes, 'Volume': volumes
    })

    def _clean(val):
        """Convert inf/nan to None for JSON serialization."""
        if val is None:
            return None
        try:
            if math.isinf(val) or math.isnan(val):
                return None
            return val
        except (TypeError, ValueError):
            return None

    indicators = {}

    # SMA — needs at least 'period' data points
    for period in [20, 50, 200]:
        col = f'SMA_{period}'
        df[col] = ta.trend.sma_indicator(df['Close'], window=period) if n >= period else pd.Series([None] * n)
        indicators[f'sma{period}'] = [_clean(v) for v in df[col].tolist()]

    # EMA
    for period in [12, 26, 200]:
        col = f'EMA_{period}'
        df[col] = ta.trend.ema_indicator(df['Close'], window=period) if n >= period else pd.Series([None] * n)
        indicators[f'ema{period}'] = [_clean(v) for v in df[col].tolist()]

    # RSI — needs at least 15 data points
    df['RSI_14'] = ta.momentum.rsi(df['Close'], window=14) if n >= 15 else pd.Series([None] * n)
    indicators['rsi'] = [_clean(v) for v in df['RSI_14'].tolist()]

    # MACD — needs at least 26 data points
    if n >= 26:
        macd_obj = ta.trend.MACD(df['Close'])
        df['MACD'] = macd_obj.macd()
        df['MACD_Signal'] = macd_obj.macd_signal()
        df['MACD_Hist'] = macd_obj.macd_diff()
    else:
        df['MACD'] = pd.Series([None] * n)
        df['MACD_Signal'] = pd.Series([None] * n)
        df['MACD_Hist'] = pd.Series([None] * n)
    indicators['macd'] = [_clean(v) for v in df['MACD'].tolist()]
    indicators['macd_signal'] = [_clean(v) for v in df['MACD_Signal'].tolist()]
    indicators['macd_hist'] = [_clean(v) for v in df['MACD_Hist'].tolist()]

    # Bollinger Bands — needs at least 20 data points
    if n >= 20:
        bb_obj = ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2)
        df['BB_Upper'] = bb_obj.bollinger_hband()
        df['BB_Middle'] = bb_obj.bollinger_mavg()
        df['BB_Lower'] = bb_obj.bollinger_lband()
    else:
        df['BB_Upper'] = pd.Series([None] * n)
        df['BB_Middle'] = pd.Series([None] * n)
        df['BB_Lower'] = pd.Series([None] * n)
    indicators['bb_upper'] = [_clean(v) for v in df['BB_Upper'].tolist()]
    indicators['bb_middle'] = [_clean(v) for v in df['BB_Middle'].tolist()]
    indicators['bb_lower'] = [_clean(v) for v in df['BB_Lower'].tolist()]

    # ATR — needs at least 14 data points
    if n >= 14:
        df['ATR_14'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], window=14)
    else:
        df['ATR_14'] = pd.Series([None] * n)
    indicators['atr'] = [_clean(v) for v in df['ATR_14'].tolist()]

    # Stochastic — needs at least 14 data points
    if n >= 14:
        stoch_obj = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'])
        df['STOCH_K'] = stoch_obj.stoch()
        df['STOCH_D'] = stoch_obj.stoch_signal()
    else:
        df['STOCH_K'] = pd.Series([None] * n)
        df['STOCH_D'] = pd.Series([None] * n)
    indicators['stoch_k'] = [_clean(v) for v in df['STOCH_K'].tolist()]
    indicators['stoch_d'] = [_clean(v) for v in df['STOCH_D'].tolist()]

    # OBV — works with any data length
    df['OBV'] = ta.volume.on_balance_volume(df['Close'], df['Volume'])
    indicators['obv'] = [_clean(v) for v in df['OBV'].tolist()]

    return indicators


@router.get("")
def list_stocks():
    return {"symbols": SYMBOLS}


@router.get("/{symbol}/full")
def get_full_data(symbol: str, period: str = Query("1Y", regex="^(1M|3M|6M|1Y|2Y)$"), db: Session = Depends(get_db)):
    symbol = symbol.upper()
    if symbol not in SYMBOLS:
        raise HTTPException(404, "Symbol not found")
    repo = PriceRepository(db)
    days = PERIOD_MAP.get(period, 365)
    prices = repo.get_by_symbol(symbol, start_date=datetime.now() - timedelta(days=days))
    if not prices:
        return {"prices": [], "indicators": {}, "stats": {}}

    sorted_p = sorted(prices, key=lambda x: x.timestamp)
    # Strip timezone info for JSON serialization
    dates = [p.timestamp.replace(tzinfo=None).isoformat() for p in sorted_p]
    opens = [float(p.open) for p in sorted_p]
    highs = [float(p.high) for p in sorted_p]
    lows = [float(p.low) for p in sorted_p]
    closes = [float(p.close) for p in sorted_p]
    volumes = [int(p.volume or 0) for p in sorted_p]

    indicators = compute_indicators(opens, highs, lows, closes, volumes)

    change_1d = ((closes[-1] - closes[-2]) / closes[-2] * 100) if len(closes) > 1 else 0
    change_1w = ((closes[-1] - closes[-6]) / closes[-6] * 100) if len(closes) > 6 else 0
    change_1m = ((closes[-1] - closes[-22]) / closes[-22] * 100) if len(closes) > 22 else 0
    period_high = max(highs)
    period_low = min(lows)
    avg_vol = round(sum(volumes) / len(volumes))
    avg_vol_10 = round(sum(volumes[-10:]) / min(10, len(volumes)))
    vol_ratio = round(avg_vol_10 / avg_vol, 2) if avg_vol > 0 else 1

    price_changes = []
    for i in range(len(closes)):
        if i == 0:
            price_changes.append(0)
        else:
            price_changes.append(round((closes[i] - closes[i - 1]) / closes[i - 1] * 100, 2))

    up_days = sum(1 for c in price_changes if c > 0)
    down_days = sum(1 for c in price_changes if c < 0)

    merged = []
    for i in range(len(dates)):
        merged.append({
            "date": dates[i],
            "open": opens[i],
            "high": highs[i],
            "low": lows[i],
            "close": closes[i],
            "volume": volumes[i],
            "change": price_changes[i] if i < len(price_changes) else 0,
            "sma20": indicators['sma20'][i],
            "sma50": indicators['sma50'][i],
            "sma200": indicators['sma200'][i],
            "ema12": indicators['ema12'][i],
            "ema26": indicators['ema26'][i],
            "ema200": indicators['ema200'][i],
            "rsi": indicators['rsi'][i],
            "macd": indicators['macd'][i],
            "macd_signal": indicators['macd_signal'][i],
            "macd_hist": indicators['macd_hist'][i],
            "bb_upper": indicators['bb_upper'][i],
            "bb_middle": indicators['bb_middle'][i],
            "bb_lower": indicators['bb_lower'][i],
            "atr": indicators['atr'][i],
            "stoch_k": indicators['stoch_k'][i],
            "stoch_d": indicators['stoch_d'][i],
            "obv": indicators['obv'][i],
        })

    def _safe(v):
        import math
        if v is None:
            return None
        try:
            if math.isinf(v) or math.isnan(v):
                return None
            return round(v, 2)
        except (TypeError, ValueError):
            return None

    stats = {
        "current_price": closes[-1] if closes else 0,
        "open": opens[-1] if opens else 0,
        "high": highs[-1] if highs else 0,
        "low": lows[-1] if lows else 0,
        "previous_close": closes[-2] if len(closes) > 1 else 0,
        "change_1d": round(change_1d, 2),
        "change_1w": round(change_1w, 2),
        "change_1m": round(change_1m, 2),
        "period_high": round(period_high, 2),
        "period_low": round(period_low, 2),
        "period_high_date": dates[highs.index(period_high)] if highs else None,
        "period_low_date": dates[lows.index(period_low)] if lows else None,
        "avg_volume": avg_vol,
        "avg_volume_10": avg_vol_10,
        "volume_ratio": vol_ratio,
        "total_volume": sum(volumes),
        "up_days": up_days,
        "down_days": down_days,
        "total_days": len(closes),
        "rsi": _safe(indicators['rsi'][-1]),
        "macd": _safe(indicators['macd'][-1]),
        "macd_signal": _safe(indicators['macd_signal'][-1]),
        "macd_hist": _safe(indicators['macd_hist'][-1]),
        "atr": _safe(indicators['atr'][-1]),
        "stoch_k": _safe(indicators['stoch_k'][-1]),
        "stoch_d": _safe(indicators['stoch_d'][-1]),
        "bb_upper": _safe(indicators['bb_upper'][-1]),
        "bb_middle": _safe(indicators['bb_middle'][-1]),
        "bb_lower": _safe(indicators['bb_lower'][-1]),
        "sma20": _safe(indicators['sma20'][-1]),
        "sma50": _safe(indicators['sma50'][-1]),
        "sma200": _safe(indicators['sma200'][-1]),
        "ema200": _safe(indicators['ema200'][-1]),
    }

    return {
        "prices": merged,
        "stats": stats,
    }


@router.get("/{symbol}/prices")
def get_prices(symbol: str, period: str = Query("1Y", regex="^(1M|3M|6M|1Y|2Y)$"), db: Session = Depends(get_db)):
    symbol = symbol.upper()
    if symbol not in SYMBOLS:
        raise HTTPException(404, "Symbol not found")
    repo = PriceRepository(db)
    days = PERIOD_MAP.get(period, 365)
    prices = repo.get_by_symbol(symbol, start_date=datetime.now() - timedelta(days=days))
    if not prices:
        return {"prices": []}
    return {
        "prices": [
            {
                "date": p.timestamp.replace(tzinfo=None).isoformat(),
                "open": float(p.open),
                "high": float(p.high),
                "low": float(p.low),
                "close": float(p.close),
                "volume": int(p.volume or 0),
            }
            for p in sorted(prices, key=lambda x: x.timestamp)
        ]
    }


@router.get("/{symbol}/indicators")
def get_indicators(symbol: str, period: str = Query("1Y", regex="^(1M|3M|6M|1Y|2Y)$"), db: Session = Depends(get_db)):
    symbol = symbol.upper()
    repo = PriceRepository(db)
    days = PERIOD_MAP.get(period, 365)
    prices = repo.get_by_symbol(symbol, start_date=datetime.now() - timedelta(days=days))
    if not prices:
        return {}
    sorted_p = sorted(prices, key=lambda x: x.timestamp)
    closes = [float(p.close) for p in sorted_p]
    highs = [float(p.high) for p in sorted_p]
    lows = [float(p.low) for p in sorted_p]
    opens = [float(p.open) for p in sorted_p]
    volumes = [int(p.volume or 0) for p in sorted_p]

    return compute_indicators(opens, highs, lows, closes, volumes)


@router.get("/fundamentals/all")
def get_all_fundamentals(db: Session = Depends(get_db)):
    repo = FundamentalRepository(db)
    stocks = []
    for symbol in SYMBOLS:
        fund = repo.get_latest_fundamentals(symbol)
        if fund:
            d = repo.fundamentals_to_dict(fund)
            scorer = FundamentalScorer(d)
            breakdown, _, _ = scorer.calculate_all_scores()
            stocks.append({
                "symbol": symbol,
                "company_name": d.get("company_name"),
                "score": round(breakdown.overall, 1),
                "current_price": d.get("current_price"),
                "pe_ratio": d.get("pe_ratio"),
                "roe": d.get("roe"),
                "roce": d.get("roce"),
                "debt_to_equity": d.get("debt_to_equity"),
                "market_cap": d.get("market_cap"),
                "eps": d.get("eps"),
                "net_profit_margin": d.get("net_profit_margin"),
                "pb_ratio": d.get("pb_ratio"),
                "dividend_yield": d.get("dividend_yield"),
            })
    return {"stocks": stocks}


@router.get("/{symbol}/fundamentals")
def get_fundamentals(symbol: str, db: Session = Depends(get_db)):
    symbol = symbol.upper()
    repo = FundamentalRepository(db)
    fund = repo.get_latest_fundamentals(symbol)
    if not fund:
        raise HTTPException(404, f"No fundamental data for {symbol}")

    fundamentals = repo.fundamentals_to_dict(fund)
    scorer = FundamentalScorer(fundamentals)
    breakdown, bullish, bearish = scorer.calculate_all_scores()

    return {
        "fundamentals": fundamentals,
        "score": round(breakdown.overall, 1),
        "score_breakdown": {
            "profitability": round(breakdown.profitability, 1),
            "growth": round(breakdown.growth, 1),
            "financial_health": round(breakdown.financial_health, 1),
            "valuation": round(breakdown.valuation, 1),
            "ownership": round(breakdown.ownership, 1),
        },
        "bullish_factors": bullish[:10],
        "bearish_factors": bearish[:10],
    }


@router.get("/{symbol}/news")
def get_stock_news(
    symbol: str,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get latest news articles for a specific stock symbol."""
    symbol = symbol.upper()
    if symbol not in SYMBOLS:
        raise HTTPException(404, "Symbol not found")
    repo = NewsSentimentRepository(db)
    clean_symbol = symbol.replace('.NS', '').replace('.BSE', '')
    news = repo.get_by_symbol(symbol=clean_symbol, limit=limit)

    if not news and symbol != clean_symbol:
        news = repo.get_by_symbol(symbol=symbol, limit=limit)
    return {
        "symbol": symbol,
        "count": len(news),
        "news": [
            {
                "id": n.id,
                "headline": n.headline,
                "source": n.source,
                "published_at": n.published_at.isoformat(),
                "sentiment_score": float(n.sentiment_score) if n.sentiment_score else None,
                "sentiment_label": n.sentiment_label,
                "url": n.url,
            }
            for n in news
        ]
    }


@router.get("/news/latest")
def get_latest_news(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get latest news articles across all Nifty 50 symbols."""
    repo = NewsSentimentRepository(db)
    news_items = repo.get_by_symbol(symbol=None, limit=limit)
    if not news_items:
        news_items = db.query(NewsSentiment).order_by(desc(NewsSentiment.published_at)).limit(limit).all()
    return {
        "count": len(news_items),
        "news": [
            {
                "id": n.id,
                "symbol": n.symbol,
                "headline": n.headline,
                "source": n.source,
                "published_at": n.published_at.isoformat(),
                "sentiment_score": float(n.sentiment_score) if n.sentiment_score else None,
                "sentiment_label": n.sentiment_label,
                "url": n.url,
            }
            for n in news_items
        ]
    }
