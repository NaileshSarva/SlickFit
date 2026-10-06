"""FastAPI application factory and middleware configuration."""

from __future__ import annotations

import time
import uuid

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ..config import settings
from .schemas import ErrorDetail, ErrorResponse
from .v1.activities import router as activities_router
from .v1.auth import router as auth_router
from .v1.checkins import router as checkins_router
from .v1.events import router as events_router
from .v1.history import router as history_router
from .v1.nutrition import router as nutrition_router
from .v1.onboarding import router as onboarding_router
from .v1.plans import router as plans_router
from .v1.users import router as users_router


def create_app() -> FastAPI:
    """Create and configure the SlickFit FastAPI application."""
    # Validate startup configuration safety invariants
    settings.validate_startup_configuration()

    # Ensure database schema is initialized for local development / SQLite
    from ..db.session import init_db
    init_db()

    app = FastAPI(
        title="SlickFit API",
        version=settings.app_version,
        description="Personalized event-preparation coach API (running-first & custom events)",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID and timing middleware
    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        start_time = time.perf_counter()

        response: Response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = f"{duration_ms:.2f}"
        return response

    # Exception Handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        request_id = getattr(request.state, "request_id", "")
        error_payload = ErrorResponse(
            code=f"HTTP_{exc.status_code}",
            message=str(exc.detail),
            request_id=request_id,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload.model_dump(),
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        request_id = getattr(request.state, "request_id", "")
        field_errors = [
            ErrorDetail(
                loc=[str(loc_item) for loc_item in err.get("loc", [])],
                msg=err.get("msg", "Validation error"),
                type=err.get("type", "value_error"),
            )
            for err in exc.errors()
        ]
        error_payload = ErrorResponse(
            code="VALIDATION_ERROR",
            message="Request payload validation failed.",
            field_errors=field_errors,
            request_id=request_id,
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_payload.model_dump(),
        )

    # Health and readiness endpoints (safe, no private or health data)
    @app.get("/health", tags=["system"])
    def health_check() -> dict[str, str]:
        return {
            "status": "ok",
            "version": settings.app_version,
            "environment": settings.environment,
        }

    @app.get("/ready", tags=["system"])
    def readiness_check() -> dict[str, str]:
        return {"status": "ready"}

    # Register API v1 routers
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(events_router, prefix="/api/v1")
    app.include_router(onboarding_router, prefix="/api/v1")
    app.include_router(plans_router, prefix="/api/v1")
    app.include_router(activities_router, prefix="/api/v1")
    app.include_router(checkins_router, prefix="/api/v1")
    app.include_router(nutrition_router, prefix="/api/v1")
    app.include_router(history_router, prefix="/api/v1")

    return app


app = create_app()
