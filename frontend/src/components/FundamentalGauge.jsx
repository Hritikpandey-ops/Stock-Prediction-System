import { PieChart, Pie, Cell } from 'recharts';

function getColor(score) {
  if (score >= 80) return '#10b981';
  if (score >= 60) return '#22c55e';
  if (score >= 40) return '#eab308';
  if (score >= 30) return '#f97316';
  return '#ef4444';
}

export default function FundamentalGauge({ score, label }) {
  const color = getColor(score);
  const data = [
    { value: score },
    { value: 100 - score },
  ];

  return (
    <div className="flex flex-col items-center bg-slate-800 rounded-xl p-4">
      <PieChart width={120} height={80}>
        <Pie data={data} cx={60} cy={70} startAngle={180} endAngle={0}
          innerRadius={45} outerRadius={65} dataKey="value" stroke="none">
          <Cell fill={color} />
          <Cell fill="#334155" />
        </Pie>
      </PieChart>
      <div className="text-2xl font-bold" style={{ color }}>{score.toFixed(0)}</div>
      <div className="text-xs text-slate-400 mt-1">{label}</div>
    </div>
  );
}