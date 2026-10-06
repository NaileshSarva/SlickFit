"""Training plans and revision history endpoints (v1)."""

from __future__ import annotations

import datetime as dt
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...auth.dependencies import CurrentUserDep
from ...db.models import Event, Plan, PlannedSession, PlanRevision
from ...db.session import get_db
from ..schemas import (
    PlanDetailResponse,
    PlannedSessionResponse,
    PlanRevisionResponse,
)

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("/current", response_model=PlanDetailResponse)
def get_current_plan(
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
) -> PlanDetailResponse:
    """Get athlete's currently active training plan with rolling 7-day session schedule."""
    plan = db.execute(
        select(Plan).where(Plan.user_id == current_user.id, Plan.status == "active")
    ).scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active training plan found. Please complete onboarding first.",
        )

    # Fetch event
    event = db.get(Event, plan.event_id)
    event_title = event.title if event else "Active Event"
    event_date = event.event_date if event else dt.date.today().isoformat()

    try:
        ev_date = dt.date.fromisoformat(event_date)
        days_until_event = max(0, (ev_date - dt.date.today()).days)
    except ValueError:
        days_until_event = 0

    # Fetch latest revision
    latest_rev = db.execute(
        select(PlanRevision)
        .where(PlanRevision.plan_id == plan.id)
        .order_by(PlanRevision.revision_number.desc())
    ).scalar_one_or_none()

    if not latest_rev:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No plan revisions found for active plan.",
        )

    # Fetch scheduled sessions for this revision
    sessions = db.execute(
        select(PlannedSession)
        .where(PlannedSession.plan_revision_id == latest_rev.id)
        .order_by(PlannedSession.local_date.asc())
    ).scalars().all()

    return PlanDetailResponse(
        id=plan.id,
        event_id=plan.event_id,
        event_title=event_title,
        event_date=event_date,
        days_until_event=days_until_event,
        algorithm_version=plan.algorithm_version,
        status=plan.status,
        current_revision=PlanRevisionResponse.model_validate(latest_rev),
        sessions=[PlannedSessionResponse.model_validate(s) for s in sessions],
        confidence="derived",
        created_at=plan.created_at,
    )


@router.get("/history", response_model=list[PlanRevisionResponse])
def get_plan_revisions_history(
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
) -> list[PlanRevisionResponse]:
    """Get immutable history of all plan adaptations and revisions for the active plan."""
    plan = db.execute(
        select(Plan).where(Plan.user_id == current_user.id, Plan.status == "active")
    ).scalar_one_or_none()

    if not plan:
        return []

    revisions = db.execute(
        select(PlanRevision)
        .where(PlanRevision.plan_id == plan.id)
        .order_by(PlanRevision.revision_number.desc())
    ).scalars().all()

    return [PlanRevisionResponse.model_validate(r) for r in revisions]
