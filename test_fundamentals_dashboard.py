"""
Standalone Fundamentals Dashboard Test
Demonstrates the dashboard with mock data
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

st.set_page_config(
    page_title="Fundamentals Dashboard - Test",
    page_icon="🏢",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    .score-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-box {
        background: white;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


def get_mock_fundamentals():
    return {
        'symbol': 'RELIANCE',
        'company_name': 'Reliance Industries Limited',
        'sector': 'Energy',
        'industry': 'Oil & Gas Refining & Marketing',
        'current_price': 2850.50,
        'market_cap': 1930000000000,
        'fifty_two_week_high': 2968.00,
        'fifty_two_week_low': 2215.00,
        'dividend_yield': 0.35,
        'shares_outstanding': 677000000,
        
        'pe_ratio': 28.5,
        'pb_ratio': 4.2,
        'peg_ratio': 1.3,
        'ev_ebitda': 14.5,
        'industry_pe': 22.0,
        
        'eps': 100.02,
        'roe': 8.50,
        'roce': 11.20,
        'net_profit_margin': 8.80,
        'operating_margin': 14.50,
        'ebitda': 147000000000,
        
        'revenue': 874760000000,
        'revenue_growth_1y': 16.8,
        'revenue_growth_3y': 11.5,
        'revenue_growth_5y': 8.2,
        
        'net_profit': 73950000000,
        'profit_growth_1y': 12.3,
        'profit_growth_3y': 9.8,
        'profit_growth_5y': 7.5,
        
        'eps_growth_1y': 13.5,
        'eps_growth_3y': 10.2,
        'eps_growth_5y': 8.0,
        
        'total_debt': 357800000000,
        'debt_to_equity': 0.62,
        'interest_coverage': 5.8,
        
        'current_assets': 296500000000,
        'current_liabilities': 248700000000,
        'current_ratio': 1.19,
        'cash_and_equivalents': 184000000000,
        'free_cash_flow': 10500000000,
        'operating_cash_flow': 24600000000,
        
        'promoter_holding': 50.3,
        'fii_holding': 25.8,
        'dii_holding': 12.5,
        'public_holding': 11.4,
    }


def get_score_color(score):
    if score >= 80:
        return '#10b981'
    elif score >= 60:
        return '#22c55e'
    elif score >= 40:
        return '#eab308'
    else:
        return '#ef4444'


def calculate_mock_scores(fundamentals):
    profitability_score = 75.0
    growth_score = 80.0
    health_score = 70.0
    valuation_score = 65.0
    ownership_score = 85.0
    
    overall = (profitability_score * 0.25 + 
               growth_score * 0.25 + 
               health_score * 0.20 + 
               valuation_score * 0.20 + 
               ownership_score * 0.10)
    
    return type('ScoreBreakdown', (), {
        'profitability': profitability_score,
        'growth': growth_score,
        'financial_health': health_score,
        'valuation': valuation_score,
        'ownership': ownership_score,
        'overall': overall
    })()


def show_overall_score(score):
    st.markdown(f"""
    <div class="main-header">
        <div style="font-size: 24px; margin-bottom: 10px;">Overall Fundamental Score</div>
        <div style="font-size: 72px; font-weight: bold;">{score.overall:.0f}/100</div>
        <div style="font-size: 24px; margin: 10px 0;">Grade: <span style="color: #fbbf24;">A-</span></div>
        <div style="font-size: 20px; padding: 10px 30px; background: #10b981; 
                    border-radius: 25px; display: inline-block; font-weight: bold;">
            BUY
        </div>
    </div>
    """, unsafe_allow_html=True)


def show_score_gauges(scores):
    col1, col2, col3, col4, col5 = st.columns(5)
    
    score_data = [
        (col1, scores.profitability, 'Profitability', '🟢'),
        (col2, scores.growth, 'Growth', '🔵'),
        (col3, scores.financial_health, 'Financial Health', '🟠'),
        (col4, scores.valuation, 'Valuation', '🟡'),
        (col5, scores.ownership, 'Ownership', '🟣')
    ]
    
    for col, score, name, icon in score_data:
        with col:
            color = get_score_color(score)
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
                    'bar': {'color': color, 'thickness': 0.3},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 30], 'color': '#fee2e2'},
                        {'range': [30, 50], 'color': '#fef3c7'},
                        {'range': [50, 70], 'color': '#d1fae5'},
                        {'range': [70, 100], 'color': '#dbeafe'}
                    ],
                },
                number={'suffix': '', 'font': {'size': 36, 'color': color}},
                title={'text': f"{icon} {name}", 'font': {'size': 14, 'color': '#374151'}}
            ))
            
            fig.update_layout(height=180, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})


def show_company_overview(fundamentals):
    st.markdown("**🏢 Company Overview**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**Name:** {fundamentals['company_name']}")
        st.markdown(f"**Sector:** {fundamentals['sector']}")
        st.markdown(f"**Industry:** {fundamentals['industry']}")
    
    with col2:
        st.markdown(f"**Current Price:** ₹{fundamentals['current_price']:.2f}")
        st.markdown(f"**Market Cap:** ₹{fundamentals['market_cap']/100000000000:.2f} L Cr")
        st.markdown(f"**Div Yield:** {fundamentals['dividend_yield']:.2f}%")
    
    with col3:
        st.markdown(f"**52W High:** ₹{fundamentals['fifty_two_week_high']:.2f}")
        st.markdown(f"**52W Low:** ₹{fundamentals['fifty_two_week_low']:.2f}")
        st.markdown(f"**Shares:** {fundamentals['shares_outstanding']/1000000:.2f}M")


def show_profitability_metrics(fundamentals):
    st.markdown("**📊 Profitability Metrics**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        (col1, 'ROE', fundamentals['roe'], '20%', 'Return on Equity'),
        (col2, 'ROCE', fundamentals['roce'], '20%', 'Return on Capital'),
        (col3, 'Net Margin', fundamentals['net_profit_margin'], '20%', 'Profit Margin'),
        (col4, 'EPS', fundamentals['eps'], '₹100', 'Earnings Per Share')
    ]
    
    for col, label, value, threshold, desc in metrics:
        with col:
            color = 'green' if (label in ['ROE', 'ROCE', 'Net Margin'] and value >= 15) else 'orange'
            st.markdown(f"""
            <div class="metric-box" style="border-left-color: {color};">
                <div style="font-size: 12px; color: gray;">{label}</div>
                <div style="font-size: 24px; font-weight: bold; color: {color};">{value:.1f}{'%' if label != 'EPS' else ''}</div>
                <div style="font-size: 10px; color: gray;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


