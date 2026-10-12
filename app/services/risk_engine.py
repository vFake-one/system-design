"""
Rule-based review-priority engine.

This is the working "AI-assisted" feature. It does not diagnose illness
and must not be described as detecting a medical emergency.
"""

from datetime import datetime, timedelta
from statistics import median

from app.models import CaregiverVisit, CheckinRecord


def _hours(delta):
    if delta is None:
        return None
    return delta.total_seconds() / 3600.0


def collect_features(elderly_id, now=None):
    now = now or datetime.now()
    since_7 = now - timedelta(days=7)
    since_14 = now - timedelta(days=14)
    since_28 = now - timedelta(days=28)

    records = (
        CheckinRecord.query.filter(
            CheckinRecord.elderly_id == elderly_id,
            CheckinRecord.due_at >= since_28,
        )
        .order_by(CheckinRecord.due_at.desc())
        .all()
    )

    completed = [
        r
        for r in records
        if r.status in ("completed", "completed_late") and r.submitted_at
    ]
    last_ok = completed[0] if completed else None
    hours_since_success = _hours(now - last_ok.submitted_at) if last_ok else None

    missed_7 = sum(
        1
        for r in records
        if r.due_at >= since_7 and r.status in ("missed", "completed_late")
    )
    missed_14 = sum(
        1
        for r in records
        if r.due_at >= since_14 and r.status in ("missed", "completed_late")
    )

    consecutive = 0
    day = now.date()
    # Count consecutive calendar days (going backwards) that have a missed record.
    by_day = {}
    for r in records:
        by_day.setdefault(r.due_at.date(), []).append(r)
    while True:
        day_recs = by_day.get(day, [])
        if any(r.status == "missed" for r in day_recs) and not any(
            r.status in ("completed", "completed_late") for r in day_recs
        ):
            consecutive += 1
            day = day - timedelta(days=1)
            if consecutive > 14:
                break
        else:
            break

    last_visit = (
        CaregiverVisit.query.filter_by(elderly_id=elderly_id)
        .order_by(CaregiverVisit.visited_at.desc())
        .first()
    )
    days_since_visit = None
    if last_visit:
        days_since_visit = (now - last_visit.visited_at).total_seconds() / 86400.0

    hours = []
    for r in completed:
        hours.append(r.submitted_at.hour + r.submitted_at.minute / 60.0)
    usual_hour = median(hours) if hours else None
    last_hour = None
    hour_deviation = None
    if last_ok:
        last_hour = last_ok.submitted_at.hour + last_ok.submitted_at.minute / 60.0
        if usual_hour is not None and len(hours) >= 3:
            hour_deviation = abs(last_hour - usual_hour)

    latest = records[0] if records else None
    hours_overdue = 0.0
    needs_assistance = False
    if latest:
        needs_assistance = bool(latest.needs_assistance)
        if latest.status == "missed":
            hours_overdue = max(0.0, _hours(now - latest.due_at) or 0.0)
        elif latest.status == "completed_late" and latest.submitted_at and latest.due_at:
            hours_overdue = max(0.0, _hours(latest.submitted_at - latest.due_at) or 0.0)

    return {
        "hours_overdue": hours_overdue,
        "hours_since_success": hours_since_success,
        "missed_7": missed_7,
        "missed_14": missed_14,
        "consecutive_misses": consecutive,
        "days_since_visit": days_since_visit,
        "hour_deviation": hour_deviation,
        "needs_assistance": needs_assistance,
    }


def score_from_features(f):
    score = 0
    reasons = []

    ho = f.get("hours_overdue") or 0
    if ho >= 24:
        score += 40
        reasons.append("Check-in overdue by 24 hours or more ({} h).".format(int(ho)))
    elif ho >= 6:
        score += 25
        reasons.append("Check-in overdue by 6 hours or more ({} h).".format(int(ho)))
    elif ho >= 1:
        score += 10
        reasons.append("Check-in overdue by at least 1 hour ({} h).".format(int(ho)))

    m7 = f.get("missed_7") or 0
    if m7 >= 3:
        score += 25
        reasons.append("Three or more missed or late check-ins in the last 7 days.")
    elif m7 >= 2:
        score += 15
        reasons.append("Two missed or late check-ins in the last 7 days.")
    elif m7 == 1:
        score += 5
        reasons.append("One missed or late check-in in the last 7 days.")

    streak = f.get("consecutive_misses") or 0
    if streak >= 3:
        score += 15
        reasons.append("Consecutive missed check-in days: {}.".format(streak))
    elif streak == 2:
        score += 8
        reasons.append("Two consecutive missed check-in days.")

    dvs = f.get("days_since_visit")
    if dvs is None:
        score += 5
        reasons.append("No caregiver visit is recorded in the system.")
    elif dvs >= 14:
        score += 15
        reasons.append("Last recorded caregiver visit was {} days ago.".format(int(dvs)))
    elif dvs >= 7:
        score += 8
        reasons.append("Last recorded caregiver visit was {} days ago.".format(int(dvs)))

    hd = f.get("hour_deviation")
    if hd is not None and hd >= 6:
        score += 10
        reasons.append(
            "Latest check-in time differs by 6+ hours from this person's usual time."
        )
    elif hd is not None and hd >= 3:
        score += 5
        reasons.append(
            "Latest check-in time differs by 3+ hours from this person's usual time."
        )

    if f.get("needs_assistance"):
        score = max(score, 80)
        reasons.append("The person (or a family member) requested help.")

    score = min(int(score), 100)
    if score >= 70:
        priority = "critical"
    elif score >= 45:
        priority = "high"
    elif score >= 25:
        priority = "medium"
    else:
        priority = "low"

    if not reasons:
        reasons.append("No overdue pattern detected from available check-in records.")

    return score, priority, reasons


def assess_risk(elderly_id, now=None):
    features = collect_features(elderly_id, now=now)
    score, priority, reasons = score_from_features(features)
    return {
        "score": score,
        "priority": priority,
        "reasons": reasons,
        "features": features,
        "explanation": " ".join(reasons),
    }
