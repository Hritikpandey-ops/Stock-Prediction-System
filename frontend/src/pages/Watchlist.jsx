import { useState, useEffect } from 'react';
import { getFullData, getAllFundamentals } from '../services/api';
import { Star, TrendingUp, TrendingDown } from 'lucide-react';
import MiniChart from '../components/MiniChart';

const DEFAULT_WATCHLIST = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'HINDUNILVR', 'ITC', 'SBIN'];

export default function Watchlist() {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all(DEFAULT_WATCHLIST.map(async symbol => {
      try {
        const [fullRes, fundRes] = await Promise.all([
          getFullData(symbol, '1M'),
          fetch(`/api/stocks/${symbol}/fundamentals`).catch(() => null)
        ]);
        const stats = fullRes.data.stats || {};
        const prices = fullRes.data.prices || [];
        const fundData = fundRes ? (await fundRes.json()) : null;
        return {
          symbol,
          company: fundData?.fundamentals?.company_name || symbol,
          price: stats.current_price || 0,
          change: stats.change_1d || 0,
          change_1w: stats.change_1w || 0,
          high: stats.high || 0,
          low: stats.low || 0,
          volume: stats.avg_volume_10 || 0,
          rsi: stats.rsi,
          macd: stats.macd,
          score: fundData?.score,
          prices: prices.map(p => p.close),
        };
      } catch {
        return { symbol, company: symbol, price: 0, change: 0, prices: [] };
      }
    })).then(setStocks).finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2"><Star size={22} className="text-yellow-400" /> Watchlist</h1>
        <p className="text-slate-400 text-sm">Track your favourite stocks at a glance — Nifty 50 heavyweights</p>
      </div>

      {loading ? (
        <div className="text-center py-20 text-slate-400">Loading watchlist...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {stocks.map(stock => (
            <div key={stock.symbol} className="bg-slate-900 border border-slate-700 rounded-xl p-4 hover:border-slate-500 transition-colors">
              <div className="flex items-center justify-between mb-2">
                <div>
                  <div className="text-white font-bold">{stock.symbol}</div>
                  <div className="text-[10px] text-slate-400 truncate max-w-[200px]">{stock.company}</div>
                </div>
                <div className="text-right">
                  <div className="text-white font-bold text-lg">₹{stock.price?.toFixed(2)}</div>
                  <div className={`text-xs font-medium flex items-center gap-1 justify-end ${stock.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {stock.change >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                    {stock.change >= 0 ? '+' : ''}{stock.change?.toFixed(2)}%
                  </div>
                </div>
              </div>
              <div className="flex gap-3 mb-2">
                <MiniChart data={stock.prices} color={stock.change >= 0 ? '#22c55e' : '#ef4444'} />
              </div>
              <div className="grid grid-cols-4 gap-2 text-center text-[10px]">
                <div><span className="text-slate-500">Range</span><div className="text-white font-medium">₹{stock.low?.toFixed(0)}-{stock.high?.toFixed(0)}</div></div>
                <div><span className="text-slate-500">1W Chg</span><div className={stock.change_1w >= 0 ? 'text-green-400' : 'text-red-400'}>{stock.change_1w >= 0 ? '+' : ''}{stock.change_1w?.toFixed(1)}%</div></div>
                <div><span className="text-slate-500">RSI</span><div className={stock.rsi > 70 ? 'text-red-400' : stock.rsi < 30 ? 'text-green-400' : 'text-yellow-400'}>{stock.rsi?.toFixed(0) || '-'}</div></div>
                <div><span className="text-slate-500">Score</span><div className={stock.score >= 60 ? 'text-green-400' : stock.score >= 40 ? 'text-yellow-400' : 'text-red-400'}>{stock.score?.toFixed(0) || '-'}</div></div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}