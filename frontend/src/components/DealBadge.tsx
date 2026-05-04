interface DealBadgeProps {
  rating: string | null;
}

const ratingConfig: Record<string, { label: string; className: string }> = {
  great: { label: "Great Deal", className: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" },
  good: { label: "Good Deal", className: "bg-blue-500/20 text-blue-400 border-blue-500/30" },
  fair: { label: "Fair Price", className: "bg-amber-500/20 text-amber-400 border-amber-500/30" },
  overpriced: { label: "Overpriced", className: "bg-red-500/20 text-red-400 border-red-500/30" },
};

export default function DealBadge({ rating }: DealBadgeProps) {
  if (!rating) return null;

  const config = ratingConfig[rating] ?? {
    label: rating,
    className: "bg-slate-500/20 text-slate-400 border-slate-500/30",
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${config.className}`}
    >
      {config.label}
    </span>
  );
}
