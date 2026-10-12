from datetime import date, datetime, timedelta

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import func

from app.decorators import role_required
from app.forms import ReportFilterForm
from app.models import Alert, CaregiverVisit, CheckinRecord, FollowupAction
from app.utils import accessible_elderly_query

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


def _range():
    form = ReportFilterForm()
    today = date.today()
    if not form.start.data:
        form.start.data = today - timedelta(days=13)
    if not form.end.data:
        form.end.data = today
    if request.method == "GET" and request.args.get("start"):
        try:
            form.start.data = datetime.strptime(request.args["start"], "%Y-%m-%d").date()
            form.end.data = datetime.strptime(request.args["end"], "%Y-%m-%d").date()
        except (KeyError, ValueError):
            pass
    start_dt = datetime.combine(form.start.data, datetime.min.time())
    end_dt = datetime.combine(form.end.data, datetime.max.time())
    return form, start_dt, end_dt


@reports_bp.route("/", methods=["GET", "POST"])
@login_required
@role_required("admin", "caregiver")
def index():
    form, start_dt, end_dt = _range()
    ids = [p.id for p in accessible_elderly_query(current_user).all()] or [0]

    checkins = (
        CheckinRecord.query.filter(
            CheckinRecord.elderly_id.in_(ids),
            CheckinRecord.due_at >= start_dt,
            CheckinRecord.due_at <= end_dt,
        )
        .order_by(CheckinRecord.due_at.desc())
        .all()
    )
    alerts = (
        Alert.query.filter(
            Alert.elderly_id.in_(ids),
            Alert.created_at >= start_dt,
            Alert.created_at <= end_dt,
        )
        .order_by(Alert.created_at.desc())
        .all()
    )
    visits = (
        CaregiverVisit.query.filter(
            CaregiverVisit.elderly_id.in_(ids),
            CaregiverVisit.visited_at >= start_dt,
            CaregiverVisit.visited_at <= end_dt,
        )
        .order_by(CaregiverVisit.visited_at.desc())
        .all()
    )
    followups = (
        FollowupAction.query.filter(
            FollowupAction.elderly_id.in_(ids),
            FollowupAction.performed_at >= start_dt,
            FollowupAction.performed_at <= end_dt,
        )
        .order_by(FollowupAction.performed_at.desc())
        .all()
    )

    # Daily completed vs missed for Chart.js
    day = start_dt.date()
    end_day = end_dt.date()
    labels = []
    completed_series = []
    missed_series = []
    while day <= end_day:
        labels.append(day.isoformat())
        completed_series.append(
            sum(
                1
                for r in checkins
                if r.due_at.date() == day and r.status in ("completed", "completed_late")
            )
        )
        missed_series.append(sum(1 for r in checkins if r.due_at.date() == day and r.status == "missed"))
        day += timedelta(days=1)

    priority_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for a in alerts:
        priority_counts[a.priority] = priority_counts.get(a.priority, 0) + 1

    outcome_counts = {}
    for f in followups:
        outcome_counts[f.outcome] = outcome_counts.get(f.outcome, 0) + 1

    return render_template(
        "reports/index.html",
        form=form,
        checkins=checkins,
        alerts=alerts,
        visits=visits,
        followups=followups,
        labels=labels,
        completed_series=completed_series,
        missed_series=missed_series,
        priority_counts=priority_counts,
        outcome_counts=outcome_counts,
    )
