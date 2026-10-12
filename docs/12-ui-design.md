# User Interface Design and Wireframes

## 1. Design goals

- Readable on a phone and on a desktop.
- Colour is never the only status cue (text labels always accompany badges).
- Elderly-facing pages use large type (base 1.2rem+) and one primary action.
- Caregiver pages emphasise today’s work: overdue, unacknowledged, follow-up.
- Admin pages emphasise registers, assignments, settings, and audit.
- A persistent disclaimer: this prototype is not emergency services.

## 2. Visual language

| Token | Value | Use |
| --- | --- | --- |
| Ink | `#1b2b28` | Body text |
| Teal | `#1f6f6a` | Primary actions, nav |
| Teal dark | `#0f3f3c` | Header |
| Sand | `#f3eee4` | Page background |
| Paper | `#fffdf8` | Cards |
| Sage | `#3e7a55` | Check-in received / resolved |
| Amber | `#b5811a` | Awaiting |
| Coral | `#b54a3c` | Overdue / critical |
| Slate | `#5c6560` | Secondary text |

Type: **Source Serif 4** for the product name, **Source Sans 3** for UI. Both are free Google fonts with good readability.

## 3. Page inventory

| Page | Route | Roles |
| --- | --- | --- |
| Login | `/auth/login` | Public |
| Register family (pending) | `/auth/register` | Public |
| Admin dashboard | `/` | Admin |
| Caregiver dashboard | `/` | Caregiver |
| Elderly home / check-in | `/` | Elderly, family |
| Household list | `/elderly/` | Admin, caregiver |
| Household form | `/elderly/new`, `/elderly/<id>/edit` | Admin |
| Household profile | `/elderly/<id>` | Admin, assigned caregiver, linked family |
| Users | `/admin/users` | Admin |
| Assign caregiver | `/elderly/<id>/assign` | Admin |
| Schedules | `/elderly/<id>/schedule` | Admin, caregiver |
| Submit check-in | `/checkins/submit/<elderly_id>` | Elderly, family, caregiver |
| Check-in history | `/elderly/<id>/history` | Authorised |
| Alerts | `/alerts/` | Admin, caregiver |
| Alert detail | `/alerts/<id>` | Admin, assigned caregiver |
| Visits | `/visits/` | Admin, caregiver |
| Reports | `/reports/` | Admin, caregiver |
| Audit log | `/admin/audit` | Admin |
| Settings | `/admin/settings` | Admin |
| Experimental ML | `/admin/ml-demo` | Admin |
| Notifications | `/notifications` | All logged-in |

## 4. Wireframes (text layout)

### Login

```
+--------------------------------------------------+
|  [leaf] Household Welfare Check-in               |
|  Academic prototype — not emergency services     |
|                                                  |
|  Username                                        |
|  Password                                        |
|  [  Sign in  ]                                   |
|  Family member? Request an account               |
+--------------------------------------------------+
```

### Caregiver dashboard

```
+------+-------------------------------------------+
| Nav  | Good afternoon, Amina                     |
| Home | [6 households] [2 overdue] [1 unacked]    |
| People|                                          |
| Alerts| Today                                      |
| Visits| - R. Nambi  OVERDUE  11h  Review          |
| Reports| - M. Okello AWAITING window 08–11         |
|      | - J. Adeyemi CHECK-IN RECEIVED             |
+------+-------------------------------------------+
```

### Elderly check-in (large targets)

```
+----------------------------------+
| Hello, Margaret                  |
| Today's check-in window          |
| 08:00 – 11:00                    |
|                                  |
| How are you feeling?             |
| [ Good ] [ Okay ] [ Not well ]   |
|                                  |
| Notes (optional)                 |
|                                  |
| [     Send today's check-in    ] |
| [  I need help now ]             |
|                                  |
| This does not call an ambulance. |
+----------------------------------+
```

### Alert detail

```
+----------------------------------+
| Overdue check-in — J. Kato       |
| Priority: HIGH (score 58)        |
| Why this was flagged:            |
|  • Overdue by 11 hours           |
|  • 2 missed check-ins in 7 days  |
|  • Last visit 9 days ago         |
|                                  |
| This is a review priority, not   |
| a medical diagnosis.             |
|                                  |
| [ Acknowledge ]                  |
| Follow-up outcome: [visited ▼]   |
| Notes:                           |
| [ Save follow-up ] [ Close case ]|
+----------------------------------+
```

## 5. Accessibility notes

- Every input has a visible `<label>`.
- Badge text includes the word (Overdue, Awaiting), not only a colour disc.
- Focus rings are visible on buttons and links.
- The elderly “I need help now” button is a separate form so it cannot be submitted by accident together with a routine mood.
- Minimum tap size on primary elderly actions is ~48px height.
