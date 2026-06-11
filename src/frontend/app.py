"""
Main Application with Multi-Page Navigation
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.database import SessionLocal
from src.database.repository import PriceRepository, FundamentalRepository
from src.analysis.fundamental_scorer import FundamentalScorer, get_score_color, get_signal_label
from src.frontend.pages.fundamentals_dashboard import create_fundamentals_dashboard
from sqlalchemy import text

st.set_page_config(
    page_title="Nifty 50 Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

PAGES = {
    "📊 Technical Analysis": "technical",
    "🏢 Fundamentals Analysis": "fundamentals"
}

def main():
    st.markdown('<div class="main-header"><h1>📈 Nifty 50 Stock Analysis</h1></div>', unsafe_allow_html=True)
    
    page = st.sidebar.radio("Select Analysis Type", list(PAGES.keys()))
    
    if page == "📊 Technical Analysis":
        show_technical_analysis()
    else:
        show_fundamentals_page()

def show_technical_analysis():
    st.header("Technical Analysis Dashboard")
    
    try:
        db = SessionLocal()
        price_repo = PriceRepository(db)
        
        available_symbols = ['RELIANCE', 'TCS', 'HDFCBANK', 'ICICIBANK', 'INFY', 
                            'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'LT']
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            selected_symbol = st.selectbox("Select Stock", available_symbols)
            time_period = st.selectbox("Time Period", ["1M", "3M", "6M", "1Y", "2Y"])
        
        period_days = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365, "2Y": 730}
        days = period_days[time_period]
        
        prices = price_repo.get_by_symbol(
            selected_symbol,
            start_date=datetime.now() - timedelta(days=days)
        )
        
        if prices:
            df = pd.DataFrame([{
                'Date': p.timestamp,
                'Open': float(p.open),
                'High': float(p.high),
                'Low': float(p.low),
                'Close': float(p.close),
                'Volume': p.volume
            } for p in prices])
            
            df = df.sort_values('Date')
            
            col2_1, col2_2, col2_3, col2_4 = st.columns(4)
            
            latest_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2] if len(df) > 1 else latest_price
            change = ((latest_price - prev_price) / prev_price) * 100
            
            with col2_1:
                st.metric("Current Price", f"₹{latest_price:.2f}", 
                         f"{change:+.2f}%" if change else "N/A")
            with col2_2:
                st.metric("High", f"₹{df['High'].max():.2f}")
            with col2_3:
                st.metric("Low", f"₹{df['Low'].min():.2f}")
            with col2_4:
                st.metric("Volume", f"{df['Volume'].iloc[-1]:,}")
            
            st.plotly_chart(create_price_chart(df), use_container_width=True)
            
        else:
            st.info(f"No price data available for {selected_symbol}")
            
    except Exception as e:
        st.error(f"Error loading data: {e}")
    finally:
        db.close()

def create_price_chart(df):
    fig = go.Figure()
    
    fig.add_trace(go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price'
    ))
    
    fig.update_layout(
        height=500,
        template='plotly_white',
        xaxis_rangeslider_visible=False,
        margin=dict(l=0, r=0, t=50, b=50)
    )
    
    return fig

def show_fundamentals_page():
    st.header("Fundamentals Analysis")
    
    try:
        db = SessionLocal()
        fundamental_repo = FundamentalRepository(db)
        
        available_symbols = ['RELIANCE', 'TCS', 'HDFCBANK', 'ICICIBANK', 'INFY',
                            'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'LT']
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            selected_symbol = st.selectbox("Select Stock", available_symbols, key="fund_symbol")
            st.info("📌 Note: Fundamental data needs to be fetched first using the fetch_fundamentals.py script")
        
        with col2:
            fundamental = fundamental_repo.get_latest_fundamentals(selected_symbol)
            
            if fundamental:
                fundamentals_dict = fundamental_repo.fundamentals_to_dict(fundamental)
                create_fundamentals_dashboard(fundamentals_dict)
            else:
                st.warning(f"""
                No fundamental data available for {selected_symbol}. 
                
                To fetch fundamental data:
                1. Run: `python scripts/fetch_fundamentals.py`
                2. Wait for data collection to complete
                3. Refresh this page
                """)
                
                st.markdown("""
                ### Quick Guide to Fundamental Analysis
                
                Our fundamentals dashboard evaluates stocks across 5 key dimensions:
                
                1. **Profitability (25%)** - ROE, ROCE, Profit Margins, EPS
                2. **Growth (25%)** - Revenue, Profit, EPS growth rates
                3. **Financial Health (20%)** - Debt levels, Liquidity, Cash Flow
                4. **Valuation (20%)** - P/E, P/B, PEG ratios vs industry
                5. **Ownership (10%)** - Promoter, FII, DII holdings
                
                **Scoring:**
                - Score 80-100: Strong Buy
                - Score 65-80: Buy  
                - Score 50-65: Hold
                - Score 35-50: Weak Hold
                - Score Below 35: Avoid
                """)
                
    except Exception as e:
        st.error(f"Error loading fundamental data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()