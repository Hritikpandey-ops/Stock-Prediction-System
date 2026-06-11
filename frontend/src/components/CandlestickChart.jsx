import {
  ComposedChart, Bar, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, Legend
} from 'recharts';

function toWeekNumber(dateStr) {
  const d = new Date(dateStr);
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1);
  const monday = new Date(d.setDate(diff));
  return monday.toISOString().slice(0, 10);
}

function aggregateWeekly(data) {
  const weeks = {};
  for (const d of data) {
    const week = toWeekNumber(d.date);
    if (!weeks[week]) weeks[week] = { date: week, open: d.open, high: d.high, low: d.low, close: d.close, volume: 0, count: 0 };
    const w = weeks[week];
    w.high = Math.max(w.high, d.high);
    w.low = Math.min(w.low, d.low);
    w.close = d.close;
    w.volume += d.volume;
    w.count++;
  }
  return Object.values(weeks).sort((a, b) => a.date.localeCompare(b.date));
}

function calculateSMA(data, period) {
  return data.map((_, i) => {
    if (i < period - 1) return null;
    const slice = data.slice(i - period + 1, i + 1);
    return +(slice.reduce((s, v) => s + v.close, 0) / period).toFixed(2);
  });
}

function calculateEMA(data, period) {
  const k = 2 / (period + 1);
  const result = [];
  let ema = data[0]?.close || 0;
  for (let i = 0; i < data.length; i++) {
    if (i === 0) ema = data[i].close;
    else ema = data[i].close * k + ema * (1 - k);
    result.push(+ema.toFixed(2));
  }
  return result;
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  const ohlc = payload.find(p => p.dataKey === 'close');
  const vol = payload.find(p => p.dataKey === 'volume');
  return (
    <div className="bg-slate-800 border border-slate-600 rounded-lg p-3 text-sm shadow-xl">
      <p className="text-slate-400 mb-1">{label}</p>
      {ohlc && <p className="text-white font-medium">Close: ₹{ohlc.value?.toFixed(2)}</p>}
      {vol && <p className="text-slate-300">Vol: {(vol.value / 1e6).toFixed(1)}M</p>}
    </div>
  );
};

export default function CandlestickChart({ data, showSMA = true }) {
  if (!data || data.length === 0) return <p className="text-slate-400 text-center py-10">No data available</p>;

  const weekly = aggregateWeekly(data);
  const closePrices = weekly.map(d => d.close);
  const sma20 = calculateSMA(weekly, Math.min(20, weekly.length));
  const sma50 = calculateSMA(weekly, Math.min(50, weekly.length));
  const ema12 = calculateEMA(weekly, Math.min(12, weekly.length));
  const ema26 = calculateEMA(weekly, Math.min(26, weekly.length));

  const chartData = weekly.map((d, i) => ({
    ...d,
    sma20: sma20[i],
    sma50: sma50[i],
    ema12: ema12[i],
    ema26: ema26[i],
    color: d.close >= d.open ? '#22c55e' : '#ef4444',
  }));

  const latest = weekly[weekly.length - 1];

  return (
    <div>
      {latest && (
        <div className="grid grid-cols-4 gap-3 mb-4">
          <MetricBox label="Open" value={latest.open} />
          <MetricBox label="High" value={latest.high} color="text-green-400" />
          <MetricBox label="Low" value={latest.low} color="text-red-400" />
          <MetricBox label="Close" value={latest.close} color="text-blue-400" />
        </div>
      )}
      <ResponsiveContainer width="100%" height={380}>
        <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="date" tick={{ fill: '#94a3b8', fontSize: 11 }} axisTick={false} tickFormatter={v => v.slice(5)} />
          <YAxis domain={['auto', 'auto']} tick={{ fill: '#94a3b8', fontSize: 11 }} tickFormatter={v => `₹${v}`} />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: 12, color: '#94a3b8' }} />
          <Bar dataKey="volume" fill="#475569" opacity={0.3} yAxisId={1} barSize={3} />
          <Area dataKey="close" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.06} dot={false} strokeWidth={2} />
          {showSMA && <Area dataKey="sma20" stroke="#f59e0b" dot={false} strokeWidth={1.5} fill="none" />}
          {showSMA && <Area dataKey="sma50" stroke="#8b5cf6" dot={false} strokeWidth={1.5} fill="none" />}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

function MetricBox({ label, value, color }) {
  return (
    <div className="bg-slate-800 rounded-lg p-3 text-center">
      <div className="text-xs text-slate-400">{label}</div>
      <div className={`text-lg font-bold ${color || 'text-white'}`}>₹{value?.toFixed(2)}</div>
    </div>
  );
}