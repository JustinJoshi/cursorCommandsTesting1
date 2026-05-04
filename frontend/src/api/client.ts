const API_BASE = "/api";

export interface Listing {
  id: number;
  title: string;
  price: number;
  year: number;
  model: string;
  trim: string | null;
  mileage: number | null;
  description: string | null;
  link: string | null;
  image_path: string | null;
  ai_summary: string | null;
  deal_rating: string | null;
  estimated_market_value: number | null;
  source_screenshot: string | null;
  captured_at: string;
  created_at: string;
}

export interface CaptureStatus {
  status: "idle" | "capturing" | "extracting" | "done" | "error" | "busy";
  message: string | null;
  listings_found: number;
}

export interface Stats {
  total_listings: number;
  avg_price: number;
  min_price: number;
  max_price: number;
  by_year: { year: number; count: number; avg_price: number }[];
  by_model: { model: string; count: number; avg_price: number }[];
  by_rating: { rating: string; count: number }[];
}

export interface ListingFilters {
  year?: number;
  min_price?: number;
  max_price?: number;
  model?: string;
  deal_rating?: string;
  sort_by?: string;
  sort_order?: string;
  limit?: number;
  offset?: number;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

export async function getListings(filters?: ListingFilters): Promise<Listing[]> {
  const params = new URLSearchParams();
  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.set(key, String(value));
      }
    });
  }
  const query = params.toString();
  return request<Listing[]>(`/listings${query ? `?${query}` : ""}`);
}

export async function getListing(id: number): Promise<Listing> {
  return request<Listing>(`/listings/${id}`);
}

export async function deleteListing(id: number): Promise<void> {
  return request<void>(`/listings/${id}`, { method: "DELETE" });
}

export async function triggerCapture(monitor?: number): Promise<CaptureStatus> {
  const params = monitor !== undefined ? `?monitor=${monitor}` : "";
  return request<CaptureStatus>(`/capture${params}`, { method: "POST" });
}

export async function triggerBatchCapture(
  count: number = 3,
  delaySeconds: number = 5
): Promise<CaptureStatus> {
  return request<CaptureStatus>(
    `/capture/batch?count=${count}&delay_seconds=${delaySeconds}`,
    { method: "POST" }
  );
}

export async function getCaptureStatus(): Promise<CaptureStatus> {
  return request<CaptureStatus>("/capture/status");
}

export async function getStats(): Promise<Stats> {
  return request<Stats>("/stats");
}

export async function getDeals(limit: number = 10): Promise<Listing[]> {
  return request<Listing[]>(`/stats/deals?limit=${limit}`);
}
