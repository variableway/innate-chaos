"use client";

import type { RegimeResponse } from "@/lib/types";

interface RegimeIndicatorProps {
  data: RegimeResponse;
}

export default function RegimeIndicator({ data }: RegimeIndicatorProps) {
  const regime = data.regime;
  const score = data.risk_score;

  const regimeColor =
    regime === "RISK_ON"
      ? "text-emerald-400"
      : regime === "RISK_OFF"
        ? "text-red-400"
        : "text-yellow-400";

  const regimeBg =
    regime === "RISK_ON"
      ? "bg-emerald-400/10 border-emerald-400/30"
      : regime === "RISK_OFF"
        ? "bg-red-400/10 border-red-400/30"
        : "bg-yellow-400/10 border-yellow-400/30";

  const barColor =
    regime === "RISK_ON"
      ? "bg-emerald-400"
      : regime === "RISK_OFF"
        ? "bg-red-400"
        : "bg-yellow-400";

  const displayRegime = regime.replace("_", " ");

  return (
    <div className="rounded-xl border border-[#262626] bg-[#141414] p-5 flex flex-col items-center justify-center gap-4">
      <h2 className="text-lg font-semibold text-white self-start">
        Market Regime
      </h2>
      <div
        className={`text-3xl font-bold tracking-wider ${regimeColor} px-6 py-3 rounded-lg border ${regimeBg}`}
      >
        {displayRegime}
      </div>
      <div className="w-full">
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>Risk Score</span>
          <span>{(score * 100).toFixed(0)}%</span>
        </div>
        <div className="h-3 w-full rounded-full bg-[#262626] overflow-hidden">
          <div
            className={`h-full rounded-full ${barColor} transition-all duration-500`}
            style={{ width: `${score * 100}%` }}
          />
        </div>
      </div>
      {data.suggestion && (
        <p className="text-sm text-gray-400 text-center mt-1">
          {data.suggestion.summary}
        </p>
      )}
    </div>
  );
}
