"""Application configuration, environment management, and security boundaries."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional

DEV_DEFAULT_SECRET = "slickfit-dev-only-secret-key-do-not-use-in-production-12345"


@dataclass
class Settings:
    app_name: str = "SlickFit API"
    app_version: str = "0.1.0"
    environment: str = os.getenv("SLICKFIT_ENV", "development").lower()
    database_url: str = os.getenv("SLICKFIT_DATABASE_URL", "sqlite:///./slickfit.db")
    raw_secret_key: Optional[str] = os.getenv("SLICKFIT_SECRET_KEY")
    token_expire_minutes: int = int(os.getenv("SLICKFIT_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
    default_timezone: str = "Asia/Kolkata"
    default_locale: str = "en-IN"
    default_units: str = "metric"
    raw_demo_mode: Optional[str] = os.getenv("SLICKFIT_DEMO_MODE")
    cors_origins: list[str] = field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv(
                "SLICKFIT_CORS_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
            ).split(",")
            if origin.strip()
        ]
    )

    @property
    def is_production(self) -> bool:
        return self.environment in ("production", "prod")

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def demo_mode_enabled(self) -> bool:
        if self.raw_demo_mode is not None:
            return self.raw_demo_mode.lower() in ("true", "1", "yes")
        # Default: enabled only in development/testing, disabled in production
        return not self.is_production

    @property
    def secret_key(self) -> str:
        """Resolve secret key with strict production safety validation."""
        if self.raw_secret_key and self.raw_secret_key != DEV_DEFAULT_SECRET:
            return self.raw_secret_key

        if self.is_production:
            raise RuntimeError(
                "CRITICAL SECURITY CONFIGURATION ERROR: SLICKFIT_SECRET_KEY environment variable "
                "must be set to a secure, unique value in production. Development default is not permitted."
            )

        return DEV_DEFAULT_SECRET

    def validate_startup_configuration(self) -> None:
        """Validate safety invariants during application startup."""
        _ = self.secret_key


settings = Settings()
