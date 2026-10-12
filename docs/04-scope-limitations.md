# Project Scope and Limitations

## 1. In scope

- Web application usable on desktop and smartphone browsers.
- Four roles: Administrator, Caregiver/Welfare Coordinator, Elderly person, Authorised family member.
- CRUD for elderly profiles and caregiver assignments (with consent).
- Daily/weekly check-in schedules and check-in submission.
- Automatic missed-check detection and in-app alerts.
- Configurable escalation period for unacknowledged alerts.
- Visit notes and follow-up actions.
- Rule-based risk priority with a visible explanation.
- Optional Isolation Forest comparison on **synthetic** feature rows.
- Dashboard charts and date-filtered reports.
- Password hashing, CSRF, role checks, audit log, SQLite backup copy.
- Installation guide, tests, and user manual.

## 2. Out of scope (explicitly)

- Native iOS/Android applications.
- Wearable sensors, fall-detection cameras, or GPS tracking.
- Real SMS/WhatsApp/voice-call gateways (the code leaves a hook; the working channel is in-app).
- Electronic health records, prescriptions, or diagnostic coding.
- Multi-tenant SaaS billing, national identity integration, or live maps.
- Training any model on real patient or resident data.
- 24/7 monitoring, SLA guarantees, or emergency dispatch.
- Full MySQL production hardening (a migration-oriented SQL script is supplied).

## 3. Limitations

1. **Prototype quality.** The default `SECRET_KEY` is for local demonstration. A real deployment must change it and use HTTPS.
2. **Time zone.** The prototype uses the server’s local time. A production system should store time zones per household.
3. **AI accuracy.** Rules are transparent but crude. Any ML comparison uses synthetic demonstration data and must not be quoted as clinical evidence.
4. **False reassurance.** A completed check-in only means someone submitted a form. It does not prove the person is uninjured.
5. **False alerts.** Network problems, forgotten passwords, or a visitor submitting late can create overdue alerts. Caregivers can mark an alert as a false alert and must record why.
6. **Single-process scanner.** Missed-check detection runs inside the web process. If the app is not running, detection pauses. Production would use an external scheduler (cron).
7. **Consent model.** Consent is a required checkbox and timestamp, not a legally reviewed protocol.

## 4. Assumptions

- Users have a smartphone or computer and a network connection.
- At least one caregiver is assigned to each active elderly profile.
- Check-in windows are agreed with the household.
- Demonstration accounts and names are fictitious.
