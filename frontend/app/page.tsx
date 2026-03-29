"use client"

import { Header } from "@/components/dashboard/Header"
import { PriceTicker } from "@/components/dashboard/PriceTicker"
import { RegimeIndicator } from "@/components/dashboard/RegimeIndicator"
import { SignalCard } from "@/components/dashboard/SignalCard"
import { AllocationPanel } from "@/components/dashboard/AllocationPanel"
import { PriceChart } from "@/components/dashboard/PriceChart"
import { useDashboard } from "@/hooks/useDashboard"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { AlertCircle, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function Dashboard() {
  const { 
    prices, 
    signals, 
    allocation, 
    regime, 
    loading, 
    error, 
    lastUpdated,
    refresh,
    rebalance 
  } = useDashboard(30000) // Refresh every 30 seconds

  // Prepare price history data for chart
  const priceHistory: Record<string, any[]> = {}
  // In a real app, you'd fetch historical data. For now, we'll use current prices.
  prices.forEach(price => {
    priceHistory[price.asset] = [price]
  })

  return (
    <div className="min-h-screen bg-background">
      <Header lastUpdated={lastUpdated || undefined} />
      
      <main className="container mx-auto px-4 py-6">
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription className="flex items-center gap-4">
              {error}
              <Button variant="outline" size="sm" onClick={refresh}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Retry
              </Button>
            </AlertDescription>
          </Alert>
        )}

        {/* Price Ticker */}
        {loading && prices.length === 0 ? (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {[1, 2, 3, 4].map(i => (
              <Skeleton key={i} className="h-24" />
            ))}
          </div>
        ) : (
          <PriceTicker prices={prices} className="mb-6" />
        )}

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Regime & Allocation */}
          <div className="space-y-6">
            {loading && !regime ? (
              <>
                <Skeleton className="h-64" />
                <Skeleton className="h-96" />
              </>
            ) : (
              <>
                {regime && <RegimeIndicator regime={regime} />}
                {allocation && (
                  <AllocationPanel 
                    allocation={allocation} 
                    onRebalance={rebalance}
                  />
                )}
              </>
            )}
          </div>

          {/* Middle & Right Columns - Signals & Charts */}
          <div className="lg:col-span-2 space-y-6">
            {/* Signal Cards */}
            {loading && signals.length === 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[1, 2, 3].map(i => (
                  <Skeleton key={i} className="h-48" />
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {signals.map(signal => (
                  <SignalCard key={signal.asset} signal={signal} />
                ))}
              </div>
            )}

            {/* Price Chart */}
            {loading ? (
              <Skeleton className="h-96" />
            ) : (
              <PriceChart prices={priceHistory} />
            )}
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-12 py-6 border-t text-center text-sm text-muted-foreground">
          <p>HyperTrace Trading Dashboard • Built with Next.js & HyperLiquid SDK</p>
          <p className="mt-1">
            Data provided by HyperLiquid API. Not financial advice.
          </p>
        </footer>
      </main>
    </div>
  )
}
