"""Daily recovery and wellness check-in endpoints (v1)."""

from __future__ import annotations

import datetime as dt
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...auth.dependencies import CurrentUserDep
from ...db.models import DailyCheckIn
from ...db.session import get_db
from ...domain.adaptation import AdaptationService
from ..schemas import DailyCheckInCreateRequest, DailyCheckInResponse

router = APIRouter(prefix="/checkins", tags=["checkins"])


@router.post("", response_model=DailyCheckInResponse, status_code=status.HTTP_201_CREATED)
def record_daily_checkin(
    body: DailyCheckInCreateRequest,
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
) -> DailyCheckInResponse:
    """Record daily recovery markers (sleep, soreness, energy, stress, pain/red-flags)."""
    checkin = DailyCheckIn(
        user_id=current_user.id,
        local_date=body.local_date,
        sleep_duration_hours=body.sleep_duration_hours,
        sleep_quality=body.sleep_quality,
        energy_level=body.energy_level,
        soreness_level=body.soreness_level,
        stress_level=body.stress_level,
        pain_flag=body.pain_flag,
        pain_area=body.pain_area,
        pain_severity=body.pain_severity,
        red_flag_symptom=body.red_flag_symptom,
        notes=body.notes,
        source="app_home",
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)

    # Trigger adaptive planner check
    AdaptationService.process_adaptation(db, current_user.id, trigger_reason="DAILY_CHECKIN")

    return DailyCheckInResponse.model_validate(checkin)


@router.get("/today", response_model=DailyCheckInResponse)
def get_today_checkin(
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
) -> DailyCheckInResponse:
    """Fetch today's recovery check-in if already recorded."""
    today = dt.date.today().isoformat()
    checkin = db.execute(
        select(DailyCheckIn)
        .where(DailyCheckIn.user_id == current_user.id, DailyCheckIn.local_date == today)
        .order_by(DailyCheckIn.created_at.desc())
    ).scalars().first()

    if not checkin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No check-in recorded for today.")
    return DailyCheckInResponse.model_validate(checkin)


@router.get("", response_model=list[DailyCheckInResponse])
def list_recent_checkins(
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
    limit: int = 30,
) -> list[DailyCheckInResponse]:
    """List recent check-ins for the authenticated athlete."""
    checkins = db.execute(
        select(DailyCheckIn)
        .where(DailyCheckIn.user_id == current_user.id)
        .order_by(DailyCheckIn.local_date.desc(), DailyCheckIn.created_at.desc())
        .limit(min(100, limit))
    ).scalars().all()
    return [DailyCheckInResponse.model_validate(c) for c in checkins]
