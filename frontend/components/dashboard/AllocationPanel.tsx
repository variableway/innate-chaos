"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Allocation } from "@/types"
import { cn, formatPercent } from "@/lib/utils"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts"
import { RefreshCw, Wallet } from "lucide-react"

interface AllocationPanelProps {
  allocation: Allocation
  onRebalance?: () => void
  className?: string
}

const COLORS = {
  ETH: "#627eea",
  BTC: "#f7931a",
  GOLD: "#ffd700",
  CASH: "#94a3b8"
}

export function AllocationPanel({ allocation, onRebalance, className }: AllocationPanelProps) {
  const data = [
    { name: "ETH", value: allocation.weights.ETH },
    { name: "BTC", value: allocation.weights.BTC },
    { name: "GOLD", value: allocation.weights.GOLD },
    { name: "CASH", value: allocation.weights.CASH },
  ].filter(d => d.value > 0)

  return (
    <Card className={cn("overflow-hidden", className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Wallet className="h-5 w-5" />
            Portfolio Allocation
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge 
              variant={allocation.rebalance_needed ? "destructive" : "secondary"}
            >
              {allocation.rebalance_needed ? "Rebalance Needed" : "Balanced"}
            </Badge>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Pie Chart */}
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={70}
                paddingAngle={2}
                dataKey="value"
              >
                {data.map((entry) => (
                  <Cell key={entry.name} fill={COLORS[entry.name as keyof typeof COLORS]} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value: number) => formatPercent(value)}
                contentStyle={{ 
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "6px"
                }}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
        
        {/* Weight Bars */}
        <div className="space-y-2">
          {data.map((item) => (
            <div key={item.name} className="flex items-center gap-3">
              <div className="w-12 text-sm font-medium">{item.name}</div>
              <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                <div 
                  className="h-full rounded-full transition-all duration-500"
                  style={{ 
                    width: `${item.value * 100}%`,
                    backgroundColor: COLORS[item.name as keyof typeof COLORS]
                  }}
                />
              </div>
              <div className="w-16 text-right text-sm font-medium">
                {formatPercent(item.value)}
              </div>
            </div>
          ))}
        </div>
        
        {/* Rationale */}
        {allocation.rationale && (
          <div className="text-sm text-muted-foreground bg-muted/50 rounded-md px-3 py-2">
            {allocation.rationale}
          </div>
        )}
        
        {/* Rebalance Button */}
        {onRebalance && (
          <Button 
            onClick={onRebalance}
            className="w-full"
            variant={allocation.rebalance_needed ? "default" : "outline"}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Rebalance Portfolio
          </Button>
        )}
      </CardContent>
    </Card>
  )
}
