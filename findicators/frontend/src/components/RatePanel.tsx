"use client";

import type { PriceData } from "@/lib/types";

interface RatePanelProps {
  prices: Record<string, PriceData>;
}

const RATE_ASSETS = [
  { key: "DFF", label: "Fed Funds Rate" },
  { key: "DGS2", label: "2Y Treasury" },
  { key: "DGS10", label: "10Y Treasury" },
  { key: "DGS30", label: "30Y Treasury" },
];

export default function RatePanel({ prices }: RatePanelProps) {
  const getRate = (key: string): number | null => {
    const p = prices[key];
    return p ? p.price : null;
  };

  const dgs10 = getRate("DGS10");
  const dgs2 = getRate("DGS2");
  const spread =
    dgs10 !== null && dgs2 !== null ? dgs10 - dgs2 : null;

  return (
    <div className="rounded-xl border border-[#262626] bg-[#141414] p-5">
      <h2 className="text-lg font-semibold text-white mb-4">
        Interest Rates
      </h2>
      <div className="space-y-3">
        {RATE_ASSETS.map(({ key, label }) => {
          const value = getRate(key);
          return (
            <div
              key={key}
              className="flex items-center justify-between py-2 border-b border-[#262626] last:border-0"
            >
              <span className="text-sm text-gray-400">{label}</span>
              <span className="text-sm font-mono font-semibold text-white">
                {value !== null ? `${value.toFixed(2)}%` : "--"}
              </span>
            </div>
          );
        })}
        <div className="flex items-center justify-between py-2 pt-3 border-t border-[#333]">
          <span className="text-sm font-medium text-gray-300">
            10Y-2Y Spread
          </span>
          <span
            className={`text-sm font-mono font-bold ${spread !== null && spread < 0 ? "text-red-400" : "text-emerald-400"}`}
          >
            {spread !== null ? `${spread.toFixed(2)}%` : "--"}
            {spread !== null && spread < 0 && (
              <span className="ml-1 text-xs text-red-400">(inverted)</span>
            )}
          </span>
        </div>
      </div>
    </div>
  );
}
