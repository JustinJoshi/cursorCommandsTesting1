import { useCallback, useEffect, useState } from "react";
import {
  getListings,
  getStats,
  deleteListing,
  type Listing,
  type ListingFilters,
  type Stats,
  type CaptureStatus,
} from "./api/client";
import CaptureButton from "./components/CaptureButton";
import DealBadge from "./components/DealBadge";
import FilterBar from "./components/FilterBar";
import ListingCard from "./components/ListingCard";
import PriceChart from "./components/PriceChart";
import StatsBar from "./components/StatsBar";

export default function App() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [filters, setFilters] = useState<ListingFilters>({
    sort_by: "captured_at",
    sort_order: "desc",
  });
  const [loading, setLoading] = useState(true);
  const [showChart, setShowChart] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [listingsData, statsData] = await Promise.all([
        getListings(filters),
        getStats(),
      ]);
      setListings(listingsData);
      setStats(statsData);
    } catch (err) {
      console.error("Failed to fetch data:", err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCaptureComplete = (_status: CaptureStatus) => {
    fetchData();
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteListing(id);
      setListings((prev) => prev.filter((l) => l.id !== id));
    } catch (err) {
      console.error("Failed to delete listing:", err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-slate-900/95 backdrop-blur border-b border-slate-800 px-4 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-white">Prius Tracker</h1>
            <p className="text-xs text-slate-400">
              {stats ? `${stats.total_listings} listings tracked` : "Loading..."}
            </p>
          </div>
          <CaptureButton onCaptureComplete={handleCaptureComplete} />
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-4 space-y-4 pb-20">
        {/* Stats */}
        <StatsBar stats={stats} />

        {/* Chart Toggle */}
        <button
          onClick={() => setShowChart(!showChart)}
          className="text-sm text-blue-400 hover:text-blue-300"
        >
          {showChart ? "Hide Chart" : "Show Price Chart"}
        </button>

        {showChart && <PriceChart stats={stats} />}

        {/* Filters */}
        <FilterBar filters={filters} onChange={setFilters} />

        {/* Listings */}
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-pulse text-slate-400">Loading listings...</div>
          </div>
        ) : listings.length === 0 ? (
          <div className="text-center py-12 space-y-3">
            <p className="text-slate-400 text-lg">No listings yet</p>
            <p className="text-slate-500 text-sm">
              Open Facebook Marketplace, search for Toyota Prius, then tap Capture
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {listings.map((listing) => (
              <ListingCard
                key={listing.id}
                listing={listing}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
