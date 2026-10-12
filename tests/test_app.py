"""Automated tests mapped to the main functional requirements."""

from datetime import datetime, timedelta, time as dtime, date

from werkzeug.security import check_password_hash

from app import db
from app.models import (
    Alert,
    CaregiverAssignment,
    CheckinRecord,
    CheckinSchedule,
    ElderlyProfile,
    FollowupAction,
    User,
)
from app.services.risk_engine import assess_risk, score_from_features
from app.services.scanner import escalate_unacknowledged, scan_missed_checkins


def _user(username, role, password="Secret@123", active=True):
    u = User(
        username=username,
        email="{}@test.invalid".format(username),
        full_name=username.title(),
        role=role,
        is_active=active,
    )
    u.set_password(password)
    db.session.add(u)
    db.session.flush()
    return u


def _profile(name="Test Elder", consent=True, status="active", user_id=None):
    p = ElderlyProfile(
        full_name=name,
        consent_given=consent,
        consent_date=datetime.utcnow() if consent else None,
        status=status if consent else "inactive",
        user_id=user_id,
        living_arrangement="lives_alone",
        mobility_status="independent",
    )
    db.session.add(p)
    db.session.flush()
    return p


def _login(client, username, password="Secret@123"):
    return client.post(
        "/auth/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )


def test_login_success(client, app):
    with app.app_context():
        _user("admin", "admin")
        db.session.commit()
    res = _login(client, "admin")
    assert res.status_code in (302, 303)


def test_login_rejects_bad_password(client, app):
    with app.app_context():
        _user("admin", "admin")
        db.session.commit()
    res = client.post(
        "/auth/login",
        data={"username": "admin", "password": "wrong"},
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"Incorrect" in res.data


def test_password_is_hashed(app):
    with app.app_context():
        u = _user("hashed", "admin", password="Secret@123")
        db.session.commit()
        stored = User.query.filter_by(username="hashed").first()
        assert stored.password_hash != "Secret@123"
        assert check_password_hash(stored.password_hash, "Secret@123")


def test_caregiver_cannot_view_unassigned_profile(client, app):
    with app.app_context():
        c1 = _user("c1", "caregiver")
        c2 = _user("c2", "caregiver")
        p = _profile("Only C1")
        db.session.add(
            CaregiverAssignment(elderly_id=p.id, caregiver_id=c1.id, is_primary=True)
        )
        db.session.commit()
        pid = p.id
    _login(client, "c2")
    res = client.get("/elderly/{}".format(pid))
    assert res.status_code == 403


def test_elderly_cannot_open_admin(client, app):
    with app.app_context():
        _user("elder1", "elderly")
        db.session.commit()
    _login(client, "elder1")
    res = client.get("/admin/users")
    assert res.status_code == 403


def test_elderly_can_submit_checkin(client, app):
    with app.app_context():
        u = _user("margaret2", "elderly")
        p = _profile("Margaret Two", user_id=u.id)
        db.session.add(
            CheckinSchedule(
                elderly_id=p.id,
                frequency="daily",
                window_start=dtime(0, 0),
                window_end=dtime(23, 50),
                days_of_week="1,2,3,4,5,6,7",
                grace_minutes=0,
            )
        )
        db.session.commit()
        pid = p.id
    _login(client, "margaret2")
    res = client.post(
        "/checkins/submit/{}".format(pid),
        data={"mood": "good", "notes": "Feeling fine (test)"},
        follow_redirects=True,
    )
    assert res.status_code == 200
    with app.app_context():
        rec = CheckinRecord.query.filter_by(elderly_id=pid).first()
        assert rec is not None
        assert rec.status in ("completed", "completed_late")
        assert rec.method == "self"


def test_missed_checkin_creates_alert_once(app):
    with app.app_context():
        c = _user("carer", "caregiver")
        p = _profile("Missed Person")
        db.session.add(
            CaregiverAssignment(elderly_id=p.id, caregiver_id=c.id, is_primary=True)
        )
        due_time = (datetime.now() - timedelta(hours=3)).time().replace(second=0, microsecond=0)
        start = (datetime.now() - timedelta(hours=5)).time().replace(second=0, microsecond=0)
        if start >= due_time:
            start = dtime(0, 0)
            due_time = dtime(0, 1)
        sched = CheckinSchedule(
            elderly_id=p.id,
            frequency="daily",
            window_start=start,
            window_end=due_time,
            days_of_week="1,2,3,4,5,6,7",
            grace_minutes=0,
        )
        db.session.add(sched)
        db.session.flush()
        # Previous days already completed so only today is outstanding.
        for offset in range(1, 4):
            day = date.today() - timedelta(days=offset)
            db.session.add(
                CheckinRecord(
                    schedule_id=sched.id,
                    elderly_id=p.id,
                    status="completed",
                    method="self",
                    due_at=datetime.combine(day, due_time),
                    submitted_at=datetime.combine(day, start),
                )
            )
        db.session.commit()
        n1 = scan_missed_checkins()
        n2 = scan_missed_checkins()
        missed = CheckinRecord.query.filter_by(elderly_id=p.id, status="missed").count()
        alerts = Alert.query.filter_by(elderly_id=p.id, alert_type="overdue").count()
        assert n1 >= 1
        assert n2 == 0
        assert missed == 1
        assert alerts == 1


def test_alert_cannot_resolve_without_followup(client, app):
    with app.app_context():
        admin = _user("admin2", "admin")
        p = _profile("Needs Followup")
        a = Alert(
            elderly_id=p.id,
            alert_type="overdue",
            priority="high",
            status="open",
            title="Test",
            reason="test reason",
            assigned_to=admin.id,
        )
        db.session.add(a)
        db.session.commit()
        aid = a.id
    _login(client, "admin2")
    res = client.post("/alerts/{}/close".format(aid), follow_redirects=True)
    assert res.status_code == 200
    assert b"only after a follow-up" in res.data
    with app.app_context():
        assert Alert.query.get(aid).status == "open"
        db.session.add(
            FollowupAction(
                alert_id=aid,
                elderly_id=Alert.query.get(aid).elderly_id,
                caregiver_id=User.query.filter_by(username="admin2").first().id,
                action_type="phone",
                outcome="contacted",
                description="Called and spoke to the person.",
            )
        )
        db.session.commit()
    res = client.post("/alerts/{}/close".format(aid), follow_redirects=True)
    assert b"Case closed" in res.data
    with app.app_context():
        assert Alert.query.get(aid).status == "resolved"


def test_risk_engine_high_for_long_overdue(app):
    features = {
        "hours_overdue": 30,
        "missed_7": 3,
        "missed_14": 4,
        "consecutive_misses": 3,
        "days_since_visit": 16,
        "hour_deviation": 1,
        "needs_assistance": False,
    }
    score, priority, reasons = score_from_features(features)
    assert score >= 45
    assert priority in ("high", "critical")
    assert reasons


def test_assistance_creates_high_alert(client, app):
    with app.app_context():
        u = _user("helpme", "elderly")
        c = _user("helper", "caregiver")
        p = _profile("Help Person", user_id=u.id)
        db.session.add(
            CaregiverAssignment(elderly_id=p.id, caregiver_id=c.id, is_primary=True)
        )
        db.session.commit()
        pid = p.id
    _login(client, "helpme")
    res = client.post(
        "/checkins/help/{}".format(pid),
        data={"notes": "Please call me"},
        follow_redirects=True,
    )
    assert res.status_code == 200
    with app.app_context():
        alert = Alert.query.filter_by(elderly_id=pid, alert_type="assistance").first()
        assert alert is not None
        assert alert.priority in ("high", "critical")


def test_profile_without_consent_not_scanned(app):
    with app.app_context():
        p = _profile("No Consent", consent=False)
        db.session.add(
            CheckinSchedule(
                elderly_id=p.id,
                frequency="daily",
                window_start=dtime(0, 0),
                window_end=dtime(0, 1),
                days_of_week="1,2,3,4,5,6,7",
                grace_minutes=0,
            )
        )
        db.session.commit()
        created = scan_missed_checkins()
        assert created == 0
        assert CheckinRecord.query.filter_by(elderly_id=p.id).count() == 0


def test_escalation_after_threshold(app):
    with app.app_context():
        from app.models import SystemSetting

        db.session.add(SystemSetting(key="escalation_hours", value="2", description="t"))
        admin = _user("escadmin", "admin")
        p = _profile("Escalate Me")
        a = Alert(
            elderly_id=p.id,
            alert_type="overdue",
            priority="medium",
            status="open",
            title="Old",
            reason="old",
            assigned_to=admin.id,
            created_at=datetime.utcnow() - timedelta(hours=5),
        )
        db.session.add(a)
        db.session.commit()
        n = escalate_unacknowledged()
        assert n >= 1
        assert Alert.query.get(a.id).status == "escalated"
