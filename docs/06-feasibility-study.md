# Feasibility Study

A Year 2 project must be feasible in **technical**, **operational**, **economic**, **schedule**, and **ethical** terms.

## 1. Technical feasibility — feasible

| Question | Answer |
| --- | --- |
| Can the team install the stack? | Yes. Python, Flask, and SQLite are free and well documented. |
| Is missed-check detection possible without sensors? | Yes. It is a comparison of “expected due time” versus “completed record exists”. |
| Is “AI” possible without a real dataset? | Yes, as **rules**. ML is optional and only compared on synthetic rows. |
| Are there skills gaps? | HTML/CSS/JS, basic SQL, and Python functions are within Year 2. Flask blueprints are extra learning but standard. |

Risk: treating scikit-learn as the main feature. **Mitigation:** ship rules first; keep ML behind a clearly labelled experimental page.

## 2. Operational feasibility — feasible as a demo, not as a care service

Staff can learn the dashboard in one session. Elderly users can use a two-button check-in page.

The prototype is **not** operationally feasible as a real welfare service because it has no on-call roster, no SMS, and no hosting SLA. The report must say this.

## 3. Economic feasibility — feasible

All core tools are open source. Hardware is a student laptop. No paid API is required for the marked prototype. Optional future SMS would add cost (Twilio or a local gateway).

## 4. Schedule feasibility — feasible if incremental

A realistic student timetable:

| Week | Work |
| --- | --- |
| 1–2 | Proposal, requirements, ERD, architecture |
| 3 | Database + authentication |
| 4 | Households and assignments |
| 5 | Schedules and check-ins |
| 6 | Missed detection and alerts |
| 7 | Visits, follow-up, dashboard, reports |
| 8 | Rule-based AI, tests, manual, polish |

Trying to build a native app, SMS, and a trained clinical model in the same semester would **not** be feasible.

## 5. Ethical / legal feasibility — feasible with constraints

- Use synthetic names only in the repository.
- Store a consent flag.
- Do not scrape or invent “real” medical histories and then treat them as evidence.
- Show disclaimers.
- Allow correction of false alerts.

A live deployment would need data-protection advice (for example GDPR or local equivalent). That advice is outside the student project.

## 6. Alternative options considered

| Option | Why not chosen |
| --- | --- |
| Android-only app | Excludes family members on other devices; two codebases |
| Django | Excellent, but heavier for a first web project; Flask matches the brief |
| MongoDB | Poor fit for strongly related check-in/alert/visit records |
| Deep learning | No ethical dataset; unjustifiable complexity |
| WhatsApp bot | External API cost and complexity; not needed for the academic objective |

**Conclusion:** The proposed Flask + SQLite + rule-based system is feasible for Year 2 Semester 1. Broader AI, messaging, and clinical claims are not.
