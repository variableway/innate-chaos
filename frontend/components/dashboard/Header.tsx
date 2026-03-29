"use client"

import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { Activity, Clock } from "lucide-react"

interface HeaderProps {
  lastUpdated?: string
  className?: string
}

export function Header({ lastUpdated, className }: HeaderProps) {
  return (
    <header className={cn("border-b bg-card", className)}>
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary rounded-lg">
              <Activity className="h-6 w-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold">HyperTrace</h1>
              <p className="text-xs text-muted-foreground">
                Trading Signal Dashboard
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            {lastUpdated && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Clock className="h-4 w-4" />
                <span>
                  Last updated: {new Date(lastUpdated).toLocaleTimeString()}
                </span>
              </div>
            )}
            <Badge variant="outline" className="text-xs">
              Live
            </Badge>
          </div>
        </div>
      </div>
    </header>
  )
}
