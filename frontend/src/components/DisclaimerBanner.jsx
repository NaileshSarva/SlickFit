import React from "react";

export default function DisclaimerBanner({ type = "general" }) {
  if (type === "nutrition") {
    return (
      <div className="alert-banner alert-info" role="note">
        <span style={{ fontSize: "18px" }}>🥗</span>
        <div>
          <strong>Non-Clinical Nutrition Guidance:</strong> Suggestions are general sports nutrition guidelines tailored for athletic fueling and Indian culinary contexts. They are not medical, dietary, or clinical prescriptions. Consult a qualified clinical dietitian or physician for specific medical dietary requirements.
        </div>
      </div>
    );
  }

  return (
    <div className="alert-banner alert-warning" role="note">
      <span style={{ fontSize: "18px" }}>⚠️</span>
      <div>
        <strong>Safety & Non-Medical Notice:</strong> SlickFit is an automated athletic planning coach. It does not provide medical diagnosis or replace sports medicine professionals. Stop training and seek immediate medical evaluation if you experience chest pain, severe dizziness, unusual shortness of breath, or sharp musculoskeletal pain.
      </div>
    </div>
  );
}
