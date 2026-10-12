# System Architecture

## 1. Architectural style

The prototype uses a **three-tier web architecture**:

1. **Presentation tier** — HTML templates, Bootstrap 5, a small amount of JavaScript, Chart.js.
2. **Application tier** — Flask routes (blueprints), forms, business rules, the missed-check scanner, and the rule-based prioritisation engine.
3. **Data tier** — SQLite via SQLAlchemy (the same schema can be pointed at MySQL later).

This is a **monolithic** Flask application. Microservices would be unnecessary for a Year 2 prototype and harder to host.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Client (browser / phone)                    │
│         HTML5 · CSS3 · JavaScript · Bootstrap 5 · Chart.js      │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTPS (production) / HTTP (demo)
┌──────────────────────────────▼──────────────────────────────────┐
│                     Flask application (Python)                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │  Auth &  │ │Household │ │ Check-in │ │  Alerts  │            │
│  │   RBAC   │ │  & users │ │ & scan   │ │ & visits │            │
│  └──────────┘ └──────────┘ └────┬─────┘ └────▲─────┘            │
│                                 │            │                  │
│                    ┌────────────▼────────────┴─────┐            │
│                    │ Rule-based risk engine        │            │
│                    │ (optional ML comparison)      │            │
│                    └───────────────────────────────┘            │
│  Cross-cutting: CSRF, validation, audit log, settings           │
└──────────────────────────────┬──────────────────────────────────┘
                               │ SQLAlchemy (parameterised SQL)
┌──────────────────────────────▼──────────────────────────────────┐
│              SQLite file  (instance/welfare.db)                 │
│     users · profiles · schedules · records · alerts · visits    │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Component responsibilities

| Component | Responsibility |
| --- | --- |
| `app/__init__.py` | Application factory, login manager, database init |
| `app/models.py` | Tables and relationships |
| `app/forms.py` | WTForms with CSRF and validators |
| `app/decorators.py` | `@role_required(...)` |
| `app/services/scanner.py` | Missed-check detection and escalation |
| `app/services/risk_engine.py` | Rule-based score + explanation |
| `app/services/audit.py` | Write audit rows |
| `app/blueprints/*` | HTTP routes per module |
| `scripts/seed_demo_data.py` | Synthetic demonstration records |

## 3. Request flow (example: submit check-in)

1. Browser posts the form with a CSRF token.
2. Flask-Login confirms the session.
3. Role decorator allows `elderly`, `family`, or `caregiver`.
4. The view checks that the user is linked to that household.
5. A `checkin_records` row is inserted (`status = completed`).
6. An audit log row is written.
7. If “I need help” was ticked, an assistance alert and notification are created.
8. The user sees a confirmation page — **not** a statement that they are medically safe.

## 4. Missed-check and escalation flow

```
Schedule exists for today
        │
        ▼
Window end + grace passed?
        │ no → status Awaiting
        ▼ yes
Completed record for this due_at?
        │ yes → status Check-in received
        ▼ no
Create missed record (idempotent)
Create overdue alert + in-app notification
        │
        ▼
Acknowledged within escalation hours?
        │ yes → caregiver records follow-up
        ▼ no
Status = escalated; notify secondary / admin
        │
        ▼
Follow-up outcome documented → case may be closed
```

## 5. Deployment view (prototype vs later)

| Environment | How it runs |
| --- | --- |
| Student demo | `python run.py` binds `0.0.0.0:5000`, SQLite file, scanner on a timer inside the process |
| Future production | Gunicorn + HTTPS reverse proxy, MySQL, system cron calling a scan command, real backup job |

## 6. Why this architecture fits Year 2

- One language on the server (Python).
- One database file to copy for backup.
- Clear mapping from “module in the proposal” to “blueprint folder”.
- The AI piece is a **function**, not a separate opaque service, so it can be explained in a viva.
