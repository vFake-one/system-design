# Test Cases and Test Results

Automated tests live in `tests/test_app.py` and run with `pytest`. They use a temporary SQLite database; they do **not** touch the demo file.

## 1. Test cases

| ID | Requirement | Steps | Expected |
| --- | --- | --- | --- |
| TC-01 | FR-A1 | POST login with valid admin credentials | Redirect to dashboard, session established |
| TC-02 | FR-A1 | POST login with wrong password | 200 on login page, flash error, not authenticated |
| TC-03 | FR-A6 | Caregiver opens another caregiver’s unassigned profile URL | 403 |
| TC-04 | FR-A2 | Create user and inspect `password_hash` | Hash present; raw password not stored |
| TC-05 | FR-K2 | Elderly user submits check-in | Record `completed`, method `self` |
| TC-06 | FR-M1 | Schedule due in the past, no record, run scanner | `missed` record + overdue alert created |
| TC-07 | FR-M1 | Run scanner twice | Still only one missed record for that `due_at` |
| TC-08 | FR-L5 | Resolve alert with no follow-up | Rejected; alert stays open |
| TC-09 | FR-L5 | Add follow-up then resolve | Status `resolved` |
| TC-10 | FR-I1 | Engine on a household with 30h overdue and 3 misses / 7 days | Score ≥ 45, reasons non-empty |
| TC-11 | FR-K4 | Submit assistance request | Alert type `assistance`, priority high or critical |
| TC-12 | FR-E2 | Create profile without consent as active | Stored inactive / consent required |
| TC-13 | NFR-3 | GET a POST-only URL without CSRF on a form | WTForms rejects empty token on POST |
| TC-14 | FR-C / RBAC | Elderly user GET `/admin/users` | 403 |
| TC-15 | FR-L4 | Open alert older than escalation hours, run escalate | Status `escalated` |

## 2. How to run

```bash
pytest -q --tb=short
```

## 3. Results

Automated suite (`pytest -q`) on Python 3.11: **12 passed**.

| ID | Result | Notes |
| --- | --- | --- |
| TC-01 | Pass | Valid admin login redirects |
| TC-02 | Pass | Bad password rejected |
| TC-03 | Pass | Unassigned caregiver receives 403 |
| TC-04 | Pass | Password stored as PBKDF2 hash |
| TC-05 | Pass | Elderly check-in stored as completed/self |
| TC-06 / TC-07 | Pass | Scanner creates one missed row + overdue alert; second run is idempotent |
| TC-08 | Pass | Resolve without follow-up rejected |
| TC-09 | Pass | Resolve after follow-up succeeds |
| TC-10 | Pass | Rule engine score ≥ 45 with reasons |
| TC-11 | Pass | Assistance request creates high/critical alert |
| TC-12 | Pass | Profiles without consent are not scanned |
| TC-14 | Pass | Elderly user cannot open `/admin/users` |
| TC-15 | Pass | Unacknowledged alert older than threshold is escalated |

Manual UI checks (not automated):

- Elderly page buttons are large enough on a 360px-wide viewport.
- Disclaimer is visible on login and dashboards.
- Chart.js charts render on `/reports/` with demo data.
- Screen reader / label: every form field has a label (spot check).

## 4. Defect log template

| Date | Severity | Description | Status |
| --- | --- | --- | --- |
| | | | |
