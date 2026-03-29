"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Price } from "@/types"
import { cn, formatPrice, formatPercent } from "@/lib/utils"
import { TrendingUp, TrendingDown, Droplets, Bitcoin, Gem, CircleDollarSign } from "lucide-react"

interface PriceTickerProps {
  prices: Price[]
  className?: string
}

const ASSET_ICONS = {
  ETH: Gem,
  BTC: Bitcoin,
  GOLD: CircleDollarSign,
  OIL: Droplets
}

const ASSET_COLORS = {
  ETH: "text-blue-500",
  BTC: "text-orange-500",
  GOLD: "text-yellow-500",
  OIL: "text-red-500"
}

export function PriceTicker({ prices, className }: PriceTickerProps) {
  return (
    <div className={cn("grid grid-cols-2 lg:grid-cols-4 gap-4", className)}>
      {prices.map((price) => {
        const Icon = ASSET_ICONS[price.asset as keyof typeof ASSET_ICONS] || CircleDollarSign
        const isPositive = (price.change_24h || 0) >= 0
        
        return (
          <Card key={price.asset} className="overflow-hidden">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Icon className={cn("h-5 w-5", ASSET_COLORS[price.asset as keyof typeof ASSET_COLORS])} />
                  <span className="font-bold">{price.asset}</span>
                </div>
                <div className={cn(
                  "flex items-center gap-1 text-xs",
                  isPositive ? "text-green-500" : "text-red-500"
                )}>
                  {isPositive ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                  {formatPercent(price.change_24h)}
                </div>
              </div>
              
              <div className="text-2xl font-bold">
                ${formatPrice(price.price, price.asset === "BTC" || price.asset === "ETH" ? 2 : 2)}
              </div>
              
              <div className="text-xs text-muted-foreground mt-1">
                Source: {price.source}
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
