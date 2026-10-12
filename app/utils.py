from datetime import date, datetime, timedelta
from typing import Optional

from flask_login import current_user

from app.models import (
    Alert,
    CaregiverAssignment,
    CheckinRecord,
    CheckinSchedule,
    ElderlyProfile,
    FamilyLink,
)


def weekday_number(d: date) -> int:
    """Monday = 1 ... Sunday = 7, matching schedule.days_of_week."""
    return d.isoweekday()


def schedule_applies_on(schedule: CheckinSchedule, d: date) -> bool:
    if not schedule.is_active:
        return False
    days = {int(x) for x in schedule.days_of_week.split(",") if x.strip()}
    if weekday_number(d) not in days:
        return False
    if schedule.frequency == "weekly":
        return True
    return True


def due_datetime(schedule: CheckinSchedule, d: date) -> datetime:
    return datetime.combine(d, schedule.window_end)


def window_open(schedule: CheckinSchedule, now: Optional[datetime] = None) -> bool:
    now = now or datetime.now()
    if not schedule_applies_on(schedule, now.date()):
        return False
    start = datetime.combine(now.date(), schedule.window_start)
    end = datetime.combine(now.date(), schedule.window_end) + timedelta(
        minutes=schedule.grace_minutes or 0
    )
    return start <= now <= end


def primary_caregiver_id(elderly_id: int):
    row = (
        CaregiverAssignment.query.filter_by(
            elderly_id=elderly_id, is_active=True, is_primary=True
        ).first()
        or CaregiverAssignment.query.filter_by(elderly_id=elderly_id, is_active=True).first()
    )
    return row.caregiver_id if row else None


def user_can_access_elderly(user, elderly: ElderlyProfile) -> bool:
    if user.role == "admin":
        return True
    if user.role == "caregiver":
        return (
            CaregiverAssignment.query.filter_by(
                elderly_id=elderly.id, caregiver_id=user.id, is_active=True
            ).first()
            is not None
        )
    if user.role == "elderly":
        return elderly.user_id == user.id
    if user.role == "family":
        return (
            FamilyLink.query.filter_by(
                elderly_id=elderly.id, family_user_id=user.id, is_active=True
            ).first()
            is not None
        )
    return False


def accessible_elderly_query(user):
    q = ElderlyProfile.query
    if user.role == "admin":
        return q
    if user.role == "caregiver":
        ids = [
            a.elderly_id
            for a in CaregiverAssignment.query.filter_by(
                caregiver_id=user.id, is_active=True
            ).all()
        ]
        return q.filter(ElderlyProfile.id.in_(ids or [0]))
    if user.role == "elderly":
        return q.filter_by(user_id=user.id)
    if user.role == "family":
        ids = [
            l.elderly_id
            for l in FamilyLink.query.filter_by(family_user_id=user.id, is_active=True).all()
        ]
        return q.filter(ElderlyProfile.id.in_(ids or [0]))
    return q.filter_by(id=0)


def today_record(elderly_id: int, day: Optional[date] = None):
    day = day or date.today()
    start = datetime.combine(day, datetime.min.time())
    end = datetime.combine(day, datetime.max.time())
    return (
        CheckinRecord.query.filter(
            CheckinRecord.elderly_id == elderly_id,
            CheckinRecord.due_at >= start,
            CheckinRecord.due_at <= end,
        )
        .order_by(CheckinRecord.due_at.desc())
        .first()
    )


def household_contact_status(elderly: ElderlyProfile, now: Optional[datetime] = None) -> str:
    """
    Operational contact status for dashboards.
    'checkin_received' is NOT a medical claim.
    """
    now = now or datetime.now()
    open_alert = (
        Alert.query.filter(
            Alert.elderly_id == elderly.id,
            Alert.status.in_(["open", "acknowledged", "escalated"]),
        )
        .order_by(Alert.created_at.desc())
        .first()
    )
    rec = today_record(elderly.id, now.date())
    sched = CheckinSchedule.query.filter_by(elderly_id=elderly.id, is_active=True).first()

    if rec and rec.status in ("missed",) and open_alert:
        return "overdue"
    if rec and rec.status == "missed":
        return "overdue"
    if open_alert and open_alert.alert_type in ("overdue", "assistance", "pattern", "escalation"):
        if rec and rec.status in ("completed", "completed_late") and open_alert.status != "open":
            return "follow_up"
        if rec and rec.status in ("completed", "completed_late") and open_alert.alert_type != "assistance":
            return "follow_up"
        if rec is None or rec.status == "missed":
            return "overdue" if (open_alert.alert_type == "overdue") else "follow_up"
        return "follow_up"
    if rec and rec.status in ("completed", "completed_late"):
        return "checkin_received"
    if sched and window_open(sched, now):
        return "awaiting"
    if sched and schedule_applies_on(sched, now.date()):
        start = datetime.combine(now.date(), sched.window_start)
        if now < start:
            return "awaiting"
        return "overdue"
    if sched:
        return "awaiting"
    return "no_schedule"


def method_for_role(role: str) -> str:
    return {"elderly": "self", "family": "family", "caregiver": "caregiver", "admin": "caregiver"}.get(
        role, "self"
    )


def current_ip():
    from flask import request

    return (request.headers.get("X-Forwarded-For") or request.remote_addr or "")[:45]


def require_current_access(elderly: ElderlyProfile) -> None:
    from flask import abort

    if not user_can_access_elderly(current_user, elderly):
        abort(403)
