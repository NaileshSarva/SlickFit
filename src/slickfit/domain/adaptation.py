"""Adaptive planner engine for SlickFit.

Evaluates recovery check-ins, workout execution (completed/partial/skipped/harder),
and safety red-flags to adjust upcoming sessions with deterministic reason codes.
Never stacks missed sessions blindly into adjacent days.
"""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import asdict, dataclass
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.models import (
    Activity,
    AdaptationEvent,
    DailyCheckIn,
    Event,
    Plan,
    PlannedSession,
    PlanRevision,
    User,
)
from .planner import (
    PLANNER_ALGORITHM_VERSION,
    GeneratedSession,
    PlannedWorkoutBlock,
    compute_snapshot_hash,
)


@dataclass
class AdaptationDecision:
    should_adapt: bool
    reason_codes: list[str]
    explanation: str
    safety_stop: bool
    adjusted_sessions: list[dict[str, Any]]


def evaluate_adaptation(
    current_sessions: list[PlannedSession],
    latest_checkin: Optional[DailyCheckIn] = None,
    recent_activities: Optional[list[Activity]] = None,
    missed_session_action: Optional[str] = None,  # "drop" | "reschedule_safe"
    today_str: Optional[str] = None,
) -> AdaptationDecision:
    """Evaluate whether upcoming sessions in the current 7-day window require adaptation."""
    today = today_str or dt.date.today().isoformat()
    reason_codes: list[str] = []
    explanation_parts: list[str] = []
    safety_stop = False

    # 1. Safety Red-Flag Check
    if latest_checkin and latest_checkin.red_flag_symptom:
        safety_stop = True
        reason_codes.append("RED_FLAG_SAFETY_STOP")
        explanation = (
            "URGENT SAFETY STOP: Red-flag symptoms reported. Exercise recommendations have been completely "
            "suspended. Please rest and consult a qualified medical professional before resuming training."
        )
        return AdaptationDecision(
            should_adapt=True,
            reason_codes=reason_codes,
            explanation=explanation,
            safety_stop=True,
            adjusted_sessions=[],
        )

    # 2. Pain Check
    pain_reported = False
    if latest_checkin and latest_checkin.pain_flag:
        pain_reported = True
        reason_codes.append("PAIN_REPORTED")
        explanation_parts.append(
            f"Pain reported in {latest_checkin.pain_area or 'body'} (severity {latest_checkin.pain_severity}/10). "
            "Upcoming high-intensity workouts converted to rest or gentle recovery walk."
        )
    elif recent_activities:
        recent_pain = any(a.pain_flag for a in recent_activities[-2:])
        if recent_pain:
            pain_reported = True
            reason_codes.append("PAIN_REPORTED_IN_WORKOUT")
            explanation_parts.append("Pain reported during recent workout. Softening upcoming training load.")

    # 3. Recovery & Fatigue Check
    low_recovery = False
    if latest_checkin:
        soreness = latest_checkin.soreness_level if latest_checkin.soreness_level is not None else 1
        energy = latest_checkin.energy_level if latest_checkin.energy_level is not None else 3
        sleep_q = latest_checkin.sleep_quality if latest_checkin.sleep_quality is not None else 3

        is_high_soreness = soreness >= 4
        is_low_energy = energy <= 2
        is_poor_sleep = sleep_q <= 2
        if is_high_soreness or is_low_energy or is_poor_sleep:
            low_recovery = True
            reason_codes.append("LOW_RECOVERY")
            explanation_parts.append(
                f"Low recovery markers (Energy: {energy}/5, "
                f"Soreness: {soreness}/5). Lightening immediate sessions."
            )

    # 4. Actual Effort vs Planned Effort Check
    high_effort = False
    if recent_activities and len(recent_activities) > 0:
        latest_act = recent_activities[-1]
        rpe = latest_act.perceived_effort if latest_act.perceived_effort is not None else 5
        if rpe >= 8 and latest_act.completion_state == "completed":
            high_effort = True
            reason_codes.append("HIGHER_THAN_PLANNED_EFFORT")
            explanation_parts.append(
                f"Recent session perceived effort was high (RPE {rpe}/10). "
                "Ensuring adequate aerobic recovery buffer."
            )

    # 5. Missed Session Handling
    missed_detected = False
    if recent_activities and len(recent_activities) > 0:
        latest_act = recent_activities[-1]
        if latest_act.completion_state == "skipped":
            missed_detected = True
            reason_codes.append("MISSED_SESSION_SAFELY_DROPPED")
            explanation_parts.append(
                "Missed workout detected. To prevent overuse injury, missed volume is intentionally dropped "
                "rather than stacked into subsequent days."
            )

    should_adapt = bool(pain_reported or low_recovery or high_effort or missed_detected)

    if not should_adapt:
        return AdaptationDecision(
            should_adapt=False,
            reason_codes=["NO_SIGNIFICANT_DEVIATION"],
            explanation="What changed: Plan kept intact. Why: Training inputs and recovery markers are on track. Event impact: Steady progression toward target event.",
            safety_stop=False,
            adjusted_sessions=[],
        )

    # Build adjusted session prescriptions for future sessions (date >= today)
    adjusted_sessions: list[dict[str, Any]] = []
    what_changed_list: list[str] = []

    for s in current_sessions:
        sess_data = {
            "id": s.id,
            "local_date": s.local_date,
            "session_type": s.session_type,
            "purpose": s.purpose,
            "duration_min_min": s.duration_min_min,
            "duration_min_max": s.duration_min_max,
            "distance_unit": s.distance_unit,
            "distance_km_min": s.distance_km_min,
            "distance_km_max": s.distance_km_max,
            "effort_target": s.effort_target,
            "blocks_json": s.blocks_json,
            "target_pace_sec_per_km": s.target_pace_sec_per_km,
            "priority": s.priority,
            "flexibility_window_days": s.flexibility_window_days,
            "status": s.status,
            "reason_codes": json.loads(s.reason_codes_json or "[]"),
        }

        # Apply adaptations only to upcoming sessions
        if s.local_date >= today and s.session_type != "rest":
            if pain_reported:
                # Convert to rest or very light 20 min walk
                sess_data["session_type"] = "recovery_walk"
                sess_data["purpose"] = "Pain mitigation: active recovery walk"
                sess_data["duration_min_min"] = 15
                sess_data["duration_min_max"] = 25
                sess_data["effort_target"] = "Very Gentle Walking (RPE 1-2)"
                sess_data["reason_codes"].append("ADAPTED_FOR_PAIN_MITIGATION")
                if "Converted upcoming workouts to gentle recovery walk" not in what_changed_list:
                    what_changed_list.append("Converted upcoming workouts to gentle recovery walk")
            elif low_recovery:
                # Reduce duration by 20-30% and ensure effort is strictly easy conversational
                sess_data["duration_min_max"] = max(20, int(s.duration_min_max * 0.75))
                sess_data["duration_min_min"] = max(15, int(s.duration_min_min * 0.75))
                if sess_data["distance_km_max"]:
                    sess_data["distance_km_max"] = round(sess_data["distance_km_max"] * 0.75, 1)
                sess_data["effort_target"] = "Very Easy / Conversational (RPE 2-3)"
                sess_data["reason_codes"].append("ADAPTED_FOR_LOW_RECOVERY")
                if "Reduced workout volume by 25% with conversational effort" not in what_changed_list:
                    what_changed_list.append("Reduced workout volume by 25% with conversational effort")
            elif high_effort:
                if s.session_type in ("tempo", "intervals"):
                    sess_data["session_type"] = "easy_run"
                    sess_data["purpose"] = "Converted quality workout to easy aerobic run for fatigue recovery"
                    sess_data["effort_target"] = "Easy / Conversational (RPE 3-4)"
                    sess_data["reason_codes"].append("DOWNGRADED_QUALITY_WORKOUT")
                    if "Replaced high-intensity workout with easy aerobic session" not in what_changed_list:
                        what_changed_list.append("Replaced high-intensity workout with easy aerobic session")

        adjusted_sessions.append(sess_data)

    what_changed = "; ".join(what_changed_list) if what_changed_list else "Adjusted upcoming microcycle schedule"
    why = " ".join(explanation_parts)
    event_impact = "Protects long-term aerobic consistency and prevents overuse injury without sacrificing overall readiness."
    full_explanation = f"What changed: {what_changed}. Why: {why} Event impact: {event_impact}"

    return AdaptationDecision(
        should_adapt=True,
        reason_codes=reason_codes,
        explanation=full_explanation,
        safety_stop=False,
        adjusted_sessions=adjusted_sessions,
    )


