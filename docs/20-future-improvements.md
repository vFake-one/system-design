# Future Improvements

The following items are **not implemented** in the assessed prototype. They are listed so examiners can see that the student distinguishes a working demo from a production care system.

## 1. Communication

- SMS or email notifications (Twilio, Africa’s Talking, or SMTP).
- Missed-check phone tree that actually rings a duty number.
- Offline SMS short codes for feature phones.

## 2. Operations

- External cron scanner so detection continues when nobody has the website open.
- Per-household time zones.
- Multi-organisation tenancy.
- Automated encrypted backups off-machine.
- High-availability hosting with HTTPS and a real secret key vault.

## 3. Product

- Native apps with push notifications and optional large-widget check-in.
- Voice check-in for users who cannot use a form.
- Optional wearable *integration* (still not a medical device unless certified).
- Translation into local languages (for example Luganda) with professional review.

## 4. AI (only with ethics approval and real consented data)

- Supervised model compared with the rule baseline on held-out data.
- Calibration plots and false-alert cost analysis.
- Never replace the explanation bullets with a black-box score.

## 5. Governance

- Formal consent forms and data-retention policy.
- Role of “duty manager” outside office hours.
- Integration with existing social-work case systems.
- Independent accessibility audit (WCAG).

Until those exist, this repository remains an **academic prototype**.
