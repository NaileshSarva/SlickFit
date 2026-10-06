import React, { useState } from "react";
import { demoLogin, loginUser, registerUser } from "../api.js";
import DisclaimerBanner from "../components/DisclaimerBanner.jsx";

export default function Landing({ onAuthSuccess }) {
  const [isRegistering, setIsRegistering] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [loading, setLoading] = useState(false);
  const [demoLoading, setDemoLoading] = useState("");
  const [error, setError] = useState("");

  async function handleDemoLogin(demoKey) {
    setDemoLoading(demoKey);
    setError("");
    try {
      const res = await demoLogin(demoKey);
      if (onAuthSuccess) onAuthSuccess(res);
    } catch (err) {
      setError(err.message || "Failed to launch demo account.");
    } finally {
      setDemoLoading("");
    }
  }

  async function handleAuthSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      let res;
      if (isRegistering) {
        res = await registerUser({
          email: email.trim(),
          password,
          full_name: fullName.trim() || undefined,
        });
      } else {
        res = await loginUser({
          email: email.trim(),
          password,
        });
      }
      if (onAuthSuccess) onAuthSuccess(res);
    } catch (err) {
      setError(err.message || "Authentication failed. Please verify credentials.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: "1080px", margin: "40px auto", padding: "0 20px" }}>
      {/* Top Header */}
      <div style={{ textAlign: "center", marginBottom: "40px" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: "10px", marginBottom: "14px" }}>
          <span style={{ fontSize: "36px" }}>⚡</span>
          <h1
            style={{
              fontSize: "42px",
              fontWeight: "800",
              fontFamily: "var(--font-heading)",
              background: "linear-gradient(135deg, #FF6D29 0%, #ffaa75 50%, #ffffff 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              letterSpacing: "-0.03em",
            }}
          >
            SlickFit
          </h1>
        </div>
        <p style={{ fontSize: "18px", color: "var(--text-secondary)", maxWidth: "700px", margin: "0 auto", lineHeight: "1.6" }}>
          The intelligent, India-first personalized endurance event coach.
        </p>
        <div style={{ display: "inline-flex", gap: "8px", marginTop: "14px", flexWrap: "wrap", justifyContent: "center" }}>
          {["Plan", "Train", "Track", "Evaluate", "Adapt", "Repeat"].map((step, idx) => (
            <React.Fragment key={step}>
              <span style={{ color: idx === 0 ? "var(--accent-primary)" : "var(--text-secondary)", fontWeight: 600, fontSize: "13px" }}>
                {step}
              </span>
              {idx < 5 && <span style={{ color: "var(--text-muted)", fontSize: "13px" }}>→</span>}
            </React.Fragment>
          ))}
        </div>
      </div>

      <DisclaimerBanner type="general" />

      {error && <div className="alert-banner alert-danger">{error}</div>}

      <div className="grid-2" style={{ marginTop: "32px", alignItems: "start" }}>
        {/* Left Column: Quick 1-Click Demo Profiles */}
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">🚀 1-Click Instant Demo Experience</h2>
              <p className="card-subtitle">Zero setup required. Explore fully provisioned test runners.</p>
            </div>
            <span className="tag tag-orange">Local Demo</span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "16px", marginTop: "16px" }}>
            <div
              className="card-interactive"
              style={{
                padding: "18px",
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--border-subtle)",
                background: "rgba(0,0,0,0.3)",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px", flexWrap: "wrap", gap: "8px" }}>
                <strong style={{ fontSize: "15px", color: "var(--text-primary)" }}>
                  🏃‍♂️ Arjun Sharma — 10K Target
                </strong>
                <span className="tag tag-cyan">Intermediate</span>
              </div>
              <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginBottom: "14px", lineHeight: "1.5" }}>
                Target: 10 km in 6 weeks. Baseline: 22 km/wk, 5:45 min/km easy pace. Vegetarian, North Indian.
              </p>
              <button
                type="button"
                className="btn btn-primary btn-sm"
                style={{ width: "100%" }}
                disabled={Boolean(demoLoading)}
                onClick={() => handleDemoLogin("demo1")}
              >
                {demoLoading === "demo1" ? "Launching Arjun..." : "Launch Arjun Sharma Profile →"}
              </button>
            </div>

            <div
              className="card-interactive"
              style={{
                padding: "18px",
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--border-subtle)",
                background: "rgba(0,0,0,0.3)",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px", flexWrap: "wrap", gap: "8px" }}>
                <strong style={{ fontSize: "15px", color: "var(--text-primary)" }}>
                  🌱 Priya Nair — Baseline Builder
                </strong>
                <span className="tag tag-amber">First-Time 5K</span>
              </div>
              <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginBottom: "14px", lineHeight: "1.5" }}>
                Unknown baseline volume, 8 weeks to 5K finish. Safe walk-run progression with South Indian regional fuel options.
              </p>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                style={{ width: "100%" }}
                disabled={Boolean(demoLoading)}
                onClick={() => handleDemoLogin("demo2")}
              >
                {demoLoading === "demo2" ? "Launching Priya..." : "Launch Priya Nair Profile →"}
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Real Account Registration / Sign-In */}
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">{isRegistering ? "Create Athlete Account" : "Sign In to SlickFit"}</h2>
              <p className="card-subtitle">
                {isRegistering
                  ? "Start fresh. No synthetic demographics will be invented."
                  : "Welcome back! Access your active plan and history."}
              </p>
            </div>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => {
                setIsRegistering(!isRegistering);
                setError("");
              }}
            >
              {isRegistering ? "Switch to Sign In" : "Register New"}
            </button>
          </div>

          <form onSubmit={handleAuthSubmit} style={{ marginTop: "16px" }}>
            {isRegistering && (
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Rahul Verma"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                />
              </div>
            )}

            <div className="form-group">
              <label className="form-label">Email Address</label>
              <input
                type="email"
                className="form-input"
                placeholder="runner@slickfit.local"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Password</label>
              <input
                type="password"
                className="form-input"
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: "100%", marginTop: "10px" }}
              disabled={loading}
            >
              {loading
                ? isRegistering
                  ? "Creating Account..."
                  : "Signing In..."
                : isRegistering
                ? "Create Account & Start Onboarding →"
                : "Sign In →"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
