import type { ListingFilters } from "../api/client";

interface FilterBarProps {
  filters: ListingFilters;
  onChange: (filters: ListingFilters) => void;
}

export default function FilterBar({ filters, onChange }: FilterBarProps) {
  return (
    <div className="flex flex-wrap gap-2 p-3 bg-slate-800/50 rounded-xl border border-slate-700">
      <select
        value={filters.year ?? ""}
        onChange={(e) =>
          onChange({ ...filters, year: e.target.value ? Number(e.target.value) : undefined })
        }
        className="bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        <option value="">All Years</option>
        {Array.from({ length: 26 }, (_, i) => 2026 - i).map((year) => (
          <option key={year} value={year}>
            {year}
          </option>
        ))}
      </select>

      <select
        value={filters.model ?? ""}
        onChange={(e) =>
          onChange({ ...filters, model: e.target.value || undefined })
        }
        className="bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        <option value="">All Models</option>
        <option value="Prius">Prius</option>
        <option value="Prius Prime">Prius Prime</option>
        <option value="Prius V">Prius V</option>
        <option value="Prius C">Prius C</option>
        <option value="Prius Plug-in">Prius Plug-in</option>
      </select>

      <select
        value={filters.deal_rating ?? ""}
        onChange={(e) =>
          onChange({ ...filters, deal_rating: e.target.value || undefined })
        }
        className="bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        <option value="">All Ratings</option>
        <option value="great">Great Deals</option>
        <option value="good">Good Deals</option>
        <option value="fair">Fair Price</option>
        <option value="overpriced">Overpriced</option>
      </select>

      <select
        value={`${filters.sort_by ?? "captured_at"}_${filters.sort_order ?? "desc"}`}
        onChange={(e) => {
          const [sort_by, sort_order] = e.target.value.split("_") as [string, string];
          onChange({ ...filters, sort_by, sort_order });
        }}
        className="bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        <option value="captured_at_desc">Newest First</option>
        <option value="captured_at_asc">Oldest First</option>
        <option value="price_asc">Price: Low to High</option>
        <option value="price_desc">Price: High to Low</option>
        <option value="year_desc">Year: Newest</option>
        <option value="year_asc">Year: Oldest</option>
      </select>
    </div>
  );
}
