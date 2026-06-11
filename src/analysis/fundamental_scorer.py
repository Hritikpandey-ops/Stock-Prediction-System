"""
Fundamental Scoring System
Calculates comprehensive scores for stock fundamentals
"""
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ScoreBreakdown:
    profitability: float
    growth: float
    financial_health: float
    valuation: float
    ownership: float
    
    @property
    def overall(self) -> float:
        return (
            self.profitability * 0.25 +
            self.growth * 0.25 +
            self.financial_health * 0.20 +
            self.valuation * 0.20 +
            self.ownership * 0.10
        )


class FundamentalScorer:
    WEIGHTS = {
        'profitability': 0.25,
        'growth': 0.25,
        'financial_health': 0.20,
        'valuation': 0.20,
        'ownership': 0.10
    }
    
    BENCHMARKS = {
        'roe': {'excellent': 20, 'good': 15, 'average': 10, 'poor': 0},
        'roce': {'excellent': 20, 'good': 15, 'average': 10, 'poor': 0},
        'net_profit_margin': {'excellent': 20, 'good': 15, 'average': 10, 'poor': 0},
        'operating_margin': {'excellent': 20, 'good': 15, 'average': 10, 'poor': 0},
        'debt_to_equity': {'excellent': 0.5, 'good': 1.0, 'average': 2.0, 'poor': 3.0},
        'current_ratio': {'excellent': 2.0, 'good': 1.5, 'average': 1.0, 'poor': 0.5},
        'pe_ratio': {'excellent': 15, 'good': 20, 'average': 25, 'poor': 40},
        'peg_ratio': {'excellent': 1.0, 'good': 1.5, 'average': 2.0, 'poor': 3.0},
        'pb_ratio': {'excellent': 2.0, 'good': 4.0, 'average': 6.0, 'poor': 10.0},
        'interest_coverage': {'excellent': 10, 'good': 5, 'average': 2, 'poor': 1},
        'free_cash_flow_positive': {'excellent': True, 'good': True, 'average': True, 'poor': False},
    }
    
    def __init__(self, fundamentals: Dict):
        self.fundamentals = fundamentals
        self.bullish_factors = []
        self.bearish_factors = []
    
    def score_profitability(self) -> float:
        score = 0
        count = 0
        
        roe = self.fundamentals.get('roe')
        if roe is not None:
            count += 1
            if roe >= 20:
                score += 100
                self.bullish_factors.append(f"✓ Strong ROE of {roe:.1f}% (above 20%)")
            elif roe >= 15:
                score += 80
                self.bullish_factors.append(f"✓ Good ROE of {roe:.1f}%")
            elif roe >= 10:
                score += 60
            else:
                score += 30
                self.bearish_factors.append(f"✗ Weak ROE of {roe:.1f}%")
        
        roce = self.fundamentals.get('roce')
        if roce is not None:
            count += 1
            if roce >= 20:
                score += 100
            elif roce >= 15:
                score += 80
            elif roce >= 10:
                score += 60
            else:
                score += 30
                self.bearish_factors.append(f"✗ Weak ROCE of {roce:.1f}%")
        
        npm = self.fundamentals.get('net_profit_margin')
        if npm is not None:
            count += 1
            if npm >= 20:
                score += 100
                self.bullish_factors.append(f"✓ Excellent profit margin of {npm:.1f}%")
            elif npm >= 15:
                score += 80
            elif npm >= 10:
                score += 60
            else:
                score += 30
                self.bearish_factors.append(f"✗ Low profit margin of {npm:.1f}%")
        
        opm = self.fundamentals.get('operating_margin')
        if opm is not None:
            count += 1
            if opm >= 25:
                score += 100
            elif opm >= 20:
                score += 80
            elif opm >= 15:
                score += 60
            else:
                score += 30
        
        eps = self.fundamentals.get('eps')
        if eps is not None and eps > 0:
            count += 1
            if eps >= 50:
                score += 100
            elif eps >= 20:
                score += 80
            elif eps >= 10:
                score += 60
            else:
                score += 40
        
        return score / count if count > 0 else 50
    
    def score_growth(self) -> float:
        score = 0
        count = 0
        
        rev_growth = self.fundamentals.get('revenue_growth_1y')
        if rev_growth is not None:
            count += 1
            if rev_growth >= 20:
                score += 100
                self.bullish_factors.append(f"✓ Strong revenue growth of {rev_growth:.1f}%")
            elif rev_growth >= 10:
                score += 80
            elif rev_growth >= 0:
                score += 50
            else:
                score += 20
                self.bearish_factors.append(f"✗ Revenue declining by {rev_growth:.1f}%")
        
        profit_growth = self.fundamentals.get('profit_growth_1y')
        if profit_growth is not None:
            count += 1
            if profit_growth >= 25:
                score += 100
            elif profit_growth >= 10:
                score += 80
            elif profit_growth >= 0:
                score += 50
            else:
                score += 20
                self.bearish_factors.append(f"✗ Profit declining by {profit_growth:.1f}%")
        
        eps_growth = self.fundamentals.get('eps_growth_1y')
        if eps_growth is not None:
            count += 1
            if eps_growth >= 20:
                score += 100
                self.bullish_factors.append(f"✓ Strong EPS growth of {eps_growth:.1f}%")
            elif eps_growth >= 10:
                score += 80
            elif eps_growth >= 0:
                score += 50
            else:
                score += 20
                self.bearish_factors.append(f"✗ EPS declining by {eps_growth:.1f}%")
        
        rev_growth_3y = self.fundamentals.get('revenue_growth_3y')
        if rev_growth_3y is not None:
            count += 1
            if rev_growth_3y >= 15:
                score += 100
                self.bullish_factors.append(f"✓ Consistent 3Y revenue CAGR of {rev_growth_3y:.1f}%")
            elif rev_growth_3y >= 10:
                score += 80
            elif rev_growth_3y >= 5:
                score += 60
            else:
                score += 30
        
        return score / count if count > 0 else 50
    
    def score_financial_health(self) -> float:
        score = 0
        count = 0
        
        de_ratio = self.fundamentals.get('debt_to_equity')
        if de_ratio is not None:
            count += 1
            if de_ratio <= 0.5:
                score += 100
                self.bullish_factors.append(f"✓ Very low debt (D/E: {de_ratio:.2f})")
            elif de_ratio <= 1.0:
                score += 80
            elif de_ratio <= 2.0:
                score += 50
            else:
                score += 20
                self.bearish_factors.append(f"✗ High leverage (D/E: {de_ratio:.2f})")
        
        current_ratio = self.fundamentals.get('current_ratio')
        if current_ratio is not None:
            count += 1
            if current_ratio >= 2.0:
                score += 100
                self.bullish_factors.append(f"✓ Strong liquidity (Current: {current_ratio:.2f})")
            elif current_ratio >= 1.5:
                score += 80
            elif current_ratio >= 1.0:
                score += 50
            else:
                score += 20
                self.bearish_factors.append(f"✗ Weak liquidity (Current: {current_ratio:.2f})")
        
        interest_coverage = self.fundamentals.get('interest_coverage')
        if interest_coverage is not None:
            count += 1
            if interest_coverage >= 10:
                score += 100
                self.bullish_factors.append(f"✓ Strong interest coverage ({interest_coverage:.1f}x)")
            elif interest_coverage >= 5:
                score += 80
            elif interest_coverage >= 2:
                score += 50
            else:
                score += 20
                self.bearish_factors.append(f"✗ Weak interest coverage ({interest_coverage:.1f}x)")
        
        fcf = self.fundamentals.get('free_cash_flow')
        if fcf is not None:
            count += 1
            if fcf > 0:
                score += 100
                self.bullish_factors.append(f"✓ Positive free cash flow")
            else:
                score += 20
                self.bearish_factors.append(f"✗ Negative free cash flow")
        
        ocf = self.fundamentals.get('operating_cash_flow')
        if ocf is not None and fcf is not None:
            count += 1
            if ocf > 0 and ocf >= fcf:
                score += 100
                self.bullish_factors.append(f"✓ Strong operating cash flow")
            elif ocf > 0:
                score += 70
            else:
                score += 30
        
        return score / count if count > 0 else 50
    
    def score_valuation(self) -> float:
        score = 0
        count = 0
        
        pe = self.fundamentals.get('pe_ratio')
        industry_pe = self.fundamentals.get('industry_pe') or 25
        
        if pe is not None:
            count += 1
            if pe <= industry_pe * 0.7:
                score += 100
                self.bullish_factors.append(f"✓ Valuation below industry (P/E: {pe:.1f} vs {industry_pe:.1f})")
            elif pe <= industry_pe:
                score += 80
            elif pe <= industry_pe * 1.3:
                score += 60
            elif pe <= industry_pe * 1.5:
                score += 40
            else:
                score += 20
                self.bearish_factors.append(f"✗ Valuation above industry (P/E: {pe:.1f} vs {industry_pe:.1f})")
        
        pb = self.fundamentals.get('pb_ratio')
        if pb is not None:
            count += 1
            if pb <= 2:
                score += 100
                self.bullish_factors.append(f"✓ Attractive P/B ratio ({pb:.1f})")
            elif pb <= 4:
                score += 80
            elif pb <= 6:
                score += 60
            else:
                score += 30
        
        peg = self.fundamentals.get('peg_ratio')
        if peg is not None:
            count += 1
            if peg <= 1:
                score += 100
                self.bullish_factors.append(f"✓ Reasonable PEG ratio ({peg:.1f})")
            elif peg <= 1.5:
                score += 80
            elif peg <= 2:
                score += 60
            else:
                score += 30
                self.bearish_factors.append(f"✗ High PEG ratio ({peg:.1f})")
        
        ev_ebitda = self.fundamentals.get('ev_ebitda')
        if ev_ebitda is not None:
            count += 1
            if ev_ebitda <= 10:
                score += 100
            elif ev_ebitda <= 15:
                score += 80
            elif ev_ebitda <= 20:
                score += 60
            else:
                score += 30
        
        return score / count if count > 0 else 50
    
    def score_ownership(self) -> float:
        score = 0
        count = 0
        
        promoter = self.fundamentals.get('promoter_holding')
        if promoter is not None:
            count += 1
            if 50 <= promoter <= 75:
                score += 100
                self.bullish_factors.append(f"✓ Healthy promoter holding ({promoter:.1f}%)")
            elif promoter > 75:
                score += 70
            elif promoter >= 30:
                score += 60
            else:
                score += 30
                self.bearish_factors.append(f"✗ Low promoter holding ({promoter:.1f}%)")
        
        fii = self.fundamentals.get('fii_holding')
        if fii is not None:
            count += 1
            if fii >= 30:
                score += 100
                self.bullish_factors.append(f"✓ Strong FII ownership ({fii:.1f}%)")
            elif fii >= 20:
                score += 80
            elif fii >= 10:
                score += 60
            else:
                score += 40
        
        dii = self.fundamentals.get('dii_holding')
        if dii is not None:
            count += 1
            if dii >= 15:
                score += 100
            elif dii >= 10:
                score += 80
            elif dii >= 5:
                score += 60
            else:
                score += 40
        
        return score / count if count > 0 else 50
    
    def calculate_all_scores(self) -> Tuple[ScoreBreakdown, List[str], List[str]]:
        profitability_score = self.score_profitability()
        growth_score = self.score_growth()
        health_score = self.score_financial_health()
        valuation_score = self.score_valuation()
        ownership_score = self.score_ownership()
        
        breakdown = ScoreBreakdown(
            profitability=profitability_score,
            growth=growth_score,
            financial_health=health_score,
            valuation=valuation_score,
            ownership=ownership_score
        )
        
        return breakdown, self.bullish_factors, self.bearish_factors
    
    def get_grade(self, score: float) -> str:
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B+"
        elif score >= 60:
            return "B"
        elif score >= 50:
            return "C+"
        elif score >= 40:
            return "C"
        elif score >= 30:
            return "D"
        else:
            return "F"
    
    def get_interpretation(self, metric: str, value: float) -> str:
        interpretations = {
            'roe': {
                'excellent': 'Exceptional returns for shareholders',
                'good': 'Strong profitability',
                'average': 'Moderate returns',
                'poor': 'Weak profitability'
            },
            'roce': {
                'excellent': 'Efficient use of capital',
                'good': 'Good capital efficiency',
                'average': 'Average capital utilization',
                'poor': 'Inefficient capital use'
            },
            'debt_to_equity': {
                'excellent': 'Conservative capital structure',
                'good': 'Healthy leverage',
                'average': 'Moderate debt levels',
                'poor': 'Highly leveraged'
            },
            'pe_ratio': {
                'excellent': 'Attractively valued',
                'good': 'Reasonably valued',
                'average': 'Fairly valued',
                'poor': 'Expensively valued'
            }
        }
        
        if metric not in interpretations:
            return 'N/A'
        
        return interpretations[metric].get(self._get_rating(metric, value), 'N/A')
    
    def _get_rating(self, metric: str, value: float) -> str:
        if metric == 'roe':
            if value >= 20: return 'excellent'
            elif value >= 15: return 'good'
            elif value >= 10: return 'average'
            else: return 'poor'
        elif metric == 'debt_to_equity':
            if value <= 0.5: return 'excellent'
            elif value <= 1.0: return 'good'
            elif value <= 2.0: return 'average'
            else: return 'poor'
        elif metric == 'pe_ratio':
            if value <= 15: return 'excellent'
            elif value <= 20: return 'good'
            elif value <= 25: return 'average'
            else: return 'poor'
        
        return 'average'


def get_score_color(score: float) -> str:
    if score >= 80:
        return '#10b981'
    elif score >= 60:
        return '#22c55e'
    elif score >= 40:
        return '#eab308'
    elif score >= 30:
        return '#f97316'
    else:
        return '#ef4444'


def get_signal_label(score: float) -> str:
    if score >= 80:
        return "STRONG BUY"
    elif score >= 65:
        return "BUY"
    elif score >= 50:
        return "HOLD"
    elif score >= 35:
        return "WEAK HOLD"
    else:
        return "AVOID"