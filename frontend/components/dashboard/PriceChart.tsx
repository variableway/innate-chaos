"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Price } from "@/types"
import { cn, formatPrice } from "@/lib/utils"
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Legend
} from "recharts"
import { TrendingUp } from "lucide-react"

interface PriceChartProps {
  prices: Record<string, Price[]>
  className?: string
}

const ASSET_COLORS = {
  ETH: "#627eea",
  BTC: "#f7931a",
  GOLD: "#ffd700",
  OIL: "#ef4444"
}

export function PriceChart({ prices, className }: PriceChartProps) {
  const [selectedAsset, setSelectedAsset] = useState<string>("all")
  
  // Prepare chart data
  const chartData = () => {
    const assets = Object.keys(prices)
    if (assets.length === 0) return []
    
    // Get all timestamps
    const allTimestamps = new Set<string>()
    assets.forEach(asset => {
      prices[asset].forEach(p => allTimestamps.add(p.time))
    })
    
    const sortedTimestamps = Array.from(allTimestamps).sort()
    
    return sortedTimestamps.map(timestamp => {
      const point: Record<string, any> = { time: timestamp }
      
      assets.forEach(asset => {
        const price = prices[asset].find(p => p.time === timestamp)
        if (price) {
          point[asset] = price.price
        }
      })
      
      return point
    })
  }
  
  const data = chartData()
  const assets = Object.keys(prices)
  
  const visibleAssets = selectedAsset === "all" 
    ? assets 
    : [selectedAsset]
  
  return (
    <Card className={cn("overflow-hidden", className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <CardTitle className="text-lg flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Price History
          </CardTitle>
          
          <Tabs value={selectedAsset} onValueChange={setSelectedAsset}>
            <TabsList>
              <TabsTrigger value="all">All</TabsTrigger>
              {assets.map(asset => (
                <TabsTrigger key={asset} value={asset}>{asset}</TabsTrigger>
              ))}
            </TabsList>
          </Tabs>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis 
                dataKey="time" 
                tickFormatter={(time) => new Date(time).toLocaleDateString()}
                stroke="hsl(var(--muted-foreground))"
                fontSize={12}
              />
              <YAxis 
                stroke="hsl(var(--muted-foreground))"
                fontSize={12}
                tickFormatter={(value) => `$${formatPrice(value, 0)}`}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "6px"
                }}
                formatter={(value: number, name: string) => [
                  `$${formatPrice(value)}`,
                  name
                ]}
                labelFormatter={(label) => new Date(label).toLocaleString()}
              />
              <Legend />
              {visibleAssets.map(asset => (
                <Line
                  key={asset}
                  type="monotone"
                  dataKey={asset}
                  stroke={ASSET_COLORS[asset as keyof typeof ASSET_COLORS]}
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4 }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
