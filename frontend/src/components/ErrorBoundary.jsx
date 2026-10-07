import React from "react";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an unhandled error:", error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.onRetry) {
      this.props.onRetry();
    }
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="card" style={{ padding: "32px", textAlign: "center", margin: "24px 0" }}>
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ margin: "0 auto 12px auto", display: "block" }}>
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <h2 className="card-title" style={{ color: "var(--accent-primary)", marginBottom: "8px" }}>
            Something went wrong in this section
          </h2>
          <p className="card-subtitle" style={{ maxWidth: "500px", margin: "0 auto 20px auto" }}>
            {this.state.error?.message || "An unexpected rendering error occurred. Your athlete data is safe."}
          </p>
          <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
            <button type="button" className="btn btn-primary" onClick={this.handleRetry}>
              Retry Section
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => window.location.reload()}
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
