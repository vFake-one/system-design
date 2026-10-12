# Background and Problem Statement

## 1. Background

Population ageing is a global trend. A growing number of older adults live in single-person households. Family members may work far from home. Community welfare programmes often rely on a small number of coordinators who cannot visit every household daily.

Welfare check-ins are a simple idea: at an agreed time, someone confirms that the older person has been heard from. In practice this is often done with informal phone calls or paper notebooks. Those methods fail when:

- the caller forgets;
- nobody records the outcome;
- a missed call is treated as “probably fine”;
- a new caregiver cannot see yesterday’s notes;
- there is no agreed time at which a missed check-in becomes an alert.

Digital systems can store the schedule, the outcome, and the follow-up. They cannot, by themselves, keep a person safe. They can only make missed contact visible to a human being who is responsible for the next action.

This project sits in that gap: **operational welfare monitoring**, not clinical monitoring. It records check-ins, visits, and alerts. It does not measure heart rate, detect falls from a camera, or issue a medical opinion.

## 2. Problem statement

Older people who live alone may experience illness, falls, injuries, loneliness, or other emergencies without receiving timely assistance. Caregivers and family members lack a shared, affordable, easy-to-use system that:

1. knows who should have checked in today;
2. notices when they did not;
3. tells the right caregiver;
4. escalates if nobody responds;
5. keeps a record of what was done.

Without such a system, delayed discovery of a missed routine is common, and accountability is weak.

## 3. Research / project questions

The project is a software-engineering exercise, not a clinical trial. The questions it answers are:

1. Can a Year 2 student implement a role-based check-in system with Flask and SQLite that enforces the alert-and-follow-up workflow?
2. Can missed check-ins be detected from schedule and timestamp data alone?
3. Can a transparent rule-based score help coordinators sort cases, and can that score be explained in plain language?
4. What must the system **refuse** to claim (medical safety, emergency dispatch, real-world training data) so that it remains honest as an academic prototype?

## 4. Significance

For a Computer Science student, the project practises:

- relational database design and foreign keys;
- authentication, authorisation, and audit logging;
- form validation and session security;
- scheduled/batch logic (missed-check detection);
- responsible use of “AI” as an assistive ranking tool;
- writing requirements, diagrams, tests, and a user manual.

For a hypothetical community user, the value would be a shared dashboard and an agreed escalation path. Real deployment would require hosting, legal review, consent processes, and a 24/7 response arrangement that this prototype does not provide.
