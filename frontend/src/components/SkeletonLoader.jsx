export function SkeletonLine({ className = '' }) {
  return <div className={`animate-pulse bg-slate-700/50 rounded ${className}`} />;
}

export function SkeletonCard({ rows = 4 }) {
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl p-4 space-y-3">
      <SkeletonLine className="h-4 w-1/3" />
      {Array.from({ length: rows }).map((_, i) => (
        <SkeletonLine key={i} className="h-3 w-full" />
      ))}
    </div>
  );
}

export function SkeletonChart() {
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl p-4">
      <SkeletonLine className="h-4 w-1/4 mb-4" />
      <SkeletonLine className="h-[380px] w-full rounded-lg" />
    </div>
  );
}

export function SkeletonTable({ rows = 8, cols = 6 }) {
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl overflow-hidden">
      <div className="p-4 space-y-3">
        <SkeletonLine className="h-4 w-1/4" />
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="flex gap-4">
            {Array.from({ length: cols }).map((_, j) => (
              <SkeletonLine key={j} className="h-3 flex-1" />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

export function SkeletonDashboard() {
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-4">
      <div className="flex items-center justify-between">
        <SkeletonLine className="h-8 w-48" />
        <SkeletonLine className="h-10 w-32" />
      </div>
      <div className="grid grid-cols-6 gap-2">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="bg-slate-900 border border-slate-700 rounded-xl p-3">
            <SkeletonLine className="h-3 w-16 mb-2" />
            <SkeletonLine className="h-5 w-20" />
          </div>
        ))}
      </div>
      <SkeletonChart />
      <div className="grid grid-cols-3 gap-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="bg-slate-900 border border-slate-700 rounded-xl p-3">
            <SkeletonLine className="h-3 w-20 mb-2" />
            <SkeletonLine className="h-16 w-full" />
          </div>
        ))}
      </div>
    </div>
  );
}

export function SkeletonFundamentals() {
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-4">
      <div className="flex items-center justify-between">
        <SkeletonLine className="h-8 w-48" />
        <SkeletonLine className="h-10 w-32" />
      </div>
      <SkeletonLine className="h-32 w-full rounded-xl" />
      <div className="grid grid-cols-5 gap-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="bg-slate-900 border border-slate-700 rounded-xl p-3">
            <SkeletonLine className="h-20 w-full" />
          </div>
        ))}
      </div>
      <div className="grid grid-cols-2 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <SkeletonCard key={i} rows={6} />
        ))}
      </div>
    </div>
  );
}

export function SkeletonNews() {
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-4">
      <SkeletonLine className="h-8 w-48" />
      <div className="grid grid-cols-3 gap-3 max-w-md">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="bg-slate-800 border border-slate-700 rounded-lg p-3 text-center">
            <SkeletonLine className="h-6 w-12 mx-auto mb-1" />
            <SkeletonLine className="h-3 w-16 mx-auto" />
          </div>
        ))}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="bg-slate-800 border border-slate-700 rounded-xl p-4">
            <SkeletonLine className="h-3 w-1/3 mb-2" />
            <SkeletonLine className="h-4 w-full mb-1" />
            <SkeletonLine className="h-4 w-3/4" />
          </div>
        ))}
      </div>
    </div>
  );
}
