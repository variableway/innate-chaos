"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import PriceTicker from "@/components/PriceTicker";
import RatePanel from "@/components/RatePanel";
import RegimeIndicator from "@/components/RegimeIndicator";
import PriceChart from "@/components/PriceChart";
import FactorBreakdown from "@/components/FactorBreakdown";
import AllocationPanel from "@/components/AllocationPanel";
import SuggestionPanel from "@/components/SuggestionPanel";
import RiskMethodology from "@/components/RiskMethodology";
import {
  fetchCurrentPrices,
  fetchPriceHistory,
  fetchCurrentRegime,
  fetchCurrentAllocation,
} from "@/lib/api";
import type { PriceData, RegimeResponse, AllocationResponse } from "@/lib/types";

const TICKER_ASSETS = ["GOLD", "OIL", "BTC", "ETH"];

function SkeletonCard() {
  return (
    <div className="rounded-xl border border-[#262626] bg-[#141414] p-4 animate-pulse">
      <div className="h-4 w-16 bg-[#262626] rounded mb-3" />
      <div className="h-8 w-28 bg-[#262626] rounded mb-2" />
      <div className="h-4 w-20 bg-[#262626] rounded" />
    </div>
  );
}

function SkeletonPanel() {
  return (
    <div className="rounded-xl border border-[#262626] bg-[#141414] p-5 animate-pulse">
      <div className="h-5 w-32 bg-[#262626] rounded mb-4" />
      <div className="space-y-3">
        <div className="h-4 w-full bg-[#262626] rounded" />
        <div className="h-4 w-3/4 bg-[#262626] rounded" />
        <div className="h-4 w-1/2 bg-[#262626] rounded" />
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const [selectedAsset, setSelectedAsset] = useState<string>("BTC");

  const pricesQuery = useQuery({
    queryKey: ["prices"],
    queryFn: fetchCurrentPrices,
    refetchInterval: 30000,
  });

  const historyQuery = useQuery({
    queryKey: ["priceHistory", selectedAsset],
    queryFn: () => fetchPriceHistory(selectedAsset, 30),
    refetchInterval: 60000,
  });

  const regimeQuery = useQuery({
    queryKey: ["regime"],
    queryFn: fetchCurrentRegime,
    refetchInterval: 30000,
  });

  const allocationQuery = useQuery({
    queryKey: ["allocation"],
    queryFn: fetchCurrentAllocation,
    refetchInterval: 30000,
  });

  // Backend returns assets as a dict { "GOLD": PriceData, ... }
  const assetsDict = pricesQuery.data?.assets ?? {};
  const tickerPrices: PriceData[] = TICKER_ASSETS
    .map((a) => assetsDict[a])
    .filter(Boolean);

  const historyData = historyQuery.data?.data ?? [];
  const regime = regimeQuery.data as RegimeResponse | undefined;
  const allocation = allocationQuery.data as AllocationResponse | undefined;

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-[#ededed]">
      <header className="border-b border-[#262626] px-6 py-4">
        <h1 className="text-xl font-bold tracking-tight">
          Findicators - Macro Dashboard
        </h1>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-6">
        {/* Top: Price tickers */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {pricesQuery.isLoading
            ? Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
            : tickerPrices.length > 0
              ? tickerPrices.map((p) => <PriceTicker key={p.asset} data={p} />)
              : Array.from({ length: 4 }).map((_, i) => (
                  <div
                    key={i}
                    className="rounded-xl border border-[#262626] bg-[#141414] p-4 flex items-center justify-center text-gray-500 text-sm"
                  >
                    Waiting for data...
                  </div>
                ))}
        </div>

        {/* Rate panel + Regime indicator */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <RatePanel prices={assetsDict} />
          {regimeQuery.isLoading ? (
            <SkeletonPanel />
          ) : regime ? (
            <RegimeIndicator data={regime} />
          ) : (
            <SkeletonPanel />
          )}
        </div>

        {/* Middle: Price chart with asset tabs */}
        <div>
          <div className="flex gap-2 mb-3">
            {TICKER_ASSETS.map((asset) => (
              <button
                key={asset}
                onClick={() => setSelectedAsset(asset)}
                className={`px-4 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                  selectedAsset === asset
                    ? "bg-blue-600 text-white"
                    : "bg-[#1a1a1a] text-gray-400 hover:bg-[#262626]"
                }`}
              >
                {asset}
              </button>
            ))}
          </div>
          {historyQuery.isLoading ? (
            <SkeletonPanel />
          ) : (
            <PriceChart asset={selectedAsset} data={historyData} />
          )}
        </div>

        {/* Bottom: Factor breakdown + Allocation */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {regime ? (
            <FactorBreakdown factor_scores={regime.factor_scores} />
          ) : (
            <SkeletonPanel />
          )}
          {allocation ? (
            <AllocationPanel data={allocation} />
          ) : (
            <SkeletonPanel />
          )}
        </div>

        {/* Suggestion */}
        {regime?.suggestion ? (
          <SuggestionPanel data={regime.suggestion} />
        ) : (
          <SkeletonPanel />
        )}

        {/* Methodology */}
        <RiskMethodology />
      </main>
    </div>
  );
}
