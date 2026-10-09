"""User profile and account management endpoints (v1)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...auth.dependencies import CurrentUserDep
from ...auth.service import AuthService
from ...db.models import AthleteProfile, NutritionProfile
from ...db.session import get_db
from ..schemas import ProfileSettingsUpdateRequest, UserResponse
import json

router = APIRouter(prefix="/me", tags=["users"])


@router.get("", response_model=UserResponse)
def get_me(current_user: CurrentUserDep) -> UserResponse:
    """Get current user record with profile and preferences."""
    return UserResponse.model_validate(current_user)


@router.patch("", response_model=UserResponse)
def update_me(
    body: ProfileSettingsUpdateRequest,
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

    profile_fields = {"age_band", "sex", "height_cm", "weight_kg", "region"}
    nutrition_fields = {
        "dietary_pattern", "regional_preference", "allergies", "foods_avoided",
        "goal_preference", "intake_target_kcal", "activity_level",
    }
    changes = body.model_dump(exclude_unset=True)
    if profile_fields.intersection(changes):
        profile = db.execute(select(AthleteProfile).where(AthleteProfile.user_id == current_user.id)).scalar_one_or_none()
        if not profile:
            profile = AthleteProfile(user_id=current_user.id)
            db.add(profile)
        for field in profile_fields.intersection(changes):
            value = changes[field]
            setattr(profile, field, value.strip() if isinstance(value, str) else value)

    if nutrition_fields.intersection(changes):
        nutrition = db.execute(select(NutritionProfile).where(NutritionProfile.user_id == current_user.id)).scalar_one_or_none()
        if not nutrition:
            nutrition = NutritionProfile(user_id=current_user.id)
            db.add(nutrition)
        for field in nutrition_fields.intersection(changes):
            value = changes[field]
            if field in ("allergies", "foods_avoided"):
                setattr(nutrition, f"{field}_json", json.dumps(value or []))
            elif value is not None:
                setattr(nutrition, field, value.strip() if isinstance(value, str) else value)

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
