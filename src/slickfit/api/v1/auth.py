"""Authentication endpoints (v1)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from ...auth.dependencies import CurrentUserDep
from ...auth.security import create_access_token
from ...auth.service import AuthService
from ...config import settings
from ...db.session import get_db
from ..schemas import DemoLoginRequest, LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(
    body: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
    response: Response,
) -> TokenResponse:
    """Register a new athlete account."""
    try:
        user = AuthService.register_user(
            db=db,
            email=body.email,
            password=body.password,
            full_name=body.full_name,
            timezone=body.timezone,
            locale=body.locale,
            units=body.units,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    token = create_access_token(subject=user.id, claims={"email": user.email, "is_demo": user.is_demo})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,  # local dev mode
    )
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_demo=user.is_demo,
    )


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
    response: Response,
) -> TokenResponse:
    """Authenticate athlete credentials and return access token."""
    try:
        user, token = AuthService.authenticate_user(db=db, email=body.email, password=body.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_demo=user.is_demo,
    )


@router.post("/demo-login", response_model=TokenResponse)
def demo_login(
    body: DemoLoginRequest,
    db: Annotated[Session, Depends(get_db)],
    response: Response,
) -> TokenResponse:
    """Fast local demo switcher requiring no credentials or external services."""
    if not settings.demo_mode_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo login is disabled in this environment.",
        )

    user, token = AuthService.get_or_create_demo_user(db=db, demo_key=body.demo_key)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_demo=user.is_demo,
    )


@router.get("/me", response_model=UserResponse)
def get_authenticated_user(current_user: CurrentUserDep) -> UserResponse:
    """Return currently authenticated athlete profile and settings."""
    return UserResponse.model_validate(current_user)


@router.post("/logout")
def logout(response: Response) -> dict[str, str]:
    """Clear session token cookie."""
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out."}
