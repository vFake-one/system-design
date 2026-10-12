# Entity-Relationship Diagram and Database Design

## 1. Design principles

- Every table has a surrogate integer primary key (`id`).
- Foreign keys use `ON DELETE RESTRICT` for people and history (we deactivate; we do not cascade-delete welfare records).
- Passwords are never stored in plain text (`password_hash` only).
- Soft flags (`is_active`) preserve history.
- Check-in uniqueness for automatic missed rows: one record per `(elderly_id, due_at)` for scanner-created rows.
- SQLite types are used in the prototype. A MySQL-oriented script is also supplied.

## 2. Entity-Relationship Diagram

```mermaid
erDiagram
    USERS ||--o| ELDERLY_PROFILES : "may login as"
    USERS ||--o{ CAREGIVER_ASSIGNMENTS : "assigned as caregiver"
    USERS ||--o{ CAREGIVER_ASSIGNMENTS : "assigned by"
    ELDERLY_PROFILES ||--o{ CAREGIVER_ASSIGNMENTS : "has"
    ELDERLY_PROFILES ||--o{ CHECKIN_SCHEDULES : "follows"
    ELDERLY_PROFILES ||--o{ CHECKIN_RECORDS : "produces"
    CHECKIN_SCHEDULES ||--o{ CHECKIN_RECORDS : "due under"
    USERS ||--o{ CHECKIN_RECORDS : "submitted by"
    ELDERLY_PROFILES ||--o{ ALERTS : "raises"
    CHECKIN_RECORDS ||--o{ ALERTS : "may trigger"
    USERS ||--o{ ALERTS : "assigned to"
    ALERTS ||--o{ ALERT_ACKNOWLEDGEMENTS : "acked in"
    USERS ||--o{ ALERT_ACKNOWLEDGEMENTS : "acknowledges"
    ELDERLY_PROFILES ||--o{ CAREGIVER_VISITS : "receives"
    USERS ||--o{ CAREGIVER_VISITS : "conducts"
    ALERTS ||--o{ FOLLOWUP_ACTIONS : "closed by"
    ELDERLY_PROFILES ||--o{ FOLLOWUP_ACTIONS : "about"
    USERS ||--o{ FOLLOWUP_ACTIONS : "performs"
    USERS ||--o{ AUDIT_LOGS : "causes"
    USERS ||--o{ NOTIFICATIONS : "receives"
    ELDERLY_PROFILES ||--o{ FAMILY_LINKS : "linked to"
    USERS ||--o{ FAMILY_LINKS : "family user"

    USERS {
        int id PK
        string username UK
        string email UK
        string password_hash
        string full_name
        string phone
        string role
        bool is_active
        datetime created_at
        datetime last_login
    }

    ELDERLY_PROFILES {
        int id PK
        int user_id FK
        string full_name
        date date_of_birth
        string gender
        string address
        string phone
        string mobility_status
        string living_arrangement
        string emergency_contact_name
        string emergency_contact_phone
        string secondary_contact_name
        string secondary_contact_phone
        text welfare_notes
        bool consent_given
        datetime consent_date
        string status
        datetime created_at
    }

    CAREGIVER_ASSIGNMENTS {
        int id PK
        int elderly_id FK
        int caregiver_id FK
        bool is_primary
        bool is_active
        datetime assigned_at
        int assigned_by FK
    }

    FAMILY_LINKS {
        int id PK
        int elderly_id FK
        int family_user_id FK
        bool is_active
    }

    CHECKIN_SCHEDULES {
        int id PK
        int elderly_id FK
        string frequency
        time window_start
        time window_end
        string days_of_week
        int grace_minutes
        bool is_active
    }

    CHECKIN_RECORDS {
        int id PK
        int schedule_id FK
        int elderly_id FK
        int submitted_by FK
        string status
        string method
        string mood
        bool needs_assistance
        text notes
        datetime due_at
        datetime submitted_at
    }

    ALERTS {
        int id PK
        int elderly_id FK
        int checkin_record_id FK
        string alert_type
        string priority
        string status
        string title
        text reason
        int risk_score
        bool is_ai_flagged
        int assigned_to FK
        int escalated_to FK
        datetime created_at
        datetime acknowledged_at
        datetime resolved_at
    }

    ALERT_ACKNOWLEDGEMENTS {
        int id PK
        int alert_id FK
        int user_id FK
        text notes
        datetime acknowledged_at
    }

    CAREGIVER_VISITS {
        int id PK
        int elderly_id FK
        int caregiver_id FK
        string visit_type
        datetime visited_at
        int duration_minutes
        text observations
    }

    FOLLOWUP_ACTIONS {
        int id PK
        int alert_id FK
        int elderly_id FK
        int caregiver_id FK
        string action_type
        string outcome
        text description
        datetime performed_at
    }

    NOTIFICATIONS {
        int id PK
        int user_id FK
        string title
        text message
        string link
        bool is_read
        datetime created_at
    }

    AUDIT_LOGS {
        int id PK
        int user_id FK
        string action
        string entity_type
        int entity_id
        text details
        string ip_address
        datetime created_at
    }

    SYSTEM_SETTINGS {
        int id PK
        string key UK
        string value
        string description
    }
```

