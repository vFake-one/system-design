# Functional and Non-Functional Requirements

Requirements are numbered so they can be traced to test cases. Priority: **M** = must have in the prototype, **S** = should have, **C** = could have later.

## 1. Functional requirements

### 1.1 Authentication and accounts

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-A1 | Users shall log in with username (or email) and password. | M |
| FR-A2 | Passwords shall be stored only as hashes (PBKDF2 via Werkzeug). | M |
| FR-A3 | Roles shall be `admin`, `caregiver`, `elderly`, `family`. | M |
| FR-A4 | An administrator may create, deactivate, and reset accounts. | M |
| FR-A5 | Self-registration, if enabled, shall create only `family` accounts pending admin approval **or** be disabled in favour of admin-created accounts. Prototype: admin creates users; a simple register form exists for family accounts and is marked pending until an admin activates them. | S |
| FR-A6 | Failed authorisation shall return HTTP 403 and must not leak another user’s records. | M |
| FR-A7 | Users shall be able to log out, which ends the session. | M |

### 1.2 Elderly household records

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-E1 | Admin (and caregivers, where allowed) shall create an elderly profile with name, date of birth, contact, address, living arrangement, mobility note, emergency contacts, and welfare notes. | M |
| FR-E2 | A profile shall not be marked active unless `consent_given` is true. | M |
| FR-E3 | Each profile may link to a login user (elderly role) and/or family users. | M |
| FR-E4 | Caregivers shall see only households assigned to them, unless they are admins. | M |
| FR-E5 | Inaccurate records shall be editable by admin; the change shall be audit-logged. | M |

### 1.3 Caregiver assignment

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-C1 | Admin shall assign one or more caregivers to a household. | M |
| FR-C2 | Exactly one assignment may be flagged primary at a time (enforced in application logic). | M |
| FR-C3 | Assignments can be deactivated without deleting history. | M |

### 1.4 Check-in scheduling and recording

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-K1 | A household may have an active daily or weekly schedule with a start time, end time, days of week, and grace minutes. | M |
| FR-K2 | Elderly, family, and assigned caregivers may submit a check-in (mood, optional notes, optional “I need help”). | M |
| FR-K3 | A successful submission shall store who submitted, when, and the method (`self`, `family`, `caregiver`). | M |
| FR-K4 | “I need help” shall create a high-priority assistance alert immediately, regardless of the schedule window. | M |
| FR-K5 | The UI for elderly users shall use large controls and plain language. | M |

### 1.5 Missed check-in detection

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-M1 | After `window_end + grace_minutes` on a scheduled day, if no completed check-in exists for that due time, the system shall create a `missed` check-in record. | M |
| FR-M2 | A missed record shall generate an overdue alert assigned to the primary caregiver (or the first active caregiver). | M |
| FR-M3 | Detection shall run periodically while the application is running and also when a staff dashboard loads. | M |

### 1.6 Alerts and escalation

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-L1 | Alerts shall have type, priority, status, written reason, and optional risk score. | M |
| FR-L2 | Assigned caregivers receive an in-app notification. | M |
| FR-L3 | A caregiver shall acknowledge an alert (name and timestamp stored). | M |
| FR-L4 | If unacknowledged beyond the configured escalation hours, status becomes `escalated` and a secondary contact / admin is notified. | M |
| FR-L5 | An alert may be closed only after at least one follow-up action with an outcome is recorded, or after it is explicitly marked `false_alert` with a reason. | M |
| FR-L6 | The UI shall state that the prototype is not emergency services. | M |

### 1.7 Visits, follow-up, dashboard, reports

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-V1 | Caregivers shall record visits (date/time, type, observations). | M |
| FR-V2 | Follow-up actions shall link to an alert and/or household. | M |
| FR-D1 | Dashboards shall show totals: registered elderly, completed today, overdue, unacknowledged alerts, high-priority cases, recent visits, unresolved follow-ups. | M |
| FR-D2 | Status values: `safe_today`, `awaiting`, `overdue`, `follow_up`. “Safe today” means a check-in was submitted today — **not** a medical claim. | M |
| FR-R1 | Reports shall filter by date range for check-ins, alerts, visits, and follow-up outcomes. | M |
| FR-R2 | Charts shall use Chart.js. | M |

### 1.8 AI-assisted prioritisation

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-I1 | A rule-based engine shall compute a 0–100 review score and a priority label. | M |
| FR-I2 | The reason list shall be stored on the alert and shown to the caregiver. | M |
| FR-I3 | The engine shall not output “this person is in medical danger” or similar. | M |
| FR-I4 | Any ML model shall be clearly labelled experimental and trained only on synthetic demonstration rows. | M |

### 1.9 Audit, privacy, backup

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-P1 | Login, profile changes, assignments, check-ins, alert status changes, and follow-ups shall be written to `audit_logs`. | M |
| FR-P2 | Admin may download a SQLite backup file. | S |
| FR-P3 | Admin may view audit logs. | M |

## 2. Non-functional requirements

| ID | Category | Requirement |
| --- | --- | --- |
| NFR-1 | Usability | Elderly-facing pages use at least 18px base font and large primary buttons. Status is shown with text **and** colour (not colour alone). |
| NFR-2 | Accessibility | Form controls have labels; contrast is high; focus states are visible. |
| NFR-3 | Security | Hashed passwords, CSRF tokens, parameterised SQL via ORM, `HttpOnly` session cookie, role checks on every mutating route. |
| NFR-4 | Reliability | Missed-check logic is idempotent (will not create duplicate missed records for the same due timestamp). |
| NFR-5 | Performance | Prototype supports tens of households on SQLite; list pages stay usable with the seeded demo set. |
| NFR-6 | Maintainability | Flask blueprints, documented schema, and a single configuration module. |
| NFR-7 | Portability | Runs locally on Windows/macOS/Linux with Python 3.10+. |
| NFR-8 | Privacy | Role-restricted queries; medical-style notes are free text and treated as sensitive. |
| NFR-9 | Honesty | Disclaimer on login, dashboard, and alert pages. |
| NFR-10 | Testability | Automated tests for auth, roles, check-in, missed detection, and alert closure rules. |

## 3. Traceability (summary)

Tests in `tests/test_app.py` map to FR-A1, FR-A2, FR-A6, FR-K2, FR-M1, FR-L5, and FR-I1.
