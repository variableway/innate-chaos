"use client";

import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import type { PriceData } from "@/lib/types";

interface PriceTickerProps {
  data: PriceData;
}

export default function PriceTicker({ data }: PriceTickerProps) {
  const changePct = data.change_24h != null ? data.change_24h * 100 : 0;
  const isPositive = changePct > 0;
  const isNegative = changePct < 0;
  const changeColor = isPositive
    ? "text-emerald-400"
    : isNegative
      ? "text-red-400"
      : "text-gray-400";

  const bgColor = isPositive
    ? "bg-emerald-400/10"
    : isNegative
      ? "bg-red-400/10"
      : "bg-gray-400/10";

  const Icon = isPositive ? TrendingUp : isNegative ? TrendingDown : Minus;

  return (
    <div className="rounded-xl border border-[#262626] bg-[#141414] p-4 flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-400 uppercase tracking-wider">
          {data.asset}
        </span>
        <span className={`rounded-md p-1 ${bgColor}`}>
          <Icon className={`h-4 w-4 ${changeColor}`} />
        </span>
      </div>
      <div className="text-2xl font-bold text-white">
        $
        {data.price.toLocaleString(undefined, {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })}
      </div>
      {data.change_24h != null ? (
        <div className={`text-sm ${changeColor}`}>
          {isPositive ? "+" : ""}
          {changePct.toFixed(2)}%
        </div>
      ) : (
        <div className="text-sm text-gray-500">--</div>
      )}
    </div>
  );
}
