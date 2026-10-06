"""Activity logging, workout execution, and data correction endpoints (v1)."""

from __future__ import annotations

import datetime as dt
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...auth.dependencies import CurrentUserDep
from ...db.models import Activity, ActivityRevision, DailyCheckIn, DataAmendment, PlannedSession
from ...db.session import get_db
from ...domain.adaptation import AdaptationService
from ..schemas import ActivityCreateRequest, ActivityResponse, ActivityUpdateRequest

router = APIRouter(prefix="/activities", tags=["activities"])


@router.post("", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def log_activity(
    body: ActivityCreateRequest,
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
) -> ActivityResponse:
    """Log an actual workout session or skipped session."""
    # 1. Enforce Red-Flag Safety Stop: block workout logging if red-flag symptoms active
    latest_checkin = db.execute(
        select(DailyCheckIn)
        .where(DailyCheckIn.user_id == current_user.id)
        .order_by(DailyCheckIn.local_date.desc(), DailyCheckIn.created_at.desc())
    ).scalars().first()

    if latest_checkin and latest_checkin.red_flag_symptom and body.completion_state != "skipped":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="URGENT SAFETY STOP: Workout logging is locked due to reported red-flag medical symptoms. Please seek professional medical evaluation before resuming training.",
        )

    # Link to planned session if supplied and belongs to user
    planned_session = None
    if body.planned_session_id:
        planned_session = db.get(PlannedSession, body.planned_session_id)
        if planned_session and planned_session.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Planned session does not belong to user.")
        if planned_session:
            planned_session.status = body.completion_state

    activity = Activity(
        user_id=current_user.id,
        planned_session_id=body.planned_session_id,
        local_date=body.local_date,
        timezone=current_user.timezone,
        activity_type=body.activity_type,
        duration_min=body.duration_min,
        distance_km=body.distance_km,
        perceived_effort=body.perceived_effort,
        completion_state=body.completion_state,
        early_stop_reason=body.early_stop_reason,
        pain_flag=body.pain_flag,
        pain_notes=body.pain_notes,
        notes=body.notes,
        source="manual_app",
        confidence="high",
        is_manual=True,
    )
    db.add(activity)
    db.flush()

    # Initial revision record
    revision = ActivityRevision(
        activity_id=activity.id,
        user_id=current_user.id,
        revision_number=1,
        duration_min=activity.duration_min,
        distance_km=activity.distance_km,
        perceived_effort=activity.perceived_effort,
        completion_state=activity.completion_state,
        notes=activity.notes,
        change_reason="Initial workout log",
    )
    db.add(revision)
    db.commit()
    db.refresh(activity)

    # Trigger adaptive planner check
    AdaptationService.process_adaptation(db, current_user.id, trigger_reason="ACTIVITY_LOGGED")

    return ActivityResponse.model_validate(activity)


@router.get("", response_model=list[ActivityResponse])
def list_activities(
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
    limit: int = 50,
) -> list[ActivityResponse]:
    """List logged workouts for the authenticated athlete."""
    activities = db.execute(
        select(Activity)
        .where(Activity.user_id == current_user.id)
        .order_by(Activity.local_date.desc(), Activity.created_at.desc())
        .limit(min(100, limit))
    ).scalars().all()
    return [ActivityResponse.model_validate(a) for a in activities]


@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity_detail(
    activity_id: str,
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
) -> ActivityResponse:
    """Get single workout details."""
    activity = db.get(Activity, activity_id)
    if not activity or activity.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found.")
    return ActivityResponse.model_validate(activity)


@router.patch("/{activity_id}", response_model=ActivityResponse)
def correct_activity(
    activity_id: str,
    body: ActivityUpdateRequest,
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
) -> ActivityResponse:
    """Correct an existing workout entry, retaining full audit trail in ActivityRevision and DataAmendment."""
    activity = db.get(Activity, activity_id)
    if not activity or activity.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found.")

    # Record data amendments
    if body.distance_km is not None and body.distance_km != activity.distance_km:
        amendment = DataAmendment(
            user_id=current_user.id,
            entity_type="activity",
            entity_id=activity.id,
            field_name="distance_km",
            prior_value=str(activity.distance_km),
            replacement_value=str(body.distance_km),
            actor_user_id=current_user.id,
            reason=body.change_reason,
        )
        db.add(amendment)
        activity.distance_km = body.distance_km

    if body.duration_min is not None and body.duration_min != activity.duration_min:
        amendment = DataAmendment(
            user_id=current_user.id,
            entity_type="activity",
            entity_id=activity.id,
            field_name="duration_min",
            prior_value=str(activity.duration_min),
            replacement_value=str(body.duration_min),
            actor_user_id=current_user.id,
            reason=body.change_reason,
        )
        db.add(amendment)
        activity.duration_min = body.duration_min

    if body.perceived_effort is not None:
        activity.perceived_effort = body.perceived_effort
    if body.completion_state is not None:
        activity.completion_state = body.completion_state
    if body.notes is not None:
        activity.notes = body.notes

    # Next revision number
    latest_rev_num = len(activity.revisions)
    next_rev_num = latest_rev_num + 1

    revision = ActivityRevision(
        activity_id=activity.id,
        user_id=current_user.id,
        revision_number=next_rev_num,
        duration_min=activity.duration_min,
        distance_km=activity.distance_km,
        perceived_effort=activity.perceived_effort,
        completion_state=activity.completion_state,
        notes=activity.notes,
        change_reason=body.change_reason,
    )
    db.add(revision)
    db.commit()
    db.refresh(activity)

    # Recalculate adaptations
    AdaptationService.process_adaptation(db, current_user.id, trigger_reason="DATA_CORRECTED")

    return ActivityResponse.model_validate(activity)
