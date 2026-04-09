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
import type { AllocationResponse } from "@/lib/types";

interface AllocationPanelProps {
  data: AllocationResponse;
}

const ASSET_COLORS: Record<string, string> = {
  BTC: "#f7931a",
  ETH: "#627eea",
  GOLD: "#ffd700",
  OIL: "#4a4a4a",
  CASH: "#a3a3a3",
};

export default function AllocationPanel({ data }: AllocationPanelProps) {
  const chartData = Object.entries(data.weights).map(([asset, weight]) => ({
    asset,
    weight: weight * 100,
  }));

  return (
    <div className="rounded-xl border border-[#262626] bg-[#141414] p-5">
      <h2 className="text-lg font-semibold text-white mb-1">
        Suggested Allocation
      </h2>
      <p className="text-xs text-gray-500 mb-4">
        Based on {data.regime.replace("_", " ")} regime
      </p>
      {chartData.length === 0 ? (
        <div className="h-48 flex items-center justify-center text-gray-500">
          No allocation data
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={chartData} layout="vertical" margin={{ left: 10 }}>
            <XAxis
              type="number"
              domain={[0, 100]}
              stroke="#555"
              tick={{ fill: "#888", fontSize: 12 }}
              tickFormatter={(v: number) => `${v.toFixed(0)}%`}
            />
            <YAxis
              type="category"
              dataKey="asset"
              stroke="#555"
              tick={{ fill: "#ccc", fontSize: 12, fontWeight: 600 }}
              width={50}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1a1a1a",
                border: "1px solid #333",
                borderRadius: "8px",
                color: "#fff",
              }}
              formatter={(value) => [
                `${Number(value).toFixed(1)}%`,
                "Weight",
              ]}
            />
            <Bar dataKey="weight" radius={[0, 4, 4, 0]} barSize={20}>
              {chartData.map((entry, index) => (
                <Cell
                  key={index}
                  fill={ASSET_COLORS[entry.asset] || "#60a5fa"}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
