from datetime import date, datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.models import (
    Alert,
    CaregiverVisit,
    CheckinRecord,
    CheckinSchedule,
    ElderlyProfile,
    FollowupAction,
    Notification,
)
from app.utils import (
    accessible_elderly_query,
    household_contact_status,
    today_record,
    window_open,
)

main_bp = Blueprint("main", __name__)


def _dashboard_counts(profiles):
    today = date.today()
    start = datetime.combine(today, datetime.min.time())
    ids = [p.id for p in profiles]
    completed_today = 0
    overdue = 0
    awaiting = 0
    follow_up = 0
    if ids:
        completed_today = CheckinRecord.query.filter(
            CheckinRecord.elderly_id.in_(ids),
            CheckinRecord.status.in_(["completed", "completed_late"]),
            CheckinRecord.submitted_at >= start,
        ).count()
        for p in profiles:
            st = household_contact_status(p)
            if st == "overdue":
                overdue += 1
            elif st == "awaiting":
                awaiting += 1
            elif st == "follow_up":
                follow_up += 1
    unacked = 0
    high = 0
    unresolved_fu = 0
    recent_visits = []
    if ids:
        unacked = Alert.query.filter(
            Alert.elderly_id.in_(ids), Alert.status.in_(["open", "escalated"])
        ).count()
        high = Alert.query.filter(
            Alert.elderly_id.in_(ids),
            Alert.status.in_(["open", "acknowledged", "escalated"]),
            Alert.priority.in_(["high", "critical"]),
        ).count()
        open_alert_ids = [
            a.id
            for a in Alert.query.filter(
                Alert.elderly_id.in_(ids),
                Alert.status.in_(["open", "acknowledged", "escalated"]),
            ).all()
        ]
        if open_alert_ids:
            unresolved_fu = Alert.query.filter(Alert.id.in_(open_alert_ids)).count()
        recent_visits = (
            CaregiverVisit.query.filter(CaregiverVisit.elderly_id.in_(ids))
            .order_by(CaregiverVisit.visited_at.desc())
            .limit(5)
            .all()
        )
    return {
        "total": len(profiles),
        "completed_today": completed_today,
        "overdue": overdue,
        "awaiting": awaiting,
        "follow_up": follow_up,
        "unacked": unacked,
        "high": high,
        "unresolved": unresolved_fu,
        "recent_visits": recent_visits,
    }


@main_bp.route("/")
@login_required
def dashboard():
    if current_user.role == "admin":
        profiles = ElderlyProfile.query.filter_by(status="active").all()
        counts = _dashboard_counts(profiles)
        rows = [(p, household_contact_status(p)) for p in profiles]
        alerts = (
            Alert.query.filter(Alert.status.in_(["open", "acknowledged", "escalated"]))
            .order_by(Alert.created_at.desc())
            .limit(8)
            .all()
        )
        return render_template(
            "dashboard/admin.html", counts=counts, rows=rows, alerts=alerts
        )
    if current_user.role == "caregiver":
        profiles = accessible_elderly_query(current_user).filter_by(status="active").all()
        counts = _dashboard_counts(profiles)
        rows = [(p, household_contact_status(p)) for p in profiles]
        ids = [p.id for p in profiles] or [0]
        alerts = (
            Alert.query.filter(
                Alert.elderly_id.in_(ids),
                Alert.status.in_(["open", "acknowledged", "escalated"]),
            )
            .order_by(Alert.created_at.desc())
            .limit(8)
            .all()
        )
        return render_template(
            "dashboard/caregiver.html", counts=counts, rows=rows, alerts=alerts
        )

    # Elderly or family: simple home
    profiles = accessible_elderly_query(current_user).all()
    cards = []
    for p in profiles:
        sched = CheckinSchedule.query.filter_by(elderly_id=p.id, is_active=True).first()
        rec = today_record(p.id)
        cards.append(
            {
                "profile": p,
                "schedule": sched,
                "record": rec,
                "status": household_contact_status(p),
                "window_open": window_open(sched) if sched else False,
            }
        )
    return render_template("dashboard/elderly.html", cards=cards)


@main_bp.route("/notifications")
@login_required
def notifications():
    items = (
        Notification.query.filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )
    return render_template("notifications.html", items=items)


@main_bp.route("/notifications/read-all", methods=["POST"])
@login_required
def read_all_notifications():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update(
        {"is_read": True}
    )
    from app import db

    db.session.commit()
    flash("Notifications marked as read.", "success")
    return redirect(url_for("main.notifications"))
