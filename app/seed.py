"""
SYNTHETIC DEMONSTRATION DATA

Every person, phone number, address, check-in, visit, and alert created here
is fictitious and exists only so a student can demonstrate the prototype.
These rows are not observations of real households and must not be used as
training evidence for a real-world model.
"""

from datetime import datetime, timedelta, time as dtime, date

from app import db
from app.models import (
    Alert,
    AlertAcknowledgement,
    CaregiverAssignment,
    CaregiverVisit,
    CheckinRecord,
    CheckinSchedule,
    ElderlyProfile,
    FamilyLink,
    FollowupAction,
    Notification,
    SystemSetting,
    User,
)
from app.services.scanner import run_scan


SYNTHETIC_BANNER = (
    "SYNTHETIC DEMONSTRATION DATA — fictitious names and events, not real people."
)


def _user(username, email, full_name, role, password, phone=None, active=True):
    u = User(
        username=username,
        email=email,
        full_name=full_name,
        role=role,
        phone=phone,
        is_active=active,
    )
    u.set_password(password)
    db.session.add(u)
    db.session.flush()
    return u


def _upsert_setting(key, value, description):
    row = SystemSetting.query.filter_by(key=key).first()
    if not row:
        db.session.add(SystemSetting(key=key, value=value, description=description))
    else:
        row.value = value


def _time_window_open(now):
    start = now - timedelta(hours=1)
    end = now + timedelta(hours=2)
    if start.date() != end.date():
        return dtime(0, 5), dtime(23, 50)
    return start.replace(second=0, microsecond=0).time(), end.replace(second=0, microsecond=0).time()


def _time_window_closed(now):
    end_dt = now - timedelta(hours=3)
    start_dt = end_dt - timedelta(hours=2)
    if start_dt.date() != now.date():
        return dtime(6, 0), dtime(8, 0)
    return start_dt.replace(second=0, microsecond=0).time(), end_dt.replace(second=0, microsecond=0).time()


def _due(day, end_time):
    return datetime.combine(day, end_time)


