"""
Enhanced Stock Prediction Dashboard
Professional trading analysis with separated charts and better spacing
"""
import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.database import SessionLocal
from src.database.repository import PriceRepository
from sqlalchemy import text

# Page config
st.set_page_config(
    page_title="📈 Nifty 50 Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better spacing
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Chart containers with spacing */
    .chart-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 25px;
        margin: 25px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: none;
    }
    
    /* Metrics spacing */
    .stMetric {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;
        backdrop-filter: blur(10px);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1e3c72;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 30px;
        color: rgba(255, 255, 255, 0.7);
        font-size: 12px;
        margin-top: 40px;
    }
    
    /* Signal boxes */
    .signal-box {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        border: none;
    }
    
    /* Remove all dividers */
    hr {
        display: none !important;
    }
    
    /* Streamlit divider override */
    .stDivider {
        display: none;
    }
</style>
""", unsafe_allow_html=True)


def get_db():
    """Get database session."""
    try:
        return SessionLocal()
    except:
        return None


def load_price_data(symbol: str, days: int = 90) -> pd.DataFrame:
    """Load price data from database."""
    db = get_db()
    if not db:
        return pd.DataFrame()
    
    try:
        price_repo = PriceRepository(db)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        prices = price_repo.get_by_symbol(symbol, start_date, end_date)
        
        if not prices:
            return pd.DataFrame()
        
        df = pd.DataFrame([{
            'Date': p.timestamp,
            'Open': float(p.open),
            'High': float(p.high),
            'Low': float(p.low),
            'Close': float(p.close),
            'Volume': int(p.volume) if p.volume else 0
        } for p in prices])
        
        df = df.sort_values('Date').reset_index(drop=True)
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()
    finally:
        if db:
            db.close()


def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate comprehensive technical indicators."""
    if df.empty:
        return df
    
    # Moving Averages
    for period in [5, 10, 20, 50, 100, 200]:
        df[f'SMA_{period}'] = df['Close'].rolling(window=period).mean()
        df[f'EMA_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    
    # Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
    
    # ATR
    high_low = df['High'] - df['Low']
    high_close = abs(df['High'] - df['Close'].shift())
    low_close = abs(df['Low'] - df['Close'].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = true_range.rolling(14).mean()
    
    # Stochastic
    low_14 = df['Low'].rolling(14).min()
    high_14 = df['High'].rolling(14).max()
    df['Stoch_K'] = 100 * ((df['Close'] - low_14) / (high_14 - low_14))
    df['Stoch_D'] = df['Stoch_K'].rolling(3).mean()
    
    # VWAP
    df['VWAP'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()
    
    return df


def plot_price_chart(df: pd.DataFrame, symbol: str):
    """Create price chart with moving averages and Bollinger Bands."""
    if df.empty:
        return
    
    with st.container():
        st.markdown(f'**📊 {symbol} - Price Action with Moving Averages & Bollinger Bands**', help="Interactive price chart")
        
        fig = go.Figure()
        
        # Candlesticks
        fig.add_trace(go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC',
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        ))
        
        # Bollinger Bands
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['BB_Upper'],
            mode='lines',
            name='BB Upper',
            line=dict(color='rgba(255, 165, 0, 0.5)', width=1)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['BB_Lower'],
            mode='lines',
            name='BB Lower',
            line=dict(color='rgba(255, 165, 0, 0.5)', width=1),
            fill='tonexty',
            fillcolor='rgba(255, 165, 0, 0.05)'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['BB_Middle'],
            mode='lines',
            name='BB Middle (20 SMA)',
            line=dict(color='orange', width=1.5, dash='dash')
        ))
        
        # EMAs
        fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA_20'], mode='lines', name='EMA 20', 
                                line=dict(color='#2196F3', width=1.5)))
        fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA_50'], mode='lines', name='EMA 50', 
                                line=dict(color='#FF9800', width=1.5)))
        fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA_200'], mode='lines', name='EMA 200', 
                                line=dict(color='#9C27B0', width=2)))
        
        fig.update_layout(
            height=500,
            template='plotly_white',
            xaxis_rangeslider_visible=False,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=60, b=50),
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor="black",
                font_size=13,
                font_family="Arial",
                font_color="white"
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': f'{symbol}_chart',
                'height': 500,
                'width': 1200,
                'scale': 2
            }
        })


