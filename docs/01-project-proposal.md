# Project Proposal

## AI-Powered Elderly Household Welfare Check-in System

**Programme:** Bachelor of Science in Computer Science  
**Level:** Year 2, Semester 1  
**Project type:** Academic prototype (web-based information system)  
**Development stack:** HTML5, CSS3, JavaScript, Bootstrap 5, Python/Flask, SQLite, pandas, scikit-learn, Chart.js

---

### 1. Title

**AI-Powered Elderly Household Welfare Check-in System**

A web-based and mobile-friendly prototype that helps caregivers, family members, and community welfare coordinators monitor scheduled welfare check-ins for older people who live alone, detect missed check-ins, flag unusual patterns for human review, and record visits and follow-up actions.

---

### 2. Introduction

Many older people live independently. Independence is valuable, but it also means that illness, a fall, confusion, or a period of isolation can go unnoticed for hours or days. Community caregivers cannot visit every household every day. Family members who live far away often rely on informal phone calls, which are easy to miss and hard to audit.

This project proposes a practical information system, not a medical device. The system records who is expected to check in, whether that check-in happened, and what a caregiver did afterwards. A transparent rule-based engine (with an optional experimental machine-learning comparison) ranks overdue cases so coordinators can review the most concerning records first.

The prototype is designed to be understandable, affordable, and completable within an undergraduate semester. It uses beginner-friendly tools that a Year 2 Computer Science student can install, explain, and demonstrate.

---

### 3. Problem statement

Older adults who live alone may experience:

- sudden illness or injury without anyone present;
- missed daily routines that family would normally notice;
- loneliness or reduced contact over several days;
- delayed help because a neighbour or caregiver was not informed in time.

Existing approaches have gaps:

| Approach | Limitation |
| --- | --- |
| Informal phone calls | No shared record, easy to forget, no escalation |
| Wearable panic buttons | Costly, not always worn, do not capture routine welfare |
| Full telehealth platforms | Expensive, clinically oriented, heavy to implement as a student project |
| Paper visit logs | Slow, hard to search, no automatic missed-check detection |

Communities therefore need a **low-cost check-in and follow-up system** that:

1. stores elderly household and caregiver records;
2. schedules routine welfare checks;
3. detects missed check-ins automatically;
4. notifies assigned caregivers;
5. keeps an audit trail of alerts and actions.

The system must **not** claim to diagnose illness, confirm that a person is medically safe, or replace emergency services.

---

### 4. Proposed solution

The proposed solution is a role-based web application that runs in a browser on a computer or smartphone.

**Routine flow**

1. An administrator registers an elderly household (with documented consent) and assigns one or more caregivers.
2. A daily or weekly check-in window is configured (for example, 08:00–11:00).
3. The elderly person, a family member, or a caregiver submits a check-in during that window.
4. If the window closes with no check-in, the system marks the check-in as missed and creates an overdue alert.
5. The assigned caregiver is notified in-app, acknowledges the alert, records a visit or other follow-up, and closes the case only after an outcome is documented.
6. If the alert is not acknowledged within a configurable period, it is escalated to a secondary contact.

**AI assistance (limited and explained)**

The prototype first applies **documented rules** (hours overdue, recent missed check-ins, time since last visit, deviation from a person's usual check-in time). Each flagged case shows **why** it was flagged. An optional scikit-learn model may be compared on **synthetic demonstration data only**. The rule-based method is the working academic feature.

---

### 5. Aim and objectives

**Aim:** To design and develop a web-based, mobile-friendly system that monitors elderly household welfare check-ins, identifies missed check-ins and unusual activity patterns, and notifies designated caregivers when human review may be necessary.

**Specific objectives**

1. Register elderly people and store basic contact and welfare information.
2. Register caregivers, family contacts, and welfare coordinators.
3. Allow caregivers or elderly users to record routine welfare check-ins.
4. Schedule daily or weekly welfare checks.
5. Detect missed check-ins automatically.
6. Use a transparent rule-based method (and, if appropriate, a simple ML comparison on labelled demonstration data) to prioritise cases for review.
7. Generate alerts when check-ins are overdue or when potentially concerning patterns are detected.
8. Allow caregivers to record visits, follow-ups, and actions taken.
9. Provide a dashboard showing people who are safe-today, awaiting check-in, overdue, or requiring follow-up.
10. Maintain records and reports for accountability.

---

### 6. Expected beneficiaries

- Community welfare coordinators who need a shared, dated record of check-ins.
- Caregivers who are assigned a caseload and must know who is overdue.
- Family members who have been authorised to submit or view check-ins.
- Academic examiners, who can inspect requirements, schema, source code, tests, and limitations.

Elderly users benefit only if a real organisation later adopts a professionally hosted, consented, and legally reviewed system. This repository is a **student prototype**.

---

### 7. Methodology (overview)

The project follows an incremental (evolutionary prototype) approach:

1. Problem analysis, requirements, architecture, and database design.
2. Database, authentication, and role-based access.
3. Household and caregiver management.
4. Check-in scheduling, recording, and missed-check detection.
5. Alerts, escalation, visits, and follow-up.
6. Dashboard, reports, audit log, and privacy controls.
7. Rule-based risk prioritisation and optional ML comparison.
8. Testing, demonstration data, user manual, and evaluation.

Each stage produces working code that integrates with the previous stage.

---

### 8. Proposed technologies (and why they are kept)

The brief specified beginner-friendly technologies. They are appropriate for this project, so **the stack is not changed**.

| Layer | Technology | Reason |
| --- | --- | --- |
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 5 | Responsive pages without a heavy JavaScript framework |
| Backend | Python and Flask | Readable routing, easy to explain in a viva |
| Database | SQLite (prototype), schema compatible with MySQL | Zero-install local database; SQL file provided for migration |
| Charts | Chart.js | Simple dashboard charts in the browser |
| Data / AI | pandas, scikit-learn | Optional comparison only; rules remain the main feature |
| Auth | Flask-Login, Werkzeug password hashing | Standard, documented security for student projects |
| Forms | Flask-WTF | CSRF protection and validation |

A mobile-native app (Android/iOS) would exceed a Year 2 semester scope. A mobile-friendly website meets the objective with one codebase.

---

### 9. Ethical and safety statement

This academic prototype:

- is **not** a substitute for emergency services or continuous medical monitoring;
- does **not** claim that a submitted check-in means a person is medically well;
- does **not** present a risk score as a diagnosis or confirmed emergency;
- uses **synthetic demonstration records**, clearly labelled as such;
- requires a recorded consent flag before an elderly profile is treated as active;
- restricts personal records by role (caregivers see assigned households only).

If a user indicates that they need help, the system creates a high-priority in-app alert. It does **not** call an ambulance or send an SMS unless a later, professionally implemented integration is added.

---

### 10. Deliverables

1. Project proposal and requirements.
2. Architecture, use-case, data-flow, and ER diagrams.
3. Database schema and SQL scripts.
4. Working Flask application with role-based modules.
5. Installation instructions and synthetic demo data.
6. Test cases, AI explanation, user manual, and report structure.

---

### 11. Project organisation

Source code lives in `app/`. Academic writing lives in `docs/`. Database scripts live in `database/`. Tests live in `tests/`. Demonstration seeding is in `scripts/seed_demo_data.py` and is labelled **SYNTHETIC**.