class AdaptationService:
    """Executes atomic plan adaptations and records immutable revision history."""

    @classmethod
    def process_adaptation(
        cls,
        db: Session,
        user_id: str,
        trigger_reason: str = "SCHEDULED_EVALUATION",
    ) -> Optional[PlanRevision]:
        user = db.get(User, user_id)
        if not user:
            return None

        # Fetch active plan
        plan = db.execute(
            select(Plan).where(Plan.user_id == user_id, Plan.status == "active")
        ).scalar_one_or_none()
        if not plan:
            return None

        # Fetch latest revision & its sessions
        latest_rev = db.execute(
            select(PlanRevision)
            .where(PlanRevision.plan_id == plan.id, PlanRevision.status == "current")
            .order_by(PlanRevision.revision_number.desc())
        ).scalar_one_or_none()
        if not latest_rev:
            return None

        current_sessions = db.execute(
            select(PlannedSession)
            .where(PlannedSession.plan_revision_id == latest_rev.id)
            .order_by(PlannedSession.local_date.asc())
        ).scalars().all()

        # Fetch latest checkin & recent activities
        latest_checkin = db.execute(
            select(DailyCheckIn)
            .where(DailyCheckIn.user_id == user_id)
            .order_by(DailyCheckIn.created_at.desc())
        ).scalars().first()

        recent_acts = db.execute(
            select(Activity)
            .where(Activity.user_id == user_id)
            .order_by(Activity.local_date.desc(), Activity.created_at.desc())
            .limit(5)
        ).scalars().all()

        # Do not re-apply a check-in or activity trigger after it has already
        # produced a revision. Ignore inputs that predate the current revision.
        if trigger_reason == "DAILY_CHECKIN":
            if latest_checkin and latest_checkin.created_at and latest_checkin.created_at <= latest_rev.created_at:
                latest_checkin = None
        elif trigger_reason in ("ACTIVITY_LOGGED", "DATA_CORRECTED"):
            if latest_checkin and latest_checkin.created_at and latest_checkin.created_at <= latest_rev.created_at:
                latest_checkin = None
        recent_acts = [a for a in recent_acts if a.created_at and a.created_at > latest_rev.created_at]

        decision = evaluate_adaptation(
            current_sessions=current_sessions,
            latest_checkin=latest_checkin,
            recent_activities=recent_acts,
        )

        if not decision.should_adapt:
            return latest_rev

        # Create new immutable PlanRevision
        next_rev_num = latest_rev.revision_number + 1
        new_hash = compute_snapshot_hash({
            "plan_id": plan.id,
            "revision_number": next_rev_num,
            "reason_codes": decision.reason_codes,
            "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        })

        new_rev = PlanRevision(
            plan_id=plan.id,
            user_id=user_id,
            revision_number=next_rev_num,
            input_snapshot_hash=new_hash,
            start_date=latest_rev.start_date,
            end_date=latest_rev.end_date,
            phases_json=latest_rev.phases_json,
            status="current",
            explanation=decision.explanation,
            trigger_reason=trigger_reason,
        )
        latest_rev.status = "superseded"
        db.add(new_rev)
        db.flush()

        # Record adaptation event
        adaptation_event = AdaptationEvent(
            user_id=user_id,
            plan_id=plan.id,
            prior_plan_revision_id=latest_rev.id,
            new_plan_revision_id=new_rev.id,
            trigger_inputs_json=json.dumps({
                "trigger_reason": trigger_reason,
                "pain_flag": latest_checkin.pain_flag if latest_checkin else False,
                "red_flag": decision.safety_stop,
            }),
            reason_codes_json=json.dumps(decision.reason_codes),
            explanation=decision.explanation,
            algorithm_version=PLANNER_ALGORITHM_VERSION,
            user_visible_impact="Plan updated with conservative adjustments" if not decision.safety_stop else "Training recommendation suspended for safety",
        )
        db.add(adaptation_event)

        # Clone sessions with adjustments
        for s_data in decision.adjusted_sessions:
            new_session = PlannedSession(
                plan_revision_id=new_rev.id,
                user_id=user_id,
                local_date=s_data["local_date"],
                session_type=s_data["session_type"],
                purpose=s_data["purpose"],
                duration_min_min=s_data["duration_min_min"],
                duration_min_max=s_data["duration_min_max"],
                distance_unit=s_data.get("distance_unit", "km"),
                distance_km_min=s_data["distance_km_min"],
                distance_km_max=s_data["distance_km_max"],
                effort_target=s_data["effort_target"],
                blocks_json=s_data["blocks_json"],
                target_pace_sec_per_km=s_data["target_pace_sec_per_km"],
                priority=s_data["priority"],
                flexibility_window_days=s_data["flexibility_window_days"],
                status=s_data["status"],
                reason_codes_json=json.dumps(s_data["reason_codes"]),
            )
            db.add(new_session)

        db.commit()
        db.refresh(new_rev)
        return new_rev
