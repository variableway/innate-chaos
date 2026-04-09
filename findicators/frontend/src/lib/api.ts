const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchApi<T>(endpoint: string): Promise<T> {
  const res = await fetch(`${API_URL}${endpoint}`);
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

import type {
  PriceResponse,
  PriceHistoryResponse,
  RegimeResponse,
  SignalResponse,
  AllocationResponse,
} from "./types";

export function fetchCurrentPrices() {
  return fetchApi<PriceResponse>("/api/v1/prices/current");
}

export function fetchPriceHistory(asset: string, days: number = 30) {
  return fetchApi<PriceHistoryResponse>(
    `/api/v1/prices/${asset}/history?days=${days}`
  );
}

export function fetchCurrentRegime() {
  return fetchApi<RegimeResponse>("/api/v1/regime/current");
}

export function fetchCurrentSignals() {
  return fetchApi<SignalResponse>("/api/v1/signals/current");
}

export function fetchCurrentAllocation() {
  return fetchApi<AllocationResponse>("/api/v1/allocation/current");
}
