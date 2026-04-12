"use client";

import type { RegimeResponse } from "@/lib/types";

interface RegimeIndicatorProps {
  data: RegimeResponse;
}

const FACTOR_LABELS: Record<string, string> = {
  oil_trend: "Oil",
  gold_trend: "Gold",
  btc_momentum: "BTC",
  yield_curve: "Yield Curve",
  volatility: "Volatility",
};

function getDrivers(
  factorScores: Record<string, number>
): { riskOn: string[]; riskOff: string[] } {
  const riskOn: string[] = [];
  const riskOff: string[] = [];

  for (const [key, score] of Object.entries(factorScores)) {
    const label = FACTOR_LABELS[key] || key;
    if (score >= 0.6) riskOn.push(`${label} (${score.toFixed(2)})`);
    else if (score <= 0.4) riskOff.push(`${label} (${score.toFixed(2)})`);
  }

  return { riskOn, riskOff };
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

  const { riskOn, riskOff } = getDrivers(data.factor_scores);

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
        {/* Threshold markers */}
        <div className="relative h-4 mt-0.5">
          <div
            className="absolute text-[10px] text-red-400/60"
            style={{ left: "40%", transform: "translateX(-50%)" }}
          >
            | 0.40
          </div>
          <div
            className="absolute text-[10px] text-emerald-400/60"
            style={{ left: "60%", transform: "translateX(-50%)" }}
          >
            | 0.60
          </div>
        </div>
      </div>

      {/* Driver summary */}
      {(riskOn.length > 0 || riskOff.length > 0) && (
        <div className="w-full text-xs space-y-1 border-t border-[#1f1f1f] pt-3 mt-1">
          {riskOn.length > 0 && (
            <p>
              <span className="text-gray-500">Pulling risk-on:</span>{" "}
              <span className="text-emerald-400">
                {riskOn.join(", ")}
              </span>
            </p>
          )}
          {riskOff.length > 0 && (
            <p>
              <span className="text-gray-500">Pulling risk-off:</span>{" "}
              <span className="text-red-400">
                {riskOff.join(", ")}
              </span>
            </p>
          )}
          {riskOn.length === 0 && riskOff.length === 0 && (
            <p className="text-gray-500">
              All factors neutral — no strong directional signal.
            </p>
          )}
        </div>
      )}

      {data.suggestion && (
        <p className="text-sm text-gray-400 text-center mt-1">
          {data.suggestion.summary}
        </p>
      )}
    </div>
  );
}