## 3. How the tables relate (plain language)

1. **users** holds every login account and its role.
2. **elderly_profiles** holds the household welfare record. It *may* point at a user who logs in as the elderly person.
3. **family_links** connects a `family` user to one or more profiles they are allowed to check in for.
4. **caregiver_assignments** is the many-to-many link between caregivers and households. `is_primary` marks who receives the first alert.
5. **checkin_schedules** says when a check-in is expected.
6. **checkin_records** says what actually happened (completed, missed, completed_late).
7. **alerts** are raised from missed records, assistance requests, or pattern flags.
8. **alert_acknowledgements** is the history of who saw an alert.
9. **caregiver_visits** are physical or phone visits, with or without an alert.
10. **followup_actions** are the work that allows an alert to be closed.
11. **notifications** are in-app messages.
12. **audit_logs** record security-relevant actions.
13. **system_settings** stores escalation hours and similar configuration.

## 4. Constraints and validation

| Table | Constraint |
| --- | --- |
| users | `username` unique, `email` unique, `role` in (`admin`,`caregiver`,`elderly`,`family`), password_hash not null |
| elderly_profiles | `full_name` not null; active profiles should have `consent_given = 1` |
| caregiver_assignments | unique active pair (`elderly_id`,`caregiver_id`); application enforces a single primary |
| checkin_schedules | `window_end` after `window_start`; `frequency` in (`daily`,`weekly`); `grace_minutes` >= 0 |
| checkin_records | `status` in (`completed`,`missed`,`completed_late`,`cancelled`); `mood` in (`good`,`okay`,`unwell`, null) |
| alerts | `priority` in (`low`,`medium`,`high`,`critical`); `status` in (`open`,`acknowledged`,`escalated`,`resolved`,`false_alert`) |
| followup_actions | `outcome` not empty when used to close an alert |

Application-level rules (harder in SQLite CHECK alone):

- A caregiver may only read assigned profiles.
- An alert cannot move to `resolved` without a follow-up row, unless status is `false_alert` with a reason.
- Scanner will not insert a second missed record for the same `elderly_id` + `due_at`.

## 5. Password storage

Werkzeug `generate_password_hash(password, method="pbkdf2:sha256")` stores a salt and iteration count in `users.password_hash`. Verification uses `check_password_hash`. Plain passwords never appear in logs.

## 6. Privacy

- List queries for caregivers always join through `caregiver_assignments`.
- Welfare notes and emergency numbers are treated as sensitive: they appear only on authorised profile pages.
- Backup download is admin-only and is audit-logged.
