from datetime import datetime, timedelta

from flask import Flask, render_template, request
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = "auth.login"
login_manager.login_message = "Please sign in to continue."
login_manager.login_message_category = "warning"

_last_scan = None


def create_app(config_class=None):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_class or "config.Config")

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.models import User  # noqa: F401

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.blueprints.auth import auth_bp
    from app.blueprints.main import main_bp
    from app.blueprints.elderly import elderly_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.checkins import checkins_bp
    from app.blueprints.alerts import alerts_bp
    from app.blueprints.visits import visits_bp
    from app.blueprints.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(elderly_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(checkins_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(visits_bp)
    app.register_blueprint(reports_bp)

    @app.context_processor
    def inject_globals():
        from app.models import Notification, SystemSetting

        unread = 0
        org = "Community Welfare Check-in"
        try:
            row = SystemSetting.query.filter_by(key="organisation_name").first()
            if row:
                org = row.value
        except Exception:
            pass
        if current_user.is_authenticated:
            unread = Notification.query.filter_by(
                user_id=current_user.id, is_read=False
            ).count()
        return {
            "unread_count": unread,
            "organisation_name": org,
            "now": datetime.now(),
        }

    @app.before_request
    def periodic_scan():
        global _last_scan
        if app.config.get("TESTING"):
            return
        if request.endpoint == "static":
            return
        now = datetime.utcnow()
        if _last_scan is None or now - _last_scan > timedelta(minutes=2):
            try:
                from app.services.scanner import run_scan

                run_scan()
            except Exception:
                app.logger.exception("Missed-check scan failed")
            _last_scan = now

    @app.errorhandler(403)
    def forbidden(_e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(_e):
        return render_template("errors/500.html"), 500

    return app
