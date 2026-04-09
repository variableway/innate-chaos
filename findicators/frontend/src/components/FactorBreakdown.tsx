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

function getBarColor(score: number): string {
  if (score >= 0.6) return "#34d399";
  if (score >= 0.4) return "#fbbf24";
  return "#f87171";
}

const LABEL_MAP: Record<string, string> = {
  oil_trend: "Oil Trend",
  gold_trend: "Gold Trend",
  btc_momentum: "BTC Momentum",
  yield_curve: "Yield Curve",
  volatility: "Volatility",
};

export default function FactorBreakdown({
  factor_scores,
}: FactorBreakdownProps) {
  const data = Object.entries(factor_scores).map(([key, value]) => ({
    name: LABEL_MAP[key] || key,
    score: value,
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
                <Cell key={index} fill={getBarColor(entry.score)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
