import { useState, useEffect } from 'react';
import { getAllFundamentals } from '../services/api';
import { SkeletonTable } from '../components/SkeletonLoader';
import { Search } from 'lucide-react';

function getScoreColor(score) {
  if (score >= 80) return 'text-green-400';
  if (score >= 60) return 'text-green-500';
  if (score >= 40) return 'text-yellow-400';
  if (score >= 30) return 'text-orange-400';
  return 'text-red-400';
}

function getScoreBg(score) {
  if (score >= 80) return 'bg-green-900/40';
  if (score >= 60) return 'bg-green-800/30';
  if (score >= 40) return 'bg-yellow-900/30';
  if (score >= 30) return 'bg-orange-900/30';
  return 'bg-red-900/30';
}

function colored(value, opts = {}) {
  if (value == null) return 'text-slate-500';
  if (opts.invert) return value <= (opts.threshold ?? 0) ? 'text-green-400' : 'text-red-400';
  return value >= (opts.threshold ?? 0) ? 'text-green-400' : 'text-red-400';
}

export default function Screener() {
  const [stocks, setStocks] = useState([]);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('score');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAllFundamentals().then(r => {
      setStocks(r.data.stocks || []);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const filtered = stocks
    .filter(s => s.symbol?.toLowerCase().includes(search.toLowerCase()) || s.company_name?.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => {
      if (sortBy === 'score') return (b.score || 0) - (a.score || 0);
      if (sortBy === 'pe') return (a.pe_ratio || 999) - (b.pe_ratio || 999);
      if (sortBy === 'roe') return (b.roe || 0) - (a.roe || 0);
      if (sortBy === 'roce') return (b.roce || 0) - (a.roce || 0);
      if (sortBy === 'mcap') return (b.market_cap || 0) - (a.market_cap || 0);
      if (sortBy === 'de') return (a.debt_to_equity || 999) - (b.debt_to_equity || 999);
      return 0;
    });

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Stock Screener</h1>
          <p className="text-slate-400 text-sm">Screen all Nifty 50 stocks by key fundamentals — {filtered.length} stocks</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input type="text" placeholder="Search stock..." value={search} onChange={e => setSearch(e.target.value)}
              className="bg-slate-800 border border-slate-600 rounded-lg pl-9 pr-4 py-2 text-white text-sm w-48 focus:outline-none focus:border-blue-500" />
          </div>
          <select value={sortBy} onChange={e => setSortBy(e.target.value)}
            className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm">
            <option value="score">Score (high-low)</option>
            <option value="pe">P/E (low-high)</option>
            <option value="roe">ROE (high-low)</option>
            <option value="roce">ROCE (high-low)</option>
            <option value="de">D/E (low-high)</option>
            <option value="mcap">Mkt Cap (high-low)</option>
          </select>
        </div>
      </div>

      {loading ? (
        <SkeletonTable rows={10} cols={8} />
      ) : (
        <div className="bg-slate-900 border border-slate-700 rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-700 bg-slate-800/50">
                  <th className="text-left px-3 py-2.5 text-slate-400 font-medium">Symbol</th>
                  <th className="text-left px-3 py-2.5 text-slate-400 font-medium">Company</th>
                  <th className="text-center px-3 py-2.5 text-slate-400 font-medium">Score</th>
                  <th className="text-right px-3 py-2.5 text-slate-400 font-medium">Price</th>
                  <th className="text-right px-3 py-2.5 text-slate-400 font-medium">Mkt Cap</th>
                  <th className="text-right px-3 py-2.5 text-slate-400 font-medium">P/E</th>
                  <th className="text-right px-3 py-2.5 text-slate-400 font-medium">ROE</th>
                  <th className="text-right px-3 py-2.5 text-slate-400 font-medium">ROCE</th>
                  <th className="text-right px-3 py-2.5 text-slate-400 font-medium">NPM</th>
                  <th className="text-right px-3 py-2.5 text-slate-400 font-medium">EPS</th>
                  <th className="text-right px-3 py-2.5 text-slate-400 font-medium">P/B</th>
                  <th className="text-right px-3 py-2.5 text-slate-400 font-medium">D/E</th>
                  <th className="text-right px-3 py-2.5 text-slate-400 font-medium">Div Yld</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((s, i) => (
                  <tr key={s.symbol || i} className="border-b border-slate-700/50 hover:bg-slate-800/30 transition-colors">
                    <td className="px-3 py-2.5 font-bold text-white">{s.symbol}</td>
                    <td className="px-3 py-2.5 text-slate-300 max-w-[180px] truncate">{s.company_name || '-'}</td>
                    <td className="px-3 py-2.5 text-center">
                      <span className={`px-1.5 py-0.5 rounded font-bold text-xs ${getScoreColor(s.score)} ${getScoreBg(s.score)}`}>
                        {s.score != null ? s.score.toFixed(0) : '-'}
                      </span>
                    </td>
                    <td className="px-3 py-2.5 text-right text-white font-medium">{s.current_price != null ? `₹${Number(s.current_price).toFixed(0)}` : '-'}</td>
                    <td className="px-3 py-2.5 text-right text-slate-300">{s.market_cap != null ? `₹${(s.market_cap / 1e7).toFixed(0)}Cr` : '-'}</td>
                    <td className={`px-3 py-2.5 text-right ${colored(s.pe_ratio, { threshold: 25, invert: true })}`}>{s.pe_ratio != null ? s.pe_ratio.toFixed(1) : '-'}</td>
                    <td className={`px-3 py-2.5 text-right ${colored(s.roe, { threshold: 15 })}`}>{s.roe != null ? `${s.roe.toFixed(1)}%` : '-'}</td>
                    <td className={`px-3 py-2.5 text-right ${colored(s.roce, { threshold: 15 })}`}>{s.roce != null ? `${s.roce.toFixed(1)}%` : '-'}</td>
                    <td className={`px-3 py-2.5 text-right ${colored(s.net_profit_margin, { threshold: 15 })}`}>{s.net_profit_margin != null ? `${s.net_profit_margin.toFixed(0)}%` : '-'}</td>
                    <td className="px-3 py-2.5 text-right text-white">{s.eps != null ? `₹${s.eps.toFixed(0)}` : '-'}</td>
                    <td className={`px-3 py-2.5 text-right ${colored(s.pb_ratio, { threshold: 4, invert: true })}`}>{s.pb_ratio != null ? s.pb_ratio.toFixed(1) : '-'}</td>
                    <td className={`px-3 py-2.5 text-right ${colored(s.debt_to_equity, { threshold: 1, invert: true })}`}>{s.debt_to_equity != null ? s.debt_to_equity.toFixed(1) : '-'}</td>
                    <td className="px-3 py-2.5 text-right text-yellow-400">{s.dividend_yield != null ? `${s.dividend_yield.toFixed(1)}%` : '-'}</td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr><td colSpan={13} className="text-center py-10 text-slate-500">No stocks found</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}