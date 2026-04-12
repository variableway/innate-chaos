"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface FactorBreakdownProps {
  factor_scores: Record<string, number>;
}

interface FactorMeta {
  label: string;
  weight: number;
  inverted: boolean;
  explanation: string;
  highLabel: string;
  lowLabel: string;
}

const FACTOR_META: Record<string, FactorMeta> = {
  oil_trend: {
    label: "Oil Trend",
    weight: 0.2,
    inverted: false,
    explanation: "7-day oil price % change (threshold: ±5%)",
    highLabel: "Rising oil = economic growth",
    lowLabel: "Falling oil = growth concern",
  },
  gold_trend: {
    label: "Gold Trend",
    weight: 0.25,
    inverted: true,
    explanation: "7-day gold % change, inverted (threshold: ±5%)",
    highLabel: "Rising gold = flight to safety",
    lowLabel: "Falling gold = risk appetite",
  },
  btc_momentum: {
    label: "BTC Momentum",
    weight: 0.25,
    inverted: false,
    explanation: "7-day BTC % change (threshold: ±10%)",
    highLabel: "Rising BTC = risk appetite",
    lowLabel: "Falling BTC = risk aversion",
  },
  yield_curve: {
    label: "Yield Curve",
    weight: 0.2,
    inverted: false,
    explanation: "7-day T10Y2Y spread change (threshold: ±2%)",
    highLabel: "Steepening = growth outlook",
    lowLabel: "Flattening = recession signal",
  },
  volatility: {
    label: "Volatility",
    weight: 0.1,
    inverted: false,
    explanation: "BTC+ETH daily return std dev (20-day)",
    highLabel: "High vol = elevated activity",
    lowLabel: "Low vol = calm market",
  },
};

function getBarColor(score: number, inverted: boolean): string {
  const effective = inverted ? 1 - score : score;
  if (effective >= 0.6) return "#34d399";
  if (effective >= 0.4) return "#fbbf24";
  return "#f87171";
}

function getDirectionLabel(score: number, inverted: boolean): {
  text: string;
  color: string;
} {
  const effective = inverted ? 1 - score : score;
  if (effective >= 0.6) return { text: "Risk-On", color: "text-emerald-400" };
  if (effective <= 0.4) return { text: "Risk-Off", color: "text-red-400" };
  return { text: "Neutral", color: "text-yellow-400" };
}

function getDriverLabel(score: number, meta: FactorMeta): string {
  if (meta.inverted) {
    return score < 0.4 ? meta.highLabel : score > 0.6 ? meta.lowLabel : meta.highLabel;
  }
  return score >= 0.6 ? meta.highLabel : score <= 0.4 ? meta.lowLabel : meta.highLabel;
}

export default function FactorBreakdown({
  factor_scores,
}: FactorBreakdownProps) {
  const data = Object.entries(factor_scores).map(([key, value]) => ({
    key,
    name: FACTOR_META[key]?.label || key,
    score: value,
    meta: FACTOR_META[key],
  }));

  return (
    <div className="rounded-xl border border-[#262626] bg-[#141414] p-5">
      <h2 className="text-lg font-semibold text-white mb-4">
        Factor Breakdown
      </h2>
      {data.length === 0 ? (
        <div className="h-48 flex items-center justify-center text-gray-500">
          No factor data
        </div>
      ) : (
        <>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={data} layout="vertical" margin={{ left: 20 }}>
              <XAxis
                type="number"
                domain={[0, 1]}
                stroke="#555"
                tick={{ fill: "#888", fontSize: 12 }}
              />
              <YAxis
                type="category"
                dataKey="name"
                stroke="#555"
                tick={{ fill: "#ccc", fontSize: 12 }}
                width={110}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1a1a1a",
                  border: "1px solid #333",
                  borderRadius: "8px",
                  color: "#fff",
                }}
                formatter={(value) => [Number(value).toFixed(3), "Score"]}
              />
              <Bar dataKey="score" radius={[0, 4, 4, 0]} barSize={20}>
                {data.map((entry, index) => (
                  <Cell
                    key={index}
                    fill={getBarColor(
                      entry.score,
                      entry.meta?.inverted ?? false
                    )}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>

          {/* Factor detail table */}
          <div className="mt-4 space-y-2">
            {data.map(({ key, score, meta }) => {
              if (!meta) return null;
              const dir = getDirectionLabel(score, meta.inverted);
              return (
                <div
                  key={key}
                  className="flex items-center justify-between text-xs px-1 py-1.5 border-b border-[#1f1f1f] last:border-0"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-gray-300 font-medium w-28">
                      {meta.label}
                    </span>
                    <span className="text-gray-500">
                      ({(meta.weight * 100).toFixed(0)}%)
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-gray-500">{getDriverLabel(score, meta)}</span>
                    <span className={`font-medium w-16 text-right ${dir.color}`}>
                      {dir.text}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
