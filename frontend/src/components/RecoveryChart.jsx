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
  if (!data || data.length === 0) {
    return (
      <div style={{ textAlign: "center", padding: "40px 20px", color: "var(--text-muted)" }}>
        No recovery check-in logs recorded yet. Complete daily check-ins to view readiness trends.
      </div>
    );
  }

  const chartData = data.map((item) => ({
    date: item.checkin_date?.slice(5) || item.local_date?.slice(5) || item.date?.slice(5) || "Day",
    sleep_quality: item.sleep_quality,
    soreness: item.soreness_level || item.soreness,
    fatigue: item.fatigue || (item.energy_level ? 6 - item.energy_level : 2),
  }));

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
          <Legend
            wrapperStyle={{ paddingTop: "10px", fontSize: "12px" }}
            formatter={(value) => {
              if (value === "sleep_quality") return "Sleep Quality (1-5)";
              if (value === "soreness") return "Muscle Soreness (1-5)";
              return "Fatigue Level (1-5)";
            }}
          />
          <Line
            type="monotone"
            dataKey="sleep_quality"
            stroke="var(--accent-primary)"
            strokeWidth={2.5}
            dot={{ r: 4, fill: "var(--accent-primary)" }}
          />
          <Line
            type="monotone"
            dataKey="soreness"
            stroke="var(--accent-amber)"
            strokeWidth={2}
            strokeDasharray="4 4"
            dot={{ r: 3, fill: "var(--accent-amber)" }}
          />
          <Line
            type="monotone"
            dataKey="fatigue"
            stroke="var(--accent-cyan)"
            strokeWidth={1.5}
            dot={{ r: 3, fill: "var(--accent-cyan)" }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