def seed(reset=True):
    if reset:
        db.drop_all()
        db.create_all()

    now = datetime.now().replace(second=0, microsecond=0)
    today = now.date()

    admin = _user("admin", "admin@demo.invalid", "Alex Mwaka (Admin)", "admin", "Admin@123", "0700000001")
    amina = _user("amina", "amina@demo.invalid", "Amina Nalwoga", "caregiver", "Care@123", "0700000002")
    david = _user("david", "david@demo.invalid", "David Ssebunya", "caregiver", "Care@123", "0700000003")
    margaret_u = _user("margaret", "margaret@demo.invalid", "Margaret Chen", "elderly", "Elder@123", "0700000101")
    john_u = _user("john", "john@demo.invalid", "John Ouma", "elderly", "Elder@123", "0700000102")
    grace = _user("grace.family", "grace@demo.invalid", "Grace Adeyemi", "family", "Family@123", "0700000201")

    _upsert_setting("organisation_name", "Nakasero Community Welfare Desk", "Demo organisation")
    _upsert_setting("escalation_hours", "2", "Hours before unacknowledged alerts escalate")
    db.session.flush()

    def profile(**kwargs):
        kwargs.setdefault("consent_given", True)
        kwargs.setdefault("consent_date", now - timedelta(days=40))
        kwargs.setdefault("status", "active")
        kwargs.setdefault("living_arrangement", "lives_alone")
        p = ElderlyProfile(**kwargs)
        db.session.add(p)
        db.session.flush()
        return p

    p_margaret = profile(
        user_id=margaret_u.id,
        full_name="Margaret Chen",
        date_of_birth=date(1948, 3, 12),
        gender="female",
        address="14 Acacia Avenue (synthetic)",
        phone="0700000101",
        mobility_status="independent",
        emergency_contact_name="Lin Chen",
        emergency_contact_phone="0700001101",
        emergency_contact_relationship="Daughter",
        secondary_contact_name="Amina Nalwoga",
        secondary_contact_phone="0700000002",
        welfare_notes="SYNTHETIC. Prefers morning calls. No clinical record.",
    )
    p_john = profile(
        user_id=john_u.id,
        full_name="John Ouma",
        date_of_birth=date(1942, 11, 2),
        gender="male",
        address="9 Nile Close (synthetic)",
        phone="0700000102",
        mobility_status="assisted",
        emergency_contact_name="Mary Ouma",
        emergency_contact_phone="0700001102",
        emergency_contact_relationship="Sister",
        welfare_notes="SYNTHETIC. Uses a walking frame indoors.",
    )
    p_rose = profile(
        full_name="Rose Nambi",
        date_of_birth=date(1939, 7, 21),
        gender="female",
        address="Plot 3, Kisaasi (synthetic)",
        phone="0700000103",
        mobility_status="limited",
        emergency_contact_name="Paul Nambi",
        emergency_contact_phone="0700001103",
        emergency_contact_relationship="Son",
        welfare_notes="SYNTHETIC. Neighbour has a spare key (demo note only).",
    )
    p_musa = profile(
        full_name="Musa Okello",
        date_of_birth=date(1951, 1, 8),
        gender="male",
        address="22 Market Lane (synthetic)",
        phone="0700000104",
        mobility_status="independent",
        living_arrangement="with_family",
        emergency_contact_name="Sarah Okello",
        emergency_contact_phone="0700001104",
        emergency_contact_relationship="Spouse",
        welfare_notes="SYNTHETIC. Family nearby; still uses the check-in app.",
    )
    p_joyce = profile(
        full_name="Joyce Adeyemi",
        date_of_birth=date(1946, 5, 30),
        gender="female",
        address="5 Garden Court (synthetic)",
        phone="0700000105",
        mobility_status="independent",
        emergency_contact_name="Grace Adeyemi",
        emergency_contact_phone="0700000201",
        emergency_contact_relationship="Daughter",
        welfare_notes="SYNTHETIC. Daughter (family account) may submit check-ins.",
    )
    p_peter = profile(
        full_name="Peter Kato",
        date_of_birth=date(1936, 9, 14),
        gender="male",
        address="18 Hill Road (synthetic)",
        phone="0700000106",
        mobility_status="assisted",
        emergency_contact_name="Rita Kato",
        emergency_contact_phone="0700001106",
        emergency_contact_relationship="Niece",
        welfare_notes="SYNTHETIC. Irregular check-in times in the demo history.",
    )
    p_asha = profile(
        full_name="Asha Namuli",
        date_of_birth=date(1944, 12, 1),
        gender="female",
        address="7 Lake View (synthetic)",
        phone="0700000107",
        mobility_status="independent",
        emergency_contact_name="Hassan Namuli",
        emergency_contact_phone="0700001107",
        emergency_contact_relationship="Brother",
        welfare_notes="SYNTHETIC. Open follow-up used to demonstrate unresolved cases.",
    )
    p_samuel = profile(
        full_name="Samuel Mwangi",
        date_of_birth=date(1940, 4, 19),
        gender="male",
        address="11 Cedar Street (synthetic)",
        phone="0700000108",
        mobility_status="assisted",
        emergency_contact_name="Jane Mwangi",
        emergency_contact_phone="0700001108",
        emergency_contact_relationship="Daughter",
        welfare_notes="SYNTHETIC. Recent home visit recorded.",
    )

    def assign(elderly, caregiver, primary=False):
        db.session.add(
            CaregiverAssignment(
                elderly_id=elderly.id,
                caregiver_id=caregiver.id,
                is_primary=primary,
                assigned_by=admin.id,
                notes="SYNTHETIC assignment",
            )
        )

    for p in (p_margaret, p_john, p_rose, p_musa, p_joyce, p_peter, p_asha):
        assign(p, amina, primary=True)
        assign(p, david, primary=False)
    assign(p_samuel, david, primary=True)
    assign(p_samuel, amina, primary=False)

    db.session.add(
        FamilyLink(
            elderly_id=p_joyce.id,
            family_user_id=grace.id,
            relationship="Daughter",
        )
    )

    open_start, open_end = _time_window_open(now)
    closed_start, closed_end = _time_window_closed(now)
    morning_start, morning_end = dtime(8, 0), dtime(11, 0)

    def schedule(profile, start, end, grace=60):
        s = CheckinSchedule(
            elderly_id=profile.id,
            frequency="daily",
            window_start=start,
            window_end=end,
            days_of_week="1,2,3,4,5,6,7",
            grace_minutes=grace,
            is_active=True,
        )
        db.session.add(s)
        db.session.flush()
        return s

    s_margaret = schedule(p_margaret, morning_start, morning_end, 60)
    s_john = schedule(p_john, closed_start, closed_end, 30)
    s_rose = schedule(p_rose, closed_start, closed_end, 15)
    s_musa = schedule(p_musa, open_start, open_end, 45)
    s_joyce = schedule(p_joyce, morning_start, morning_end, 60)
    s_peter = schedule(p_peter, closed_start, closed_end, 30)
    s_asha = schedule(p_asha, morning_start, morning_end, 60)
    s_samuel = schedule(p_samuel, morning_start, morning_end, 60)

    def rec(profile, sched, day, status, mood=None, method="self", hour=9, submitter=None, notes=None):
        due = _due(day, sched.window_end)
        submitted = None
        if status in ("completed", "completed_late"):
            submitted = datetime.combine(day, dtime(hour, 10 if hour < 23 else 0))
            if status == "completed_late":
                submitted = due + timedelta(hours=2)
        row = CheckinRecord(
            schedule_id=sched.id,
            elderly_id=profile.id,
            submitted_by=submitter,
            status=status,
            method=method if status != "missed" else "system",
            mood=mood,
            notes=notes,
            due_at=due,
            submitted_at=submitted,
        )
        db.session.add(row)
        db.session.flush()
        return row

    # History for the last 10 days (synthetic)
    for i in range(1, 11):
        day = today - timedelta(days=i)
        rec(p_margaret, s_margaret, day, "completed", "good", submitter=margaret_u.id, hour=9)
        rec(p_joyce, s_joyce, day, "completed", "okay", submitter=grace.id, method="family", hour=10)
        rec(p_samuel, s_samuel, day, "completed", "good", method="caregiver", submitter=david.id, hour=8)
        rec(p_musa, s_musa, day, "completed", "good", method="caregiver", submitter=amina.id, hour=9)
        if i <= 3:
            rec(p_rose, s_rose, day, "missed")
            rec(p_peter, s_peter, day, "missed")
            rec(p_john, s_john, day, "completed_late", "okay", submitter=john_u.id, hour=16)
        else:
            rec(p_rose, s_rose, day, "completed", "okay", method="caregiver", submitter=amina.id, hour=10)
            rec(p_peter, s_peter, day, "completed" if i % 2 == 0 else "missed", "okay" if i % 2 == 0 else None, submitter=amina.id if i % 2 == 0 else None, method="caregiver" if i % 2 == 0 else "system", hour=20)
            rec(p_john, s_john, day, "completed", "good", submitter=john_u.id, hour=9)
        rec(p_asha, s_asha, day, "completed", "good", method="caregiver", submitter=amina.id, hour=9)

    # Today: Margaret and Joyce and Samuel have completed; Musa awaiting (no row);
    # John/Rose/Peter will be picked up by scanner as missed.
    rec(
        p_margaret,
        s_margaret,
        today,
        "completed",
        "good",
        submitter=margaret_u.id,
        hour=min(now.hour, 22),
        notes="SYNTHETIC. Morning check-in from the app.",
    )
    rec(
        p_joyce,
        s_joyce,
        today,
        "completed",
        "okay",
        method="family",
        submitter=grace.id,
        hour=min(now.hour, 22),
        notes="SYNTHETIC. Daughter submitted after a phone call.",
    )
    rec(
        p_samuel,
        s_samuel,
        today,
        "completed",
        "good",
        method="caregiver",
        submitter=david.id,
        hour=min(max(now.hour - 1, 0), 22),
        notes="SYNTHETIC. Caregiver recorded after a brief call.",
    )
    rec(
        p_asha,
        s_asha,
        today,
        "completed_late",
        "unwell",
        method="self",
        notes="SYNTHETIC. Late check-in; follow-up still open.",
    )

    db.session.add(
        CaregiverVisit(
            elderly_id=p_samuel.id,
            caregiver_id=david.id,
            visit_type="home",
            visited_at=now - timedelta(days=1, hours=2),
            duration_minutes=35,
            observations="SYNTHETIC. Conversation at the door; no further action recorded.",
        )
    )
    db.session.add(
        CaregiverVisit(
            elderly_id=p_margaret.id,
            caregiver_id=amina.id,
            visit_type="phone",
            visited_at=now - timedelta(days=3),
            duration_minutes=10,
            observations="SYNTHETIC. Routine phone visit.",
        )
    )
    db.session.add(
        CaregiverVisit(
            elderly_id=p_rose.id,
            caregiver_id=amina.id,
            visit_type="home",
            visited_at=now - timedelta(days=16),
            duration_minutes=40,
            observations="SYNTHETIC. Older visit so the rule engine can show 'days since visit'.",
        )
    )

    # Open acknowledged alert for Asha (needs follow-up to close)
    asha_alert = Alert(
        elderly_id=p_asha.id,
        alert_type="pattern",
        priority="medium",
        status="acknowledged",
        title="Late check-in pattern — Asha Namuli",
        reason=(
            "SYNTHETIC DEMO. Ranked for review because today's check-in was after the deadline "
            "and the submitted mood was 'not well'. This is not a diagnosis."
        ),
        risk_score=40,
        is_ai_flagged=True,
        assigned_to=amina.id,
        acknowledged_at=now - timedelta(hours=1),
    )
    db.session.add(asha_alert)
    db.session.flush()
    db.session.add(
        AlertAcknowledgement(
            alert_id=asha_alert.id,
            user_id=amina.id,
            notes="SYNTHETIC. Seen on dashboard; follow-up not yet written.",
        )
    )
    db.session.add(
        Notification(
            user_id=amina.id,
            title="Follow-up still open",
            message="Asha Namuli has an acknowledged alert without a documented outcome (synthetic).",
            link="/alerts/{}".format(asha_alert.id),
        )
    )

    # Resolved example with follow-up
    old_alert = Alert(
        elderly_id=p_samuel.id,
        alert_type="overdue",
        priority="low",
        status="resolved",
        title="Overdue check-in — Samuel Mwangi",
        reason="SYNTHETIC. Missed yesterday; caregiver visited and closed the case.",
        risk_score=20,
        assigned_to=david.id,
        acknowledged_at=now - timedelta(days=1, hours=3),
        resolved_at=now - timedelta(days=1, hours=1),
        created_at=now - timedelta(days=1, hours=4),
    )
    db.session.add(old_alert)
    db.session.flush()
    db.session.add(
        FollowupAction(
            alert_id=old_alert.id,
            elderly_id=p_samuel.id,
            caregiver_id=david.id,
            action_type="visit",
            outcome="visited",
            description="SYNTHETIC. Home visit completed; person was at home watching radio.",
            performed_at=now - timedelta(days=1, hours=2),
        )
    )

    db.session.commit()
    run_scan(now=now)

    return {
        "banner": SYNTHETIC_BANNER,
        "users": {
            "admin": "Admin@123",
            "amina": "Care@123",
            "david": "Care@123",
            "margaret": "Elder@123",
            "john": "Elder@123",
            "grace.family": "Family@123",
        },
    }
