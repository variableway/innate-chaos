"use client"

import { useState, useEffect, useCallback } from "react"
import { 
  getCurrentPrices, 
  getCurrentSignals, 
  getCurrentAllocation,
  triggerRebalance 
} from "@/lib/api"
import { Price, Signal, Allocation, RegimeData } from "@/types"

interface DashboardState {
  prices: Price[]
  signals: Signal[]
  allocation: Allocation | null
  regime: RegimeData | null
  loading: boolean
  error: string | null
  lastUpdated: string | null
}

export function useDashboard(refreshInterval: number = 30000) {
  const [state, setState] = useState<DashboardState>({
    prices: [],
    signals: [],
    allocation: null,
    regime: null,
    loading: true,
    error: null,
    lastUpdated: null
  })

  const fetchData = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }))
    
    try {
      const [pricesData, signalsData, allocationData] = await Promise.all([
        getCurrentPrices(),
        getCurrentSignals(),
        getCurrentAllocation()
      ])
      
      // Extract regime from first signal (they all have the same regime)
      const regime: RegimeData = signalsData.signals.length > 0 
        ? {
            regime: signalsData.signals[0].regime,
            regime_text: signalsData.signals[0].regime === "RISK_OFF" 
              ? "Risk-Off" 
              : signalsData.signals[0].regime === "RISK_ON"
                ? "Risk-On"
                : "Neutral",
            oil_change_24h: 0, // Will be populated from allocation or separate call
            gold_change_24h: 0,
            description: "",
            recommendation: "",
            time: signalsData.timestamp
          }
        : {
            regime: "NEUTRAL",
            regime_text: "Neutral",
            oil_change_24h: 0,
            gold_change_24h: 0,
            description: "No data available",
            recommendation: "Wait for data",
            time: new Date().toISOString()
          }
      
      setState({
        prices: pricesData.prices,
        signals: signalsData.signals,
        allocation: allocationData,
        regime,
        loading: false,
        error: null,
        lastUpdated: new Date().toISOString()
      })
    } catch (err) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : "Failed to fetch data"
      }))
    }
  }, [])

  const rebalance = useCallback(async () => {
    try {
      await triggerRebalance()
      await fetchData() // Refresh data after rebalance
    } catch (err) {
      setState(prev => ({
        ...prev,
        error: err instanceof Error ? err.message : "Failed to rebalance"
      }))
    }
  }, [fetchData])

  useEffect(() => {
    fetchData()
    
    const interval = setInterval(fetchData, refreshInterval)
    return () => clearInterval(interval)
  }, [fetchData, refreshInterval])

  return {
    ...state,
    refresh: fetchData,
    rebalance
  }
}
