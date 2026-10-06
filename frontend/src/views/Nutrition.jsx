import React from "react";
import DisclaimerBanner from "../components/DisclaimerBanner.jsx";

export default function Nutrition({ todayNutrition, user }) {
  const nutrition = todayNutrition || {
    diet_type: "vegetarian",
    region: "north_indian",
    target_carbs_g_per_kg: 5.0,
    target_protein_g_per_kg: 1.4,
    target_hydration_liters: 2.8,
    meal_suggestions: [
      {
        timing: "Pre-Run (1-2 Hours Before)",
        food: "Banana with 1-2 slices of toast or a small bowl of light poha / oats.",
        benefit: "Easily digestible complex carbohydrates for stable blood glucose.",
      },
      {
        timing: "Intra-Run Fuel (Runs > 60 mins)",
        food: "Nimbu pani (lemon water) with pinch of rock salt & jaggery, or electrolyte sports drink.",
        benefit: "Sustains electrolyte balance and rapid glycogen replenishment.",
      },
      {
        timing: "Post-Run Recovery (Within 45 mins)",
        food: "Sattu drink with curd / buttermilk or Paneer bhurji with 2 rotis & dal.",
        benefit: "High-quality protein and carbs for muscle repair and glycogen replenishment.",
      },
    ],
    allergy_filtered_items: [],
  };

  const regionalHighlights = {
    north_indian: [
      { name: "Poha with Steamed Sprouts", desc: "Light iron-rich flattened rice with steamed moong sprouts for balanced morning fuel." },
      { name: "Paneer / Tofu Bhurji with Whole Wheat Roti", desc: "Clean vegetarian protein paired with whole wheat carbs for muscle recovery." },
      { name: "Moong Dal Khichdi with Dahi", desc: "Easy to digest post-hard session dinner restoring gut flora and glycogen." },
    ],
    south_indian: [
      { name: "Steamed Idli with Sambar & Tomato Chutney", desc: "Fermented rice & urad dal providing rapid clean energy and probiotics." },
      { name: "Ragi Dosa with Coconut Chutney", desc: "Finger millet rich in calcium and complex carbohydrates for sustained energy." },
      { name: "Curd Rice with Pomegranate", desc: "Cooling recovery staple replenishing electrolytes and soothing digestion." },
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

  const currentRegion = nutrition.region || "north_indian";
  const mealItems = regionalHighlights[currentRegion] || regionalHighlights.north_indian;

  return (
    <div>
      <DisclaimerBanner type="nutrition" />

      {/* Hero Targets Banner */}
      <div className="hero-card">
        <div className="hero-orb" />
        <div style={{ position: "relative", zIndex: 2 }}>
          <div className="card-header">
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                <span className="tag tag-orange">Evidence-Calibrated</span>
                <span className="tag tag-espresso">{nutrition.region?.replace("_", " ")}</span>
              </div>
              <h1 style={{ fontSize: "28px", fontWeight: 800 }}>
                🥗 Daily Athletic Fuel & Hydration Blueprint
              </h1>
              <p style={{ color: "var(--text-secondary)", fontSize: "14px", marginTop: "4px" }}>
                Tailored for: <strong style={{ color: "var(--text-primary)" }}>{nutrition.diet_type?.replace("_", " ")}</strong> (
                {nutrition.region?.replace("_", " ")})
              </p>
            </div>
          </div>

          <div className="grid-3" style={{ marginTop: "16px" }}>
            <div className="stat-box">
              <div className="stat-value" style={{ color: "var(--accent-cyan)", fontSize: "26px" }}>
                {todayNutrition?.carbs_g_min && todayNutrition?.carbs_g_max
                  ? `${todayNutrition.carbs_g_min}–${todayNutrition.carbs_g_max} g`
                  : "230–310 g"}
              </div>
              <div className="stat-label">Carbohydrate Target</div>
              <p style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "6px" }}>
                Glycogen replenishment range
              </p>
            </div>

            <div className="stat-box">
              <div className="stat-value" style={{ color: "var(--accent-primary)", fontSize: "26px" }}>
                {todayNutrition?.protein_g_min && todayNutrition?.protein_g_max
                  ? `${todayNutrition.protein_g_min}–${todayNutrition.protein_g_max} g`
                  : "80–105 g"}
              </div>
              <div className="stat-label">Daily Protein Target</div>
              <p style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "6px" }}>
                Distributed for muscular recovery
              </p>
            </div>

            <div className="stat-box">
              <div className="stat-value" style={{ color: "var(--accent-amber)", fontSize: "26px" }}>
                {todayNutrition?.min_kcal && todayNutrition?.max_kcal
                  ? `${todayNutrition.min_kcal}–${todayNutrition.max_kcal} kcal`
                  : "1900–2250 kcal"}
              </div>
              <div className="stat-label">Estimated Energy</div>
              <p style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "6px" }}>
                Hydration: {todayNutrition?.hydration_liters || "2.8"}L / day
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Timing Meal Guidance */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">⏱️ Session Fuel Timing Protocol</h2>
            <p className="card-subtitle">What and when to eat around your scheduled workout</p>
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "12px", marginTop: "12px" }}>
          {(nutrition.meal_suggestions || []).map((m, idx) => (
            <div
              key={idx}
              style={{
                padding: "18px",
                borderRadius: "var(--radius-md)",
                background: "rgba(0,0,0,0.3)",
                border: "1px solid var(--border-subtle)",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                <strong style={{ fontSize: "15px", color: "var(--accent-primary)" }}>
                  {m.timing}
                </strong>
              </div>
              <p style={{ fontSize: "14px", color: "var(--text-primary)", marginBottom: "6px", lineHeight: "1.5" }}>
                {m.food}
              </p>
              <p style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                💡 <em>{m.benefit}</em>
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Regional Indian Nutrition Options */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">🍛 Regional Indian Performance Staples</h2>
            <p className="card-subtitle">
              Authentic performance food ideas tailored to {currentRegion.replace("_", " ")} cuisine
            </p>
          </div>
        </div>

        <div className="grid-3" style={{ marginTop: "14px" }}>
          {mealItems.map((item, idx) => (
            <div
              key={idx}
              style={{
                padding: "18px",
                borderRadius: "var(--radius-md)",
                background: "rgba(0,0,0,0.25)",
                border: "1px solid var(--border-subtle)",
              }}
            >
              <strong style={{ fontSize: "15px", color: "var(--accent-primary)", display: "block", marginBottom: "6px" }}>
                {item.name}
              </strong>
              <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: "1.5" }}>
                {item.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
