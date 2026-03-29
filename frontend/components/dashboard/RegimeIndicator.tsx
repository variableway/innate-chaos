"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { RegimeData } from "@/types"
import { 
  formatPercent, 
  getRegimeColor, 
  getRegimeBgColor,
  cn 
} from "@/lib/utils"
import { AlertTriangle, TrendingUp, Shield, AlertCircle } from "lucide-react"

interface RegimeIndicatorProps {
  regime: RegimeData
  className?: string
}

export function RegimeIndicator({ regime, className }: RegimeIndicatorProps) {
  const isRiskOff = regime.regime === "RISK_OFF"
  const isRiskOn = regime.regime === "RISK_ON"
  
  const Icon = isRiskOff ? AlertTriangle : isRiskOn ? TrendingUp : AlertCircle
  
  return (
    <Card className={cn("overflow-hidden", className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Icon className={cn("h-5 w-5", getRegimeColor(regime.regime))} />
            Market Regime
          </CardTitle>
          <Badge 
            variant={isRiskOff ? "danger" : isRiskOn ? "success" : "warning"}
            className="text-sm"
          >
            {regime.regime_text}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* OIL and GOLD Changes */}
        <div className="grid grid-cols-2 gap-4">
          <div className={cn(
            "rounded-lg p-3 border",
            isRiskOff ? "bg-red-500/10 border-red-500/30" : "bg-muted/50"
          )}>
            <div className="text-xs text-muted-foreground mb-1">OIL (24h)</div>
            <div className={cn(
              "text-xl font-bold",
              regime.oil_change_24h > 0 ? "text-red-500" : "text-green-500"
            )}>
              {formatPercent(regime.oil_change_24h)}
            </div>
          </div>
          
          <div className={cn(
            "rounded-lg p-3 border",
            regime.gold_change_24h > 0 ? "bg-yellow-500/10 border-yellow-500/30" : "bg-muted/50"
          )}>
            <div className="text-xs text-muted-foreground mb-1">GOLD (24h)</div>
            <div className={cn(
              "text-xl font-bold",
              regime.gold_change_24h > 0 ? "text-yellow-500" : "text-green-500"
            )}>
              {formatPercent(regime.gold_change_24h)}
            </div>
          </div>
        </div>
        
        {/* Description */}
        <div className={cn(
          "rounded-md px-4 py-3 text-sm border",
          getRegimeBgColor(regime.regime)
        )}>
          <p className="font-medium mb-1">{regime.description}</p>
        </div>
        
        {/* Recommendation */}
        <div className="flex items-start gap-2 text-sm">
          <Shield className="h-4 w-4 text-primary mt-0.5 shrink-0" />
          <div>
            <span className="font-medium">Recommendation: </span>
            <span className="text-muted-foreground">{regime.recommendation}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
