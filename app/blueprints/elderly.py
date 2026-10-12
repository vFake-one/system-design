from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.decorators import role_required
from app.forms import AssignmentForm, ElderlyForm, FamilyLinkForm, ScheduleForm
from app.models import (
    CaregiverAssignment,
    CheckinRecord,
    CheckinSchedule,
    ElderlyProfile,
    FamilyLink,
    User,
)
from app.services.audit import log_action
from app.services.risk_engine import assess_risk
from app.utils import accessible_elderly_query, household_contact_status, require_current_access

elderly_bp = Blueprint("elderly", __name__, url_prefix="/elderly")


@elderly_bp.route("/")
@login_required
@role_required("admin", "caregiver")
def list_households():
    q = request.args.get("q", "").strip()
    query = accessible_elderly_query(current_user)
    if q:
        query = query.filter(ElderlyProfile.full_name.ilike("%{}%".format(q)))
    profiles = query.order_by(ElderlyProfile.full_name).all()
    rows = [(p, household_contact_status(p)) for p in profiles]
    return render_template("elderly/list.html", rows=rows, q=q)


@elderly_bp.route("/new", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create():
    form = ElderlyForm()
    if form.validate_on_submit():
        profile = ElderlyProfile()
        _apply_elderly_form(profile, form)
        db.session.add(profile)
        db.session.commit()
        log_action("create_elderly", "elderly_profile", profile.id, profile.full_name)
        flash("Household record saved.", "success")
        return redirect(url_for("elderly.profile", elderly_id=profile.id))
    return render_template("elderly/form.html", form=form, title="Register household")


@elderly_bp.route("/<int:elderly_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit(elderly_id):
    profile = ElderlyProfile.query.get_or_404(elderly_id)
    form = ElderlyForm(obj=profile)
    if request.method == "GET" and profile.login_user:
        form.login_username.data = profile.login_user.username
    if form.validate_on_submit():
        _apply_elderly_form(profile, form)
        profile.updated_at = datetime.utcnow()
        db.session.commit()
        log_action("update_elderly", "elderly_profile", profile.id, profile.full_name)
        flash("Household record updated. The change is recorded in the audit log.", "success")
        return redirect(url_for("elderly.profile", elderly_id=profile.id))
    return render_template(
        "elderly/form.html", form=form, title="Edit household", profile=profile
    )


def _apply_elderly_form(profile, form):
    profile.full_name = form.full_name.data.strip()
    profile.date_of_birth = form.date_of_birth.data
    profile.gender = form.gender.data or None
    profile.address = form.address.data
    profile.phone = form.phone.data
    profile.mobility_status = form.mobility_status.data
    profile.living_arrangement = form.living_arrangement.data
    profile.emergency_contact_name = form.emergency_contact_name.data
    profile.emergency_contact_phone = form.emergency_contact_phone.data
    profile.emergency_contact_relationship = form.emergency_contact_relationship.data
    profile.secondary_contact_name = form.secondary_contact_name.data
    profile.secondary_contact_phone = form.secondary_contact_phone.data
    profile.welfare_notes = form.welfare_notes.data
    profile.consent_given = bool(form.consent_given.data)
    if profile.consent_given and not profile.consent_date:
        profile.consent_date = datetime.utcnow()
    if not profile.consent_given:
        profile.consent_date = None
        profile.status = "inactive"
    else:
        profile.status = form.status.data
    username = (form.login_username.data or "").strip()
    if username:
        user = User.query.filter_by(username=username).first()
        profile.user_id = user.id if user else None
        if not user:
            flash("Linked username was not found; login was left unlinked.", "warning")
    else:
        profile.user_id = None


@elderly_bp.route("/<int:elderly_id>")
@login_required
def profile(elderly_id):
    profile = ElderlyProfile.query.get_or_404(elderly_id)
    require_current_access(profile)
    assignments = CaregiverAssignment.query.filter_by(elderly_id=profile.id).all()
    families = FamilyLink.query.filter_by(elderly_id=profile.id).all()
    schedule = CheckinSchedule.query.filter_by(elderly_id=profile.id, is_active=True).first()
    recent = (
        CheckinRecord.query.filter_by(elderly_id=profile.id)
        .order_by(CheckinRecord.due_at.desc())
        .limit(10)
        .all()
    )
    assessment = assess_risk(profile.id)
    status = household_contact_status(profile)
    return render_template(
        "elderly/profile.html",
        profile=profile,
        assignments=assignments,
        families=families,
        schedule=schedule,
        recent=recent,
        assessment=assessment,
        status=status,
    )


@elderly_bp.route("/<int:elderly_id>/assign", methods=["GET", "POST"])
@login_required
@role_required("admin")
def assign(elderly_id):
    profile = ElderlyProfile.query.get_or_404(elderly_id)
    form = AssignmentForm()
    caregivers = User.query.filter_by(role="caregiver", is_active=True).order_by(User.full_name).all()
    form.caregiver_id.choices = [(u.id, "{} ({})".format(u.full_name, u.username)) for u in caregivers]
    if form.validate_on_submit():
        if form.is_primary.data:
            CaregiverAssignment.query.filter_by(elderly_id=profile.id, is_active=True).update(
                {"is_primary": False}
            )
        existing = CaregiverAssignment.query.filter_by(
            elderly_id=profile.id, caregiver_id=form.caregiver_id.data, is_active=True
        ).first()
        if existing:
            existing.is_primary = bool(form.is_primary.data)
            existing.notes = form.notes.data
        else:
            db.session.add(
                CaregiverAssignment(
                    elderly_id=profile.id,
                    caregiver_id=form.caregiver_id.data,
                    is_primary=bool(form.is_primary.data),
                    assigned_by=current_user.id,
                    notes=form.notes.data,
                )
            )
        db.session.commit()
        log_action("assign_caregiver", "elderly_profile", profile.id, str(form.caregiver_id.data))
        flash("Caregiver assignment saved.", "success")
        return redirect(url_for("elderly.profile", elderly_id=profile.id))
    assignments = CaregiverAssignment.query.filter_by(elderly_id=profile.id).all()
    return render_template(
        "elderly/assign.html", form=form, profile=profile, assignments=assignments
    )


@elderly_bp.route("/<int:elderly_id>/assign/<int:assignment_id>/deactivate", methods=["POST"])
@login_required
@role_required("admin")
def deactivate_assignment(elderly_id, assignment_id):
    row = CaregiverAssignment.query.get_or_404(assignment_id)
    if row.elderly_id != elderly_id:
        abort(404)
    row.is_active = False
    row.is_primary = False
    db.session.commit()
    log_action("deactivate_assignment", "caregiver_assignment", row.id)
    flash("Assignment deactivated. History is kept.", "info")
    return redirect(url_for("elderly.assign", elderly_id=elderly_id))


@elderly_bp.route("/<int:elderly_id>/family", methods=["GET", "POST"])
@login_required
@role_required("admin")
def family(elderly_id):
    profile = ElderlyProfile.query.get_or_404(elderly_id)
    form = FamilyLinkForm()
    users = User.query.filter_by(role="family").order_by(User.full_name).all()
    form.family_user_id.choices = [
        (u.id, "{} ({}){}".format(u.full_name, u.username, "" if u.is_active else " — inactive"))
        for u in users
    ]
    if form.validate_on_submit():
        db.session.add(
            FamilyLink(
                elderly_id=profile.id,
                family_user_id=form.family_user_id.data,
                relationship=form.relationship.data,
            )
        )
        fam = User.query.get(form.family_user_id.data)
        if fam and not fam.is_active:
            fam.is_active = True
        db.session.commit()
        log_action("link_family", "elderly_profile", profile.id, str(form.family_user_id.data))
        flash("Family account linked and activated if it was pending.", "success")
        return redirect(url_for("elderly.profile", elderly_id=profile.id))
    return render_template("elderly/family.html", form=form, profile=profile)


@elderly_bp.route("/<int:elderly_id>/schedule", methods=["GET", "POST"])
@login_required
@role_required("admin", "caregiver")
def schedule(elderly_id):
    profile = ElderlyProfile.query.get_or_404(elderly_id)
    require_current_access(profile)
    existing = CheckinSchedule.query.filter_by(elderly_id=profile.id, is_active=True).first()
    form = ScheduleForm(obj=existing) if existing else ScheduleForm()
    if existing and request.method == "GET":
        form.days.data = [d for d in (existing.days_of_week or "").split(",") if d]
    if form.validate_on_submit():
        if form.window_end.data <= form.window_start.data:
            flash("Window end must be after window start.", "danger")
            return render_template("elderly/schedule.html", form=form, profile=profile)
        days = form.days.data or ["1", "2", "3", "4", "5", "6", "7"]
        if existing:
            sched = existing
        else:
            sched = CheckinSchedule(elderly_id=profile.id)
            db.session.add(sched)
        sched.frequency = form.frequency.data
        sched.window_start = form.window_start.data
        sched.window_end = form.window_end.data
        sched.days_of_week = ",".join(days)
        sched.grace_minutes = form.grace_minutes.data
        sched.is_active = bool(form.is_active.data)
        db.session.commit()
        log_action("update_schedule", "checkin_schedule", sched.id, profile.full_name)
        flash("Check-in schedule saved.", "success")
        return redirect(url_for("elderly.profile", elderly_id=profile.id))
    return render_template("elderly/schedule.html", form=form, profile=profile)


@elderly_bp.route("/<int:elderly_id>/history")
@login_required
def history(elderly_id):
    profile = ElderlyProfile.query.get_or_404(elderly_id)
    require_current_access(profile)
    records = (
        CheckinRecord.query.filter_by(elderly_id=profile.id)
        .order_by(CheckinRecord.due_at.desc())
        .limit(60)
        .all()
    )
    return render_template("elderly/history.html", profile=profile, records=records)
