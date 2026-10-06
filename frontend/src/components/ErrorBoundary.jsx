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
          <div style={{ fontSize: "36px", marginBottom: "12px" }}>⚠️</div>
          <h2 className="card-title" style={{ color: "var(--accent-primary)", marginBottom: "8px" }}>
            Something went wrong in this section
          </h2>
          <p className="card-subtitle" style={{ maxWidth: "500px", margin: "0 auto 20px auto" }}>
            {this.state.error?.message || "An unexpected rendering error occurred. Your athlete data is safe."}
          </p>
          <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
            <button type="button" className="btn btn-primary" onClick={this.handleRetry}>
              🔄 Retry Section
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
