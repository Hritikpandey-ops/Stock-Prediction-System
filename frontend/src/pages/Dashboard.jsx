import { useState, useEffect } from 'react';
import { getFullData, getSymbols } from '../services/api';
import MetricCard from '../components/MetricCard';
import { SkeletonDashboard } from '../components/SkeletonLoader';
import {
  ComposedChart, Bar, Area, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, ReferenceLine
} from 'recharts';
import { TrendingUp, TrendingDown, BarChart3, DollarSign } from 'lucide-react';

const periods = [
  { label: '1M', days: 30 }, { label: '3M', days: 90 },
  { label: '6M', days: 180 }, { label: '1Y', days: 365 }, { label: '2Y', days: 730 }
];

const overlays = [
  { key: 'sma20', label: 'SMA 20', color: '#f59e0b' },
  { key: 'sma50', label: 'SMA 50', color: '#8b5cf6' },
  { key: 'sma200', label: 'SMA 200', color: '#ec4899' },
  { key: 'ema12', label: 'EMA 12', color: '#06b6d4' },
  { key: 'ema26', label: 'EMA 26', color: '#f97316' },
  { key: 'ema200', label: 'EMA 200', color: '#14b8a6' },
  { key: 'bb_upper', label: 'BB Upper', color: '#22c55e', dash: '3 3' },
  { key: 'bb_middle', label: 'BB Middle', color: '#22c55e' },
  { key: 'bb_lower', label: 'BB Lower', color: '#ef4444', dash: '3 3' },
];

const ChartTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload || {};
  return (
    <div className="bg-slate-800 border border-slate-600 rounded-lg p-3 text-xs shadow-xl max-w-xs">
      <p className="text-slate-400 mb-1 font-medium">{label}</p>
      <div className="grid grid-cols-2 gap-x-4 gap-y-0.5">
        <span className="text-slate-400">O:</span><span className="text-white text-right">{d.open?.toFixed(2)}</span>
        <span className="text-slate-400">H:</span><span className="text-green-400 text-right">{d.high?.toFixed(2)}</span>
        <span className="text-slate-400">L:</span><span className="text-red-400 text-right">{d.low?.toFixed(2)}</span>
        <span className="text-slate-400">C:</span><span className="text-blue-400 text-right">{d.close?.toFixed(2)}</span>
        <span className="text-slate-400">Vol:</span><span className="text-purple-400 text-right">{(d.volume / 1e6)?.toFixed(1)}M</span>
        {d.rsi != null && <><span className="text-slate-400">RSI:</span><span className="text-right" style={{ color: d.rsi > 70 ? '#ef4444' : d.rsi < 30 ? '#22c55e' : '#eab308' }}>{d.rsi}</span></>}
        {d.macd != null && <><span className="text-slate-400">MACD:</span><span className="text-right" style={{ color: d.macd >= 0 ? '#22c55e' : '#ef4444' }}>{d.macd?.toFixed(2)}</span></>}
      </div>
    </div>
  );
};

const SubTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-slate-800 border border-slate-600 rounded-lg p-2 text-xs shadow-xl">
      <p className="text-slate-400 mb-1">{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color }}>{p.name}: {typeof p.value === 'number' ? p.value.toFixed(2) : p.value}</p>
      ))}
    </div>
  );
};

function indicator(value, thresholds) {
  if (value == null) return 'text-slate-500';
  if (thresholds.high != null && value > thresholds.high) return 'text-red-400';
  if (thresholds.low != null && value < thresholds.low) return 'text-green-400';
  return 'text-yellow-400';
}

