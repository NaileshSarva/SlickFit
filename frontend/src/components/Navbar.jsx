import React from "react";

export default function Navbar({ activeTab, setActiveTab, user, activeEvent, onLogout }) {
  const eventDateStr = activeEvent?.event_date || activeEvent?.target_date;
  const eventDaysLeft = eventDateStr
    ? Math.max(0, Math.ceil((new Date(eventDateStr + "T00:00:00") - new Date()) / (1000 * 60 * 60 * 24)))
    : null;

  const navItems = [
    { id: "home", label: "Home", icon: "⚡" },
    { id: "plan", label: "Plan", icon: "📅" },
    { id: "train", label: "Train", icon: "⏱️" },
    { id: "nutrition", label: "Fuel", icon: "🥗" },
    { id: "progress", label: "Progress", icon: "📈" },
    { id: "profile", label: "Profile", icon: "⚙️" },
  ];

  return (
    <>
      <header className="top-nav">
        <div className="brand-section">
          <div
            className="brand-logo"
            onClick={() => setActiveTab("home")}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") setActiveTab("home");
            }}
          >
            <span>⚡</span> SlickFit
          </div>
          {user?.is_demo && (
            <span className="brand-badge" title="Running in isolated synthetic demo mode">
              Demo Mode
            </span>
          )}
        </div>

        {activeEvent && (
          <div className="event-countdown-pill" title={`Target Event: ${activeEvent.title}`}>
            <span>🎯</span>
            <span className="event-title-text">{activeEvent.title}</span>
            {eventDaysLeft !== null && (
              <>
                <span style={{ color: "var(--text-muted)" }}>•</span>
                <span className="countdown-num">{eventDaysLeft}d</span>
                <span className="countdown-label" style={{ color: "var(--text-secondary)", fontSize: "12px" }}>remaining</span>
              </>
            )}
          </div>
        )}

        {/* Desktop Navigation Links & Sign Out - Visible only on desktop (>=768px) */}
        <nav className="desktop-nav-menu" aria-label="Main Navigation">
          <ul className="nav-links">
            {navItems.map((item) => (
              <li key={item.id}>
                <button
                  type="button"
                  className={`nav-item-btn ${activeTab === item.id ? "active" : ""}`}
                  onClick={() => setActiveTab(item.id)}
                  aria-current={activeTab === item.id ? "page" : undefined}
                >
                  <span style={{ marginRight: "6px" }}>{item.icon}</span>
                  {item.label}
                </button>
              </li>
            ))}
          </ul>

          <div className="desktop-user-actions">
            <span className="desktop-user-name">
              {user?.full_name || user?.email?.split("@")[0] || "Athlete"}
            </span>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={onLogout}
              title="Sign out of current account"
            >
              Sign Out
            </button>
          </div>
        </nav>
      </header>

      {/* Mobile Bottom Navigation Bar - Visible only on mobile (<768px) */}
      <nav className="mobile-nav" role="navigation" aria-label="Mobile Bottom Navigation">
        {navItems.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`mobile-nav-btn ${activeTab === item.id ? "active" : ""}`}
            onClick={() => setActiveTab(item.id)}
            aria-label={item.label}
            aria-current={activeTab === item.id ? "page" : undefined}
          >
            <span className="mobile-nav-icon">{item.icon}</span>
            <span className="mobile-nav-label">{item.label}</span>
          </button>
        ))}
      </nav>
    </>
  );
}