def show_growth_metrics(fundamentals):
    st.markdown("**📈 Growth Metrics**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Revenue Growth**")
        rev_data = pd.DataFrame({
            'Period': ['1Y', '3Y CAGR', '5Y CAGR'],
            'Growth': [f"{fundamentals['revenue_growth_1y']:.1f}%", 
                      f"{fundamentals['revenue_growth_3y']:.1f}%", 
                      f"{fundamentals['revenue_growth_5y']:.1f}%"]
        })
        st.dataframe(rev_data, hide_index=True, use_container_width=True)
    
    with col2:
        st.markdown("**Profit Growth**")
        profit_data = pd.DataFrame({
            'Period': ['1Y', '3Y CAGR', '5Y CAGR'],
            'Growth': [f"{fundamentals['profit_growth_1y']:.1f}%", 
                      f"{fundamentals['profit_growth_3y']:.1f}%", 
                      f"{fundamentals['profit_growth_5y']:.1f}%"]
        })
        st.dataframe(profit_data, hide_index=True, use_container_width=True)
    
    with col3:
        st.markdown("**EPS Growth**")
        eps_data = pd.DataFrame({
            'Period': ['1Y', '3Y CAGR', '5Y CAGR'],
            'Growth': [f"{fundamentals['eps_growth_1y']:.1f}%", 
                      f"{fundamentals['eps_growth_3y']:.1f}%", 
                      f"{fundamentals['eps_growth_5y']:.1f}%"]
        })
        st.dataframe(eps_data, hide_index=True, use_container_width=True)


