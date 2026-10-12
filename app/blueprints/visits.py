from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app import db
from app.decorators import role_required
from app.forms import VisitForm
from app.models import CaregiverVisit, ElderlyProfile
from app.services.audit import log_action
from app.utils import accessible_elderly_query, user_can_access_elderly

visits_bp = Blueprint("visits", __name__, url_prefix="/visits")


@visits_bp.route("/")
@login_required
@role_required("admin", "caregiver")
def list_visits():
    profiles = accessible_elderly_query(current_user).all()
    ids = [p.id for p in profiles] or [0]
    visits = (
        CaregiverVisit.query.filter(CaregiverVisit.elderly_id.in_(ids))
        .order_by(CaregiverVisit.visited_at.desc())
        .limit(80)
        .all()
    )
    return render_template("visits/list.html", visits=visits)


@visits_bp.route("/new", methods=["GET", "POST"])
@login_required
@role_required("admin", "caregiver")
def create():
    form = VisitForm()
    profiles = accessible_elderly_query(current_user).order_by(ElderlyProfile.full_name).all()
    form.elderly_id.choices = [(p.id, p.full_name) for p in profiles]
    if form.validate_on_submit():
        profile = ElderlyProfile.query.get_or_404(form.elderly_id.data)
        if not user_can_access_elderly(current_user, profile):
            from flask import abort

            abort(403)
        visit = CaregiverVisit(
            elderly_id=profile.id,
            caregiver_id=current_user.id,
            visit_type=form.visit_type.data,
            visited_at=form.visited_at.data,
            duration_minutes=form.duration_minutes.data,
            observations=form.observations.data,
        )
        db.session.add(visit)
        db.session.commit()
        log_action("record_visit", "caregiver_visit", visit.id, profile.full_name)
        flash("Visit recorded.", "success")
        return redirect(url_for("visits.list_visits"))
    return render_template("visits/form.html", form=form)