def plot_volume_chart(df: pd.DataFrame):
    """Create volume chart."""
    if df.empty:
        return
    
    with st.container():
        st.markdown('**📊 Trading Volume**')
        
        colors = ['#26a69a' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#ef5350' for i in range(len(df))]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df['Date'],
            y=df['Volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.7
        ))
        
        # Add volume moving average
        df['Vol_SMA'] = df['Volume'].rolling(20).mean()
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Vol_SMA'],
            mode='lines',
            name='Volume SMA (20)',
            line=dict(color='blue', width=2)
        ))
        
        fig.update_layout(
            height=250,
            template='plotly_white',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=50, b=50),
            hovermode="x unified",
            hoverlabel=dict(bgcolor="black", font_size=13, font_family="Arial", font_color="white")
        )
        
        st.plotly_chart(fig, use_container_width=True, config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d']
        })


def plot_rsi_chart(df: pd.DataFrame):
    """Create RSI chart."""
    if df.empty or 'RSI' not in df.columns:
        return
    
    with st.container():
        st.markdown('**📈 Relative Strength Index (RSI 14)**')
        
        fig = go.Figure()
        
        # RSI Line
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['RSI'],
            mode='lines',
            name='RSI',
            line=dict(color='#9C27B0', width=2.5)
        ))
        
        # Overbought line
        fig.add_hline(y=70, line_dash="dash", line_color="red", line_width=2)
        fig.add_hline(y=30, line_dash="dash", line_color="green", line_width=2)
        fig.add_hline(y=50, line_dash="dot", line_color="gray", line_width=1)
        
        # Fill overbought/oversold zones
        fig.add_hrect(y0=70, y1=100, fillcolor="red", opacity=0.1, line_width=0)
        fig.add_hrect(y0=0, y1=30, fillcolor="green", opacity=0.1, line_width=0)
        
        fig.update_layout(
            height=280,
            template='plotly_white',
            showlegend=False,
            yaxis=dict(range=[0, 100]),
            annotations=[
                dict(x=0, y=70.5, text="Overbought", showarrow=False, font=dict(color="red")),
                dict(x=0, y=29.5, text="Oversold", showarrow=False, font=dict(color="green"))
            ],
            margin=dict(l=0, r=0, t=50, b=50),
            hovermode="x unified",
            hoverlabel=dict(bgcolor="black", font_size=13, font_family="Arial", font_color="white")
        )
        
        st.plotly_chart(fig, use_container_width=True, config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d']
        })


def plot_macd_chart(df: pd.DataFrame):
    """Create MACD chart."""
    if df.empty or 'MACD' not in df.columns:
        return
    
    with st.container():
        st.markdown('**📉 MACD (12, 26, 9)**')
        
        fig = go.Figure()
        
        # MACD Line
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['MACD'],
            mode='lines',
            name='MACD',
            line=dict(color='#2196F3', width=2.5)
        ))
        
        # Signal Line
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['MACD_Signal'],
            mode='lines',
            name='Signal',
            line=dict(color='#FF9800', width=2.5)
        ))
        
        # MACD Histogram
        colors = ['#26a69a' if val >= 0 else '#ef5350' for val in df['MACD_Hist']]
        fig.add_trace(go.Bar(
            x=df['Date'],
            y=df['MACD_Hist'],
            name='Histogram',
            marker_color=colors,
            opacity=0.7
        ))
        
        fig.update_layout(
            height=300,
            template='plotly_white',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=50, b=50),
            hovermode="x unified",
            hoverlabel=dict(bgcolor="black", font_size=13, font_family="Arial", font_color="white")
        )
        
        st.plotly_chart(fig, use_container_width=True, config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d']
        })


def plot_stochastic_chart(df: pd.DataFrame):
    """Create Stochastic chart."""
    if df.empty or 'Stoch_K' not in df.columns:
        return
    
    with st.container():
        st.markdown('**🔄 Stochastic Oscillator (14, 3, 3)**')
        
        fig = go.Figure()
        
        # Stochastic %K
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Stoch_K'],
            mode='lines',
            name='%K',
            line=dict(color='#00BCD4', width=2.5)
        ))
        
        # Stochastic %D
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Stoch_D'],
            mode='lines',
            name='%D',
            line=dict(color='#FF5722', width=2.5)
        ))
        
        # Overbought/Oversold lines
        fig.add_hline(y=80, line_dash="dash", line_color="red", line_width=2)
        fig.add_hline(y=20, line_dash="dash", line_color="green", line_width=2)
        fig.add_hline(y=50, line_dash="dot", line_color="gray", line_width=1)
        
        # Fill zones
        fig.add_hrect(y0=80, y1=100, fillcolor="red", opacity=0.1, line_width=0)
        fig.add_hrect(y0=0, y1=20, fillcolor="green", opacity=0.1, line_width=0)
        
        fig.update_layout(
            height=280,
            template='plotly_white',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis=dict(range=[0, 100]),
            annotations=[
                dict(x=0, y=80.5, text="Overbought", showarrow=False, font=dict(color="red")),
                dict(x=0, y=19.5, text="Oversold", showarrow=False, font=dict(color="green"))
            ],
            margin=dict(l=0, r=0, t=50, b=50),
            hovermode="x unified",
            hoverlabel=dict(bgcolor="black", font_size=13, font_family="Arial", font_color="white")
        )
        
        st.plotly_chart(fig, use_container_width=True, config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d']
        })


