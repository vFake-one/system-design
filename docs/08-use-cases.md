# Use-Case Diagram and Descriptions

## 1. Actors

| Actor | Description |
| --- | --- |
| Administrator | Manages accounts, households, assignments, settings, audit, backups |
| Caregiver / Welfare coordinator | Works assigned caseload: check-ins, alerts, visits, follow-up |
| Elderly person | Submits own check-in, views own history, requests help |
| Authorised family member | Submits check-in for a linked household, views that history |
| System (scanner) | Time-triggered actor that creates missed records and escalations |

## 2. Use-case diagram (UML-style)

```
                    ┌──────────────────────────────────────────────┐
                    │     Elderly Household Welfare Check-in       │
                    │                   System                     │
                    │                                              │
  Administrator ────┼── UC01 Manage user accounts                  │
                    │── UC02 Register / update elderly profile     │
                    │── UC03 Assign caregivers                     │
                    │── UC04 Configure schedules & settings        │
                    │── UC05 View audit log and reports            │
                    │── UC06 Download database backup              │
                    │                                              │
  Caregiver ────────┼── UC07 View assigned households              │
                    │── UC08 Record check-in (for a household)     │
                    │── UC09 Acknowledge alert                     │
                    │── UC10 Record visit                          │
                    │── UC11 Record follow-up and close case       │
                    │── UC12 Review risk explanation               │
                    │                                              │
  Elderly ──────────┼── UC13 Submit own check-in                   │
                    │── UC14 Request assistance                    │
                    │── UC15 View own check-in history             │
                    │                                              │
  Family ───────────┼── UC13 (for linked household)                │
                    │── UC14, UC15 (for linked household)          │
                    │                                              │
  System ───────────┼── UC16 Detect missed check-in                │
                    │── UC17 Escalate unacknowledged alert         │
                    │── UC18 Compute review priority               │
                    └──────────────────────────────────────────────┘

  Include:  UC08/UC13 include UC-AUTH (login)
  Extend:   UC14 extends UC13 when “I need help” is selected
  Extend:   UC11 extends UC09 when closing
```

## 3. Use-case descriptions

### UC01 Manage user accounts

- **Actor:** Administrator
- **Precondition:** Admin is authenticated.
- **Main flow:** Admin creates a user, chooses a role, sets a temporary password. The password is hashed before storage. Admin may deactivate a user.
- **Postcondition:** Row in `users`; audit log entry.

### UC02 Register / update elderly profile

- **Precondition:** Admin authenticated; consent obtained from the person or lawful representative.
- **Main flow:** Admin enters identity, contacts, living arrangement, emergency contacts, ticks consent. Profile becomes eligible for schedules only if consent is true.
- **Alternative:** Edit existing profile; previous values remain in audit notes.

### UC03 Assign caregivers

- **Main flow:** Admin selects household and caregiver, optionally marks primary. Previous primary is unset if a new primary is chosen.

### UC07 View assigned households

- **Actor:** Caregiver
- **Main flow:** List shows only households linked in `caregiver_assignments` with `is_active = 1`, each with today’s status badge.

### UC13 Submit own check-in

- **Actor:** Elderly person
- **Precondition:** Linked `elderly_profiles.user_id`; profile active; consent given.
- **Main flow:** User opens the large-button page, selects mood (Good / Okay / Not well), optionally writes a note, submits. Record status `completed`.
- **Extension UC14:** If “I need help now” is used, create `alert_type = assistance`, priority `high` or `critical`, notify caregivers immediately.
- **Postcondition:** Confirmation text does **not** say “you are safe”.

### UC16 Detect missed check-in

- **Actor:** System
- **Trigger:** Periodic scan.
- **Main flow:** For each active schedule whose due instant has passed, if no completed record exists for that `due_at`, insert `status = missed` and an overdue alert. If a row already exists for that `due_at`, do nothing (idempotent).

### UC11 Record follow-up and close case

- **Precondition:** Alert is acknowledged (or the same form acknowledges it).
- **Main flow:** Caregiver records action type, notes, and outcome (`contacted`, `visited`, `no_answer`, `referred`, `false_alert`, `other`).
- **Business rule:** Status `resolved` is allowed only when a follow-up exists **or** outcome is `false_alert` with a non-empty reason.

### UC18 Compute review priority

- **Actor:** System, invoked when an alert is created or when a coordinator opens the priority list.
- **Main flow:** Rule engine returns score, label, and bullet-list reasons. Result is stored on the alert. Caregiver may disagree and still close as false alert.

## 4. Brief use-case vs test mapping

| Use case | Test |
| --- | --- |
| UC01 / login | `test_login_success`, `test_login_rejects_bad_password` |
| Caregiver isolation | `test_caregiver_cannot_view_unassigned_profile` |
| UC13 | `test_elderly_can_submit_checkin` |
| UC16 | `test_missed_checkin_creates_alert` |
| UC11 | `test_alert_cannot_resolve_without_followup` |
