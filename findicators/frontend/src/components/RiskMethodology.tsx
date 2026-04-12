"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

interface FactorDef {
  name: string;
  weight: string;
  asset: string;
  threshold: string;
  logic: string;
  source: string;
}

const FACTORS: FactorDef[] = [
  {
    name: "Oil Trend",
    weight: "20%",
    asset: "WTI Crude (OIL)",
    threshold: "±5% over 7 days",
    logic: "Rising oil signals economic growth and demand → risk on. Falling oil signals demand weakness → risk off.",
    source: "FRED (DCOILWTICO)",
  },
  {
    name: "Gold Trend",
    weight: "25%",
    asset: "Gold (PAXG/XAU)",
    threshold: "±5% over 7 days",
    logic: "Inverted: rising gold signals flight to safety → risk off. Falling gold signals risk appetite → risk on.",
    source: "HyperLiquid (PAXG) / CoinGecko",
  },
  {
    name: "BTC Momentum",
    weight: "25%",
    asset: "Bitcoin (BTC)",
    threshold: "±10% over 7 days",
    logic: "Rising BTC reflects speculative appetite and market confidence → risk on. Falling BTC signals fear → risk off.",
    source: "HyperLiquid / CoinGecko",
  },
  {
    name: "Yield Curve",
    weight: "20%",
    asset: "10Y-2Y Treasury Spread",
    threshold: "±2% over 7 days",
    logic: "A steepening yield curve signals growth expectations → risk on. An inverted/flattening curve signals recession fears → risk off.",
    source: "FRED (T10Y2Y)",
  },
  {
    name: "Volatility",
    weight: "10%",
    asset: "BTC + ETH",
    threshold: "Daily return std dev (20-day)",
    logic: "Higher volatility reflects elevated market activity. Current model maps high vol to risk on.",
    source: "HyperLiquid / CoinGecko",
  },
];

export default function RiskMethodology() {
  const [open, setOpen] = useState(false);

  return (
    <div className="rounded-xl border border-[#262626] bg-[#141414] p-5">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between text-lg font-semibold text-white"
      >
        How Risk Score is Calculated
        {open ? (
          <ChevronUp className="w-5 h-5 text-gray-400" />
        ) : (
          <ChevronDown className="w-5 h-5 text-gray-400" />
        )}
      </button>

      {open && (
        <div className="mt-4 space-y-5 text-sm text-gray-300">
          {/* Model overview */}
          <div>
            <h3 className="text-white font-medium mb-2">
              5-Factor Weighted Model
            </h3>
            <p>
              The risk score is a weighted average of 5 independent market
              signals. Each factor&apos;s raw trend is{" "}
              <span className="text-white">normalized to a 0-1 score</span>{" "}
              using a threshold, then multiplied by its weight.
            </p>
          </div>

          {/* Formula */}
          <div className="bg-[#0a0a0a] rounded-lg p-4 font-mono text-xs text-gray-400 border border-[#1f1f1f]">
            <p className="text-white mb-2">Normalization:</p>
            <p>score = (clamp(trend, -threshold, threshold) / threshold + 1) / 2</p>
            <p className="text-white mt-3 mb-2">Composite score:</p>
            <p>
              risk_score = 0.20 × oil + 0.25 × gold + 0.25 × btc + 0.20 ×
              yield + 0.10 × vol
            </p>
            <p className="text-white mt-3 mb-2">Classification:</p>
            <p>
              <span className="text-emerald-400">RISK_ON</span>{" "}
              {"  "}if risk_score &ge; 0.60
            </p>
            <p>
              <span className="text-red-400">RISK_OFF</span>{" "}
              {"  "}if risk_score &le; 0.40
            </p>
            <p>
              <span className="text-yellow-400">NEUTRAL</span>{" "}
              {"  "}otherwise
            </p>
          </div>

          {/* Factor table */}
          <div>
            <h3 className="text-white font-medium mb-3">Factor Details</h3>
            <div className="space-y-3">
              {FACTORS.map((f) => (
                <div
                  key={f.name}
                  className="border border-[#1f1f1f] rounded-lg p-3 bg-[#0f0f0f]"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-white font-medium">{f.name}</span>
                    <span className="text-blue-400 text-xs font-mono">
                      Weight: {f.weight}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-gray-500 mt-2">
                    <span>
                      Asset: <span className="text-gray-300">{f.asset}</span>
                    </span>
                    <span>
                      Threshold:{" "}
                      <span className="text-gray-300">{f.threshold}</span>
                    </span>
                    <span>
                      Source: <span className="text-gray-300">{f.source}</span>
                    </span>
                  </div>
                  <p className="text-xs text-gray-400 mt-2">{f.logic}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Important note */}
          <div className="text-xs text-gray-500 border-t border-[#1f1f1f] pt-3">
            <p>
              Note: The gold trend factor is <span className="text-white">inverted</span> because
              rising gold typically signals a flight to safety (risk-off
              behavior). All trends are calculated over a 7-day window. Scores
              of 0.5 indicate no clear directional signal.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
