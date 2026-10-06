import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

function toChartData(curve) {
  if (!curve) return [];
  return curve.dates.map((date, index) => ({
    date,
    fitness: curve.fitness[index],
    fatigue: curve.fatigue[index],
    performance: curve.performance[index],
  }));
}

function Curve({ title, curve }) {
  const data = toChartData(curve);

  return (
    <div className="chart-block">
      <div className="panel-heading">
        <span className="step">Curve</span>
        <h2>{title}</h2>
      </div>
      <div className="chart-frame">
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={data} margin={{ top: 16, right: 24, bottom: 10, left: 0 }}>
            <CartesianGrid stroke="#243348" strokeDasharray="3 3" />
            <XAxis dataKey="date" stroke="#92a4bd" tick={{ fontSize: 12 }} minTickGap={24} />
            <YAxis stroke="#92a4bd" tick={{ fontSize: 12 }} />
            <Tooltip
              contentStyle={{ background: "#101927", border: "1px solid #2d4059", borderRadius: 8 }}
              labelStyle={{ color: "#eef4ff" }}
            />
            <Legend />
            <Line type="monotone" dataKey="fitness" stroke="#49a6ff" dot={false} strokeWidth={2} />
            <Line type="monotone" dataKey="fatigue" stroke="#ff626f" dot={false} strokeWidth={2} />
            <Line type="monotone" dataKey="performance" stroke="#4ee3a5" dot={false} strokeWidth={3} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default function FormCurveChart({ fitCurve, taperCurve }) {
  if (!fitCurve && !taperCurve) {
    return (
      <section className="panel chart-panel empty-chart">
        <div className="panel-heading">
          <span className="step">Output</span>
          <h2>Form Curve</h2>
        </div>
        <p className="muted">Fit the model to plot fitness, fatigue, and predicted performance.</p>
      </section>
    );
  }

  return (
    <section className="panel chart-panel">
      {fitCurve && <Curve title="Post-fit Form Curve" curve={fitCurve} />}
      {taperCurve && <Curve title="Projected Curve Including Taper" curve={taperCurve} />}
    </section>
  );
}
