import React from "react";

export default function DisclaimerBanner({ type = "general" }) {
  if (type === "nutrition") {
    return (
      <div className="alert-banner alert-info" role="note">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: "2px" }}>
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="16" x2="12" y2="12" />
          <line x1="12" y1="8" x2="12.01" y2="8" />
        </svg>
        <div>
          <strong>Non-Clinical Nutrition Guidance:</strong> Suggestions are general sports nutrition guidelines tailored for athletic fueling and Indian culinary contexts. They are not medical, dietary, or clinical prescriptions. Consult a qualified clinical dietitian or physician for specific medical dietary requirements.
        </div>
      </div>
    );
  }

  return (
    <div className="alert-banner alert-warning" role="note">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: "2px" }}>
        <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
        <line x1="12" y1="9" x2="12" y2="13" />
        <line x1="12" y1="17" x2="12.01" y2="17" />
      </svg>
      <div>
        <strong>Safety &amp; Non-Medical Notice:</strong> SlickFit is an automated athletic planning coach. It does not provide medical diagnosis or replace sports medicine professionals. Stop training and seek immediate medical evaluation if you experience chest pain, severe dizziness, unusual shortness of breath, or sharp musculoskeletal pain.
      </div>
    </div>
  );
}