def show_metrics(df: pd.DataFrame):
    """Display key metrics."""
    if df.empty:
        return
    
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    
    change = latest['Close'] - prev['Close']
    change_pct = (change / prev['Close']) * 100
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "📊 Close Price",
            f"₹{latest['Close']:.2f}",
            f"{change:+.2f} ({change_pct:+.2f}%)",
            delta_color="normal" if change >= 0 else "inverse"
        )
    
    with col2:
        rsi_val = latest.get('RSI', 0)
        status = "🔴" if rsi_val > 70 else "🟢" if rsi_val < 30 else "🟡"
        st.metric(f"{status} RSI (14)", f"{rsi_val:.1f}", 
                 "Overbought" if rsi_val > 70 else "Oversold" if rsi_val < 30 else "Neutral")
    
    with col3:
        macd_val = latest.get('MACD', 0)
        macd_hist = latest.get('MACD_Hist', 0)
        direction = "📈" if macd_val > latest.get('MACD_Signal', 0) else "📉"
        st.metric(f"{direction} MACD", f"{macd_val:.2f}", f"Hist: {macd_hist:+.2f}")
    
    with col4:
        stoch_k = latest.get('Stoch_K', 0)
        stoch_status = "🔴" if stoch_k > 80 else "🟢" if stoch_k < 20 else "🟡"
        st.metric(f"{stoch_status} Stochastic %K", f"{stoch_k:.1f}",
                 "Overbought" if stoch_k > 80 else "Oversold" if stoch_k < 20 else "Neutral")
    
    with col5:
        vol = latest['Volume']
        avg_vol = df['Volume'].mean()
        vol_change = ((vol - avg_vol) / avg_vol) * 100 if avg_vol > 0 else 0
        vol_status = "📈" if vol > avg_vol else "📉"
        st.metric(f"{vol_status} Volume", f"{vol:,}", f"{vol_change:+.1f}% vs avg")


def show_signal_summary(df: pd.DataFrame, symbol: str):
    """Show trading signals."""
    if df.empty:
        return
    
    st.markdown('<div class="signal-box">', unsafe_allow_html=True)
    st.markdown(f'### 🎯 Trading Signals for {symbol}')
    
    latest = df.iloc[-1]
    cols = st.columns(4)
    
    # RSI Signal
    rsi = latest['RSI']
    with cols[0]:
        if rsi > 70:
            signal = "🔴 SELL"
            color = "red"
        elif rsi < 30:
            signal = "🟢 BUY"
            color = "green"
        else:
            signal = "🟡 NEUTRAL"
            color = "orange"
        
        st.markdown(f"**RSI ({rsi:.1f})**")
        st.markdown(f"<h4 style='color: {color};'>{signal}</h4>", unsafe_allow_html=True)
    
    # MACD Signal
    macd = latest['MACD']
    macd_signal = latest['MACD_Signal']
    with cols[1]:
        if macd > macd_signal:
            signal = "🟢 BULLISH"
            color = "green"
        else:
            signal = "🔴 BEARISH"
            color = "red"
        
        st.markdown(f"**MACD ({macd:.2f})**")
        st.markdown(f"<h4 style='color: {color};'>{signal}</h4>", unsafe_allow_html=True)
    
    # Stochastic Signal
    stoch = latest['Stoch_K']
    with cols[2]:
        if stoch > 80:
            signal = "🔴 OVERBOUGHT"
            color = "red"
        elif stoch < 20:
            signal = "🟢 OVERSOLD"
            color = "green"
        else:
            signal = "🟡 NEUTRAL"
            color = "orange"
        
        st.markdown(f"**Stoch ({stoch:.1f})**")
        st.markdown(f"<h4 style='color: {color};'>{signal}</h4>", unsafe_allow_html=True)
    
    # Trend Signal
    ema_20 = latest['EMA_20']
    ema_50 = latest['EMA_50']
    price = latest['Close']
    
    with cols[3]:
        if price > ema_20 > ema_50:
            signal = "🟢 UPTREND"
            color = "green"
        elif price < ema_20 < ema_50:
            signal = "🔴 DOWNTREND"
            color = "red"
        else:
            signal = "🟡 SIDEWAYS"
            color = "orange"
        
        st.markdown(f"**Trend**")
        st.markdown(f"<h4 style='color: {color};'>{signal}</h4>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def show_daily_table(df: pd.DataFrame):
    """Show daily statistics table."""
    if df.empty:
        return
    
    with st.container():
        st.markdown('**📋 Recent Daily Data**')
        
        # Prepare data
        display_df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'MACD', 'Stoch_K']].tail(10).copy()
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
        display_df['Change %'] = ((display_df['Close'] - display_df['Open']) / display_df['Open'] * 100).round(2)
        
        # Format columns
        for col in ['Open', 'High', 'Low', 'Close']:
            display_df[col] = display_df[col].round(2)
        
        display_df['RSI'] = display_df['RSI'].round(1)
        display_df['MACD'] = display_df['MACD'].round(2)
        display_df['Stoch_K'] = display_df['Stoch_K'].round(1)
        display_df['Volume'] = display_df['Volume'].apply(lambda x: f"{x:,}")
        
        display_df = display_df.rename(columns={
            'Date': 'Date',
            'Open': 'Open',
            'High': 'High',
            'Low': 'Low',
            'Close': 'Close',
            'Volume': 'Volume',
            'Change %': 'Change %',
            'RSI': 'RSI',
            'MACD': 'MACD',
            'Stoch_K': 'Stoch'
        })
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)


