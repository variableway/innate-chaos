import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatPercent(value: number | undefined): string {
  if (value === undefined || value === null) return "N/A"
  const sign = value >= 0 ? "+" : ""
  return `${sign}${(value * 100).toFixed(2)}%`
}

export function formatPrice(value: number | undefined, decimals: number = 2): string {
  if (value === undefined || value === null) return "N/A"
  return value.toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })
}

export function formatSignal(value: number | undefined): string {
  if (value === undefined || value === null) return "N/A"
  return (value * 100).toFixed(0)
}

export function getSignalColor(value: number): string {
  if (value >= 0.7) return "text-green-500"
  if (value >= 0.5) return "text-emerald-500"
  if (value >= 0.3) return "text-yellow-500"
  return "text-red-500"
}

export function getSignalBgColor(value: number): string {
  if (value >= 0.7) return "bg-green-500/20 border-green-500/50"
  if (value >= 0.5) return "bg-emerald-500/20 border-emerald-500/50"
  if (value >= 0.3) return "bg-yellow-500/20 border-yellow-500/50"
  return "bg-red-500/20 border-red-500/50"
}

export function getRegimeColor(regime: string): string {
  switch (regime) {
    case "RISK_ON":
      return "text-green-500"
    case "RISK_OFF":
      return "text-red-500"
    default:
      return "text-yellow-500"
  }
}

export function getRegimeBgColor(regime: string): string {
  switch (regime) {
    case "RISK_ON":
      return "bg-green-500/20 border-green-500/50"
    case "RISK_OFF":
      return "bg-red-500/20 border-red-500/50"
    default:
      return "bg-yellow-500/20 border-yellow-500/50"
  }
}