def show_financial_health(fundamentals):
    st.markdown("**💪 Financial Health**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        (col1, 'D/E Ratio', fundamentals['debt_to_equity'], '1.0', 'Debt to Equity'),
        (col2, 'ICR', fundamentals['interest_coverage'], '5x', 'Interest Coverage'),
        (col3, 'Current Ratio', fundamentals['current_ratio'], '1.5', 'Liquidity'),
        (col4, 'FCF', fundamentals['free_cash_flow']/10000000, '₹1000 Cr', 'Free Cash Flow')
    ]
    
    for col, label, value, threshold, desc in metrics:
        with col:
            color = 'green' if value <= 1.0 if label == 'D/E Ratio' else 'green' if value >= 1.5 else 'orange'
            st.markdown(f"""
            <div class="metric-box" style="border-left-color: {color};">
                <div style="font-size: 12px; color: gray;">{label}</div>
                <div style="font-size: 24px; font-weight: bold; color: {color};">{value:.2f}{'x' if label == 'ICR' else ' Cr' if label == 'FCF' else ''}</div>
                <div style="font-size: 10px; color: gray;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


def show_valuation_metrics(fundamentals):
    st.markdown("**💰 Valuation Metrics**")
    
    pe = fundamentals['pe_ratio']
    industry_pe = fundamentals['industry_pe']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**P/E Ratio Comparison**")
        
        diff = ((pe - industry_pe) / industry_pe * 100)
        color = 'green' if diff < 0 else 'red'
        assessment = 'Below Industry' if diff < 0 else 'Above Industry'
        
        st.markdown(f"""
        <div style="background: white; padding: 15px; border-radius: 10px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <div>
                    <div style="font-size: 12px; color: gray;">Stock P/E</div>
                    <div style="font-size: 28px; font-weight: bold;">{pe:.1f}</div>
                </div>
                <div>
                    <div style="font-size: 12px; color: gray;">Industry P/E</div>
                    <div style="font-size: 28px; font-weight: bold;">{industry_pe:.1f}</div>
                </div>
            </div>
            <div style="text-align: center; padding: 5px; background: {color}20; border-radius: 5px; color: {color}; font-weight: bold;">
                {assessment} ({diff:+.1f}%)
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("**Other Metrics**")
        
        val_data = pd.DataFrame({
            'Metric': ['P/B Ratio', 'EV/EBITDA', 'PEG Ratio'],
            'Value': [f"{fundamentals['pb_ratio']:.2f}", 
                     f"{fundamentals['ev_ebitda']:.1f}", 
                     f"{fundamentals['peg_ratio']:.2f}"],
            'Assessment': ['Fair', 'Fair', 'Reasonable']
        })
        st.dataframe(val_data, hide_index=True, use_container_width=True)
    
    with col3:
        assessment = "UNDERVALUED" if pe < industry_pe * 0.8 else "OVERVALUED" if pe > industry_pe * 1.2 else "FAIRLY VALUED"
        assessment_color = 'green' if 'UNDER' in assessment else 'red' if 'OVER' in assessment else 'orange'
        
        st.markdown("**Overall Valuation**")
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {assessment_color}20, {assessment_color}40); 
                    padding: 25px; border-radius: 10px; text-align: center; border: 2px solid {assessment_color};">
            <div style="font-size: 18px; color: {assessment_color}; font-weight: bold;">{assessment}</div>
        </div>
        """, unsafe_allow_html=True)


def show_shareholding_pattern(fundamentals):
    st.markdown("**👥 Shareholding Pattern**")
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "pie"}, {"type": "bar"}]],
        subplot_titles=['Current Holdings', 'Distribution']
    )
    
    fig.add_trace(
        go.Pie(
            labels=['Promoters', 'FIIs', 'DIIs', 'Public'],
            values=[fundamentals['promoter_holding'], fundamentals['fii_holding'], 
                   fundamentals['dii_holding'], fundamentals['public_holding']],
            marker=dict(colors=['#3b82f6', '#10b981', '#f59e0b', '#6b7280']),
            textinfo='label+percent',
            textposition='inside',
            hole=0.4
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=['Promoters', 'FIIs', 'DIIs', 'Public'],
            y=[fundamentals['promoter_holding'], fundamentals['fii_holding'],
              fundamentals['dii_holding'], fundamentals['public_holding']],
            marker_color=['#3b82f6', '#10b981', '#f59e0b', '#6b7280'],
            text=[f"{v:.1f}%" for v in [fundamentals['promoter_holding'], fundamentals['fii_holding'],
                                         fundamentals['dii_holding'], fundamentals['public_holding']]],
            textposition='outside'
        ),
        row=1, col=2
    )
    
    fig.update_layout(height=300, showlegend=False, margin=dict(l=0, r=0, t=50, b=0))
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def show_fundamentals_dashboard():
    fundamentals = get_mock_fundamentals()
    scores = calculate_mock_scores(fundamentals)
    
    show_overall_score(scores)
    
    st.markdown("---")
    
    show_score_gauges(scores)
    
    st.markdown("---")
    
    tabs = st.tabs(["📊 Overview", "📈 Growth", "💪 Health", "💰 Valuation", "👥 Ownership"])
    
    with tabs[0]:
        show_company_overview(fundamentals)
        st.empty()
        show_profitability_metrics(fundamentals)
    
    with tabs[1]:
        show_growth_metrics(fundamentals)
        
        st.markdown("**📊 Growth Trend**")
        fig = go.Figure()
        
        periods = ['1Y', '3Y CAGR', '5Y CAGR']
        rev_growth = [fundamentals['revenue_growth_1y'], fundamentals['revenue_growth_3y'], fundamentals['revenue_growth_5y']]
        profit_growth = [fundamentals['profit_growth_1y'], fundamentals['profit_growth_3y'], fundamentals['profit_growth_5y']]
        
        fig.add_trace(go.Bar(name='Revenue', x=periods, y=rev_growth, marker_color='#3b82f6'))
        fig.add_trace(go.Bar(name='Profit', x=periods, y=profit_growth, marker_color='#10b981'))
        
        fig.update_layout(barmode='group', height=300, template='plotly_white',
                         legend=dict(orientation="h", y=1.1))
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with tabs[2]:
        show_financial_health(fundamentals)
    
    with tabs[3]:
        show_valuation_metrics(fundamentals)
    
    with tabs[4]:
        show_shareholding_pattern(fundamentals)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #d1fae5, #a7f3d0); 
                    padding: 20px; border-radius: 10px; border: 2px solid #10b981;">
            <div style="font-size: 18px; font-weight: bold; color: #065f46; margin-bottom: 15px;">
                🟢 Bullish Factors
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.success("✓ Strong revenue growth of 16.8%")
        st.success("✓ Consistent profit growth over 3Y & 5Y")
        st.success("✓ Low debt levels (D/E: 0.62)")
        st.success("✓ Strong FII ownership (25.8%)")
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fee2e2, #fecaca); 
                    padding: 20px; border-radius: 10px; border: 2px solid #ef4444;">
            <div style="font-size: 18px; font-weight: bold; color: #991b1b; margin-bottom: 15px;">
                🔴 Bearish Factors
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.error("✗ Valuation above industry (P/E: 28.5 vs 22)")
        st.error("✗ ROE below 15%")


if __name__ == "__main__":
    show_fundamentals_dashboard()