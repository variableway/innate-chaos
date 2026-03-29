import { Price, Signal, Allocation, RegimeData } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

async function fetchApi<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`)
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Unknown error" }))
    throw new Error(error.error?.message || `API error: ${response.status}`)
  }
  
  const data = await response.json()
  return data.data
}

export async function getCurrentPrices(): Promise<{ timestamp: string; prices: Price[] }> {
  return fetchApi("/prices/current")
}

export async function getPriceHistory(asset: string, limit: number = 100): Promise<{ asset: string; prices: Price[] }> {
  return fetchApi(`/prices/${asset}?limit=${limit}`)
}

export async function getCurrentSignals(): Promise<{ timestamp: string; regime: string; signals: Signal[] }> {
  return fetchApi("/signals/current")
}

export async function getSignalHistory(asset: string, limit: number = 168): Promise<{ asset: string; signals: Signal[] }> {
  return fetchApi(`/signals/${asset}?limit=${limit}`)
}

export async function getCurrentAllocation(): Promise<Allocation> {
  return fetchApi("/allocation/current")
}

export async function getAllocationHistory(limit: number = 50): Promise<{ allocations: Allocation[] }> {
  return fetchApi(`/allocation/history?limit=${limit}`)
}

export async function triggerRebalance(): Promise<{
  previous_weights: Record<string, number>
  new_weights: Record<string, number>
  changes: Record<string, number>
  regime: string
}> {
  const response = await fetch(`${API_BASE}/allocation/rebalance`, {
    method: "POST"
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Unknown error" }))
    throw new Error(error.error?.message || `API error: ${response.status}`)
  }
  
  const data = await response.json()
  return data.data
}
