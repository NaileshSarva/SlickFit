import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from "recharts";

export default function VolumeChart({ data = [] }) {
  if (!data || data.length === 0) {
    return (
      <div style={{ textAlign: "center", padding: "40px 20px", color: "var(--text-muted)" }}>
        No weekly volume data recorded yet. Complete planned sessions to generate volume trends.
      </div>
    );
  }

  const hasPlannedSeries = data.some((item) => item.planned_km != null);
  const chartData = data.map((item) => ({
    week: item.week_label || item.week_start?.slice(5) || "Week",
    planned_km: Number(item.planned_km || 0),
    actual_km: Number(item.distance_km ?? item.actual_km ?? 0),
  }));

  return (
    <div style={{ width: "100%", height: 260 }}>
      <ResponsiveContainer>
        <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
          <XAxis dataKey="week" stroke="var(--text-muted)" fontSize={12} tickLine={false} />
          <YAxis stroke="var(--text-muted)" fontSize={12} unit=" km" tickLine={false} />
          <Tooltip
            contentStyle={{
              backgroundColor: "rgba(22, 19, 22, 0.95)",
              borderColor: "rgba(255, 255, 255, 0.12)",
              borderRadius: "12px",
              color: "var(--text-primary)",
              boxShadow: "0 12px 30px rgba(0,0,0,0.6)",
            }}
          />
          {hasPlannedSeries && (
            <Legend
              wrapperStyle={{ paddingTop: "10px", fontSize: "12px" }}
              formatter={(value) => (value === "planned_km" ? "Planned (km)" : "Completed (km)")}
            />
          )}
          {hasPlannedSeries && (
            <Bar dataKey="planned_km" fill="rgba(56, 189, 248, 0.45)" radius={[6, 6, 0, 0]} />
          )}
          <Bar dataKey="actual_km" fill="var(--accent-primary)" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
