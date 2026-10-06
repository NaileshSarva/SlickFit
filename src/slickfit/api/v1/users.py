"""User profile and account management endpoints (v1)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...auth.dependencies import CurrentUserDep
from ...auth.service import AuthService
from ...db.session import get_db
from ..schemas import UserResponse, UserUpdateRequest

router = APIRouter(prefix="/me", tags=["users"])


@router.get("", response_model=UserResponse)
def get_me(current_user: CurrentUserDep) -> UserResponse:
    """Get current user record with profile and preferences."""
    return UserResponse.model_validate(current_user)


@router.patch("", response_model=UserResponse)
def update_me(
    body: UserUpdateRequest,
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    """Update current user settings (timezone, locale, units, full name)."""
    if body.full_name is not None:
        current_user.full_name = body.full_name.strip()
    if body.timezone is not None:
        current_user.timezone = body.timezone
    if body.locale is not None:
        current_user.locale = body.locale
    if body.units is not None:
        current_user.units = body.units

    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Completely delete current user and all associated data."""
    AuthService.delete_user_account(db, current_user.id)
