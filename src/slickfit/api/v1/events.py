"""Event management endpoints (v1)."""

from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...auth.dependencies import CurrentUserDep
from ...db.models import Event
from ...db.session import get_db
from ..schemas import EventCreateRequest, EventResponse

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventResponse])
def list_events(
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
) -> list[EventResponse]:
    """List all events belonging to the authenticated athlete."""
    events = db.execute(
        select(Event).where(Event.user_id == current_user.id).order_by(Event.created_at.desc())
    ).scalars().all()
    return [EventResponse.model_validate(ev) for ev in events]


@router.get("/active", response_model=EventResponse)
def get_active_event(
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
) -> EventResponse:
    """Get the currently active target event for the athlete."""
    event = db.execute(
        select(Event).where(Event.user_id == current_user.id, Event.status == "active")
    ).scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active event found. Please complete onboarding or create an event.",
        )
    return EventResponse.model_validate(event)


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    body: EventCreateRequest,
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
) -> EventResponse:
    """Create a new event and activate it."""
    # Archive previous active events
    prev_active = db.execute(
        select(Event).where(Event.user_id == current_user.id, Event.status == "active")
    ).scalars().all()
    for prev in prev_active:
        prev.status = "archived"

    event = Event(
        user_id=current_user.id,
        kind=body.kind,
        sport=body.sport,
        title=body.title,
        event_date=body.event_date,
        timezone=current_user.timezone,
        location=body.location,
        goal_type=body.goal_type,
        target_value=body.target_value,
        target_unit=body.target_unit,
        demands_json=json.dumps(body.demands),
        status="active",
        notes=body.notes,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return EventResponse.model_validate(event)
