import { useState, useEffect } from 'react';
import { getFullData } from '../services/api';
import { Star, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react';
import MiniChart from '../components/MiniChart';

const DEFAULT_WATCHLIST = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'HINDUNILVR', 'ITC', 'SBIN'];

function WatchlistSkeleton() {
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-4">
      <div className="animate-pulse">
        <div className="h-8 w-48 bg-slate-700/50 rounded mb-2" />
        <div className="h-4 w-72 bg-slate-700/50 rounded" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="bg-slate-900 border border-slate-700 rounded-xl p-4 animate-pulse">
            <div className="flex justify-between mb-2">
              <div><div className="h-4 w-24 bg-slate-700/50 rounded mb-1" /><div className="h-3 w-32 bg-slate-700/50 rounded" /></div>
              <div className="text-right"><div className="h-5 w-20 bg-slate-700/50 rounded mb-1" /><div className="h-3 w-16 bg-slate-700/50 rounded" /></div>
            </div>
            <div className="h-12 bg-slate-700/30 rounded mb-2" />
            <div className="grid grid-cols-4 gap-2">{Array.from({ length: 4 }).map((_, j) => <div key={j} className="h-8 bg-slate-700/30 rounded" />)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Watchlist() {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all(DEFAULT_WATCHLIST.map(async symbol => {
      try {
        const [fullRes, fundRes] = await Promise.all([
          getFullData(symbol, '1M'),
          fetch(`/api/stocks/${symbol}/fundamentals`).catch(() => null)
        ]);
        const stats = fullRes.data.stats || {};
        const prices = fullRes.data.prices || [];
        const fundData = fundRes ? (await fundRes.json().catch(() => null)) : null;
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
    }))
      .then(setStocks)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <WatchlistSkeleton />;

  if (error) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="bg-slate-900 border border-red-700/50 rounded-xl p-8 text-center">
          <AlertTriangle size={40} className="text-red-400 mx-auto mb-3" />
          <h2 className="text-white text-lg font-bold mb-2">Failed to load watchlist</h2>
          <p className="text-slate-400 text-sm">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2"><Star size={22} className="text-yellow-400" /> Watchlist</h1>
        <p className="text-slate-400 text-sm">Track your favourite stocks at a glance — Nifty 50 heavyweights</p>
      </div>

      {loading ? (
        <WatchlistSkeleton />
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