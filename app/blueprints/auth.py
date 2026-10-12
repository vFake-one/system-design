from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.forms import LoginForm, RegisterForm
from app.models import User
from app.services.audit import log_action

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        ident = form.username.data.strip()
        user = User.query.filter(
            (User.username == ident) | (User.email == ident.lower())
        ).first()
        if user and user.check_password(form.password.data) and user.is_active:
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            log_action("login", "user", user.id, "Successful login")
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            return redirect(url_for("main.dashboard"))
        flash("Incorrect username/email or password, or the account is inactive.", "danger")
        log_action("login_failed", "user", user.id if user else None, ident)
    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            full_name=form.full_name.data.strip(),
            phone=form.phone.data.strip() if form.phone.data else None,
            role="family",
            is_active=False,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        log_action("register_pending", "user", user.id, "Family self-registration pending admin", user_id=user.id)
        flash(
            "Account created but not yet active. An administrator must activate it "
            "and link it to a household before you can sign in.",
            "info",
        )
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    log_action("logout", "user", current_user.id)
    logout_user()
    flash("You have signed out.", "info")
    return redirect(url_for("auth.login"))
