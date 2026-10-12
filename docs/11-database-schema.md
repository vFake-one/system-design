# Database Schema and SQL Scripts

Executable SQLite DDL lives in `database/schema.sql`.  
A MySQL-flavoured variant lives in `database/schema_mysql.sql`.  
The running prototype creates the same structure with SQLAlchemy (`app/models.py`) so students can inspect either the ORM or the SQL.

## Field catalogue

### users

| Field | Type | Notes |
| --- | --- | --- |
| id | INTEGER PK | Auto-increment |
| username | VARCHAR(80) UNIQUE NOT NULL | Login name |
| email | VARCHAR(120) UNIQUE NOT NULL | |
| password_hash | VARCHAR(255) NOT NULL | PBKDF2 hash |
| full_name | VARCHAR(120) NOT NULL | |
| phone | VARCHAR(30) | |
| role | VARCHAR(30) NOT NULL | admin / caregiver / elderly / family |
| is_active | BOOLEAN NOT NULL DEFAULT 1 | |
| created_at | DATETIME | |
| last_login | DATETIME | nullable |

### elderly_profiles

| Field | Type | Notes |
| --- | --- | --- |
| id | INTEGER PK | |
| user_id | INTEGER FK users.id | nullable |
| full_name | VARCHAR(120) NOT NULL | |
| date_of_birth | DATE | |
| gender | VARCHAR(20) | |
| address | VARCHAR(255) | |
| phone | VARCHAR(30) | |
| mobility_status | VARCHAR(50) | independent / assisted / limited |
| living_arrangement | VARCHAR(50) | lives_alone / with_family / other |
| emergency_contact_name | VARCHAR(120) | |
| emergency_contact_phone | VARCHAR(30) | |
| emergency_contact_relationship | VARCHAR(50) | |
| secondary_contact_name | VARCHAR(120) | Escalation target name |
| secondary_contact_phone | VARCHAR(30) | |
| welfare_notes | TEXT | Sensitive free text, not a diagnosis |
| consent_given | BOOLEAN NOT NULL DEFAULT 0 | |
| consent_date | DATETIME | |
| status | VARCHAR(30) DEFAULT 'active' | active / inactive |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### caregiver_assignments

| Field | Type | Notes |
| --- | --- | --- |
| id | INTEGER PK | |
| elderly_id | INTEGER FK elderly_profiles.id NOT NULL | |
| caregiver_id | INTEGER FK users.id NOT NULL | |
| is_primary | BOOLEAN DEFAULT 0 | |
| is_active | BOOLEAN DEFAULT 1 | |
| assigned_at | DATETIME | |
| assigned_by | INTEGER FK users.id | |
| notes | VARCHAR(255) | |

### family_links

| Field | Type | Notes |
| --- | --- | --- |
| id | INTEGER PK | |
| elderly_id | INTEGER FK NOT NULL | |
| family_user_id | INTEGER FK users.id NOT NULL | |
| relationship | VARCHAR(50) | |
| is_active | BOOLEAN DEFAULT 1 | |

### checkin_schedules

| Field | Type | Notes |
| --- | --- | --- |
| id | INTEGER PK | |
| elderly_id | INTEGER FK NOT NULL | |
| frequency | VARCHAR(20) NOT NULL | daily / weekly |
| window_start | TIME NOT NULL | |
| window_end | TIME NOT NULL | |
| days_of_week | VARCHAR(20) | e.g. `1,2,3,4,5,6,7` Monday=1 |
| grace_minutes | INTEGER DEFAULT 60 | |
| is_active | BOOLEAN DEFAULT 1 | |
| created_at | DATETIME | |

### checkin_records

| Field | Type | Notes |
| --- | --- | --- |
| id | INTEGER PK | |
| schedule_id | INTEGER FK | nullable |
| elderly_id | INTEGER FK NOT NULL | |
| submitted_by | INTEGER FK users.id | null if system-generated missed row |
| status | VARCHAR(20) NOT NULL | |
| method | VARCHAR(20) | self / family / caregiver / system |
| mood | VARCHAR(20) | |
| needs_assistance | BOOLEAN DEFAULT 0 | |
| notes | TEXT | |
| due_at | DATETIME NOT NULL | |
| submitted_at | DATETIME | |
| created_at | DATETIME | |

### alerts

| Field | Type | Notes |
| --- | --- | --- |
| id | INTEGER PK | |
| elderly_id | INTEGER FK NOT NULL | |
| checkin_record_id | INTEGER FK | |
| alert_type | VARCHAR(40) NOT NULL | overdue / pattern / assistance / escalation |
| priority | VARCHAR(20) NOT NULL | |
| status | VARCHAR(20) NOT NULL DEFAULT 'open' | |
| title | VARCHAR(200) NOT NULL | |
| reason | TEXT NOT NULL | Human-readable explanation |
| risk_score | INTEGER | 0–100 |
| is_ai_flagged | BOOLEAN DEFAULT 0 | True if rules or experimental model flagged a pattern |
| assigned_to | INTEGER FK users.id | |
| escalated_to | INTEGER FK users.id | |
| created_at | DATETIME | |
| acknowledged_at | DATETIME | |
| resolved_at | DATETIME | |

### alert_acknowledgements

| Field | Type | Notes |
| --- | --- | --- |
| id | INTEGER PK | |
| alert_id | INTEGER FK NOT NULL | |
| user_id | INTEGER FK NOT NULL | |
| notes | TEXT | |
| acknowledged_at | DATETIME | |

### caregiver_visits

| Field | Type | Notes |
| --- | --- | --- |
| id | INTEGER PK | |
| elderly_id | INTEGER FK NOT NULL | |
| caregiver_id | INTEGER FK NOT NULL | |
| visit_type | VARCHAR(30) | home / phone / community / other |
| visited_at | DATETIME NOT NULL | |
| duration_minutes | INTEGER | |
| observations | TEXT | |
| created_at | DATETIME | |

### followup_actions

| Field | Type | Notes |
| --- | --- | --- |
| id | INTEGER PK | |
| alert_id | INTEGER FK | |
| elderly_id | INTEGER FK NOT NULL | |
| caregiver_id | INTEGER FK NOT NULL | |
| action_type | VARCHAR(40) | phone / visit / message / referral / other |
| outcome | VARCHAR(40) | contacted / visited / no_answer / referred / false_alert / other |
| description | TEXT | |
| performed_at | DATETIME | |

### notifications, audit_logs, system_settings

See `database/schema.sql` for full DDL. Settings keys used by the prototype:

- `escalation_hours` (default 2)
- `scan_interval_minutes` (default 2)
- `organisation_name`

## Indexes

- `checkin_records (elderly_id, due_at)`
- `alerts (elderly_id, status)`
- `notifications (user_id, is_read)`
- `audit_logs (created_at)`
- `caregiver_assignments (caregiver_id, is_active)`
