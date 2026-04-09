"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import type { PriceHistoryPoint } from "@/lib/types";

interface PriceChartProps {
  asset: string;
  data: PriceHistoryPoint[];
}

export default function PriceChart({ asset, data }: PriceChartProps) {
  const chartData = data.map((point) => ({
    date: new Date(point.time).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
    price: point.price,
  }));

  return (
    <div className="rounded-xl border border-[#262626] bg-[#141414] p-5">
      <h2 className="text-lg font-semibold text-white mb-4">
        {asset} Price History
      </h2>
      {chartData.length === 0 ? (
        <div className="h-64 flex items-center justify-center text-gray-500">
          No data available
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
            <XAxis
              dataKey="date"
              stroke="#555"
              tick={{ fill: "#888", fontSize: 12 }}
            />
            <YAxis
              stroke="#555"
              tick={{ fill: "#888", fontSize: 12 }}
              domain={["auto", "auto"]}
              tickFormatter={(v: number) =>
                `$${Number(v).toLocaleString(undefined, { maximumFractionDigits: 0 })}`
              }
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1a1a1a",
                border: "1px solid #333",
                borderRadius: "8px",
                color: "#fff",
              }}
              formatter={(value) => [
                `$${Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
                "Price",
              ]}
            />
            <Line
              type="monotone"
              dataKey="price"
              stroke="#60a5fa"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: "#60a5fa" }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
