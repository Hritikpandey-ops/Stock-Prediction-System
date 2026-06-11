"""
Fundamentals Dashboard
Professional fundamental analysis with scoring system
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from typing import Dict, List
from src.analysis.fundamental_scorer import (
    FundamentalScorer,
    get_score_color,
    get_signal_label
)


def format_currency(value, in_crores=True):
    if value is None:
        return "N/A"
    
    if in_crores:
        if abs(value) >= 10000000:
            return f"₹{value/10000000:.2f} Cr"
        elif abs(value) >= 100000:
            return f"₹{value/100000:.2f} L"
        else:
            return f"₹{value:,.0f}"
    else:
        return f"₹{value:,.2f}"


def format_market_cap(value):
    if value is None:
        return "N/A"
    if value >= 100000000000:
        return f"₹{value/100000000000:.2f} L Cr"
    elif value >= 10000000:
        return f"₹{value/10000000:.2f} Cr"
    elif value >= 100000:
        return f"₹{value/100000:.2f} L"
    else:
        return f"₹{value:,.0f}"


def show_fundamental_score_gauge(score, title, color=None):
    if color is None:
        color = get_score_color(score)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
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
        delta={'reference': 50, 'increasing': {'color': 'green'}},
        number={'suffix': '', 'font': {'size': 48, 'color': color}},
        title={'text': title, 'font': {'size': 14, 'color': '#374151'}}
    ))
    
    fig.update_layout(
        height=180,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='white'
    )
    
    return fig


def show_score_breakdown(breakdown):
    categories = ['Profitability', 'Growth', 'Financial\nHealth', 'Valuation', 'Ownership']
    scores = [
        breakdown.profitability,
        breakdown.growth,
        breakdown.financial_health,
        breakdown.valuation,
        breakdown.ownership
    ]
    colors = [get_score_color(s) for s in scores]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=categories,
        y=scores,
        mode='lines+markers+text',
        marker=dict(size=20, color=colors),
        line=dict(width=3, color='gray'),
        text=[f'{s:.0f}' for s in scores],
        textposition='top center',
        textfont=dict(size=14, color='black'),
        fill='toself',
        fillcolor='rgba(59, 130, 246, 0.1)',
        name='Score'
    ))
    
    fig.update_layout(
        height=280,
        yaxis=dict(range=[0, 100], title='Score', gridcolor='lightgray'),
        xaxis=dict(title=''),
        template='plotly_white',
        showlegend=False,
        margin=dict(l=0, r=0, t=20, b=30)
    )
    
    return fig


def show_company_overview(fundamentals):
    st.markdown("**🏢 Company Overview**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**Name:** {fundamentals.get('company_name', 'N/A')}")
        st.markdown(f"**Sector:** {fundamentals.get('sector', 'N/A')}")
        st.markdown(f"**Industry:** {fundamentals.get('industry', 'N/A')}")
    
    with col2:
        price = fundamentals.get('current_price')
        st.markdown(f"**Current Price:** {'₹'+f'{price:.2f}' if price else 'N/A'}")
        mcap = fundamentals.get('market_cap')
        st.markdown(f"**Market Cap:** {format_market_cap(mcap) if mcap else 'N/A'}")
        div_yield = fundamentals.get('dividend_yield')
        st.markdown(f"**Div Yield:** {'{:.2f}%'.format(div_yield) if div_yield else 'N/A'}")
    
    with col3:
        high_52 = fundamentals.get('fifty_two_week_high')
        low_52 = fundamentals.get('fifty_two_week_low')
        st.markdown(f"**52W High:** {'₹'+f'{high_52:.2f}' if high_52 else 'N/A'}")
        st.markdown(f"**52W Low:** {'₹'+f'{low_52:.2f}' if low_52 else 'N/A'}")
        shares = fundamentals.get('shares_outstanding')
        st.markdown(f"**Shares:** {f'{shares/1000000:.2f}M' if shares else 'N/A'}")


def show_profitability_metrics(fundamentals):
    st.markdown("**📊 Profitability Metrics**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    roe = fundamentals.get('roe')
    roce = fundamentals.get('roce')
    npm = fundamentals.get('net_profit_margin')
    opm = fundamentals.get('operating_margin')
    eps = fundamentals.get('eps')
    
    with col1:
        color = 'green' if (roe and roe >= 15) else 'orange' if (roe and roe >= 10) else 'red'
        st.markdown(f"""
        <div style="background: white; padding: 15px; border-radius: 10px; border-left: 4px solid {color};">
            <div style="font-size: 12px; color: gray;">ROE</div>
            <div style="font-size: 24px; font-weight: bold; color: {color};">{roe:.1f}%</div>
            <div style="font-size: 10px; color: gray;">Return on Equity</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        color = 'green' if (roce and roce >= 15) else 'orange' if (roce and roce >= 10) else 'red'
        st.markdown(f"""
        <div style="background: white; padding: 15px; border-radius: 10px; border-left: 4px solid {color};">
            <div style="font-size: 12px; color: gray;">ROCE</div>
            <div style="font-size: 24px; font-weight: bold; color: {color};">{roce:.1f}%</div>
            <div style="font-size: 10px; color: gray;">Return on Capital</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        color = 'green' if (npm and npm >= 15) else 'orange' if (npm and npm >= 10) else 'red'
        st.markdown(f"""
        <div style="background: white; padding: 15px; border-radius: 10px; border-left: 4px solid {color};">
            <div style="font-size: 12px; color: gray;">Net Margin</div>
            <div style="font-size: 24px; font-weight: bold; color: {color};">{npm:.1f}%</div>
            <div style="font-size: 10px; color: gray;">Profit Margin</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        color = 'green' if (eps and eps >= 20) else 'orange' if (eps and eps >= 10) else 'red'
        st.markdown(f"""
        <div style="background: white; padding: 15px; border-radius: 10px; border-left: 4px solid {color};">
            <div style="font-size: 12px; color: gray;">EPS</div>
            <div style="font-size: 24px; font-weight: bold; color: {color};">₹{eps:.2f}</div>
            <div style="font-size: 10px; color: gray;">Earnings Per Share</div>
        </div>
        """, unsafe_allow_html=True)


def show_growth_metrics(fundamentals):
    st.markdown("**📈 Growth Metrics**")
    
    col1, col2, col3 = st.columns(3)
    
    rev_1y = fundamentals.get('revenue_growth_1y')
    rev_3y = fundamentals.get('revenue_growth_3y')
    rev_5y = fundamentals.get('revenue_growth_5y')
    
    profit_1y = fundamentals.get('profit_growth_1y')
    profit_3y = fundamentals.get('profit_growth_3y')
    profit_5y = fundamentals.get('profit_growth_5y')
    
    with col1:
        st.markdown("**Revenue Growth**")
        growth_data = pd.DataFrame({
            'Period': ['1Y', '3Y CAGR', '5Y CAGR'],
            'Growth': [
                f"{rev_1y:.1f}%" if rev_1y else "N/A",
                f"{rev_3y:.1f}%" if rev_3y else "N/A",
                f"{rev_5y:.1f}%" if rev_5y else "N/A"
            ]
        })
        st.dataframe(growth_data, hide_index=True, use_container_width=True)
    
    with col2:
        st.markdown("**Profit Growth**")
        profit_data = pd.DataFrame({
            'Period': ['1Y', '3Y CAGR', '5Y CAGR'],
            'Growth': [
                f"{profit_1y:.1f}%" if profit_1y else "N/A",
                f"{profit_3y:.1f}%" if profit_3y else "N/A",
                f"{profit_5y:.1f}%" if profit_5y else "N/A"
            ]
        })
        st.dataframe(profit_data, hide_index=True, use_container_width=True)
    
    with col3:
        eps_1y = fundamentals.get('eps_growth_1y')
        eps_3y = fundamentals.get('eps_growth_3y')
        eps_5y = fundamentals.get('eps_growth_5y')
        
        st.markdown("**EPS Growth**")
        eps_data = pd.DataFrame({
            'Period': ['1Y', '3Y CAGR', '5Y CAGR'],
            'Growth': [
                f"{eps_1y:.1f}%" if eps_1y else "N/A",
                f"{eps_3y:.1f}%" if eps_3y else "N/A",
                f"{eps_5y:.1f}%" if eps_5y else "N/A"
            ]
        })
        st.dataframe(eps_data, hide_index=True, use_container_width=True)


def show_financial_health(fundamentals):
    st.markdown("**💪 Financial Health**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    de = fundamentals.get('debt_to_equity')
    icr = fundamentals.get('interest_coverage')
    cr = fundamentals.get('current_ratio')
    fcf = fundamentals.get('free_cash_flow')
    
    with col1:
        color = 'green' if (de and de <= 1.0) else 'orange' if (de and de <= 2.0) else 'red'
        st.markdown(f"""
        <div style="background: white; padding: 15px; border-radius: 10px; border-left: 4px solid {color};">
            <div style="font-size: 12px; color: gray;">D/E Ratio</div>
            <div style="font-size: 24px; font-weight: bold; color: {color};">{de:.2f if de else 'N/A'}</div>
            <div style="font-size: 10px; color: gray;">Debt to Equity</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        color = 'green' if (icr and icr >= 5) else 'orange' if (icr and icr >= 2) else 'red'
        st.markdown(f"""
        <div style="background: white; padding: 15px; border-radius: 10px; border-left: 4px solid {color};">
            <div style="font-size: 12px; color: gray;">ICR</div>
            <div style="font-size: 24px; font-weight: bold; color: {color};">{icr:.1fx' if icr else 'N/A'}</div>
            <div style="font-size: 10px; color: gray;">Interest Coverage</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        color = 'green' if (cr and cr >= 1.5) else 'orange' if (cr and cr >= 1.0) else 'red'
        st.markdown(f"""
        <div style="background: white; padding: 15px; border-radius: 10px; border-left: 4px solid {color};">
            <div style="font-size: 12px; color: gray;">Current Ratio</div>
            <div style="font-size: 24px; font-weight: bold; color: {color};">{cr:.2f if cr else 'N/A'}</div>
            <div style="font-size: 10px; color: gray;">Liquidity</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        color = 'green' if (fcf and fcf > 0) else 'red'
        fcf_str = format_currency(fcf) if fcf else 'N/A'
        st.markdown(f"""
        <div style="background: white; padding: 15px; border-radius: 10px; border-left: 4px solid {color};">
            <div style="font-size: 12px; color: gray;">FCF</div>
            <div style="font-size: 20px; font-weight: bold; color: {color};">{fcf_str}</div>
            <div style="font-size: 10px; color: gray;">Free Cash Flow</div>
        </div>
        """, unsafe_allow_html=True)


def show_valuation_metrics(fundamentals):
    st.markdown("**💰 Valuation Metrics**")
    
    pe = fundamentals.get('pe_ratio')
    industry_pe = fundamentals.get('industry_pe')
    pb = fundamentals.get('pb_ratio')
    peg = fundamentals.get('peg_ratio')
    ev_ebitda = fundamentals.get('ev_ebitda')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**P/E Ratio Comparison**")
        
        if pe and industry_pe:
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
        else:
            st.info("P/E data not available")
    
    with col2:
        st.markdown("**Other Valuation Metrics**")
        
        val_data = pd.DataFrame({
            'Metric': ['P/B Ratio', 'EV/EBITDA', 'PEG Ratio'],
            'Value': [
                f"{pb:.2f}" if pb else "N/A",
                f"{ev_ebitda:.1f}" if ev_ebitda else "N/A",
                f"{peg:.2f}" if peg else "N/A"
            ],
            'Assessment': [
                'Attractive' if (pb and pb < 4) else 'Expensive' if (pb and pb > 6) else 'Fair',
                'Cheap' if (ev_ebitda and ev_ebitda < 12) else 'Fair' if (ev_ebitda and ev_ebitda < 20) else 'Expensive',
                'Reasonable' if (peg and peg < 1.5) else 'High'
            ]
        })
        
        def color_assessment(ass):
            if 'Attr' in ass or 'Reas' in ass or 'Cheap' in ass:
                return 'green'
            elif 'Fair' in ass:
                return 'orange'
            else:
                return 'red'
        
        st.dataframe(val_data, hide_index=True, use_container_width=True)
    
    with col3:
        assessment = "UNDERVALUED" if (pe and industry_pe and pe < industry_pe * 0.8) else \
                     "OVERVALUED" if (pe and industry_pe and pe > industry_pe * 1.2) else "FAIRLY VALUED"
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
    
    promoter = fundamentals.get('promoter_holding', 0)
    fii = fundamentals.get('fii_holding', 0)
    dii = fundamentals.get('dii_holding', 0)
    public = fundamentals.get('public_holding', 100 - promoter)
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "pie"}, {"type": "bar"}]],
        subplot_titles=['Current Holdings', 'Trend Analysis']
    )
    
    fig.add_trace(
        go.Pie(
            labels=['Promoters', 'FIIs', 'DIIs', 'Public'],
            values=[promoter, fii, dii, public],
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
            y=[promoter, fii, dii, public],
            marker_color=['#3b82f6', '#10b981', '#f59e0b', '#6b7280'],
            text=[f'{v:.1f}%' for v in [promoter, fii, dii, public]],
            textposition='outside'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        height=300,
        showlegend=False,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Promoters", f"{promoter:.1f}%", 
                   "High" if promoter >= 50 else "Low" if promoter < 30 else "Normal")
    with col2:
        st.metric("FIIs", f"{fii:.1f}%", 
                   "Strong" if fii >= 20 else "Weak" if fii < 10 else "Moderate")
    with col3:
        st.metric("DIIs", f"{dii:.1f}%", 
                   "Strong" if dii >= 15 else "Moderate")
    with col4:
        st.metric("Public", f"{public:.1f}%", 
                   "Low" if public < 40 else "High")


def show_cash_flow_analysis(fundamentals):
    st.markdown("**💵 Cash Flow Analysis**")
    
    ocf = fundamentals.get('operating_cash_flow')
    fcf = fundamentals.get('free_cash_flow')
    cash = fundamentals.get('cash_and_equivalents')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig = go.Figure(go.Indicator(
            mode="number",
            value=ocf if ocf else 0,
            number={'prefix': '₹', 'valueformat': ',.0f'},
            title={'text': "Operating Cash Flow", 'font': {'size': 14}},
            domain={'x': [0, 1], 'y': [0, 1]}
        ))
        fig.update_layout(height=150, margin=dict(l=0, r=0, t=30, b=0))
        fig.update_xaxis(visible=False)
        fig.update_yaxis(visible=False)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        quality = "Excellent" if (ocf and fcf and ocf > fcf > 0) else \
                  "Good" if (ocf and ocf > 0) else "Poor"
        color = 'green' if quality == "Excellent" else 'orange' if quality == "Good" else 'red'
        st.markdown(f"<div style='text-align: center; color: {color}; font-weight: bold;'>{quality} Quality</div>", 
                    unsafe_allow_html=True)
    
    with col2:
        fig = go.Figure(go.Indicator(
            mode="number",
            value=fcf if fcf else 0,
            number={'prefix': '₹', 'valueformat': ',.0f'},
            title={'text': "Free Cash Flow", 'font': {'size': 14}},
            domain={'x': [0, 1], 'y': [0, 1]}
        ))
        fig.update_layout(height=150, margin=dict(l=0, r=0, t=30, b=0))
        fig.update_xaxis(visible=False)
        fig.update_yaxis(visible=False)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        status = "Positive ✓" if (fcf and fcf > 0) else "Negative ✗"
        color = 'green' if fcf and fcf > 0 else 'red'
        st.markdown(f"<div style='text-align: center; color: {color}; font-weight: bold;'>{status}</div>", 
                    unsafe_allow_html=True)
    
    with col3:
        fig = go.Figure(go.Indicator(
            mode="number",
            value=cash if cash else 0,
            number={'prefix': '₹', 'valueformat': ',.0f'},
            title={'text': "Cash Reserves", 'font': {'size': 14}},
            domain={'x': [0, 1], 'y': [0, 1]}
        ))
        fig.update_layout(height=150, margin=dict(l=0, r=0, t=30, b=0))
        fig.update_xaxis(visible=False)
        fig.update_yaxis(visible=False)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        adequacy = "Strong" if (cash and ocf and cash > ocf * 0.5) else \
                   "Adequate" if (cash and cash > 0) else "Weak"
        color = 'green' if adequacy == "Strong" else 'orange' if adequacy == "Adequate" else 'red'
        st.markdown(f"<div style='text-align: center; color: {color}; font-weight: bold;'>{adequacy} Position</div>", 
                    unsafe_allow_html=True)


def show_bullish_bearish_factors(bullish_factors, bearish_factors):
    st.markdown("**🎯 Key Factors**")
    
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
        
        for factor in bullish_factors[:5]:
            st.success(factor)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fee2e2, #fecaca); 
                    padding: 20px; border-radius: 10px; border: 2px solid #ef4444;">
            <div style="font-size: 18px; font-weight: bold; color: #991b1b; margin-bottom: 15px;">
                🔴 Bearish Factors
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        for factor in bearish_factors[:5]:
            st.error(factor)


def show_investment_radar(score_breakdown):
    categories = ['Profitability', 'Growth', 'Financial\nHealth', 'Valuation', 'Ownership']
    values = [
        score_breakdown.profitability,
        score_breakdown.growth,
        score_breakdown.financial_health,
        score_breakdown.valuation,
        score_breakdown.ownership
    ]
    
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(59, 130, 246, 0.2)',
        line=dict(color='rgb(59, 130, 246)', width=2),
        marker=dict(size=8, color='rgb(59, 130, 246)'),
        name='Current Score'
    ))

    fig.add_trace(go.Scatterpolar(
        r=[80, 80, 80, 80, 80, 80],
        theta=categories + [categories[0]],
        mode='lines',
        line=dict(color='gray', width=1, dash='dash'),
        name='Target (80)'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        height=350,
        margin=dict(l=80, r=80, t=50, b=50)
    )

    return fig


def create_fundamentals_dashboard(fundamentals: Dict):
    if not fundamentals:
        st.error("No fundamental data available")
        return
    
    scorer = FundamentalScorer(fundamentals)
    score_breakdown, bullish_factors, bearish_factors = scorer.calculate_all_scores()
    overall_score = score_breakdown.overall
    grade = scorer.get_grade(overall_score)
    signal = get_signal_label(overall_score)
    signal_color = 'green' if 'BUY' in signal else 'orange' if 'HOLD' in signal else 'red'
    
    st.markdown("""
    <style>
    .fundamentals-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    .score-display {
        font-size: 72px;
        font-weight: bold;
        color: white;
    }
    .grade-display {
        font-size: 48px;
        font-weight: bold;
        color: #fbbf24;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="fundamentals-header">
        <div style="font-size: 24px; margin-bottom: 10px;">Overall Fundamental Score</div>
        <div class="score-display">{overall_score:.0f}/100</div>
        <div style="font-size: 24px; margin: 10px 0;">Grade: <span class="grade-display">{grade}</span></div>
        <div style="font-size: 20px; padding: 10px 30px; background: {signal_color}; 
                    border-radius: 25px; display: inline-block; font-weight: bold;">
            {signal}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    scores = [
        (score_breakdown.profitability, 'Profitability', '🟢'),
        (score_breakdown.growth, 'Growth', '🔵'),
        (score_breakdown.financial_health, 'Financial Health', '🟠'),
        (score_breakdown.valuation, 'Valuation', '🟡'),
        (score_breakdown.ownership, 'Ownership', '🟣')
    ]
    
    for col, (score, name, icon) in zip([col1, col2, col3, col4, col5], scores):
        with col:
            fig = show_fundamental_score_gauge(score, name)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview",
        "📈 Growth",
        "💪 Health",
        "💰 Valuation",
        "👥 Ownership"
    ])
    
    with tab1:
        show_company_overview(fundamentals)
        st.empty()
        show_profitability_metrics(fundamentals)
        st.empty()
        show_investment_radar(score_breakdown)
    
    with tab2:
        show_growth_metrics(fundamentals)
        st.empty()
        st.markdown("**📊 Growth Trend Analysis**")
        fig = show_growth_chart(fundamentals)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with tab3:
        show_financial_health(fundamentals)
        st.empty()
        show_cash_flow_analysis(fundamentals)
    
    with tab4:
        show_valuation_metrics(fundamentals)
    
    with tab5:
        show_shareholding_pattern(fundamentals)
    
    st.markdown("---")
    
    show_bullish_bearish_factors(bullish_factors, bearish_factors)


def show_growth_chart(fundamentals):
    periods = ['1Y', '3Y', '5Y']
    
    rev_growth = [
        fundamentals.get('revenue_growth_1y', 0) or 0,
        fundamentals.get('revenue_growth_3y', 0) or 0,
        fundamentals.get('revenue_growth_5y', 0) or 0
    ]
    
    profit_growth = [
        fundamentals.get('profit_growth_1y', 0) or 0,
        fundamentals.get('profit_growth_3y', 0) or 0,
        fundamentals.get('profit_growth_5y', 0) or 0
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Revenue Growth',
        x=periods,
        y=rev_growth,
        marker_color='#3b82f6',
        text=[f'{v:.1f}%' for v in rev_growth],
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        name='Profit Growth',
        x=periods,
        y=profit_growth,
        marker_color='#10b981',
        text=[f'{v:.1f}%' for v in profit_growth],
        textposition='outside'
    ))
    
    fig.update_layout(
        barmode='group',
        height=300,
        yaxis_title='Growth %',
        template='plotly_white',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=20, b=0)
    )
    
    return fig


def get_api_response_structure(fundamentals: Dict, score_breakdown, 
                               bullish_factors: List, bearish_factors: List) -> Dict:
    return {
        "status": "success",
        "data": {
            "symbol": fundamentals.get('symbol'),
            "company_name": fundamentals.get('company_name'),
            "sector": fundamentals.get('sector'),
            "industry": fundamentals.get('industry'),
            
            "overall_score": {
                "score": score_breakdown.overall,
                "grade": FundamentalScorer(fundamentals).get_grade(score_breakdown.overall),
                "signal": get_signal_label(score_breakdown.overall),
                "breakdown": {
                    "profitability": round(score_breakdown.profitability, 2),
                    "growth": round(score_breakdown.growth, 2),
                    "financial_health": round(score_breakdown.financial_health, 2),
                    "valuation": round(score_breakdown.valuation, 2),
                    "ownership": round(score_breakdown.ownership, 2)
                }
            },
            
            "price_info": {
                "current_price": fundamentals.get('current_price'),
                "market_cap": fundamentals.get('market_cap'),
                "fifty_two_week_high": fundamentals.get('fifty_two_week_high'),
                "fifty_two_week_low": fundamentals.get('fifty_two_week_low'),
                "dividend_yield": fundamentals.get('dividend_yield'),
                "shares_outstanding": fundamentals.get('shares_outstanding')
            },
            
            "profitability": {
                "roe": fundamentals.get('roe'),
                "roce": fundamentals.get('roce'),
                "net_profit_margin": fundamentals.get('net_profit_margin'),
                "operating_margin": fundamentals.get('operating_margin'),
                "eps": fundamentals.get('eps'),
                "interpretation": FundamentalScorer(fundamentals).get_interpretation('roe', fundamentals.get('roe', 0))
            },
            
            "growth": {
                "revenue_growth": {
                    "1y": fundamentals.get('revenue_growth_1y'),
                    "3y_cagr": fundamentals.get('revenue_growth_3y'),
                    "5y_cagr": fundamentals.get('revenue_growth_5y')
                },
                "profit_growth": {
                    "1y": fundamentals.get('profit_growth_1y'),
                    "3y_cagr": fundamentals.get('profit_growth_3y'),
                    "5y_cagr": fundamentals.get('profit_growth_5y')
                },
                "eps_growth": {
                    "1y": fundamentals.get('eps_growth_1y'),
                    "3y_cagr": fundamentals.get('eps_growth_3y'),
                    "5y_cagr": fundamentals.get('eps_growth_5y')
                }
            },
            
            "financial_health": {
                "debt_to_equity": fundamentals.get('debt_to_equity'),
                "interest_coverage": fundamentals.get('interest_coverage'),
                "current_ratio": fundamentals.get('current_ratio'),
                "cash_reserves": fundamentals.get('cash_and_equivalents'),
                "free_cash_flow": fundamentals.get('free_cash_flow'),
                "operating_cash_flow": fundamentals.get('operating_cash_flow')
            },
            
            "valuation": {
                "pe_ratio": fundamentals.get('pe_ratio'),
                "industry_pe": fundamentals.get('industry_pe'),
                "pb_ratio": fundamentals.get('pb_ratio'),
                "ev_ebitda": fundamentals.get('ev_ebitda'),
                "peg_ratio": fundamentals.get('peg_ratio'),
                "vs_industry": "undervalued" if (fundamentals.get('pe_ratio') and fundamentals.get('industry_pe') and 
                                                  fundamentals.get('pe_ratio') < fundamentals.get('industry_pe')) else "overvalued"
            },
            
            "ownership": {
                "promoter": fundamentals.get('promoter_holding'),
                "fii": fundamentals.get('fii_holding'),
                "dii": fundamentals.get('dii_holding'),
                "public": fundamentals.get('public_holding')
            },
            
            "factors": {
                "bullish": bullish_factors,
                "bearish": bearish_factors
            }
        },
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "data_source": "yfinance",
            "report_date": fundamentals.get('report_date').isoformat() if fundamentals.get('report_date') else None
        }
    }