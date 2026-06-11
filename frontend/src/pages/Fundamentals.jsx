import { useState, useEffect } from 'react';
import { getFundamentals, getSymbols } from '../services/api';
import FundamentalGauge from '../components/FundamentalGauge';
import RadarScore from '../components/RadarScore';
import { TrendingUp, TrendingDown, Building2, DollarSign, Activity, PieChart, Shield, BarChart3 } from 'lucide-react';

function formatCurrency(v) {
  if (v == null) return 'N/A';
  const abs = Math.abs(v);
  if (abs >= 1e11) return `₹${(v / 1e11).toFixed(2)} L Cr`;
  if (abs >= 1e8) return `₹${(v / 1e8).toFixed(2)} Cr`;
  if (abs >= 1e5) return `₹${(v / 1e5).toFixed(2)} L`;
  return `₹${Number(v).toLocaleString()}`;
}

function marketCapLabel(v) {
  if (v == null) return 'N/A';
  if (v >= 1e12) return `₹${(v / 1e12).toFixed(2)} T`;
  if (v >= 1e9) return `₹${(v / 1e9).toFixed(2)} K Cr`;
  if (v >= 1e7) return `₹${(v / 1e7).toFixed(2)} Cr`;
  return `₹${Number(v).toLocaleString()}`;
}

function getSignal(score) {
  if (score >= 80) return { label: 'STRONG BUY', color: 'bg-green-600' };
  if (score >= 65) return { label: 'BUY', color: 'bg-green-500' };
  if (score >= 50) return { label: 'HOLD', color: 'bg-yellow-500' };
  if (score >= 35) return { label: 'WEAK HOLD', color: 'bg-orange-500' };
  return { label: 'AVOID', color: 'bg-red-500' };
}

function getGrade(score) {
  if (score >= 90) return 'A+';
  if (score >= 80) return 'A';
  if (score >= 70) return 'B+';
  if (score >= 60) return 'B';
  if (score >= 50) return 'C+';
  if (score >= 40) return 'C';
  if (score >= 30) return 'D';
  return 'F';
}

function colored(value, opts = {}) {
  if (value == null) return 'text-slate-500';
  if (opts.invert) return value <= (opts.threshold ?? 0) ? 'text-green-400' : 'text-red-400';
  return value >= (opts.threshold ?? 0) ? 'text-green-400' : 'text-red-400';
}

function StatRow({ label, value, color, hint }) {
  return (
    <div className="flex justify-between items-center py-1.5 border-b border-slate-700/50 last:border-0">
      <div>
        <span className="text-xs text-slate-400">{label}</span>
        {hint && <span className="text-[10px] text-slate-600 ml-1">({hint})</span>}
      </div>
      <span className={`text-xs font-medium ${color || 'text-white'}`}>{value ?? 'N/A'}</span>
    </div>
  );
}

function Section({ title, icon: Icon, children, color = 'blue' }) {
  const borderColor = { blue: 'border-blue-700/50', green: 'border-green-700/50', purple: 'border-purple-700/50', orange: 'border-orange-700/50', cyan: 'border-cyan-700/50' }[color] || 'border-slate-700';
  return (
    <div className={`bg-slate-900 border ${borderColor} rounded-xl p-4`}>
      <h3 className="text-white font-bold text-sm mb-3 flex items-center gap-2">
        {Icon && <Icon size={16} className={`text-${color}-400`} />}
        {title}
      </h3>
      {children}
    </div>
  );
}

function DataTable({ items }) {
  return (
    <div className="divide-y divide-slate-700/50">
      {items.map((item, i) => (
        <div key={i} className="flex justify-between py-1.5 text-xs">
          <span className="text-slate-400">{item.label}</span>
          <span className={`font-medium ${item.color || 'text-white'}`}>{item.value ?? 'N/A'}</span>
        </div>
      ))}
    </div>
  );
}

