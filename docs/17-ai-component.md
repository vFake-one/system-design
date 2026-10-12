# AI Component: Design, Implementation, and Evaluation

## 1. What “AI” means in this project

The brief asks for a simple AI or machine-learning model to identify unusual check-in patterns and prioritise cases. For a Year 2 prototype, and because **no ethically obtained real dataset is available**, the working feature is a **transparent rule-based engine**.

An optional scikit-learn Isolation Forest is included only as an **experimental comparison** on synthetic demonstration rows. It is not used as the authority for alerts in the default configuration.

This is assistive ranking, not diagnosis.

## 2. Features considered

| Feature | Why it matters | How it is computed |
| --- | --- | --- |
| Hours since last successful check-in | Long silence is the primary overdue signal | `now - last completed submitted_at` |
| Hours overdue relative to due_at | Distinguishes “a little late” from “a day late” | `now - due_at` if missed |
| Missed check-ins in last 7 days | Repeated misses are more concerning than one | Count `status in (missed, completed_late)` |
| Missed check-ins in last 14 days | Medium-term pattern | Same, 14-day window |
| Consecutive missed days | A streak is more urgent than scattered misses | Walk backwards from today |
| Days since last caregiver visit | No human contact for a long time | `now - last visit` |
| Deviation from usual check-in hour | If the person normally checks in at 09:00 and recent times jump to 21:00 | Absolute difference vs median hour of completed check-ins in last 28 days |
| Assistance flag | Explicit request overrides ranking | Immediate high/critical alert |

None of these features is a vital sign. They are operational contact features.

## 3. Rule-based baseline (the working method)

The engine returns a score from 0 to 100, a priority label, and a list of **plain-language reasons**.

```
score = 0
reasons = []

if hours_overdue >= 24:          score += 40; reason "Overdue by 24h+"
elif hours_overdue >= 6:         score += 25; reason "Overdue by 6h+"
elif hours_overdue >= 1:         score += 10; reason "Overdue by 1h+"

if missed_last_7d >= 3:          score += 25
elif missed_last_7d >= 2:        score += 15
elif missed_last_7d == 1:        score += 5

if consecutive_misses >= 3:      score += 15
elif consecutive_misses == 2:    score += 8

if days_since_visit >= 14:       score += 15
elif days_since_visit >= 7:      score += 8

if hour_deviation >= 6:          score += 10
elif hour_deviation >= 3:        score += 5

if needs_assistance:             score = max(score, 80); reason "Person requested help"

score = min(score, 100)

priority =
    critical if score >= 70
    high     if score >= 45
    medium   if score >= 25
    low      otherwise
```

**Labels shown to users**

- Do say: “This case is ranked high for review because the check-in is 26 hours overdue and two check-ins were missed in the last 7 days.”
- Do not say: “This person has had a medical emergency” or “This person is safe.”

## 4. Optional machine-learning comparison

If we had a large, consented, labelled dataset of “coordinator later confirmed a genuine welfare concern” versus “false alarm”, a supervised model (for example logistic regression) could be trained and compared with the rules using precision, recall, and F1.

**We do not have that dataset.** Inventing labels and then reporting F1 as if it were real-world evidence would be misleading.

Therefore:

1. Synthetic feature rows are generated in `app/services/ml_compare.py` and labelled **SYNTHETIC DEMONSTRATION DATA**.
2. An Isolation Forest (unsupervised novelty detection) is fitted on the “typical” synthetic cluster.
3. The experimental page shows how often the forest agrees with the rule engine on the demo set.
4. The result is **not** a performance claim about real households.

Why Isolation Forest? It is available in scikit-learn, needs no class labels, and is a reasonable teaching example of “is this row unusual compared with the majority?” It is a poor substitute for clinical judgement.

## 5. Integration with alerts

When the scanner creates an overdue alert, it calls `assess_risk(elderly_id)` and stores:

- `risk_score`
- `priority`
- `reason` (joined explanation bullets)
- `is_ai_flagged` if score >= 25 or assistance was requested

Caregivers can still mark `false_alert`. The human decision is the record of truth.

## 6. Evaluation (academic, not clinical)

| Criterion | Rule engine | Isolation Forest (synthetic only) |
| --- | --- | --- |
| Explainable to a caregiver | Yes — bullet reasons | Weak — anomaly score only |
| Works with small N | Yes | Unstable |
| Needs real labels | No | No (but then cannot measure true emergencies) |
| Risk of false authority | Low if wording is careful | Higher if presented as “the AI detected danger” |
| Used in production path | **Yes** | **No** (experimental page) |

**Honesty checks implemented in the UI**

- Disclaimer banner on dashboards and alert pages.
- Reason text always visible.
- “Check-in received today” is labelled as a **contact status**, not a health status.
- Seed data banner: synthetic demonstration records.

## 7. What would be needed for a real ML study (future work)

- Ethical approval and informed consent.
- A definition of the positive class that a welfare organisation actually uses.
- Time-based training/test split (no leaking future visits into past predictions).
- Comparison against the rule baseline on **held-out real data**.
- Calibration and a human override log.

Until those exist, the rule-based method is the correct academic main feature.
