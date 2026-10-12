from datetime import datetime
from io import BytesIO
import os
import shutil

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy import or_

from app import db
from app.decorators import role_required
from app.forms import SettingsForm, UserForm
from app.models import AuditLog, SystemSetting, User
from app.services.audit import log_action
from app.services.ml_compare import compare_on_synthetic
from app.services.scanner import run_scan

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/users")
@login_required
@role_required("admin")
def users():
    q = request.args.get("q", "").strip()
    query = User.query
    if q:
        like = "%{}%".format(q)
        query = query.filter(
            or_(User.username.ilike(like), User.full_name.ilike(like), User.email.ilike(like))
        )
    people = query.order_by(User.role, User.full_name).all()
    return render_template("admin/users.html", people=people, q=q)


@admin_bp.route("/users/new", methods=["GET", "POST"])
@login_required
@role_required("admin")
def user_new():
    form = UserForm()
    if form.validate_on_submit():
        if not form.password.data:
            flash("A password is required for a new account.", "danger")
            return render_template("admin/user_form.html", form=form, title="Add user")
        if User.query.filter(
            or_(User.username == form.username.data.strip(), User.email == form.email.data.strip().lower())
        ).first():
            flash("Username or email already exists.", "danger")
            return render_template("admin/user_form.html", form=form, title="Add user")
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            full_name=form.full_name.data.strip(),
            phone=form.phone.data,
            role=form.role.data,
            is_active=bool(form.is_active.data),
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        log_action("create_user", "user", user.id, "{} ({})".format(user.username, user.role))
        flash("User created.", "success")
        return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", form=form, title="Add user")


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def user_edit(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.full_name = form.full_name.data.strip()
        user.username = form.username.data.strip()
        user.email = form.email.data.strip().lower()
        user.phone = form.phone.data
        user.role = form.role.data
        user.is_active = bool(form.is_active.data)
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        log_action("update_user", "user", user.id, user.username)
        flash("User updated.", "success")
        return redirect(url_for("admin.users"))
    form.password.data = ""
    return render_template("admin/user_form.html", form=form, title="Edit user", user=user)


@admin_bp.route("/audit")
@login_required
@role_required("admin")
def audit():
    page = request.args.get("page", 1, type=int)
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=40)
    return render_template("admin/audit.html", logs=logs)


@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
@role_required("admin")
def settings():
    form = SettingsForm()
    if request.method == "GET":
        form.organisation_name.data = (
            SystemSetting.query.filter_by(key="organisation_name").first() or SystemSetting()
        ).value or "Community Welfare Check-in"
        esc = SystemSetting.query.filter_by(key="escalation_hours").first()
        form.escalation_hours.data = int(esc.value) if esc else 2
    if form.validate_on_submit():
        _upsert_setting("organisation_name", form.organisation_name.data.strip(), "Shown in the header")
        _upsert_setting(
            "escalation_hours",
            str(form.escalation_hours.data),
            "Hours before an unacknowledged alert is escalated",
        )
        db.session.commit()
        log_action("update_settings", "system_settings", None, "organisation/escalation")
        flash("Settings saved.", "success")
        return redirect(url_for("admin.settings"))
    return render_template("admin/settings.html", form=form)


def _upsert_setting(key, value, description):
    row = SystemSetting.query.filter_by(key=key).first()
    if not row:
        row = SystemSetting(key=key, value=value, description=description)
        db.session.add(row)
    else:
        row.value = value
        row.description = description


@admin_bp.route("/scan", methods=["POST"])
@login_required
@role_required("admin")
def scan_now():
    result = run_scan()
    log_action("manual_scan", "system", None, str(result))
    flash(
        "Scan finished. New missed alerts: {}. Escalated: {}.".format(
            result["missed_alerts_created"], result["escalated"]
        ),
        "info",
    )
    return redirect(url_for("admin.settings"))


@admin_bp.route("/backup")
@login_required
@role_required("admin")
def backup():
    uri = current_app.config["SQLALCHEMY_DATABASE_URI"]
    if not uri.startswith("sqlite:///"):
        flash("Backup download is implemented for SQLite only.", "warning")
        return redirect(url_for("admin.settings"))
    path = uri.replace("sqlite:///", "", 1)
    if not os.path.exists(path):
        flash("Database file not found.", "danger")
        return redirect(url_for("admin.settings"))
    log_action("download_backup", "database", None, path)
    buf = BytesIO()
    with open(path, "rb") as fh:
        buf.write(fh.read())
    buf.seek(0)
    name = "welfare-backup-{}.db".format(datetime.now().strftime("%Y%m%d-%H%M"))
    return send_file(buf, as_attachment=True, download_name=name, mimetype="application/octet-stream")


@admin_bp.route("/ml-demo")
@login_required
@role_required("admin")
def ml_demo():
    result = compare_on_synthetic()
    return render_template("admin/ml_demo.html", result=result)
