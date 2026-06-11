import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';

function getColor(score) {
  if (score >= 80) return '#10b981';
  if (score >= 60) return '#22c55e';
  if (score >= 40) return '#eab308';
  if (score >= 30) return '#f97316';
  return '#ef4444';
}

export default function RadarScore({ breakdown }) {
  const data = [
    { category: 'Profitability', score: breakdown.profitability, fullMark: 100 },
    { category: 'Growth', score: breakdown.growth, fullMark: 100 },
    { category: 'Financial\nHealth', score: breakdown.financial_health, fullMark: 100 },
    { category: 'Valuation', score: breakdown.valuation, fullMark: 100 },
    { category: 'Ownership', score: breakdown.ownership, fullMark: 100 },
  ];
  const avg = data.reduce((s, d) => s + d.score, 0) / data.length;
  const color = getColor(avg);

  return (
    <ResponsiveContainer width="100%" height={280}>
      <RadarChart data={data}>
        <PolarGrid stroke="#475569" />
        <PolarAngleAxis dataKey="category" tick={{ fill: '#94a3b8', fontSize: 11 }} />
        <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 10 }} />
        <Radar dataKey="score" stroke={color} fill={color} fillOpacity={0.2} strokeWidth={2} />
      </RadarChart>
    </ResponsiveContainer>
  );
}