from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.decorators import role_required
from app.forms import AlertAckForm, FollowupForm
from app.models import Alert, AlertAcknowledgement, FollowupAction
from app.services.audit import log_action
from app.utils import accessible_elderly_query, user_can_access_elderly

alerts_bp = Blueprint("alerts", __name__, url_prefix="/alerts")


@alerts_bp.route("/")
@login_required
@role_required("admin", "caregiver")
def list_alerts():
    status = request.args.get("status", "open")
    profiles = accessible_elderly_query(current_user).all()
    ids = [p.id for p in profiles] or [0]
    q = Alert.query.filter(Alert.elderly_id.in_(ids))
    if status == "open":
        q = q.filter(Alert.status.in_(["open", "acknowledged", "escalated"]))
    elif status != "all":
        q = q.filter_by(status=status)
    alerts = q.order_by(Alert.created_at.desc()).all()
    return render_template("alerts/list.html", alerts=alerts, status=status)


@alerts_bp.route("/<int:alert_id>", methods=["GET", "POST"])
@login_required
@role_required("admin", "caregiver")
def detail(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    if not user_can_access_elderly(current_user, alert.elderly):
        from flask import abort

        abort(403)
    ack_form = AlertAckForm()
    fu_form = FollowupForm()
    followups = alert.followups.order_by(FollowupAction.performed_at.desc()).all()
    acks = alert.acknowledgements.order_by(AlertAcknowledgement.acknowledged_at.desc()).all()
    return render_template(
        "alerts/detail.html",
        alert=alert,
        ack_form=ack_form,
        fu_form=fu_form,
        followups=followups,
        acks=acks,
    )


@alerts_bp.route("/<int:alert_id>/ack", methods=["POST"])
@login_required
@role_required("admin", "caregiver")
def acknowledge(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    if not user_can_access_elderly(current_user, alert.elderly):
        from flask import abort

        abort(403)
    form = AlertAckForm()
    if form.validate_on_submit():
        db.session.add(
            AlertAcknowledgement(
                alert_id=alert.id, user_id=current_user.id, notes=form.notes.data
            )
        )
        if alert.status in ("open", "escalated"):
            alert.status = "acknowledged"
            alert.acknowledged_at = datetime.utcnow()
        db.session.commit()
        log_action("acknowledge_alert", "alert", alert.id)
        flash("Alert acknowledged.", "success")
    return redirect(url_for("alerts.detail", alert_id=alert.id))


@alerts_bp.route("/<int:alert_id>/followup", methods=["POST"])
@login_required
@role_required("admin", "caregiver")
def followup(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    if not user_can_access_elderly(current_user, alert.elderly):
        from flask import abort

        abort(403)
    form = FollowupForm()
    if not form.validate_on_submit():
        flash("Please complete the follow-up notes (at least a short description).", "danger")
        return redirect(url_for("alerts.detail", alert_id=alert.id))
    db.session.add(
        FollowupAction(
            alert_id=alert.id,
            elderly_id=alert.elderly_id,
            caregiver_id=current_user.id,
            action_type=form.action_type.data,
            outcome=form.outcome.data,
            description=form.description.data,
        )
    )
    if alert.status == "open":
        alert.status = "acknowledged"
        alert.acknowledged_at = alert.acknowledged_at or datetime.utcnow()
    db.session.commit()
    log_action("followup", "alert", alert.id, form.outcome.data)
    flash("Follow-up recorded.", "success")
    return redirect(url_for("alerts.detail", alert_id=alert.id))


@alerts_bp.route("/<int:alert_id>/close", methods=["POST"])
@login_required
@role_required("admin", "caregiver")
def close(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    if not user_can_access_elderly(current_user, alert.elderly):
        from flask import abort

        abort(403)
    as_false = request.form.get("as_false") == "1"
    followups = alert.followups.count()
    if as_false:
        last = alert.followups.order_by(FollowupAction.performed_at.desc()).first()
        if not last or last.outcome != "false_alert" or not (last.description or "").strip():
            flash(
                "To mark a false alert, first save a follow-up with outcome "
                "“False alert / known explanation” and a written reason.",
                "danger",
            )
            return redirect(url_for("alerts.detail", alert_id=alert.id))
        alert.status = "false_alert"
        alert.resolved_at = datetime.utcnow()
        db.session.commit()
        log_action("false_alert", "alert", alert.id)
        flash("Alert marked as a false alert. The explanation is kept on file.", "info")
        return redirect(url_for("alerts.detail", alert_id=alert.id))

    if followups < 1:
        flash("A case can be closed only after a follow-up action is documented.", "danger")
        return redirect(url_for("alerts.detail", alert_id=alert.id))
    alert.status = "resolved"
    alert.resolved_at = datetime.utcnow()
    db.session.commit()
    log_action("resolve_alert", "alert", alert.id)
    flash("Case closed.", "success")
    return redirect(url_for("alerts.detail", alert_id=alert.id))
