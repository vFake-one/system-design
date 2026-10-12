from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db

ROLES = ("admin", "caregiver", "elderly", "family")


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30))
    role = db.Column(db.String(30), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    def is_admin(self):
        return self.role == "admin"

    def is_staff(self):
        return self.role in ("admin", "caregiver")


class ElderlyProfile(db.Model):
    __tablename__ = "elderly_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    full_name = db.Column(db.String(120), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))
    address = db.Column(db.String(255))
    phone = db.Column(db.String(30))
    mobility_status = db.Column(db.String(50))
    living_arrangement = db.Column(db.String(50))
    emergency_contact_name = db.Column(db.String(120))
    emergency_contact_phone = db.Column(db.String(30))
    emergency_contact_relationship = db.Column(db.String(50))
    secondary_contact_name = db.Column(db.String(120))
    secondary_contact_phone = db.Column(db.String(30))
    welfare_notes = db.Column(db.Text)
    consent_given = db.Column(db.Boolean, default=False, nullable=False)
    consent_date = db.Column(db.DateTime)
    status = db.Column(db.String(30), default="active", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    login_user = db.relationship("User", foreign_keys=[user_id])
    assignments = db.relationship("CaregiverAssignment", backref="elderly", lazy="dynamic")
    schedules = db.relationship("CheckinSchedule", backref="elderly", lazy="dynamic")
    records = db.relationship("CheckinRecord", backref="elderly", lazy="dynamic")
    alerts = db.relationship("Alert", backref="elderly", lazy="dynamic")
    visits = db.relationship("CaregiverVisit", backref="elderly", lazy="dynamic")


class CaregiverAssignment(db.Model):
    __tablename__ = "caregiver_assignments"

    id = db.Column(db.Integer, primary_key=True)
    elderly_id = db.Column(db.Integer, db.ForeignKey("elderly_profiles.id"), nullable=False)
    caregiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    is_primary = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    notes = db.Column(db.String(255))

    caregiver = db.relationship("User", foreign_keys=[caregiver_id])
    assigner = db.relationship("User", foreign_keys=[assigned_by])


class FamilyLink(db.Model):
    __tablename__ = "family_links"

    id = db.Column(db.Integer, primary_key=True)
    elderly_id = db.Column(db.Integer, db.ForeignKey("elderly_profiles.id"), nullable=False)
    family_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    relationship = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    elderly = db.relationship("ElderlyProfile", backref="family_links")
    family_user = db.relationship("User", foreign_keys=[family_user_id])


class CheckinSchedule(db.Model):
    __tablename__ = "checkin_schedules"

    id = db.Column(db.Integer, primary_key=True)
    elderly_id = db.Column(db.Integer, db.ForeignKey("elderly_profiles.id"), nullable=False)
    frequency = db.Column(db.String(20), nullable=False)
    window_start = db.Column(db.Time, nullable=False)
    window_end = db.Column(db.Time, nullable=False)
    days_of_week = db.Column(db.String(20), default="1,2,3,4,5,6,7")
    grace_minutes = db.Column(db.Integer, default=60, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CheckinRecord(db.Model):
    __tablename__ = "checkin_records"

    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey("checkin_schedules.id"))
    elderly_id = db.Column(db.Integer, db.ForeignKey("elderly_profiles.id"), nullable=False)
    submitted_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    status = db.Column(db.String(20), nullable=False)
    method = db.Column(db.String(20))
    mood = db.Column(db.String(20))
    needs_assistance = db.Column(db.Boolean, default=False, nullable=False)
    notes = db.Column(db.Text)
    due_at = db.Column(db.DateTime, nullable=False)
    submitted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    submitter = db.relationship("User", foreign_keys=[submitted_by])
    schedule = db.relationship("CheckinSchedule")


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    elderly_id = db.Column(db.Integer, db.ForeignKey("elderly_profiles.id"), nullable=False)
    checkin_record_id = db.Column(db.Integer, db.ForeignKey("checkin_records.id"))
    alert_type = db.Column(db.String(40), nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="open", nullable=False)
    title = db.Column(db.String(200), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    risk_score = db.Column(db.Integer)
    is_ai_flagged = db.Column(db.Boolean, default=False, nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"))
    escalated_to = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    acknowledged_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)

    assignee = db.relationship("User", foreign_keys=[assigned_to])
    escalated_user = db.relationship("User", foreign_keys=[escalated_to])
    checkin_record = db.relationship("CheckinRecord")
    acknowledgements = db.relationship("AlertAcknowledgement", backref="alert", lazy="dynamic")
    followups = db.relationship("FollowupAction", backref="alert", lazy="dynamic")


class AlertAcknowledgement(db.Model):
    __tablename__ = "alert_acknowledgements"

    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.Integer, db.ForeignKey("alerts.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    notes = db.Column(db.Text)
    acknowledged_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User")


class CaregiverVisit(db.Model):
    __tablename__ = "caregiver_visits"

    id = db.Column(db.Integer, primary_key=True)
    elderly_id = db.Column(db.Integer, db.ForeignKey("elderly_profiles.id"), nullable=False)
    caregiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    visit_type = db.Column(db.String(30), nullable=False)
    visited_at = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer)
    observations = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    caregiver = db.relationship("User")


class FollowupAction(db.Model):
    __tablename__ = "followup_actions"

    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.Integer, db.ForeignKey("alerts.id"))
    elderly_id = db.Column(db.Integer, db.ForeignKey("elderly_profiles.id"), nullable=False)
    caregiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action_type = db.Column(db.String(40), nullable=False)
    outcome = db.Column(db.String(40), nullable=False)
    description = db.Column(db.Text)
    performed_at = db.Column(db.DateTime, default=datetime.utcnow)

    caregiver = db.relationship("User")
    elderly = db.relationship("ElderlyProfile")


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    link = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(80), nullable=False)
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User")


class SystemSetting(db.Model):
    __tablename__ = "system_settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False)
    value = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))


def get_setting(key: str, default: str = "") -> str:
    row = SystemSetting.query.filter_by(key=key).first()
    return row.value if row else default
