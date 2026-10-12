# AI-Powered Elderly Household Welfare Check-in System

Year 2, Semester 1 Computer Science **academic prototype**.

A web application that helps caregivers and family members record scheduled welfare check-ins, detect missed check-ins, rank cases for human review with a transparent rule engine, and document visits and follow-up actions.

**This is not emergency services, not a medical device, and not continuous monitoring.**  
A submitted check-in means someone made contact. It does not mean the person is medically well.

All demonstration people and events are **synthetic / fictitious**.

---

## What is implemented

| Module | Status |
| --- | --- |
| Authentication, roles, password hashing, CSRF | Implemented |
| Elderly household register, consent flag, caregiver assignment, family links | Implemented |
| Daily/weekly schedules and check-in submission | Implemented |
| Missed-check scanner and in-app alerts | Implemented |
| Escalation of unacknowledged alerts | Implemented |
| Rule-based review priority with visible reasons | Implemented |
| Visits, follow-up, case closure rules | Implemented |
| Dashboards, Chart.js reports, audit log, SQLite backup | Implemented |
| Isolation Forest comparison | Experimental, synthetic data only — not used for live alerts |

## Technology

HTML5, CSS3, JavaScript, Bootstrap 5, Python/Flask, SQLite, Flask-Login, Flask-WTF, pandas/scikit-learn (experimental page), Chart.js.

The stack matches the project brief. It was not replaced.

## Folder structure

```
app/                 Flask application (models, blueprints, templates, static)
config.py            Configuration
database/            SQL schema (SQLite + MySQL-oriented)
docs/                Academic write-up (proposal through future work)
scripts/             Seed wrapper
tests/               pytest cases
run.py               Start the server or initialise the database
requirements.txt
```

Academic documents (start here for the report):

1. `docs/01-project-proposal.md`
2. `docs/02-background-problem-statement.md`
3. `docs/03-objectives.md`
4. `docs/04-scope-limitations.md`
5. `docs/05-requirements.md`
6. `docs/06-feasibility-study.md`
7. `docs/07-system-architecture.md`
8. `docs/08-use-cases.md`
9. `docs/09-data-flow.md`
10. `docs/10-database-design.md`
11. `docs/11-database-schema.md`
12. `docs/12-ui-design.md`
13. Source code in `app/`
14. `docs/14-installation.md`
15. `docs/15-sample-data.md`
16. `docs/16-test-cases.md`
17. `docs/17-ai-component.md`
18. `docs/18-user-manual.md`
19. `docs/19-final-report-structure.md`
20. `docs/20-future-improvements.md`

## Quick start

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py --init              # SQLite file + synthetic demo data
python run.py                     # http://127.0.0.1:5000
```

| Username | Password | Role |
| --- | --- | --- |
| admin | Admin@123 | Administrator |
| amina | Care@123 | Caregiver |
| david | Care@123 | Caregiver |
| margaret | Elder@123 | Elderly person |
| john | Elder@123 | Elderly person |
| grace.family | Family@123 | Family member |

```bash
pytest -q
```

## How the “AI” works

Live alerts use **documented rules** (hours overdue, recent misses, consecutive misses, days since visit, time-of-day deviation, explicit help request). Each alert shows why it was flagged.

An Isolation Forest page exists for teaching comparison on **synthetic** rows. It does not raise production alerts.

## Security notes for students

- Change `SECRET_KEY` in `.env` before any shared hosting.
- SQLite + Flask development server are for local demonstration.
- Never commit a database that contains real people’s data.
