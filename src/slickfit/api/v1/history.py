"""Unified history feed, progress trends, and amendment audit trail endpoints (v1)."""

from __future__ import annotations

import datetime as dt
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...auth.dependencies import CurrentUserDep
from ...db.models import (
    Activity,
    AdaptationEvent,
    DailyCheckIn,
    DataAmendment,
    Plan,
    PlannedSession,
    PlanRevision,
)
from ...db.session import get_db
from ..schemas import (
    DataAmendmentResponse,
    HistoryFeedItem,
    ProgressTrendResponse,
)

router = APIRouter(tags=["history_and_progress"])


@router.get("/history", response_model=list[HistoryFeedItem])
def get_unified_history(
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=50, ge=1, le=100),
) -> list[HistoryFeedItem]:
    """Retrieve unified chronological feed of activities, check-ins, adaptations, and corrections."""
    items: list[HistoryFeedItem] = []

    # 1. Activities
    activities = db.execute(
        select(Activity).where(Activity.user_id == current_user.id).order_by(Activity.local_date.desc()).limit(limit)
    ).scalars().all()
    for act in activities:
        items.append(
            HistoryFeedItem(
                id=act.id,
                item_type="activity",
                local_date=act.local_date,
                timestamp=act.created_at,
                title=f"{act.activity_type.replace('_', ' ').title()} ({act.completion_state.title()})",
                summary=f"Duration: {act.duration_min:.1f} min | Distance: {act.distance_km or 0:.1f} km | Effort: RPE {act.perceived_effort}/10",
                metrics={
                    "duration_min": act.duration_min,
                    "distance_km": act.distance_km,
                    "perceived_effort": act.perceived_effort,
                    "completion_state": act.completion_state,
                    "pain_flag": act.pain_flag,
                },
                details={"notes": act.notes, "early_stop_reason": act.early_stop_reason},
            )
        )

    # 2. Check-Ins
    checkins = db.execute(
        select(DailyCheckIn).where(DailyCheckIn.user_id == current_user.id).order_by(DailyCheckIn.local_date.desc()).limit(limit)
    ).scalars().all()
    for c in checkins:
        items.append(
            HistoryFeedItem(
                id=c.id,
                item_type="checkin",
                local_date=c.local_date,
                timestamp=c.created_at,
                title="Recovery & Wellness Check-In",
                summary=f"Energy: {c.energy_level}/5 | Soreness: {c.soreness_level}/5 | Sleep: {c.sleep_duration_hours or 0:.1f}h (Q: {c.sleep_quality}/5)",
                metrics={
                    "energy_level": c.energy_level,
                    "soreness_level": c.soreness_level,
                    "sleep_duration_hours": c.sleep_duration_hours,
                    "pain_flag": c.pain_flag,
                    "red_flag": c.red_flag_symptom,
                },
                details={"notes": c.notes, "pain_area": c.pain_area, "pain_severity": c.pain_severity},
            )
        )

    # 3. Adaptation Events
    adaptations = db.execute(
        select(AdaptationEvent).where(AdaptationEvent.user_id == current_user.id).order_by(AdaptationEvent.created_at.desc()).limit(limit)
    ).scalars().all()
    for ad in adaptations:
        items.append(
            HistoryFeedItem(
                id=ad.id,
                item_type="adaptation",
                local_date=ad.created_at.strftime("%Y-%m-%d"),
                timestamp=ad.created_at,
                title="Plan Adaptation Event",
                summary=ad.explanation,
                metrics={"reason_codes": ad.reason_codes_json},
                details={"user_visible_impact": ad.user_visible_impact},
            )
        )

    # 4. Data Amendments
    amendments = db.execute(
        select(DataAmendment).where(DataAmendment.user_id == current_user.id).order_by(DataAmendment.created_at.desc()).limit(limit)
    ).scalars().all()
    for am in amendments:
        items.append(
            HistoryFeedItem(
                id=am.id,
                item_type="amendment",
                local_date=am.created_at.strftime("%Y-%m-%d"),
                timestamp=am.created_at,
                title=f"Data Correction: {am.entity_type}.{am.field_name}",
                summary=f"Changed from '{am.prior_value}' to '{am.replacement_value}'. Reason: {am.reason}",
                metrics={"field": am.field_name, "prior": am.prior_value, "replacement": am.replacement_value},
                details={"reason": am.reason, "source": am.source},
            )
        )

    # Sort unified feed by timestamp descending
    items.sort(key=lambda x: x.timestamp, reverse=True)
    return items[:limit]


@router.get("/progress", response_model=ProgressTrendResponse)
def get_progress_trends(
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
) -> ProgressTrendResponse:
    """Answer 'Am I improving?' with measured running trends and plan adherence."""
    activities = db.execute(
        select(Activity)
        .where(Activity.user_id == current_user.id)
        .order_by(Activity.local_date.asc())
    ).scalars().all()

    completed_acts = [a for a in activities if a.completion_state == "completed"]
    total_runs = len(completed_acts)
    total_distance = sum(a.distance_km or 0.0 for a in completed_acts)
    total_duration = sum(a.duration_min for a in completed_acts)

    # Plan adherence calculation
    planned_sessions = db.execute(
        select(PlannedSession).where(PlannedSession.user_id == current_user.id)
    ).scalars().all()

    active_planned_count = len([s for s in planned_sessions if s.session_type != "rest"])
    consistency_rate = (total_runs / active_planned_count * 100.0) if active_planned_count > 0 else 100.0

    recent_runs_data = [
        {
            "date": a.local_date,
            "duration_min": a.duration_min,
            "distance_km": a.distance_km,
            "pace_min_km": round(a.duration_min / a.distance_km, 2) if a.distance_km and a.distance_km > 0 else None,
            "effort": a.perceived_effort,
        }
        for a in completed_acts[-10:]
    ]

    # Weekly series
    weekly_agg: dict[str, float] = {}
    for a in completed_acts:
        try:
            d = dt.date.fromisoformat(a.local_date)
            # Monday of the week
            week_key = (d - dt.timedelta(days=d.weekday())).isoformat()
            weekly_agg[week_key] = weekly_agg.get(week_key, 0.0) + (a.distance_km or 0.0)
        except Exception:
            continue

    weekly_series = [{"week_start": k, "distance_km": round(v, 1)} for k, v in sorted(weekly_agg.items())]

    return ProgressTrendResponse(
        total_runs_completed=total_runs,
        total_distance_km=round(total_distance, 1),
        total_duration_min=round(total_duration, 1),
        consistency_rate_pct=round(min(100.0, consistency_rate), 1),
        recent_runs=recent_runs_data,
        weekly_mileage_series=weekly_series,
    )


@router.get("/data/amendments", response_model=list[DataAmendmentResponse])
def list_data_amendments(
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
) -> list[DataAmendmentResponse]:
    """List data amendment audit records for the authenticated athlete."""
    amendments = db.execute(
        select(DataAmendment).where(DataAmendment.user_id == current_user.id).order_by(DataAmendment.created_at.desc())
    ).scalars().all()
    return [DataAmendmentResponse.model_validate(a) for a in amendments]