export default function Fundamentals() {
  const [symbols, setSymbols] = useState([]);
  const [symbol, setSymbol] = useState('RELIANCE');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSymbols().then(r => setSymbols(r.data.symbols)).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    getFundamentals(symbol).then(r => setData(r.data)).catch(() => setData(null)).finally(() => setLoading(false));
  }, [symbol]);

  const f = data?.fundamentals || {};
  const score = data?.score;
  const breakdown = data?.score_breakdown;
  const bullish = data?.bullish_factors || [];
  const bearish = data?.bearish_factors || [];
  const signal = score ? getSignal(score) : null;
  const grade = score ? getGrade(score) : null;
  const price = f.current_price;

  const peColor = f.pe_ratio && f.industry_pe
    ? (f.pe_ratio <= f.industry_pe ? 'text-green-400' : 'text-red-400')
    : 'text-white';

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Building2 size={22} className="text-blue-400" /> {symbol}
            {f.company_name && <span className="text-sm text-slate-400 font-normal">- {f.company_name}</span>}
          </h1>
        </div>
        <select value={symbol} onChange={e => setSymbol(e.target.value)}
          className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm min-w-[120px]">
          {symbols.map(s => <option key={s} value={s}>{s}</option>)}
          {symbols.length === 0 && ['RELIANCE','TCS','HDFCBANK'].map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      {loading ? (
        <div className="text-center py-20 text-slate-400">Loading fundamentals...</div>
      ) : !data ? (
        <div className="text-center py-20 text-slate-500">No fundamental data available.<br/>Run <code className="text-blue-400">python scripts/fetch_fundamentals.py</code> first.</div>
      ) : (
        <>
          {/* Score Header */}
          <div className="bg-gradient-to-r from-blue-900 to-slate-800 rounded-xl p-6 text-center mb-6 border border-blue-700">
            <div className="text-slate-300 text-sm">Overall Fundamental Score</div>
            <div className="text-5xl font-bold text-white">{score?.toFixed(0) || 'N/A'}<span className="text-2xl text-slate-400">/100</span></div>
            <div className="text-2xl font-bold text-yellow-400 my-1">Grade: {grade || 'N/A'}</div>
            {signal && <div className={`inline-block px-6 py-1 rounded-full text-sm font-bold text-white ${signal.color}`}>{signal.label}</div>}
            {f.sector && <div className="text-xs text-slate-400 mt-2">{f.sector} | {f.industry}</div>}
          </div>

          {/* Gauges */}
          <div className="grid grid-cols-5 gap-2 mb-6">
            {breakdown && (
              <>
                <FundamentalGauge score={breakdown.profitability} label="Profitability" />
                <FundamentalGauge score={breakdown.growth} label="Growth" />
                <FundamentalGauge score={breakdown.financial_health} label="Health" />
                <FundamentalGauge score={breakdown.valuation} label="Valuation" />
                <FundamentalGauge score={breakdown.ownership} label="Ownership" />
              </>
            )}
          </div>

          {/* Radar + Key Info */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-slate-900 border border-slate-700 rounded-xl p-4">
              <RadarScore breakdown={breakdown || { profitability: 0, growth: 0, financial_health: 0, valuation: 0, ownership: 0 }} />
            </div>
            <div className="col-span-2 grid grid-cols-2 gap-4">
              <Section title="Company Info" icon={Building2} color="blue">
                <DataTable items={[
                  { label: 'Company', value: f.company_name },
                  { label: 'Sector', value: f.sector },
                  { label: 'Industry', value: f.industry },
                  { label: 'Symbol', value: f.symbol },
                  { label: 'Report Date', value: f.report_date?.slice(0, 10) },
                  { label: 'Period', value: f.period_type },
                ]} />
              </Section>
              <Section title="Market Snapshot" icon={DollarSign} color="green">
                <DataTable items={[
                  { label: 'Current Price', value: price ? `₹${Number(price).toFixed(2)}` : 'N/A', color: 'text-green-400' },
                  { label: 'Market Cap', value: marketCapLabel(f.market_cap), color: 'text-purple-400' },
                  { label: '52W High', value: f.fifty_two_week_high ? `₹${Number(f.fifty_two_week_high).toFixed(2)}` : 'N/A' },
                  { label: '52W Low', value: f.fifty_two_week_low ? `₹${Number(f.fifty_two_week_low).toFixed(2)}` : 'N/A' },
                  { label: 'Dividend Yield', value: f.dividend_yield != null ? `${f.dividend_yield.toFixed(2)}%` : 'N/A', color: 'text-yellow-400' },
                  { label: 'Shares Outstanding', value: f.shares_outstanding ? `${(f.shares_outstanding / 1e7).toFixed(2)} Cr` : 'N/A' },
                ]} />
              </Section>
            </div>
          </div>

          {/* Profitability + Growth */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <Section title="Profitability Metrics" icon={Activity} color="green">
              <DataTable items={[
                { label: 'ROE', value: f.roe != null ? `${f.roe.toFixed(1)}%` : 'N/A', color: colored(f.roe, { threshold: 15 }), hint: 'Return on Equity' },
                { label: 'ROCE', value: f.roce != null ? `${f.roce.toFixed(1)}%` : 'N/A', color: colored(f.roce, { threshold: 15 }), hint: 'Return on Capital' },
                { label: 'Net Profit Margin', value: f.net_profit_margin != null ? `${f.net_profit_margin.toFixed(1)}%` : 'N/A', color: colored(f.net_profit_margin, { threshold: 15 }) },
                { label: 'Operating Margin', value: f.operating_margin != null ? `${f.operating_margin.toFixed(1)}%` : 'N/A', color: colored(f.operating_margin, { threshold: 15 }) },
                { label: 'EPS', value: f.eps != null ? `₹${f.eps.toFixed(2)}` : 'N/A', color: colored(f.eps, { threshold: 20 }), hint: 'Earnings Per Share' },
                { label: 'EBITDA', value: formatCurrency(f.ebitda) },
              ]} />
            </Section>
            <Section title="Growth Rates" icon={TrendingUp} color="cyan">
              <DataTable items={[
                { label: 'Revenue 1Y', value: f.revenue_growth_1y != null ? `${f.revenue_growth_1y >= 0 ? '+' : ''}${f.revenue_growth_1y.toFixed(1)}%` : 'N/A', color: colored(f.revenue_growth_1y, { threshold: 0 }) },
                { label: 'Revenue 3Y CAGR', value: f.revenue_growth_3y != null ? `${f.revenue_growth_3y >= 0 ? '+' : ''}${f.revenue_growth_3y.toFixed(1)}%` : 'N/A', color: colored(f.revenue_growth_3y, { threshold: 0 }) },
                { label: 'Revenue 5Y CAGR', value: f.revenue_growth_5y != null ? `${f.revenue_growth_5y >= 0 ? '+' : ''}${f.revenue_growth_5y.toFixed(1)}%` : 'N/A', color: colored(f.revenue_growth_5y, { threshold: 0 }) },
                { label: 'Profit 1Y', value: f.profit_growth_1y != null ? `${f.profit_growth_1y >= 0 ? '+' : ''}${f.profit_growth_1y.toFixed(1)}%` : 'N/A', color: colored(f.profit_growth_1y, { threshold: 0 }) },
                { label: 'Profit 3Y CAGR', value: f.profit_growth_3y != null ? `${f.profit_growth_3y >= 0 ? '+' : ''}${f.profit_growth_3y.toFixed(1)}%` : 'N/A', color: colored(f.profit_growth_3y, { threshold: 0 }) },
                { label: 'Profit 5Y CAGR', value: f.profit_growth_5y != null ? `${f.profit_growth_5y >= 0 ? '+' : ''}${f.profit_growth_5y.toFixed(1)}%` : 'N/A', color: colored(f.profit_growth_5y, { threshold: 0 }) },
                { label: 'EPS Growth 1Y', value: f.eps_growth_1y != null ? `${f.eps_growth_1y >= 0 ? '+' : ''}${f.eps_growth_1y.toFixed(1)}%` : 'N/A', color: colored(f.eps_growth_1y, { threshold: 0 }) },
                { label: 'EPS Growth 3Y', value: f.eps_growth_3y != null ? `${f.eps_growth_3y >= 0 ? '+' : ''}${f.eps_growth_3y.toFixed(1)}%` : 'N/A', color: colored(f.eps_growth_3y, { threshold: 0 }) },
              ]} />
            </Section>
          </div>

          {/* Financial Health + Valuation */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <Section title="Financial Health" icon={Shield} color="orange">
              <DataTable items={[
                { label: 'Debt to Equity', value: f.debt_to_equity != null ? f.debt_to_equity.toFixed(2) : 'N/A', color: colored(f.debt_to_equity, { threshold: 1, invert: true }) },
                { label: 'Interest Coverage', value: f.interest_coverage != null ? `${f.interest_coverage.toFixed(1)}x` : 'N/A', color: colored(f.interest_coverage, { threshold: 5 }) },
                { label: 'Current Ratio', value: f.current_ratio != null ? f.current_ratio.toFixed(2) : 'N/A', color: colored(f.current_ratio, { threshold: 1.5 }), hint: 'Liquidity' },
                { label: 'Total Debt', value: formatCurrency(f.total_debt) },
                { label: 'Cash & Equivalents', value: formatCurrency(f.cash_and_equivalents) },
                { label: 'Free Cash Flow', value: formatCurrency(f.free_cash_flow), color: f.free_cash_flow > 0 ? 'text-green-400' : 'text-red-400' },
                { label: 'Operating Cash Flow', value: formatCurrency(f.operating_cash_flow), color: f.operating_cash_flow > 0 ? 'text-green-400' : 'text-red-400' },
                { label: 'Current Assets', value: formatCurrency(f.current_assets) },
                { label: 'Current Liabilities', value: formatCurrency(f.current_liabilities) },
              ]} />
            </Section>
            <Section title="Valuation Metrics" icon={BarChart3} color="purple">
              <DataTable items={[
                { label: 'P/E Ratio', value: f.pe_ratio != null ? f.pe_ratio.toFixed(1) : 'N/A', color: peColor },
                { label: 'Industry P/E', value: f.industry_pe != null ? f.industry_pe.toFixed(1) : 'N/A', color: 'text-blue-400' },
                { label: 'P/E vs Industry', value: f.pe_ratio && f.industry_pe ? `${(((f.pe_ratio - f.industry_pe) / f.industry_pe) * 100).toFixed(0)}%` : 'N/A', color: f.pe_ratio && f.industry_pe ? (f.pe_ratio <= f.industry_pe ? 'text-green-400' : 'text-red-400') : 'text-slate-500' },
                { label: 'P/B Ratio', value: f.pb_ratio != null ? f.pb_ratio.toFixed(2) : 'N/A', color: colored(f.pb_ratio, { threshold: 4, invert: true }) },
                { label: 'PEG Ratio', value: f.peg_ratio != null ? f.peg_ratio.toFixed(2) : 'N/A', color: colored(f.peg_ratio, { threshold: 1.5, invert: true }) },
                { label: 'EV/EBITDA', value: f.ev_ebitda != null ? f.ev_ebitda.toFixed(1) : 'N/A', color: f.ev_ebitda ? (f.ev_ebitda < 15 ? 'text-green-400' : 'text-red-400') : '' },
              ]} />
              {f.pe_ratio && f.industry_pe && (
                <div className="mt-3 pt-2 border-t border-slate-700">
                  <div className="text-[10px] text-slate-500 mb-1">P/E vs Industry</div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-slate-700 rounded-full h-2">
                      <div className="bg-blue-500 rounded-full h-2" style={{ width: `${Math.min(f.pe_ratio / f.industry_pe * 100, 200)}%` }} />
                    </div>
                    <span className={`text-xs font-bold ${peColor}`}>
                      {f.pe_ratio <= f.industry_pe ? 'Undervalued' : 'Overvalued'}
                    </span>
                  </div>
                </div>
              )}
            </Section>
          </div>

          {/* Revenue/Profit Fundamentals + Shareholding */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <Section title="Revenue & Profit" icon={DollarSign} color="green">
              <DataTable items={[
                { label: 'Total Revenue', value: formatCurrency(f.revenue) },
                { label: 'Net Profit', value: formatCurrency(f.net_profit) },
                { label: 'Revenue 1Y Growth', value: f.revenue_growth_1y != null ? `${f.revenue_growth_1y.toFixed(1)}%` : 'N/A', color: colored(f.revenue_growth_1y, { threshold: 0 }) },
                { label: 'Revenue 3Y CAGR', value: f.revenue_growth_3y != null ? `${f.revenue_growth_3y.toFixed(1)}%` : 'N/A', color: colored(f.revenue_growth_3y, { threshold: 10 }) },
                { label: 'Revenue 5Y CAGR', value: f.revenue_growth_5y != null ? `${f.revenue_growth_5y.toFixed(1)}%` : 'N/A', color: colored(f.revenue_growth_5y, { threshold: 10 }) },
                { label: 'Profit 1Y Growth', value: f.profit_growth_1y != null ? `${f.profit_growth_1y.toFixed(1)}%` : 'N/A', color: colored(f.profit_growth_1y, { threshold: 0 }) },
                { label: 'Profit 3Y CAGR', value: f.profit_growth_3y != null ? `${f.profit_growth_3y.toFixed(1)}%` : 'N/A', color: colored(f.profit_growth_3y, { threshold: 10 }) },
                { label: 'EPS', value: f.eps != null ? `₹${f.eps.toFixed(2)}` : 'N/A' },
                { label: 'EPS Growth 1Y', value: f.eps_growth_1y != null ? `${f.eps_growth_1y.toFixed(1)}%` : 'N/A', color: colored(f.eps_growth_1y, { threshold: 0 }) },
                { label: 'EPS Growth 3Y', value: f.eps_growth_3y != null ? `${f.eps_growth_3y.toFixed(1)}%` : 'N/A', color: colored(f.eps_growth_3y, { threshold: 10 }) },
              ]} />
            </Section>
            <Section title="Shareholding Pattern" icon={PieChart} color="purple">
              <DataTable items={[
                { label: 'Promoter Holding', value: f.promoter_holding != null ? `${f.promoter_holding.toFixed(1)}%` : 'N/A', color: colored(f.promoter_holding, { threshold: 50 }), hint: 'Ideal > 50%' },
                { label: 'FII Holding', value: f.fii_holding != null ? `${f.fii_holding.toFixed(1)}%` : 'N/A', color: colored(f.fii_holding, { threshold: 20 }), hint: 'Foreign Institutions' },
                { label: 'DII Holding', value: f.dii_holding != null ? `${f.dii_holding.toFixed(1)}%` : 'N/A', color: colored(f.dii_holding, { threshold: 15 }), hint: 'Domestic Institutions' },
                { label: 'Public Holding', value: f.public_holding != null ? `${f.public_holding.toFixed(1)}%` : 'N/A' },
              ]} />
              {f.promoter_holding != null && (
                <div className="mt-3 pt-2 border-t border-slate-700">
                  <div className="text-[10px] text-slate-500 mb-1">Promoter Confidence</div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-slate-700 rounded-full h-2.5">
                      <div className="bg-blue-500 rounded-full h-2.5" style={{ width: `${Math.min(f.promoter_holding, 100)}%` }} />
                    </div>
                    <span className={`text-xs font-bold ${f.promoter_holding >= 50 ? 'text-green-400' : f.promoter_holding >= 30 ? 'text-yellow-400' : 'text-red-400'}`}>
                      {f.promoter_holding.toFixed(0)}%
                    </span>
                  </div>
                </div>
              )}
              <div className="mt-3 grid grid-cols-4 gap-1">
                {[
                  { label: 'Promoter', val: f.promoter_holding, color: '#3b82f6' },
                  { label: 'FII', val: f.fii_holding, color: '#10b981' },
                  { label: 'DII', val: f.dii_holding, color: '#f59e0b' },
                  { label: 'Public', val: f.public_holding || f.promoter_holding != null ? (100 - (f.promoter_holding || 0) - (f.fii_holding || 0) - (f.dii_holding || 0)) : null, color: '#6b7280' },
                ].map(({ label, val, color }) => (
                  <div key={label} className="text-center">
                    <div className="text-[10px] text-slate-500">{label}</div>
                    <div className="text-xs font-bold" style={{ color }}>{val != null ? `${val.toFixed(0)}%` : '-'}</div>
                  </div>
                ))}
              </div>
            </Section>
          </div>

          {/* Bullish / Bearish Factors */}
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="bg-green-900/20 border border-green-700/50 rounded-xl p-4">
              <h3 className="text-green-400 font-bold text-sm mb-3 flex items-center gap-2"><TrendingUp size={16} /> Bullish Factors ({bullish.length})</h3>
              {bullish.length > 0 ? (
                <ul className="space-y-1">
                  {bullish.map((f, i) => <li key={i} className="text-green-300 text-xs flex items-start gap-1.5"><span className="text-green-400 mt-0.5 shrink-0">&#10003;</span>{f}</li>)}
                </ul>
              ) : <p className="text-slate-500 text-xs">No bullish factors identified</p>}
            </div>
            <div className="bg-red-900/20 border border-red-700/50 rounded-xl p-4">
              <h3 className="text-red-400 font-bold text-sm mb-3 flex items-center gap-2"><TrendingDown size={16} /> Bearish Factors ({bearish.length})</h3>
              {bearish.length > 0 ? (
                <ul className="space-y-1">
                  {bearish.map((f, i) => <li key={i} className="text-red-300 text-xs flex items-start gap-1.5"><span className="text-red-400 mt-0.5 shrink-0">&#10007;</span>{f}</li>)}
                </ul>
              ) : <p className="text-slate-500 text-xs">No bearish factors identified</p>}
            </div>
          </div>
        </>
      )}
    </div>
  );
}