export default function Dashboard() {
  const [symbols, setSymbols] = useState([]);
  const [symbol, setSymbol] = useState('RELIANCE');
  const [period, setPeriod] = useState('1Y');
  const [data, setData] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [activeOverlays, setActiveOverlays] = useState(['sma20', 'sma50']);

  useEffect(() => {
    getSymbols().then(r => setSymbols(r.data.symbols)).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    getFullData(symbol, period).then(r => {
      setData(r.data.prices || []);
      setStats(r.data.stats || {});
    }).catch(() => {
      setData([]);
      setStats({});
    }).finally(() => setLoading(false));
  }, [symbol, period]);

  const s = stats;

  const toggleOverlay = (key) => {
    setActiveOverlays(prev =>
      prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]
    );
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <BarChart3 size={22} className="text-blue-400" /> {symbol}
          </h1>
          {s.current_price && (
            <div className="flex items-center gap-3 mt-1">
              <span className="text-2xl font-bold text-white">₹{s.current_price?.toFixed(2)}</span>
              <span className={`text-sm font-medium flex items-center gap-1 ${s.change_1d >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {s.change_1d >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                {s.change_1d >= 0 ? '+' : ''}{s.change_1d}%
              </span>
              <span className="text-xs text-slate-400">Prev: ₹{s.previous_close?.toFixed(2)}</span>
            </div>
          )}
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          <select value={symbol} onChange={e => setSymbol(e.target.value)}
            className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm min-w-[120px]">
            {symbols.map(s => <option key={s} value={s}>{s}</option>)}
            {symbols.length === 0 && ['RELIANCE','TCS','HDFCBANK'].map(s => <option key={s} value={s}>{s}</option>)}
          </select>
          <div className="flex bg-slate-800 rounded-lg border border-slate-600">
            {periods.map(p => (
              <button key={p.label} onClick={() => setPeriod(p.label)}
                className={`px-3 py-2 text-xs font-medium transition-colors ${period === p.label ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'}`}>
                {p.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {loading ? (
        <SkeletonDashboard />
      ) : data.length === 0 ? (
        <div className="text-center py-20 text-slate-500">No price data available</div>
      ) : (
        <>
          {/* Key Stats Row */}
          <div className="grid grid-cols-6 gap-2 mb-4">
            <MetricCard label="Open" value={`₹${s.open?.toFixed(2)}`} subtitle={`High: ₹${s.high?.toFixed(2)}`} />
            <MetricCard label="Prev Close" value={`₹${s.previous_close?.toFixed(2)}`} subtitle={`Low: ₹${s.low?.toFixed(2)}`} />
            <MetricCard label="Volume" value={s.avg_volume_10 ? `${(s.avg_volume_10 / 1e6).toFixed(1)}M` : 'N/A'} subtitle={`Vol ratio: ${s.volume_ratio}`} color={s.volume_ratio > 1.5 ? 'text-green-400' : 'text-purple-400'} />
            <MetricCard label="RSI (14)" value={s.rsi?.toFixed(1)} color={indicator(s.rsi, { high: 70, low: 30 })} subtitle={s.rsi > 70 ? 'Overbought' : s.rsi < 30 ? 'Oversold' : 'Neutral'} />
            <MetricCard label="MACD" value={s.macd?.toFixed(2)} color={s.macd >= 0 ? 'text-green-400' : 'text-red-400'} subtitle={`Signal: ${s.macd_signal?.toFixed(2)}`} />
            <MetricCard label="ATR (14)" value={s.atr?.toFixed(2)} color="text-orange-400" />
          </div>

          {/* Change Metrics */}
          <div className="grid grid-cols-4 gap-2 mb-4">
            <MetricCard label="1D Change" value={`${s.change_1d >= 0 ? '+' : ''}${s.change_1d}%`} color={s.change_1d >= 0 ? 'text-green-400' : 'text-red-400'} />
            <MetricCard label="1W Change" value={`${s.change_1w >= 0 ? '+' : ''}${s.change_1w}%`} color={s.change_1w >= 0 ? 'text-green-400' : 'text-red-400'} />
            <MetricCard label="1M Change" value={`${s.change_1m >= 0 ? '+' : ''}${s.change_1m}%`} color={s.change_1m >= 0 ? 'text-green-400' : 'text-red-400'} />
            <MetricCard label="Period Range" value={`₹${s.period_low?.toFixed(0)} - ₹${s.period_high?.toFixed(0)}`} color="text-blue-400" />
          </div>

          {/* MA Stats */}
          <div className="grid grid-cols-4 gap-2 mb-4">
            <MetricCard label="SMA 20" value={s.sma20 ? `₹${s.sma20}` : 'N/A'}
              color={s.sma20 && s.current_price >= s.sma20 ? 'text-green-400' : 'text-red-400'}
              subtitle={s.sma20 ? `Price ${s.current_price >= s.sma20 ? 'Above' : 'Below'}` : ''} />
            <MetricCard label="SMA 50" value={s.sma50 ? `₹${s.sma50}` : 'N/A'}
              color={s.sma50 && s.current_price >= s.sma50 ? 'text-green-400' : 'text-red-400'}
              subtitle={s.sma50 ? `Price ${s.current_price >= s.sma50 ? 'Above' : 'Below'}` : ''} />
            <MetricCard label="SMA 200" value={s.sma200 ? `₹${s.sma200}` : 'N/A'}
              color={s.sma200 && s.current_price >= s.sma200 ? 'text-green-400' : 'text-red-400'} />
            <MetricCard label="Price/Vol Days" value={`${s.up_days}/${s.down_days}/${s.total_days}`} subtitle="Up/Down/Total" color="text-blue-400" />
          </div>

          {/* Price & Volume Chart */}
          <div className="bg-slate-900 border border-slate-700 rounded-xl p-4 mb-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-white text-sm font-medium flex items-center gap-1"><DollarSign size={14} /> Price Chart</h3>
              <div className="flex flex-wrap gap-1">
                {overlays.map(o => (
                  <button key={o.key} onClick={() => toggleOverlay(o.key)}
                    className={`px-2 py-0.5 text-[10px] rounded transition-colors ${activeOverlays.includes(o.key) ? 'text-white font-medium' : 'text-slate-500'}`}
                    style={activeOverlays.includes(o.key) ? { background: o.color + '40', borderColor: o.color, borderWidth: 1 } : {}}>
                    {o.label}
                  </button>
                ))}
              </div>
            </div>
            <ResponsiveContainer width="100%" height={380}>
              <ComposedChart data={data} margin={{ top: 5, right: 5, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" tick={{ fill: '#94a3b8', fontSize: 10 }} tickFormatter={v => v.slice(5, 10)} axisLine={false} tickLine={false} interval="preserveStartEnd" />
                <YAxis domain={['auto', 'auto']} tick={{ fill: '#94a3b8', fontSize: 10 }} tickFormatter={v => `₹${v}`} axisLine={false} tickLine={false} width={60} />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="volume" fill="#475569" opacity={0.25} yAxisId={2} barSize={data.length > 100 ? 2 : 4} />
                {activeOverlays.includes('bb_upper') && <Line dataKey="bb_upper" stroke="#22c55e" strokeWidth={0.8} dot={false} strokeDasharray="3 3" opacity={0.6} />}
                {activeOverlays.includes('bb_middle') && <Line dataKey="bb_middle" stroke="#22c55e" strokeWidth={0.8} dot={false} opacity={0.6} />}
                {activeOverlays.includes('bb_lower') && <Line dataKey="bb_lower" stroke="#ef4444" strokeWidth={0.8} dot={false} strokeDasharray="3 3" opacity={0.6} />}
                {activeOverlays.includes('sma20') && <Line dataKey="sma20" stroke="#f59e0b" strokeWidth={1.5} dot={false} />}
                {activeOverlays.includes('sma50') && <Line dataKey="sma50" stroke="#8b5cf6" strokeWidth={1.5} dot={false} />}
                {activeOverlays.includes('sma200') && <Line dataKey="sma200" stroke="#ec4899" strokeWidth={1.5} dot={false} />}
                {activeOverlays.includes('ema12') && <Line dataKey="ema12" stroke="#06b6d4" strokeWidth={1.2} dot={false} strokeDasharray="4 2" />}
                {activeOverlays.includes('ema26') && <Line dataKey="ema26" stroke="#f97316" strokeWidth={1.2} dot={false} strokeDasharray="4 2" />}
                {activeOverlays.includes('ema200') && <Line dataKey="ema200" stroke="#14b8a6" strokeWidth={1.5} dot={false} />}
                <Area dataKey="close" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.04} dot={false} strokeWidth={2} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* RSI Panel */}
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="bg-slate-900 border border-slate-700 rounded-xl p-3">
              <h4 className="text-xs text-slate-400 font-medium mb-1">RSI (14)</h4>
              <div className="flex items-center gap-4 mb-1">
                <span className={`text-lg font-bold ${s.rsi > 70 ? 'text-red-400' : s.rsi < 30 ? 'text-green-400' : 'text-yellow-400'}`}>{s.rsi?.toFixed(1)}</span>
                <span className="text-[10px] text-slate-500">OB: 70 | OS: 30</span>
              </div>
              <ResponsiveContainer width="100%" height={80}>
                <ComposedChart data={data} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                  <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3" strokeWidth={0.8} />
                  <ReferenceLine y={30} stroke="#22c55e" strokeDasharray="3 3" strokeWidth={0.8} />
                  <ReferenceLine y={50} stroke="#475569" strokeWidth={0.5} />
                  <Area dataKey="rsi" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.1} dot={false} strokeWidth={1.5} />
                  <Tooltip content={<SubTooltip />} />
                </ComposedChart>
              </ResponsiveContainer>
            </div>

            {/* MACD Panel */}
            <div className="bg-slate-900 border border-slate-700 rounded-xl p-3">
              <h4 className="text-xs text-slate-400 font-medium mb-1">MACD (12, 26, 9)</h4>
              <div className="flex items-center gap-3 mb-1 text-xs">
                <span className={`font-bold ${s.macd >= 0 ? 'text-green-400' : 'text-red-400'}`}>{s.macd?.toFixed(2)}</span>
                <span className="text-slate-400">Sig: {s.macd_signal?.toFixed(2)}</span>
                <span className={`${s.macd_hist >= 0 ? 'text-green-400' : 'text-red-400'}`}>Hist: {s.macd_hist?.toFixed(2)}</span>
              </div>
              <ResponsiveContainer width="100%" height={80}>
                <ComposedChart data={data} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                  <ReferenceLine y={0} stroke="#475569" strokeWidth={0.8} />
                  <Bar dataKey="macd_hist" fill="#3b82f6" opacity={0.3} barSize={data.length > 100 ? 1 : 2} />
                  <Line dataKey="macd" stroke="#22c55e" strokeWidth={1.2} dot={false} />
                  <Line dataKey="macd_signal" stroke="#ef4444" strokeWidth={1} dot={false} />
                  <Tooltip content={<SubTooltip />} />
                </ComposedChart>
              </ResponsiveContainer>
            </div>

            {/* Stochastic Panel */}
            <div className="bg-slate-900 border border-slate-700 rounded-xl p-3">
              <h4 className="text-xs text-slate-400 font-medium mb-1">Stochastic (14, 3, 3)</h4>
              <div className="flex items-center gap-3 mb-1 text-xs">
                <span className="text-blue-400 font-bold">K: {s.stoch_k?.toFixed(1)}</span>
                <span className="text-orange-400">D: {s.stoch_d?.toFixed(1)}</span>
                <span className="text-slate-500">OB: 80 | OS: 20</span>
              </div>
              <ResponsiveContainer width="100%" height={80}>
                <ComposedChart data={data} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                  <ReferenceLine y={80} stroke="#ef4444" strokeDasharray="3 3" strokeWidth={0.8} />
                  <ReferenceLine y={20} stroke="#22c55e" strokeDasharray="3 3" strokeWidth={0.8} />
                  <ReferenceLine y={50} stroke="#475569" strokeWidth={0.5} />
                  <Line dataKey="stoch_k" stroke="#3b82f6" strokeWidth={1.2} dot={false} />
                  <Line dataKey="stoch_d" stroke="#f97316" strokeWidth={1} dot={false} />
                  <Tooltip content={<SubTooltip />} />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Period Summary */}
          <div className="grid grid-cols-4 gap-3">
            <div className="bg-slate-900 border border-slate-700 rounded-xl p-3">
              <h4 className="text-xs text-slate-400 mb-2">Period High / Low</h4>
              <div className="space-y-1 text-xs">
                <div className="flex justify-between"><span className="text-slate-500">High</span><span className="text-green-400 font-medium">₹{s.period_high?.toFixed(2)}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">High Date</span><span className="text-white">{s.period_high_date?.slice(0, 10)}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Low</span><span className="text-red-400 font-medium">₹{s.period_low?.toFixed(2)}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Low Date</span><span className="text-white">{s.period_low_date?.slice(0, 10)}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Range %</span><span className="text-blue-400">{((s.period_high - s.period_low) / s.period_low * 100)?.toFixed(1)}%</span></div>
              </div>
            </div>
            <div className="bg-slate-900 border border-slate-700 rounded-xl p-3">
              <h4 className="text-xs text-slate-400 mb-2">Volume Analysis</h4>
              <div className="space-y-1 text-xs">
                <div className="flex justify-between"><span className="text-slate-500">Avg (10d)</span><span className="text-purple-400">{(s.avg_volume_10 / 1e6)?.toFixed(1)}M</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Avg (total)</span><span className="text-white">{(s.avg_volume / 1e6)?.toFixed(1)}M</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Vol Ratio</span><span className={s.volume_ratio > 1.2 ? 'text-green-400' : 'text-yellow-400'}>{s.volume_ratio}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Total Vol</span><span className="text-white">{(s.total_volume / 1e7)?.toFixed(2)}Cr</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Up/Down Days</span><span className="text-white">{s.up_days}/{s.down_days}</span></div>
              </div>
            </div>
            <div className="bg-slate-900 border border-slate-700 rounded-xl p-3">
              <h4 className="text-xs text-slate-400 mb-2">Moving Averages</h4>
              <div className="space-y-1 text-xs">
                {[
                  { label: 'SMA 20', val: s.sma20, good: s.current_price >= s.sma20 },
                  { label: 'SMA 50', val: s.sma50, good: s.current_price >= s.sma50 },
                  { label: 'SMA 200', val: s.sma200, good: s.sma200 && s.current_price >= s.sma200 },
                  { label: 'EMA 200', val: s.ema200, good: s.ema200 && s.current_price >= s.ema200 },
                ].map(({ label, val, good }) => (
                  <div key={label} className="flex justify-between">
                    <span className="text-slate-500">{label}</span>
                    <span className={val ? (good ? 'text-green-400' : 'text-red-400') : 'text-slate-600'}>
                      {val ? `₹${val}` : 'N/A'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-slate-900 border border-slate-700 rounded-xl p-3">
              <h4 className="text-xs text-slate-400 mb-2">Bollinger Bands</h4>
              <div className="space-y-1 text-xs">
                <div className="flex justify-between"><span className="text-slate-500">Upper</span><span className="text-green-400">₹{s.bb_upper?.toFixed(2)}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Middle</span><span className="text-yellow-400">₹{s.bb_middle?.toFixed(2)}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Lower</span><span className="text-red-400">₹{s.bb_lower?.toFixed(2)}</span></div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Position</span>
                  {s.bb_upper && s.bb_lower ? (
                    <span className={s.current_price > s.bb_upper ? 'text-red-400' : s.current_price < s.bb_lower ? 'text-green-400' : 'text-yellow-400'}>
                      {s.current_price > s.bb_upper ? 'Above' : s.current_price < s.bb_lower ? 'Below' : 'Inside'}
                    </span>
                  ) : <span className="text-slate-600">N/A</span>}
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}