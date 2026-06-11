export default function MetricCard({ label, value, color, subtitle }) {
  const textColor = color || (value && typeof value === 'string' && value.startsWith('-') ? 'text-red-400' : 'text-green-400');
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-4">
      <div className="text-xs text-slate-400 uppercase tracking-wider mb-1">{label}</div>
      <div className={`text-xl font-bold ${typeof textColor === 'string' && textColor.startsWith('text-') ? textColor : 'text-white'}`}
        style={typeof textColor === 'string' && !textColor.startsWith('text-') ? { color: textColor } : {}}>
        {value ?? 'N/A'}
      </div>
      {subtitle && <div className="text-xs text-slate-500 mt-1">{subtitle}</div>}
    </div>
  );
}