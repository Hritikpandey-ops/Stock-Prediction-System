import { Area, AreaChart, ResponsiveContainer, Tooltip } from 'recharts';

export default function MiniChart({ data, color = '#22c55e' }) {
  if (!data || data.length === 0) return null;
  const chartData = data.map((d, i) => ({ i, v: typeof d === 'number' ? d : d.close }));
  return (
    <ResponsiveContainer width="100%" height={60}>
      <AreaChart data={chartData} margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
        <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #475569', borderRadius: 6, fontSize: 12 }}
          formatter={(v) => [`₹${v?.toFixed(2)}`]} />
        <Area dataKey="v" stroke={color} fill={color} fillOpacity={0.15} dot={false} strokeWidth={2} />
      </AreaChart>
    </ResponsiveContainer>
  );
}