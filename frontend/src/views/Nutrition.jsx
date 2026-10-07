import React from "react";
import DisclaimerBanner from "../components/DisclaimerBanner.jsx";

/**
 * Nutrition view.
 * API shape (from /nutrition/today):
 *   dietary_pattern, regional_preference, min_kcal, max_kcal,
 *   protein_g_min, protein_g_max, carbs_g_min, carbs_g_max,
 *   fats_g_min, fats_g_max, hydration_liters,
 *   meal_ideas[{meal, idea, protein_source}], rationale, limitations
 */
export default function Nutrition({ todayNutrition, user }) {
  const n = todayNutrition || null;

  // Readable labels — explicit null check prevents rendering empty parentheses.
  const rawDiet = n?.dietary_pattern;
  const rawRegion = n?.regional_preference;
  const dietLabel = rawDiet ? rawDiet.replace(/_/g, " ") : null;
  const regionLabel = rawRegion ? rawRegion.replace(/_/g, " ") : null;

  // meal_ideas from the API
  const mealIdeas = Array.isArray(n?.meal_ideas) ? n.meal_ideas : [];

  // Regional food highlights keyed on regional_preference values
  const regionalHighlights = {
    north_indian: [
      { name: "Poha with Steamed Sprouts", desc: "Light iron-rich flattened rice with steamed moong sprouts for balanced morning fuel." },
      { name: "Paneer / Tofu Bhurji with Whole Wheat Roti", desc: "Clean protein paired with whole wheat carbs for muscle recovery." },
      { name: "Moong Dal Khichdi with Dahi", desc: "Easy to digest post-session dinner restoring gut flora and glycogen." },
    ],
    south_indian: [
      { name: "Steamed Idli with Sambar & Chutney", desc: "Fermented rice & urad dal providing rapid clean energy and probiotics." },
      { name: "Ragi Dosa with Coconut Chutney", desc: "Finger millet rich in calcium and complex carbohydrates for sustained energy." },
      { name: "Curd Rice with Pomegranate", desc: "Cooling recovery staple replenishing electrolytes and aiding digestion." },
    ],
    west_indian: [
      { name: "Methi Thepla with Low-Fat Curd", desc: "Fenugreek flatbread rich in fiber, minerals, and complex carbs." },
      { name: "Sprouted Matki / Usal", desc: "High protein legume preparation with light traditional spices." },
      { name: "Steamed Khaman Dhokla", desc: "Fermented gram flour snack offering rapid, light pre-workout carbs." },
    ],
    east_indian: [
      { name: "Chana Sattu Sharbat (Sweet or Salted)", desc: "Traditional Bihar superfood rich in natural plant protein and insoluble fiber." },
      { name: "Ghugni (Yellow Pea Curry) with Rice", desc: "High-protein slow-release legume meal ideal for recovery." },
      { name: "Dahi-Chura with Jaggery", desc: "Classic pre-race digestive-friendly energy powerhouse." },
    ],
    central_indian: [
      { name: "Indori Poha with Boiled Moong", desc: "Gentle steamed poha boosted with plant protein." },
      { name: "Dal Bafla with Mixed Dal", desc: "Traditional baked wheat dumplings served with rich five-lentil protein stew." },
    ],
  };

  const mealItems = rawRegion
    ? regionalHighlights[rawRegion] || null
    : null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      <DisclaimerBanner type="nutrition" />

      {/* Hero Targets Banner */}
      <div className="highlight-hero-card">
        <div className="hero-glow" />
        <div style={{ position: "relative", zIndex: 2 }}>
          <div className="card-header" style={{ marginBottom: "12px" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                <span className="tag tag-orange">Evidence-Calibrated</span>
                {regionLabel && <span className="tag tag-espresso">{regionLabel}</span>}
              </div>
              <h1 style={{ fontSize: "24px", fontWeight: 800 }}>
                Daily Athletic Fuel &amp; Hydration Blueprint
              </h1>
              <p style={{ color: "var(--text-secondary)", fontSize: "13px", marginTop: "4px" }}>
                {dietLabel && regionLabel ? (
                  <>
                    Tailored for:{" "}
                    <strong style={{ color: "var(--text-primary)" }}>{dietLabel}</strong>{" "}
                    ({regionLabel})
                  </>
                ) : dietLabel ? (
                  <>
                    Diet type:{" "}
                    <strong style={{ color: "var(--text-primary)" }}>{dietLabel}</strong>
                  </>
                ) : (
                  <span style={{ color: "var(--text-muted)" }}>
                    Diet and region not set — targets below are general guidance only.
                  </span>
                )}
              </p>
              {n?.rationale && (
                <p style={{ color: "var(--text-muted)", fontSize: "12px", marginTop: "4px" }}>
                  {n.rationale}
                </p>
              )}
            </div>
          </div>

          <div className="grid-3" style={{ marginTop: "14px" }}>
            <div className="stat-box">
              <div className="stat-value" style={{ color: "var(--accent-cyan)", fontSize: "24px" }}>
                {n?.carbs_g_min && n?.carbs_g_max
                  ? `${n.carbs_g_min}–${n.carbs_g_max} g`
                  : "--"}
              </div>
              <div className="stat-label">Carbohydrate Target</div>
              <p style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "4px" }}>
                {n?.carbs_g_min ? "Glycogen replenishment range" : "Log a session to get a target"}
              </p>
            </div>

            <div className="stat-box">
              <div className="stat-value" style={{ color: "var(--accent-primary)", fontSize: "24px" }}>
                {n?.protein_g_min && n?.protein_g_max
                  ? `${n.protein_g_min}–${n.protein_g_max} g`
                  : "--"}
              </div>
              <div className="stat-label">Daily Protein Target</div>
              <p style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "4px" }}>
                {n?.protein_g_min ? "Distributed for muscular recovery" : "Log a session to get a target"}
              </p>
            </div>

            <div className="stat-box">
              <div className="stat-value" style={{ color: "var(--accent-amber)", fontSize: "24px" }}>
                {n?.min_kcal && n?.max_kcal
                  ? `${n.min_kcal}–${n.max_kcal} kcal`
                  : "--"}
              </div>
              <div className="stat-label">Estimated Energy</div>
              <p style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "4px" }}>
                {n?.hydration_liters
                  ? `Hydration: ${n.hydration_liters}L / day`
                  : "Log check-ins to refine estimates"}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Today's Meal Ideas — from API meal_ideas field */}
      <div className="card">
        <div className="card-header" style={{ marginBottom: "14px" }}>
          <div>
            <h2 className="card-title">Today's Meal Ideas</h2>
            <p className="card-subtitle">
              {mealIdeas.length > 0
                ? "Suggested meals based on your training day and preferences"
                : "What and when to eat around your scheduled workout"}
            </p>
          </div>
        </div>

        {mealIdeas.length > 0 ? (
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {mealIdeas.map((m, idx) => (
              <div
                key={idx}
                style={{
                  padding: "14px 16px",
                  borderRadius: "var(--radius-md)",
                  background: "rgba(0,0,0,0.3)",
                  border: "1px solid var(--border-subtle)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px", flexWrap: "wrap", gap: "6px" }}>
                  <strong style={{ fontSize: "14px", color: "var(--accent-primary)" }}>
                    {m.meal}
                  </strong>
                  {m.protein_source && (
                    <span className="tag tag-cyan" style={{ fontSize: "10px", padding: "2px 8px" }}>
                      {m.protein_source}
                    </span>
                  )}
                </div>
                <p style={{ fontSize: "13px", color: "var(--text-primary)", lineHeight: "1.4" }}>
                  {m.idea}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div
            style={{
              padding: "24px 16px",
              borderRadius: "var(--radius-md)",
              background: "rgba(0,0,0,0.2)",
              border: "1px solid var(--border-subtle)",
              textAlign: "center",
              color: "var(--text-muted)",
              fontSize: "13px",
            }}
          >
            <strong style={{ display: "block", marginBottom: "4px", color: "var(--text-secondary)" }}>
              No meal ideas yet
            </strong>
            <p>
              Meal suggestions appear once your daily plan has been generated.
              Complete onboarding and set a target event to get started.
            </p>
          </div>
        )}
      </div>

      {/* Regional Indian Performance Staples — only shown when region is known */}
      <div className="card">
        <div className="card-header" style={{ marginBottom: "14px" }}>
          <div>
            <h2 className="card-title">Regional Indian Performance Staples</h2>
            <p className="card-subtitle">
              {mealItems
                ? `Authentic performance food ideas tailored to ${regionLabel} cuisine`
                : "Set your regional preference in Profile to see localised suggestions"}
            </p>
          </div>
        </div>

        {mealItems ? (
          <div className="grid-3" style={{ marginTop: "6px" }}>
            {mealItems.map((item, idx) => (
              <div
                key={idx}
                style={{
                  padding: "14px 16px",
                  borderRadius: "var(--radius-md)",
                  background: "rgba(0,0,0,0.25)",
                  border: "1px solid var(--border-subtle)",
                }}
              >
                <strong style={{ fontSize: "14px", color: "var(--accent-primary)", display: "block", marginBottom: "4px" }}>
                  {item.name}
                </strong>
                <p style={{ fontSize: "12px", color: "var(--text-secondary)", lineHeight: "1.4" }}>
                  {item.desc}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: "var(--text-muted)", fontSize: "13px", textAlign: "center", padding: "12px 0" }}>
            Go to Profile → set your region to see localised food ideas here.
          </p>
        )}
      </div>

      {/* Limitations notice when present */}
      {n?.limitations && (
        <p style={{ fontSize: "11px", color: "var(--text-dim)", textAlign: "center", lineHeight: "1.5" }}>
          {n.limitations}
        </p>
      )}
    </div>
  );
}
