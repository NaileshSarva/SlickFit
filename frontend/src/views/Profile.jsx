import React, { useState, useEffect } from "react";
import { listAmendments, updateProfileSettings } from "../api.js";
import DisclaimerBanner from "../components/DisclaimerBanner.jsx";

export default function Profile({
  user = null,
  activeEvent = null,
  onUserUpdated = () => {},
  onLogout = null,
}) {
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [ageBand, setAgeBand] = useState(user?.profile?.age_band || user?.athlete_profile?.age_band || "");
  const [region, setRegion] = useState(user?.profile?.region || user?.athlete_profile?.region || "");
  const [sex, setSex] = useState(user?.profile?.sex || "");
  const [heightCm, setHeightCm] = useState(user?.profile?.height_cm ?? "");
  const [weightKg, setWeightKg] = useState(user?.profile?.weight_kg ?? "");
  const [timezone, setTimezone] = useState(user?.timezone || "Asia/Kolkata");
  const [units, setUnits] = useState(user?.units || "metric");
  const [dietaryPattern, setDietaryPattern] = useState(user?.nutrition_profile?.dietary_pattern || "vegetarian");
  const [regionalPreference, setRegionalPreference] = useState(user?.nutrition_profile?.regional_preference || "south_indian");
  const [allergies, setAllergies] = useState(() => { try { return JSON.parse(user?.nutrition_profile?.allergies_json || "[]"); } catch { return []; } });
  const [foodsAvoided, setFoodsAvoided] = useState(() => { try { return JSON.parse(user?.nutrition_profile?.foods_avoided_json || "[]"); } catch { return []; } });
  const [intakeTarget, setIntakeTarget] = useState(user?.nutrition_profile?.intake_target_kcal ?? "");
  const [activityLevel, setActivityLevel] = useState(user?.nutrition_profile?.activity_level || "moderate");
  const [amendments, setAmendments] = useState([]);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || "");
      setAgeBand(user.profile?.age_band || user.athlete_profile?.age_band || "");
      setRegion(user.profile?.region || user.athlete_profile?.region || "");
      setSex(user.profile?.sex || "");
      setHeightCm(user.profile?.height_cm ?? "");
      setWeightKg(user.profile?.weight_kg ?? "");
      setTimezone(user.timezone || "Asia/Kolkata");
      setUnits(user.units || "metric");
      setDietaryPattern(user.nutrition_profile?.dietary_pattern || "vegetarian");
      setRegionalPreference(user.nutrition_profile?.regional_preference || "south_indian");
      try { setAllergies(JSON.parse(user.nutrition_profile?.allergies_json || "[]")); } catch { setAllergies([]); }
      try { setFoodsAvoided(JSON.parse(user.nutrition_profile?.foods_avoided_json || "[]")); } catch { setFoodsAvoided([]); }
      setIntakeTarget(user.nutrition_profile?.intake_target_kcal ?? "");
      setActivityLevel(user.nutrition_profile?.activity_level || "moderate");
    }
  }, [user]);

  useEffect(() => {
    let isMounted = true;
    listAmendments()
      .then((res) => {
        if (!isMounted) return;
        setAmendments(Array.isArray(res) ? res : (res?.amendments || []));
      })
      .catch(() => {
        if (isMounted) setAmendments([]);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  async function handleSaveProfile(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    setMessage("");

    try {
      const updated = await updateProfileSettings({
        full_name: fullName.trim(), age_band: ageBand, region: region.trim(), sex,
        height_cm: heightCm === "" ? null : Number(heightCm),
        weight_kg: weightKg === "" ? null : Number(weightKg), timezone, units,
        dietary_pattern: dietaryPattern, regional_preference: regionalPreference,
        allergies, foods_avoided: foodsAvoided,
        activity_level: activityLevel,
        intake_target_kcal: intakeTarget === "" ? null : Number(intakeTarget),
      });
      setMessage("Profile and coaching preferences saved.");
      if (onUserUpdated) onUserUpdated(updated);
    } catch (err) {
      setError(err.message || "Failed to update profile.");
    } finally {
      setSaving(false);
    }
  }

  const eventTargetDist = activeEvent?.target_value || activeEvent?.target_distance_km || null;
  const eventDate = activeEvent?.event_date || activeEvent?.target_date || null;

  return (
    <div>
      <DisclaimerBanner type="general" />

      {message && <div className="alert-banner alert-success">{message}</div>}
      {error && <div className="alert-banner alert-danger">{error}</div>}

      <div className="grid-2">
        {/* Left Column: Athlete Profile & Account Settings */}
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Athlete Account & Profile</h2>
              <p className="card-subtitle">Manage personal information and preferences</p>
            </div>
            {user?.is_demo && <span className="tag tag-orange">Demo Mode</span>}
          </div>

          <form onSubmit={handleSaveProfile}>
            <div className="form-group">
              <label className="form-label">Email Address (Account Identifier)</label>
              <input
                type="email"
                className="form-input"
                value={user?.email || ""}
                disabled
                style={{ opacity: 0.6 }}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input
                type="text"
                className="form-input"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Age Band (Optional)</label>
                <select
                  className="form-select"
                  value={ageBand}
                  onChange={(e) => setAgeBand(e.target.value)}
                >
                  <option value="">Not Specified</option>
                  <option value="18-29">18-29</option>
                  <option value="30-39">30-39</option>
                  <option value="40-49">40-49</option>
                  <option value="50-59">50-59</option>
                  <option value="60+">60+</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Region / City (Optional)</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Bengaluru, Mumbai"
                  value={region}
                  onChange={(e) => setRegion(e.target.value)}
                />
              </div>
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Sex (Optional)</label>
                <select className="form-select" value={sex} onChange={(e) => setSex(e.target.value)}>
                  <option value="">Not specified</option><option value="female">Female</option><option value="male">Male</option><option value="another">Another identity</option><option value="prefer_not_to_say">Prefer not to say</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Height (cm, optional)</label>
                <input className="form-input" type="number" min="50" max="280" value={heightCm} onChange={(e) => setHeightCm(e.target.value)} />
              </div>
            </div>
            <div className="grid-2">
              <div className="form-group"><label className="form-label">Weight (kg, optional)</label><input className="form-input" type="number" min="20" max="350" step="0.1" value={weightKg} onChange={(e) => setWeightKg(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Timezone</label><input className="form-input" value={timezone} onChange={(e) => setTimezone(e.target.value)} placeholder="Asia/Kolkata" /></div>
            </div>
            <div className="grid-2">
              <div className="form-group"><label className="form-label">Units</label><select className="form-select" value={units} onChange={(e) => setUnits(e.target.value)}><option value="metric">Metric</option><option value="imperial">Imperial</option></select></div>
              <div className="form-group"><label className="form-label">Diet preference</label><select className="form-select" value={dietaryPattern} onChange={(e) => setDietaryPattern(e.target.value)}><option value="vegetarian">Vegetarian</option><option value="eggetarian">Eggetarian</option><option value="non_vegetarian">Non-vegetarian</option><option value="vegan">Vegan</option><option value="jain">Jain</option><option value="swaminarayan">Swaminarayan</option></select></div>
            </div>
            <div className="grid-2">
              <div className="form-group"><label className="form-label">Cuisine preference</label><select className="form-select" value={regionalPreference} onChange={(e) => setRegionalPreference(e.target.value)}><option value="south_indian">South Indian</option><option value="north_indian">North Indian</option><option value="west_indian">West Indian</option><option value="east_indian">East Indian</option><option value="central_indian">Central Indian</option><option value="pan_indian">Pan Indian</option></select></div>
              <div className="form-group"><label className="form-label">Optional daily kcal target</label><input className="form-input" type="number" min="500" max="10000" value={intakeTarget} onChange={(e) => setIntakeTarget(e.target.value)} placeholder="No target set" /></div>
            </div>
            <div className="form-group"><label className="form-label">Typical activity level</label><select className="form-select" value={activityLevel} onChange={(e) => setActivityLevel(e.target.value)}><option value="low">Low / mostly seated</option><option value="moderate">Moderate / regularly active</option><option value="high">High / frequent training</option></select></div>
            <div className="form-group"><label className="form-label">Allergies (comma separated)</label><input className="form-input" value={allergies.join(", ")} onChange={(e) => setAllergies(e.target.value.split(",").map((v) => v.trim()).filter(Boolean))} placeholder="peanuts, dairy" /></div>
            <div className="form-group"><label className="form-label">Foods avoided (comma separated)</label><input className="form-input" value={foodsAvoided.join(", ")} onChange={(e) => setFoodsAvoided(e.target.value.split(",").map((v) => v.trim()).filter(Boolean))} placeholder="foods you prefer to avoid" /></div>

            <div style={{ display: "flex", gap: "12px", alignItems: "center", marginTop: "12px", flexWrap: "wrap" }}>
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? "Saving Changes..." : "Save Profile Settings"}
              </button>
              {onLogout && (
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={onLogout}
                  title="Sign out of current account"
                >
                  Sign Out
                </button>
              )}
            </div>
          </form>
        </div>

        {/* Right Column: Active Event & Availability Summary */}
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Active Target Event</h2>
              <p className="card-subtitle">Current preparation target</p>
            </div>
            <span className="tag tag-cyan">{activeEvent?.sport || activeEvent?.kind || "Running"}</span>
          </div>

          {activeEvent ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              <div className="workout-block-item">
                <div>
                  <strong style={{ fontSize: "14px", color: "var(--text-primary)" }}>Event Title</strong>
                  <p style={{ fontSize: "13px", color: "var(--text-secondary)" }}>{activeEvent.title}</p>
                </div>
              </div>

              <div className="grid-2">
                {eventTargetDist && (
                  <div className="workout-block-item">
                    <div>
                      <strong style={{ fontSize: "14px", color: "var(--text-primary)" }}>Target Distance</strong>
                      <p style={{ fontSize: "13px", color: "var(--text-secondary)" }}>
                        {eventTargetDist} {activeEvent.target_unit || "km"}
                      </p>
                    </div>
                  </div>
                )}

                {eventDate && (
                  <div className="workout-block-item">
                    <div>
                      <strong style={{ fontSize: "14px", color: "var(--text-primary)" }}>Target Date</strong>
                      <p style={{ fontSize: "13px", color: "var(--text-secondary)" }}>
                        {eventDate}
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {activeEvent.notes && (
                <div className="workout-block-item">
                  <div>
                    <strong style={{ fontSize: "14px", color: "var(--text-primary)" }}>Goal Notes</strong>
                    <p style={{ fontSize: "13px", color: "var(--text-secondary)" }}>
                      {activeEvent.notes}
                    </p>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="muted" style={{ padding: "20px 0", textAlign: "center" }}>
              No active target event registered.
            </p>
          )}
        </div>
      </div>

      {/* Immutable Data Amendments Table */}
      <div className="card" style={{ marginTop: "22px" }}>
        <div className="card-header">
          <div>
            <h2 className="card-title">Immutable Data Amendment Audit Trail</h2>
            <p className="card-subtitle">
              All manual changes to logged activities are preserved with mandatory reasoning.
            </p>
          </div>
          <span className="tag tag-neutral">{amendments.length} Amendments</span>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "12px" }}>
          {amendments.length === 0 ? (
            <p className="muted" style={{ padding: "24px 0", textAlign: "center" }}>
              No data amendments recorded. Your logged activities remain exactly as originally recorded.
            </p>
          ) : (
            amendments.map((a, idx) => (
              <div
                key={a.id || idx}
                style={{
                  padding: "16px",
                  borderRadius: "var(--radius-md)",
                  background: "rgba(0,0,0,0.3)",
                  border: "1px solid var(--border-subtle)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px" }}>
                  <div>
                    <strong>Entity #{a.entity_id} ({a.entity_type})</strong>
                    <span style={{ fontSize: "12px", color: "var(--text-muted)", marginLeft: "8px" }}>
                      {new Date(a.created_at).toLocaleString()}
                    </span>
                  </div>
                  <span className="tag tag-amber">{a.field_name}</span>
                </div>
                <div style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "6px" }}>
                  Changed from <span style={{ color: "#fca5a5" }}>"{a.old_value}"</span> to{" "}
                  <span style={{ color: "var(--accent-primary)" }}>"{a.new_value}"</span>
                </div>
                <p style={{ fontSize: "12px", color: "var(--accent-cyan)", marginTop: "4px" }}>
                  <strong>Audit Reason:</strong> {a.amendment_reason}
                </p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
