"""Nutrition guidance and meal suggestions endpoints (v1)."""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...auth.dependencies import CurrentUserDep
from ...db.models import AthleteProfile, NutritionProfile, Plan, PlannedSession, PlanRevision
from ...db.session import get_db
from ...domain.nutrition import generate_daily_nutrition_guidance
from ..schemas import NutritionGuidanceResponse

router = APIRouter(prefix="/nutrition", tags=["nutrition"])


@router.get("/today", response_model=NutritionGuidanceResponse)
def get_today_nutrition_guidance(
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
) -> NutritionGuidanceResponse:
    """Generate today's non-clinical nutrition and hydration guidance tailored to athlete's diet and training demand."""
    today = dt.date.today().isoformat()

    # Fetch user profile and preferences
    nut_profile = db.execute(
        select(NutritionProfile).where(NutritionProfile.user_id == current_user.id)
    ).scalar_one_or_none()

    ath_profile = db.execute(
        select(AthleteProfile).where(AthleteProfile.user_id == current_user.id)
    ).scalar_one_or_none()

    dietary_pattern = nut_profile.dietary_pattern if nut_profile else "vegetarian"
    regional_preference = nut_profile.regional_preference if nut_profile else "south_indian"
    allergies = json.loads(nut_profile.allergies_json or "[]") if nut_profile else []
    foods_avoided = json.loads(nut_profile.foods_avoided_json or "[]") if nut_profile else []
    weight_kg = ath_profile.weight_kg if ath_profile else None
    intake_target_kcal = nut_profile.intake_target_kcal if nut_profile else None

    # Determine today's training demand
    training_demand_type = "easy_run"
    plan = db.execute(
        select(Plan).where(Plan.user_id == current_user.id, Plan.status == "active")
    ).scalar_one_or_none()

    if plan:
        latest_rev = db.execute(
            select(PlanRevision)
            .where(PlanRevision.plan_id == plan.id, PlanRevision.status == "current")
            .order_by(PlanRevision.revision_number.desc())
        ).scalar_one_or_none()
        if latest_rev:
            session = db.execute(
                select(PlannedSession)
                .where(PlannedSession.plan_revision_id == latest_rev.id, PlannedSession.local_date == today)
            ).scalar_one_or_none()
            if session:
                training_demand_type = session.session_type

    advice = generate_daily_nutrition_guidance(
        dietary_pattern=dietary_pattern,
        regional_preference=regional_preference,
        allergies=allergies,
        foods_avoided=foods_avoided,
        training_demand_type=training_demand_type,
        weight_kg=weight_kg,
        activity_level=nut_profile.activity_level if nut_profile else "moderate",
        intake_target_kcal=intake_target_kcal,
    )

    return NutritionGuidanceResponse(
        local_date=today,
        dietary_pattern=advice.dietary_pattern,
        regional_preference=advice.regional_preference,
        min_kcal=advice.min_kcal,
        max_kcal=advice.max_kcal,
        protein_g_min=advice.protein_g_min,
        protein_g_max=advice.protein_g_max,
        carbs_g_min=advice.carbs_g_min,
        carbs_g_max=advice.carbs_g_max,
        fats_g_min=advice.fats_g_min,
        fats_g_max=advice.fats_g_max,
        hydration_liters=advice.hydration_liters,
        meal_ideas=advice.meal_ideas,
        rationale=advice.rationale,
        limitations=advice.limitations,
    )
