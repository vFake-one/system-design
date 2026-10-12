# Data-Flow Diagrams

Data-flow diagrams (Yourdon/DeMarco style) show **how data moves**, not the user-interface layout.

## 1. Context diagram (Level 0)

```
                  ┌────────────┐
                  │ Admin      │
                  └─────┬──────┘
           accounts,    │    reports, audit
           profiles     ▼
     ┌────────────────────────────────────────┐
     │                                        │
     │   AI-Powered Elderly Household         │
     │   Welfare Check-in System              │
     │                                        │
     └──────▲──────────▲──────────▲───────────┘
            │          │          │
   check-in │   alerts,│   visits │
   + help   │   lists  │   + FU   │
     ┌──────┴──┐  ┌────┴────┐ ┌───┴────────┐
     │ Elderly │  │ Family  │ │ Caregiver  │
     │ /Family │  │         │ │            │
     └─────────┘  └─────────┘ └────────────┘
```

External entities: Administrator, Caregiver, Elderly person, Family member.  
The scanner is **inside** the system boundary (it is not an outside organisation).

## 2. Level 1 DFD

Processes:

1. Authenticate user  
2. Maintain household and assignment data  
3. Record check-in  
4. Detect missed check-in  
5. Prioritise and raise alert  
6. Record visit and follow-up  
7. Produce dashboard and reports  
8. Write audit log  

Data stores:

- D1 Users  
- D2 Elderly profiles  
- D3 Assignments  
- D4 Schedules  
- D5 Check-in records  
- D6 Alerts  
- D7 Visits  
- D8 Follow-up actions  
- D9 Audit logs  
- D10 Notifications / settings  

**Selected flows**

- Elderly → P3 Record check-in → D5  
- D4 + D5 → P4 Detect missed → D5 (missed row) → P5 Raise alert → D6, D10  
- D5 + D7 → P5 Prioritise → D6 (score + reasons)  
- Caregiver → P6 Follow-up → D8 → updates D6 status  
- All mutating processes → P8 Audit → D9  
- P7 reads D2, D5, D6, D7, D8 for charts  

## 3. Level 2 (Process 5 — alert)

```
        hours overdue, missed count,
        days since visit, usual hour
                    │
                    ▼
            5.1 Apply rule score
                    │
                    ▼
            5.2 Create / update alert
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     5.3 Notify           5.4 If still
     assigned             unacked past
     caregiver            threshold →
                          escalate
```

## 4. What DFDs deliberately omit

Control flow (if/else) belongs in the architecture and use-case docs. DFDs do not show screens. Passwords never flow in clear text to a store — only a hash is written to D1.
