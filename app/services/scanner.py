"""
Missed-check detection and unacknowledged-alert escalation.

Idempotent: running twice will not create duplicate missed rows for the same due_at.
"""

from datetime import datetime, timedelta

from app import db
from app.models import (
    Alert,
    CheckinRecord,
    CheckinSchedule,
    ElderlyProfile,
    User,
    get_setting,
)
from app.services.notifications import notify, notify_many
from app.services.risk_engine import assess_risk
from app.utils import due_datetime, primary_caregiver_id, schedule_applies_on


def _open_overdue_alert(elderly_id, record_id):
    return Alert.query.filter(
        Alert.elderly_id == elderly_id,
        Alert.checkin_record_id == record_id,
        Alert.alert_type == "overdue",
        Alert.status.in_(["open", "acknowledged", "escalated"]),
    ).first()


def _admin_ids():
    return [u.id for u in User.query.filter_by(role="admin", is_active=True).all()]


def scan_missed_checkins(now=None):
    now = now or datetime.now()
    created = 0
    schedules = CheckinSchedule.query.filter_by(is_active=True).all()
    # Look back a few days in case the app was stopped.
    for schedule in schedules:
        elderly = ElderlyProfile.query.get(schedule.elderly_id)
        if not elderly or elderly.status != "active" or not elderly.consent_given:
            continue
        for offset in range(0, 4):
            day = (now - timedelta(days=offset)).date()
            if not schedule_applies_on(schedule, day):
                continue
            due = due_datetime(schedule, day)
            deadline = due + timedelta(minutes=schedule.grace_minutes or 0)
            if now < deadline:
                continue
            existing = CheckinRecord.query.filter_by(
                elderly_id=elderly.id, due_at=due
            ).first()
            if existing:
                if existing.status in ("completed", "completed_late", "cancelled"):
                    continue
                if existing.status == "missed" and _open_overdue_alert(elderly.id, existing.id):
                    continue
                record = existing
            else:
                record = CheckinRecord(
                    schedule_id=schedule.id,
                    elderly_id=elderly.id,
                    submitted_by=None,
                    status="missed",
                    method="system",
                    due_at=due,
                    submitted_at=None,
                )
                db.session.add(record)
                db.session.flush()

            if _open_overdue_alert(elderly.id, record.id):
                continue

            assessment = assess_risk(elderly.id, now=now)
            assignee = primary_caregiver_id(elderly.id)
            reason = "Missed check-in due at {}. {}".format(
                due.strftime("%Y-%m-%d %H:%M"), assessment["explanation"]
            )
            alert = Alert(
                elderly_id=elderly.id,
                checkin_record_id=record.id,
                alert_type="overdue",
                priority=assessment["priority"],
                status="open",
                title="Overdue check-in — {}".format(elderly.full_name),
                reason=reason,
                risk_score=assessment["score"],
                is_ai_flagged=assessment["score"] >= 25,
                assigned_to=assignee,
            )
            db.session.add(alert)
            db.session.flush()
            notify(
                assignee,
                "Overdue check-in",
                "{} did not complete the scheduled check-in. Review priority: {}.".format(
                    elderly.full_name, assessment["priority"]
                ),
                link="/alerts/{}".format(alert.id),
            )
            created += 1
    db.session.commit()
    return created


def escalate_unacknowledged(now=None):
    now = now or datetime.now()
    try:
        hours = float(get_setting("escalation_hours", "2"))
    except ValueError:
        hours = 2.0
    threshold = now - timedelta(hours=hours)
    escalated = 0
    open_alerts = Alert.query.filter(
        Alert.status == "open", Alert.created_at <= threshold
    ).all()
    admins = _admin_ids()
    for alert in open_alerts:
        elderly = ElderlyProfile.query.get(alert.elderly_id)
        secondary_admin = admins[0] if admins else None
        # Prefer a non-assigned caregiver if present, else admin.
        other = None
        from app.models import CaregiverAssignment

        for a in CaregiverAssignment.query.filter_by(
            elderly_id=alert.elderly_id, is_active=True
        ).all():
            if a.caregiver_id != alert.assigned_to:
                other = a.caregiver_id
                break
        target = other or secondary_admin
        alert.status = "escalated"
        alert.alert_type = "escalation" if alert.alert_type == "overdue" else alert.alert_type
        alert.escalated_to = target
        extra = (
            " Escalated because it was not acknowledged within "
            "{} hour(s). This is not an automated call to emergency services."
        ).format(int(hours))
        if extra not in (alert.reason or ""):
            alert.reason = (alert.reason or "") + extra
        db.session.flush()
        notify_many(
            [target, secondary_admin],
            "Escalated alert",
            "Unacknowledged alert for {} needs review.".format(
                elderly.full_name if elderly else "a household"
            ),
            link="/alerts/{}".format(alert.id),
        )
        escalated += 1
    db.session.commit()
    return escalated


def run_scan(now=None):
    missed = scan_missed_checkins(now=now)
    esc = escalate_unacknowledged(now=now)
    return {"missed_alerts_created": missed, "escalated": esc}