def main():
    # Header
    st.markdown("""
    <div style='text-align: center; padding: 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 30px;'>
        <h1 style='color: white; margin: 0; font-size: 2.5rem;'>📈 Nifty 50 Trading Dashboard</h1>
        <p style='color: rgba(255,255,255,0.9); margin: 15px 0 0 0; font-size: 1.1rem;'>
            Professional Technical Analysis | Real-time Indicators | Trading Signals
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar - Filters
    with st.sidebar:
        st.markdown("### 🎛️ **Controls**")
        
        # Symbol selection
        st.markdown("**📌 Select Stock**")
        all_symbols = [
            "^NSEI", "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
            "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS", "LT.NS",
            "HCLTECH.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS",
            "TITAN.NS", "BAJFINANCE.NS", "WIPRO.NS", "ULTRACEMCO.NS", "TATASTEEL.NS",
            "ADANIENT.NS", "ADANIPORTS.NS", "NESTLEIND.NS", "BAJAJFINSV.NS", "TATACONSUM.NS",
            "DRREDDY.NS", "CIPLA.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "JSWSTEEL.NS",
            "COALINDIA.NS", "M&M.NS", "EICHERMOT.NS", "GRASIM.NS", "BRITANNIA.NS",
            "APOLLOHOSP.NS", "SHRIRAMFIN.NS", "HINDALCO.NS", "SBILIFE.NS", "HDFCLIFE.NS",
            "INDUSINDBK.NS", "PETRONET.NS", "VEDL.NS", "IDEA.NS", "FEDERALBNK.NS"
        ]
        
        selected_symbol = st.selectbox("Choose a stock", options=all_symbols, index=0)
        
        # Time range
        st.markdown("**📅 Time Range**")
        days = st.slider("Days to analyze", 7, 365, 90, step=7)
        st.markdown(f"**Showing last {days} days**")
        
        # Quick stats
        st.markdown("### 📊 **Database**")
        db = get_db()
        if db:
            try:
                total_stocks = db.execute(text("SELECT COUNT(DISTINCT symbol) FROM prices")).fetchone()[0]
                total_records = db.execute(text("SELECT COUNT(*) FROM prices")).fetchone()[0]
                latest_date = db.execute(text("SELECT MAX(timestamp) FROM prices")).fetchone()[0]
                
                st.success(f"**Stocks**: {total_stocks} | **Records**: {total_records:,}")
            except:
                st.warning("Stats unavailable")
            finally:
                db.close()
        else:
            st.error("DB offline")
        
        # Refresh
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    # Load data
    with st.spinner(f'Loading {selected_symbol} data...'):
        df = load_price_data(selected_symbol, days)
        df = calculate_all_indicators(df)
    
    if df.empty:
        st.error(f"No data available for {selected_symbol}")
        return
    
    # Show metrics
    show_metrics(df)
    
    # Signal summary
    show_signal_summary(df, selected_symbol)
    
    # Charts - Clean layout without dividers
    st.empty()  # This removes any extra spacing
    
    # 1. Price Chart
    plot_price_chart(df, selected_symbol)
    
    # 2. Volume Chart
    plot_volume_chart(df)
    
    # 3. RSI Chart
    plot_rsi_chart(df)
    
    # 4. MACD Chart
    plot_macd_chart(df)
    
    # 5. Stochastic Chart
    plot_stochastic_chart(df)
    
    # Daily Table
    show_daily_table(df)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p><strong>📈 Nifty 50 Trading Dashboard</strong> | Built with Streamlit & Plotly</p>
        <p>Data sourced from Yahoo Finance | For educational purposes only</p>
        <p style='margin-top: 10px;'><em>⚠️ Not financial advice. Always do your own research.</em></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()