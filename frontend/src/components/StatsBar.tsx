import type { Stats } from "../api/client";

interface StatsBarProps {
  stats: Stats | null;
}

export default function StatsBar({ stats }: StatsBarProps) {
  if (!stats) return null;

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <StatCard label="Total Listings" value={stats.total_listings.toString()} />
      <StatCard
        label="Avg Price"
        value={`$${stats.avg_price.toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
      />
      <StatCard
        label="Lowest"
        value={`$${stats.min_price.toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
        className="text-emerald-400"
      />
      <StatCard
        label="Highest"
        value={`$${stats.max_price.toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
        className="text-red-400"
      />
    </div>
  );
}

function StatCard({
  label,
  value,
  className = "text-white",
}: {
  label: string;
  value: string;
  className?: string;
}) {
  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 p-3 text-center">
      <p className="text-xs text-slate-400 uppercase tracking-wide">{label}</p>
      <p className={`text-lg font-bold mt-1 ${className}`}>{value}</p>
    </div>
  );
}
