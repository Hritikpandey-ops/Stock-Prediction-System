from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
import math

from config.database import SessionLocal
from src.database.repository import PriceRepository, FundamentalRepository, NewsSentimentRepository
from src.database.models import NewsSentiment
from src.analysis.fundamental_scorer import FundamentalScorer

router = APIRouter(prefix="/api/stocks", tags=["stocks"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SYMBOLS = [
    'RELIANCE', 'TCS', 'HDFCBANK', 'ICICIBANK', 'INFY', 'HINDUNILVR', 'ITC', 'SBIN',
    'BHARTIARTL', 'LT', 'KOTAKBANK', 'HCLTECH', 'AXISBANK', 'ASIANPAINT', 'MARUTI',
    'SUNPHARMA', 'TITAN', 'BAJFINANCE', 'WIPRO', 'ADANIENT', 'ADANIPORTS', 'APOLLOHOSP',
    'BAJAJ-AUTO', 'BAJAJFINSV', 'BPCL', 'BRITANNIA', 'CIPLA', 'COALINDIA', 'DIVISLAB',
    'DRREDDY', 'EICHERMOT', 'GRASIM', 'HDFCLIFE', 'HEROMOTOCO', 'HINDALCO', 'INDUSINDBK',
    'JSWSTEEL', 'M&M', 'NESTLEIND', 'NTPC', 'ONGC', 'POWERGRID', 'SBILIFE', 'SHRIRAMFIN',
    'TATACONSUM', 'TATAMOTORS', 'TATASTEEL', 'TECHM', 'TRENT', 'ULTRACEMCO'
]

PERIOD_MAP = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365, "2Y": 730}


def compute_sma(data, period):
    result = []
    for i in range(len(data)):
        if i < period - 1:
            result.append(None)
        else:
            result.append(round(sum(data[i - period + 1:i + 1]) / period, 2))
    return result


def compute_ema(data, period):
    k = 2 / (period + 1)
    result = []
    ema = data[0] if data else 0
    for i, val in enumerate(data):
        if i == 0:
            ema = val
        else:
            ema = val * k + ema * (1 - k)
        result.append(round(ema, 2))
    return result


def compute_rsi(data, period=14):
    if len(data) < period + 1:
        return [None] * len(data)
    gains, losses = [], []
    for i in range(1, len(data)):
        diff = data[i] - data[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    results = [None] * period
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(gains)):
        rs = avg_gain / avg_loss if avg_loss != 0 else 100
        results.append(round(100 - (100 / (1 + rs)), 2))
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    return [None] + results


def compute_macd(data):
    ema12 = compute_ema(data, 12)
    ema26 = compute_ema(data, 26)
    macd_line = [round(e12 - e26, 2) for e12, e26 in zip(ema12, ema26)]
    signal = [macd_line[0]]
    for i in range(1, len(macd_line)):
        signal.append(round(macd_line[i] * (2 / 10) + signal[-1] * (8 / 10), 2))
    histogram = [round(m - s, 2) for m, s in zip(macd_line, signal)]
    return macd_line, signal, histogram


def compute_bollinger(data, period=20):
    upper, middle, lower = [], [], []
    for i in range(len(data)):
        if i < period - 1:
            upper.append(None)
            middle.append(None)
            lower.append(None)
        else:
            window = data[i - period + 1:i + 1]
            sma = sum(window) / period
            variance = sum((x - sma) ** 2 for x in window) / period
            std = variance ** 0.5
            middle.append(round(sma, 2))
            upper.append(round(sma + 2 * std, 2))
            lower.append(round(sma - 2 * std, 2))
    return upper, middle, lower


def compute_atr(highs, lows, closes, period=14):
    if len(highs) < 2:
        return [None] * len(highs)
    tr = []
    for i in range(1, len(highs)):
        hl = highs[i] - lows[i]
        hc = abs(highs[i] - closes[i - 1])
        lc = abs(lows[i] - closes[i - 1])
        tr.append(max(hl, hc, lc))
    atr_values = [None]
    for i in range(len(tr)):
        if i < period - 1:
            atr_values.append(None)
        elif i == period - 1:
            atr_values.append(round(sum(tr[:period]) / period, 2))
        else:
            val = (atr_values[-1] * (period - 1) + tr[i]) / period
            atr_values.append(round(val, 2))
    return atr_values


def compute_stochastic(highs, lows, closes, k_period=14, d_period=3):
    k_vals, d_vals = [], []
    for i in range(len(closes)):
        if i < k_period - 1:
            k_vals.append(None)
            d_vals.append(None)
        else:
            hh = max(highs[i - k_period + 1:i + 1])
            ll = min(lows[i - k_period + 1:i + 1])
            if hh == ll:
                k_vals.append(50)
            else:
                k_vals.append(round(((closes[i] - ll) / (hh - ll)) * 100, 2))
    for i in range(len(k_vals)):
        if k_vals[i] is None or i < d_period - 1:
            d_vals.append(None)
        else:
            valid = [k_vals[j] for j in range(i - d_period + 1, i + 1) if k_vals[j] is not None]
            d_vals.append(round(sum(valid) / len(valid), 2) if valid else None)
    return k_vals, d_vals


def compute_obv(closes, volumes):
    obv = [volumes[0]] if volumes else [0]
    for i in range(1, len(closes)):
        if closes[i] > closes[i - 1]:
            obv.append(obv[-1] + volumes[i])
        elif closes[i] < closes[i - 1]:
            obv.append(obv[-1] - volumes[i])
        else:
            obv.append(obv[-1])
    return obv


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
    dates = [p.timestamp.isoformat() for p in sorted_p]
    opens = [float(p.open) for p in sorted_p]
    highs = [float(p.high) for p in sorted_p]
    lows = [float(p.low) for p in sorted_p]
    closes = [float(p.close) for p in sorted_p]
    volumes = [p.volume or 0 for p in sorted_p]

    sma20 = compute_sma(closes, 20)
    sma50 = compute_sma(closes, 50)
    sma200 = compute_sma(closes, min(200, len(closes)))
    ema12 = compute_ema(closes, 12)
    ema26 = compute_ema(closes, 26)
    ema200 = compute_ema(closes, min(200, len(closes)))
    rsi = compute_rsi(closes)
    macd_line, macd_signal, macd_hist = compute_macd(closes)
    bb_upper, bb_middle, bb_lower = compute_bollinger(closes)
    atr = compute_atr(highs, lows, closes)
    stoch_k, stoch_d = compute_stochastic(highs, lows, closes)
    obv = compute_obv(closes, volumes)

    latest = sorted_p[-1]
    prev = sorted_p[-2] if len(sorted_p) > 1 else None
    change_1d = ((closes[-1] - closes[-2]) / closes[-2] * 100) if len(closes) > 1 else 0
    change_1w = ((closes[-1] - closes[-6]) / closes[-6] * 100) if len(closes) > 6 else 0
    change_1m = ((closes[-1] - closes[-22]) / closes[-22] * 100) if len(closes) > 22 else 0
    period_high = max(highs)
    period_low = min(lows)
    avg_vol = round(sum(volumes) / len(volumes))
    avg_vol_10 = round(sum(volumes[-10:]) / min(10, len(volumes)))
    vol_ratio = round(avg_vol_10 / avg_vol, 2) if avg_vol > 0 else 1

    price_changes = []
    if len(closes) > 1:
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
            "sma20": sma20[i],
            "sma50": sma50[i],
            "sma200": sma200[i],
            "ema12": ema12[i],
            "ema26": ema26[i],
            "ema200": ema200[i],
            "rsi": rsi[i],
            "macd": macd_line[i],
            "macd_signal": macd_signal[i],
            "macd_hist": macd_hist[i],
            "bb_upper": bb_upper[i],
            "bb_middle": bb_middle[i],
            "bb_lower": bb_lower[i],
            "atr": atr[i],
            "stoch_k": stoch_k[i],
            "stoch_d": stoch_d[i],
            "obv": obv[i],
        })

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
        "rsi": rsi[-1] if rsi else None,
        "macd": macd_line[-1] if macd_line else None,
        "macd_signal": macd_signal[-1] if macd_signal else None,
        "macd_hist": macd_hist[-1] if macd_hist else None,
        "atr": atr[-1] if atr else None,
        "stoch_k": stoch_k[-1] if stoch_k else None,
        "stoch_d": stoch_d[-1] if stoch_d else None,
        "bb_upper": bb_upper[-1] if bb_upper else None,
        "bb_middle": bb_middle[-1] if bb_middle else None,
        "bb_lower": bb_lower[-1] if bb_lower else None,
        "sma20": sma20[-1] if sma20 else None,
        "sma50": sma50[-1] if sma50 else None,
        "sma200": sma200[-1] if sma200 else None,
        "ema200": ema200[-1] if ema200 else None,
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
                "date": p.timestamp.isoformat(),
                "open": float(p.open),
                "high": float(p.high),
                "low": float(p.low),
                "close": float(p.close),
                "volume": p.volume or 0,
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
    volumes = [p.volume or 0 for p in sorted_p]

    rsi = compute_rsi(closes)
    macd_line, macd_signal, macd_hist = compute_macd(closes)
    bb_upper, bb_middle, bb_lower = compute_bollinger(closes)
    sma20 = compute_sma(closes, 20)
    sma50 = compute_sma(closes, 50)
    ema12 = compute_ema(closes, 12)
    ema26 = compute_ema(closes, 26)
    atr = compute_atr(highs, lows, closes)
    stoch_k, stoch_d = compute_stochastic(highs, lows, closes)
    obv = compute_obv(closes, volumes)

    return {
        "rsi": rsi,
        "macd": macd_line,
        "macd_signal": macd_signal,
        "macd_histogram": macd_hist,
        "bb_upper": bb_upper,
        "bb_middle": bb_middle,
        "bb_lower": bb_lower,
        "sma20": sma20,
        "sma50": sma50,
        "ema12": ema12,
        "ema26": ema26,
        "atr": atr,
        "stoch_k": stoch_k,
        "stoch_d": stoch_d,
        "obv": obv,
    }


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
    # Search for both symbol and clean symbol (without .NS/.BSE)
    clean_symbol = symbol.replace('.NS', '').replace('.BSE', '')
    news = repo.get_by_symbol(symbol=clean_symbol, limit=limit)
    
    # If no news found for clean symbol, try the original symbol
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