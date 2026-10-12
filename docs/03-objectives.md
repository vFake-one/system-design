# Main Objective and Specific Objectives

## Main objective

To design and develop a web-based and mobile-friendly system that monitors elderly household welfare, identifies missed check-ins and unusual activity patterns, and notifies designated caregivers when intervention may be necessary.

“Intervention” in this prototype means **human review** (a phone call, a visit, or another documented follow-up). It does not mean automatic medical treatment.

## Specific objectives

| No. | Objective | How the prototype meets it |
| --- | --- | --- |
| 1 | Register elderly people and store basic contact and welfare information | `elderly_profiles` table, admin/caregiver forms, consent flag |
| 2 | Register caregivers, family contacts, and welfare coordinators | `users` with roles `admin`, `caregiver`, `elderly`, `family` |
| 3 | Record routine welfare check-ins | Check-in form for elderly, family, and caregiver roles |
| 4 | Schedule daily or weekly welfare checks | `checkin_schedules` with window times and days of week |
| 5 | Detect missed check-ins automatically | Scanner runs on a short interval and when staff open the dashboard |
| 6 | Identify unusual patterns and prioritise review | Rule-based engine with an optional ML comparison on synthetic data |
| 7 | Generate alerts | `alerts` + in-app `notifications` |
| 8 | Record visits, follow-ups, and actions | `caregiver_visits`, `followup_actions` |
| 9 | Dashboard of safe / awaiting / overdue / follow-up | Role-specific dashboards with status badges |
| 10 | Records and reports | Date-filtered reports, Chart.js summaries, audit log |

## Success criteria (academic)

The project is considered successful if:

- a demonstrator can log in as each role and only see permitted pages;
- a missed check-in produces an overdue alert without manual data entry;
- an alert cannot be marked resolved until a follow-up outcome is saved;
- every flagged case shows a written reason;
- synthetic data is labelled as synthetic;
- tests cover login, authorisation, check-in, alert, and follow-up paths.
