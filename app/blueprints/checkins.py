from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app import db
from app.forms import AssistanceForm, CheckinForm
from app.models import Alert, CheckinRecord, CheckinSchedule, ElderlyProfile
from app.services.audit import log_action
from app.services.notifications import notify
from app.services.risk_engine import assess_risk
from app.utils import (
    due_datetime,
    method_for_role,
    primary_caregiver_id,
    require_current_access,
    schedule_applies_on,
    today_record,
)

checkins_bp = Blueprint("checkins", __name__, url_prefix="/checkins")


def _today_due(schedule, now):
    if not schedule or not schedule_applies_on(schedule, now.date()):
        # Still allow an ad-hoc check-in for today using window_end if present,
        # otherwise end of morning as a default due marker.
        from datetime import time as dtime

        end = schedule.window_end if schedule else dtime(11, 0)
        return datetime.combine(now.date(), end)
    return due_datetime(schedule, now.date())


@checkins_bp.route("/submit/<int:elderly_id>", methods=["GET", "POST"])
@login_required
def submit(elderly_id):
    profile = ElderlyProfile.query.get_or_404(elderly_id)
    require_current_access(profile)
    form = CheckinForm()
    help_form = AssistanceForm()
    schedule = CheckinSchedule.query.filter_by(elderly_id=profile.id, is_active=True).first()
    existing = today_record(profile.id)
    if form.validate_on_submit():
        rec, late = _save_checkin(profile, schedule, form.mood.data, form.notes.data, False)
        log_action("submit_checkin", "checkin_record", rec.id, profile.full_name)
        if late:
            flash(
                "Check-in saved after the deadline. A caregiver may still review the overdue alert.",
                "warning",
            )
        else:
            flash(
                "Check-in received. This records contact only — it does not mean a medical assessment.",
                "success",
            )
        return redirect(url_for("checkins.confirm", elderly_id=profile.id))
    return render_template(
        "checkins/submit.html",
        form=form,
        help_form=help_form,
        profile=profile,
        schedule=schedule,
        existing=existing,
    )


@checkins_bp.route("/help/<int:elderly_id>", methods=["POST"])
@login_required
def help_request(elderly_id):
    profile = ElderlyProfile.query.get_or_404(elderly_id)
    require_current_access(profile)
    help_form = AssistanceForm()
    if not help_form.validate_on_submit():
        flash("Please try the help request again.", "danger")
        return redirect(url_for("checkins.submit", elderly_id=profile.id))
    schedule = CheckinSchedule.query.filter_by(elderly_id=profile.id, is_active=True).first()
    rec, _late = _save_checkin(
        profile, schedule, "unwell", help_form.notes.data, True
    )
    assessment = assess_risk(profile.id)
    assignee = primary_caregiver_id(profile.id)
    alert = Alert(
        elderly_id=profile.id,
        checkin_record_id=rec.id,
        alert_type="assistance",
        priority="critical" if assessment["score"] >= 70 else "high",
        status="open",
        title="Help requested — {}".format(profile.full_name),
        reason="Assistance requested through the app. {}".format(assessment["explanation"]),
        risk_score=max(assessment["score"], 80),
        is_ai_flagged=True,
        assigned_to=assignee,
    )
    db.session.add(alert)
    db.session.commit()
    notify(
        assignee,
        "Help requested",
        "{} asked for help through the check-in app. This is not an ambulance call.".format(
            profile.full_name
        ),
        link="/alerts/{}".format(alert.id),
    )
    log_action("request_help", "alert", alert.id, profile.full_name)
    flash(
        "Your caregivers have been notified in the app. If this is an emergency, "
        "call your local emergency number. This website cannot send an ambulance.",
        "warning",
    )
    return redirect(url_for("checkins.confirm", elderly_id=profile.id))


def _save_checkin(profile, schedule, mood, notes, needs_help):
    now = datetime.now()
    due = _today_due(schedule, now)
    existing = CheckinRecord.query.filter_by(elderly_id=profile.id, due_at=due).first()
    late = now > due
    status = "completed_late" if late else "completed"
    if existing:
        existing.status = status
        existing.mood = mood
        existing.notes = notes
        existing.needs_assistance = needs_help
        existing.submitted_by = current_user.id
        existing.submitted_at = now
        existing.method = method_for_role(current_user.role)
        rec = existing
    else:
        rec = CheckinRecord(
            schedule_id=schedule.id if schedule else None,
            elderly_id=profile.id,
            submitted_by=current_user.id,
            status=status,
            method=method_for_role(current_user.role),
            mood=mood,
            needs_assistance=needs_help,
            notes=notes,
            due_at=due,
            submitted_at=now,
        )
        db.session.add(rec)
    db.session.commit()
    return rec, late


@checkins_bp.route("/confirm/<int:elderly_id>")
@login_required
def confirm(elderly_id):
    profile = ElderlyProfile.query.get_or_404(elderly_id)
    require_current_access(profile)
    rec = today_record(profile.id)
    return render_template("checkins/confirm.html", profile=profile, record=rec)
