# User Manual

**System:** AI-Powered Elderly Household Welfare Check-in System  
**Audience:** Demonstrators, examiners, and hypothetical community users  
**Important:** This is a student prototype. It does not call emergency services.

---

## 1. Signing in

1. Open the application URL.
2. Enter your username and password.
3. Choose **Sign in**.

If your account is deactivated, you will see an error. Ask an administrator.

To sign out, use **Sign out** in the top bar.

---

## 2. Administrator

### 2.1 Dashboard

The admin home page shows counts: registered people, today’s completed check-ins, overdue check-ins, unacknowledged alerts, high-priority reviews, recent visits, and unresolved follow-ups.

### 2.2 Create a user

**Users → Add user**

- Choose a role: Administrator, Caregiver, Elderly person, or Family member.
- Give a unique username and email.
- Set a temporary password and tell the person to keep it private.

### 2.3 Register an elderly household

**Households → Add household**

Complete name, contacts, living arrangement, and emergency contacts.  
You **must** tick **Consent has been given** before the record can be used for scheduling. This is a prototype consent flag, not a legal form.

Optionally link a login user (the elderly person) on the same form.

### 2.4 Assign a caregiver

Open the household profile → **Assign caregiver**. Mark one assignment as **Primary**. The primary caregiver receives overdue alerts first.

### 2.5 Link a family member

On the profile, **Link family account**. That user can submit check-ins for that household only.

### 2.6 Schedule a check-in

On the profile, **Schedule**.

- Frequency: daily or weekly.
- Window start and end (for example 08:00–11:00).
- Days of week.
- Grace minutes (default 60). After the window plus grace, a missed check-in is raised.

### 2.7 Settings

- Escalation hours (when an unacknowledged alert is escalated).
- Organisation name (shown in the header).
- **Run missed-check scan now** — useful in a viva if the due time has already passed.
- **Download backup** — copies the SQLite file.

### 2.8 Audit log

Shows who created profiles, changed assignments, submitted check-ins, and closed alerts.

---

## 3. Caregiver / welfare coordinator

### 3.1 Your caseload

You only see households assigned to you. Status words:

| Status | Meaning |
| --- | --- |
| Check-in received | Someone submitted a check-in today. This is **not** a medical all-clear. |
| Awaiting | The window is still open. |
| Overdue | The window and grace period passed with no check-in. |
| Follow-up | An alert is still open or acknowledged. |

### 3.2 Record a check-in on someone’s behalf

Open the household → **Record check-in**. Use this after a phone call. Method is stored as `caregiver`.

### 3.3 Alerts

**Alerts** lists open, acknowledged, and escalated items.

1. Open the alert and read **Why this was flagged**.
2. **Acknowledge** so the team knows you have seen it.
3. Contact the person or visit, then **Save follow-up** with an outcome.
4. Only then **Close case**, or mark **False alert** with a reason if the miss was a known error (for example the person was in hospital and already known).

If you ignore an alert, it escalates after the configured hours.

### 3.4 Visits

**Visits → Record visit**. Choose home / phone / community, time, duration, and observations.

---

## 4. Elderly person

1. After login you see today’s window and a large check-in form.
2. Choose how you feel: Good, Okay, or Not well.
3. Optionally type a short note.
4. Press **Send today’s check-in**.

**I need help now** tells your caregiver through the app. It does **not** call an ambulance. If you have an emergency, use your local emergency number.

---

## 5. Family member

You see the household you are linked to. You may submit a check-in (for example after a morning call) and view history. You cannot see other families’ records.

---

## 6. Reports

Caregivers and admins can filter check-ins, alerts, visits, and follow-up outcomes by date. Charts summarise the selected period.

---

## 7. Correcting mistakes

- Wrong check-in note: a caregiver can add a follow-up explaining the correction. History rows are not silently deleted.
- False overdue alert: mark **False alert** and write why.
- Wrong profile data: admin edits the profile; the change is audit-logged.

---

## 8. Privacy reminders

- Do not share passwords.
- Do not screenshot records onto public social media.
- Demonstration names in this project are fictitious.
