"""Onboarding API endpoints (v1)."""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...auth.dependencies import CurrentUserDep
from ...db.models import Event, Plan, PlannedSession, PlanRevision
from ...db.session import get_db
from ...domain.onboarding import OnboardingService
from ..schemas import (
    EventResponse,
    OnboardingRequest,
    OnboardingResponse,
    PlanDetailResponse,
    PlannedSessionResponse,
    PlanRevisionResponse,
)

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.post("", response_model=OnboardingResponse, status_code=status.HTTP_201_CREATED)
def complete_onboarding_flow(
    body: OnboardingRequest,
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
) -> OnboardingResponse:
    """Complete multi-step onboarding intake and generate the first training plan revision."""
    try:
        event, plan, plan_rev, sessions = OnboardingService.complete_onboarding(
            db=db,
            user_id=current_user.id,
            event_data=body.event.model_dump(),
            baseline_data=body.baseline.model_dump(),
            availability_data=body.availability.model_dump(),
            profile_data=body.profile.model_dump() if body.profile else None,
            nutrition_data=body.nutrition.model_dump() if body.nutrition else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    # Calculate days until event
    try:
        ev_date = dt.date.fromisoformat(event.event_date)
        days_until_event = max(0, (ev_date - dt.date.today()).days)
    except ValueError:
        days_until_event = 0

    plan_detail = PlanDetailResponse(
        id=plan.id,
        event_id=event.id,
        event_title=event.title,
        event_date=event.event_date,
        days_until_event=days_until_event,
        algorithm_version=plan.algorithm_version,
        status=plan.status,
        current_revision=PlanRevisionResponse.model_validate(plan_rev),
        sessions=[PlannedSessionResponse.model_validate(s) for s in sessions],
        confidence="derived",
        created_at=plan.created_at,
    )

    return OnboardingResponse(
        message="Onboarding complete. Your personalized training plan has been created.",
        event=EventResponse.model_validate(event),
        plan=plan_detail,
    )


@router.get("/status")
def get_onboarding_status(
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    """Check whether the current athlete has completed onboarding and has an active plan."""
    active_event = db.execute(
        select(Event).where(Event.user_id == current_user.id, Event.status == "active")
    ).scalar_one_or_none()

    active_plan = db.execute(
        select(Plan).where(Plan.user_id == current_user.id, Plan.status == "active")
    ).scalar_one_or_none()

    return {
        "onboarding_completed": bool(active_event and active_plan),
        "active_event_id": active_event.id if active_event else None,
        "active_plan_id": active_plan.id if active_plan else None,
        "timezone": current_user.timezone,
    }
