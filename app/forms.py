from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    DateTimeLocalField,
    IntegerField,
    PasswordField,
    SelectField,
    SelectMultipleField,
    StringField,
    TextAreaField,
    TimeField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    NumberRange,
    Optional,
    ValidationError,
)

from app.models import User


class LoginForm(FlaskForm):
    username = StringField("Username or email", validators=[DataRequired(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired()])


class RegisterForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired(), Length(max=120)])
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField("Phone", validators=[Optional(), Length(max=30)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    confirm = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password")])

    def validate_username(self, field):
        if User.query.filter_by(username=field.data.strip()).first():
            raise ValidationError("That username is already used.")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.strip().lower()).first():
            raise ValidationError("That email is already used.")


class UserForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired(), Length(max=120)])
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField("Phone", validators=[Optional(), Length(max=30)])
    role = SelectField(
        "Role",
        choices=[
            ("admin", "Administrator"),
            ("caregiver", "Caregiver / coordinator"),
            ("elderly", "Elderly person"),
            ("family", "Family member"),
        ],
        validators=[DataRequired()],
    )
    password = PasswordField("Password (leave blank to keep current)", validators=[Optional(), Length(min=8, max=128)])
    is_active = BooleanField("Account is active", default=True)


class ElderlyForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired(), Length(max=120)])
    date_of_birth = DateField("Date of birth", validators=[Optional()])
    gender = SelectField(
        "Gender",
        choices=[("", "Prefer not to say"), ("female", "Female"), ("male", "Male"), ("other", "Other")],
        validators=[Optional()],
    )
    address = StringField("Address", validators=[Optional(), Length(max=255)])
    phone = StringField("Phone", validators=[Optional(), Length(max=30)])
    mobility_status = SelectField(
        "Mobility",
        choices=[
            ("independent", "Independent"),
            ("assisted", "Needs some assistance"),
            ("limited", "Limited mobility"),
        ],
    )
    living_arrangement = SelectField(
        "Living arrangement",
        choices=[
            ("lives_alone", "Lives alone"),
            ("with_family", "Lives with family"),
            ("other", "Other"),
        ],
    )
    emergency_contact_name = StringField("Emergency contact name", validators=[Optional(), Length(max=120)])
    emergency_contact_phone = StringField("Emergency contact phone", validators=[Optional(), Length(max=30)])
    emergency_contact_relationship = StringField("Relationship", validators=[Optional(), Length(max=50)])
    secondary_contact_name = StringField("Secondary contact name", validators=[Optional(), Length(max=120)])
    secondary_contact_phone = StringField("Secondary contact phone", validators=[Optional(), Length(max=30)])
    welfare_notes = TextAreaField("Welfare notes (sensitive)", validators=[Optional(), Length(max=4000)])
    consent_given = BooleanField("Consent has been given to store this record and run scheduled check-ins")
    login_username = StringField("Linked login username (optional)", validators=[Optional(), Length(max=80)])
    status = SelectField(
        "Record status",
        choices=[("active", "Active"), ("inactive", "Inactive")],
        default="active",
    )


class AssignmentForm(FlaskForm):
    caregiver_id = SelectField("Caregiver", coerce=int, validators=[DataRequired()])
    is_primary = BooleanField("Primary caregiver (receives first alerts)")
    notes = StringField("Notes", validators=[Optional(), Length(max=255)])


class FamilyLinkForm(FlaskForm):
    family_user_id = SelectField("Family account", coerce=int, validators=[DataRequired()])
    relationship = StringField("Relationship", validators=[Optional(), Length(max=50)])


class ScheduleForm(FlaskForm):
    frequency = SelectField(
        "Frequency",
        choices=[("daily", "Daily"), ("weekly", "Weekly")],
        validators=[DataRequired()],
    )
    window_start = TimeField("Window start", validators=[DataRequired()])
    window_end = TimeField("Window end", validators=[DataRequired()])
    days = SelectMultipleField(
        "Days of week",
        choices=[
            ("1", "Monday"),
            ("2", "Tuesday"),
            ("3", "Wednesday"),
            ("4", "Thursday"),
            ("5", "Friday"),
            ("6", "Saturday"),
            ("7", "Sunday"),
        ],
        default=["1", "2", "3", "4", "5", "6", "7"],
    )
    grace_minutes = IntegerField(
        "Grace minutes after window end",
        default=60,
        validators=[DataRequired(), NumberRange(min=0, max=720)],
    )
    is_active = BooleanField("Schedule is active", default=True)


class CheckinForm(FlaskForm):
    mood = SelectField(
        "How are you feeling?",
        choices=[("good", "Good"), ("okay", "Okay"), ("unwell", "Not well")],
        validators=[DataRequired()],
    )
    notes = TextAreaField("Optional note", validators=[Optional(), Length(max=2000)])


class AssistanceForm(FlaskForm):
    notes = TextAreaField("What do you need? (optional)", validators=[Optional(), Length(max=2000)])


class AlertAckForm(FlaskForm):
    notes = TextAreaField("Acknowledgement note", validators=[Optional(), Length(max=2000)])


class FollowupForm(FlaskForm):
    action_type = SelectField(
        "Action",
        choices=[
            ("phone", "Phone call"),
            ("visit", "Visit"),
            ("message", "Message"),
            ("referral", "Referral"),
            ("other", "Other"),
        ],
        validators=[DataRequired()],
    )
    outcome = SelectField(
        "Outcome",
        choices=[
            ("contacted", "Contacted — person responded"),
            ("visited", "Visited"),
            ("no_answer", "No answer"),
            ("referred", "Referred"),
            ("false_alert", "False alert / known explanation"),
            ("other", "Other"),
        ],
        validators=[DataRequired()],
    )
    description = TextAreaField("What was done?", validators=[DataRequired(), Length(min=5, max=4000)])


class VisitForm(FlaskForm):
    elderly_id = SelectField("Household", coerce=int, validators=[DataRequired()])
    visit_type = SelectField(
        "Visit type",
        choices=[
            ("home", "Home visit"),
            ("phone", "Phone visit"),
            ("community", "Community / clinic"),
            ("other", "Other"),
        ],
        validators=[DataRequired()],
    )
    visited_at = DateTimeLocalField("Date and time", validators=[DataRequired()])
    duration_minutes = IntegerField("Duration (minutes)", validators=[Optional(), NumberRange(min=1, max=600)])
    observations = TextAreaField("Observations", validators=[Optional(), Length(max=4000)])


class ReportFilterForm(FlaskForm):
    start = DateField("From", validators=[DataRequired()])
    end = DateField("To", validators=[DataRequired()])


class SettingsForm(FlaskForm):
    organisation_name = StringField("Organisation name", validators=[DataRequired(), Length(max=120)])
    escalation_hours = IntegerField(
        "Escalate unacknowledged alerts after (hours)",
        validators=[DataRequired(), NumberRange(min=1, max=72)],
    )
