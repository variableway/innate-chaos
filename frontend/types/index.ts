export interface Price {
  asset: string
  price: number
  time: string
  source: string
  change_24h?: number
  change_7d?: number
  volume_24h?: number
}

export interface SignalBreakdown {
  policy?: number
  momentum?: number
  risk?: number
}

export interface Signal {
  asset: string
  signal: number
  score_breakdown: SignalBreakdown
  regime: string
  time: string
  action?: string
  action_text?: string
}

export interface AllocationWeights {
  ETH: number
  BTC: number
  GOLD: number
  CASH: number
}

export interface Allocation {
  id?: number
  created_at?: string
  weights: AllocationWeights
  regime: string
  macro_state: string
  rebalance_triggered: boolean
  rebalance_needed?: boolean
  rationale?: string
}

export interface RegimeData {
  regime: string
  regime_text: string
  oil_change_24h: number
  gold_change_24h: number
  description: string
  recommendation: string
  time: string
}

export interface DashboardData {
  timestamp: string
  prices: Record<string, Price>
  signals: Record<string, Signal>
  regime: RegimeData
  allocation: Allocation
}

export interface PriceHistoryPoint {
  time: string
  price: number
  change_24h?: number
}

export interface SignalHistoryPoint {
  time: string
  signal: number
  regime: string
}

export type AssetType = "ETH" | "BTC" | "GOLD" | "OIL"
export type RegimeType = "RISK_ON" | "RISK_OFF" | "NEUTRAL"
