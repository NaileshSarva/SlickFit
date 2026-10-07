import React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from "recharts";

export default function RecoveryChart({ data = [] }) {
  const chartData = (Array.isArray(data) ? data : [])
    .map((item) => {
      const energy = Number(item.energy_level ?? item.metrics?.energy_level);
      const soreness = Number(item.soreness_level ?? item.metrics?.soreness_level);
      return {
        date: item.local_date?.slice(5) || item.checkin_date?.slice(5) || item.date?.slice(5) || "Day",
        energy_level: Number.isFinite(energy) ? energy : null,
        soreness_level: Number.isFinite(soreness) ? soreness : null,
      };
    })
    .filter((item) => item.energy_level !== null || item.soreness_level !== null);

  if (chartData.length === 0) {
    return (
      <div style={{ textAlign: "center", padding: "40px 20px", color: "var(--text-muted)" }}>
        No recovery check-ins with energy or soreness scores yet.
      </div>
    );
  }

  return (
    <div style={{ width: "100%", height: 260 }}>
      <ResponsiveContainer>
        <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
          <XAxis dataKey="date" stroke="var(--text-muted)" fontSize={12} tickLine={false} />
          <YAxis stroke="var(--text-muted)" fontSize={12} domain={[1, 5]} ticks={[1, 2, 3, 4, 5]} tickLine={false} />
          <Tooltip
            contentStyle={{
              backgroundColor: "rgba(22, 19, 22, 0.95)",
              borderColor: "rgba(255, 255, 255, 0.12)",
              borderRadius: "12px",
              color: "var(--text-primary)",
              boxShadow: "0 12px 30px rgba(0,0,0,0.6)",
            }}
          />
          <Line
            type="monotone"
            dataKey="energy_level"
            stroke="var(--accent-primary)"
            strokeWidth={2.5}
            dot={{ r: 4, fill: "var(--accent-primary)" }}
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="soreness_level"
            stroke="var(--accent-amber)"
            strokeWidth={2}
            strokeDasharray="4 4"
            dot={{ r: 3, fill: "var(--accent-amber)" }}
            connectNulls={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
