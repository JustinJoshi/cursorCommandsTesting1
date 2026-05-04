import type { Listing } from "../api/client";
import DealBadge from "./DealBadge";

interface ListingCardProps {
  listing: Listing;
  onDelete?: (id: number) => void;
}

export default function ListingCard({ listing, onDelete }: ListingCardProps) {
  const savings =
    listing.estimated_market_value !== null
      ? listing.estimated_market_value - listing.price
      : null;

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 p-4 space-y-3 hover:border-slate-600 transition-colors">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <h3 className="font-semibold text-slate-100 truncate">{listing.title}</h3>
          <p className="text-sm text-slate-400">
            {listing.year} {listing.model} {listing.trim ?? ""}
          </p>
        </div>
        <DealBadge rating={listing.deal_rating} />
      </div>

      <div className="flex items-baseline gap-3">
        <span className="text-2xl font-bold text-white">
          ${listing.price.toLocaleString()}
        </span>
        {listing.estimated_market_value !== null && (
          <span className="text-sm text-slate-400">
            Market: ${listing.estimated_market_value.toLocaleString()}
          </span>
        )}
      </div>

      {savings !== null && savings > 0 && (
        <p className="text-sm text-emerald-400 font-medium">
          ${savings.toLocaleString()} below market value
        </p>
      )}

      {listing.mileage !== null && (
        <p className="text-sm text-slate-400">
          {listing.mileage.toLocaleString()} miles
        </p>
      )}

      {listing.ai_summary && (
        <p className="text-sm text-slate-300 bg-slate-700/50 rounded-lg p-3">
          {listing.ai_summary}
        </p>
      )}

      {listing.description && (
        <p className="text-sm text-slate-400 line-clamp-2">{listing.description}</p>
      )}

      <div className="flex items-center gap-2 pt-1">
        {listing.link && (
          <a
            href={listing.link}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-blue-400 hover:text-blue-300 underline"
          >
            View Listing
          </a>
        )}
        <span className="flex-1" />
        <span className="text-xs text-slate-500">
          {new Date(listing.captured_at).toLocaleDateString()}
        </span>
        {onDelete && (
          <button
            onClick={() => onDelete(listing.id)}
            className="text-xs text-red-400 hover:text-red-300 px-2 py-1"
          >
            Remove
          </button>
        )}
      </div>
    </div>
  );
}
