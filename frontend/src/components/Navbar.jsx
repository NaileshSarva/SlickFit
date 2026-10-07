import React from "react";

function NavIcon({ type }) {
  const iconProps = { width: "16", height: "16", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round" };
  switch (type) {
    case "home":
      return <svg {...iconProps}><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>;
    case "plan":
      return <svg {...iconProps}><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>;
    case "train":
      return <svg {...iconProps}><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>;
    case "nutrition":
      return <svg {...iconProps}><path d="M18 8h1a4 4 0 0 1 0 8h-1"/><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg>;
    case "progress":
      return <svg {...iconProps}><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>;
    case "profile":
      return <svg {...iconProps}><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>;
    default:
      return null;
  }
}

export default function Navbar({ activeTab, setActiveTab, user, activeEvent, onLogout }) {
  const eventDateStr = activeEvent?.event_date || activeEvent?.target_date;
  const eventDaysLeft = eventDateStr
    ? Math.max(0, Math.ceil((new Date(eventDateStr + "T00:00:00") - new Date()) / (1000 * 60 * 60 * 24)))
    : null;

  const navItems = [
    { id: "home", label: "Home" },
    { id: "plan", label: "Plan" },
    { id: "train", label: "Train" },
    { id: "nutrition", label: "Fuel" },
    { id: "progress", label: "Progress" },
    { id: "profile", label: "Profile" },
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
            SlickFit
          </div>
          {user?.is_demo && (
            <span className="brand-badge" title="Running in isolated synthetic demo mode">
              Demo Mode
            </span>
          )}
        </div>

        {activeEvent && (
          <div className="event-countdown-pill" title={`Target Event: ${activeEvent.title}`}>
            <span className="event-title-text">{activeEvent.title}</span>
            {eventDaysLeft !== null && (
              <>
                <span style={{ color: "var(--text-muted)" }}>•</span>
                <span className="countdown-num">{eventDaysLeft}d</span>
                <span className="countdown-label">remaining</span>
              </>
            )}
          </div>
        )}

        {/* Desktop Navigation Links & Sign Out */}
        <nav className="desktop-nav-menu" aria-label="Main Navigation">
          <ul className="nav-links">
            {navItems.map((item) => (
              <li key={item.id}>
                <button
                  type="button"
                  className={`nav-item-btn ${activeTab === item.id ? "active" : ""}`}
                  onClick={() => setActiveTab(item.id)}
                  aria-current={activeTab === item.id ? "page" : undefined}
                  style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
                >
                  <NavIcon type={item.id} />
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

      {/* Mobile Bottom Navigation Bar */}
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
            <span className="mobile-nav-icon"><NavIcon type={item.id} /></span>
            <span className="mobile-nav-label">{item.label}</span>
          </button>
        ))}
      </nav>
    </>
  );
}
