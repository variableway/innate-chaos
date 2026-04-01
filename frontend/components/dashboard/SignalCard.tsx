"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Signal } from "@/types"
import { 
  formatSignal, 
  getSignalColor, 
  getSignalBgColor,
  cn 
} from "@/lib/utils"
import { TrendingUp, TrendingDown, Activity } from "lucide-react"

interface SignalCardProps {
  signal: Signal
  className?: string
}

export function SignalCard({ signal, className }: SignalCardProps) {
  const signalPercent = signal.signal * 100
  
  return (
    <Card className={cn("overflow-hidden", className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold">{signal.asset}</span>
            <Badge 
              variant={signal.signal >= 0.5 ? "success" : signal.signal >= 0.3 ? "warning" : "danger"}
            >
              {signal.action}
            </Badge>
          </div>
          <div className={cn("text-3xl font-bold", getSignalColor(signal.signal))}>
            {formatSignal(signal.signal)}
          </div>
        </div>
        <CardDescription className="text-xs">
          {signal.action_text}
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Signal Progress Bar */}
        <div className="space-y-1">
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Signal Strength</span>
            <span>{formatSignal(signal.signal)}/100</span>
          </div>
          <Progress value={signalPercent} className="h-2" />
        </div>
        
        {/* Score Breakdown */}
        {signal.score_breakdown && (
          <div className="grid grid-cols-3 gap-2 text-xs">
            {signal.score_breakdown.policy !== undefined && (
              <div className="space-y-1">
                <div className="flex items-center gap-1 text-muted-foreground">
                  <Activity className="h-3 w-3" />
                  Policy
                </div>
                <div className="font-medium">
                  {Math.round(signal.score_breakdown.policy * 100)}
                </div>
              </div>
            )}
            {signal.score_breakdown.momentum !== undefined && (
              <div className="space-y-1">
                <div className="flex items-center gap-1 text-muted-foreground">
                  {signal.score_breakdown.momentum >= 0.5 ? (
                    <TrendingUp className="h-3 w-3" />
                  ) : (
                    <TrendingDown className="h-3 w-3" />
                  )}
                  Momentum
                </div>
                <div className="font-medium">
                  {Math.round(signal.score_breakdown.momentum * 100)}
                </div>
              </div>
            )}
            {signal.score_breakdown.risk !== undefined && (
              <div className="space-y-1">
                <div className="flex items-center gap-1 text-muted-foreground">
                  <Activity className="h-3 w-3" />
                  Risk
                </div>
                <div className="font-medium">
                  {Math.round(signal.score_breakdown.risk * 100)}
                </div>
              </div>
            )}
          </div>
        )}
        
        {/* Regime Indicator */}
        <div className={cn(
          "rounded-md px-3 py-2 text-xs border",
          getSignalBgColor(signal.signal)
        )}>
          <span className="font-medium">Market Regime: </span>
          {signal.regime}
        </div>
      </CardContent>
    </Card>
  )
}
