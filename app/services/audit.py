from flask_login import current_user

from app import db
from app.models import AuditLog
from app.utils import current_ip


def log_action(action, entity_type=None, entity_id=None, details=None, user_id=None):
    uid = user_id
    if uid is None and current_user.is_authenticated:
        uid = current_user.id
    row = AuditLog(
        user_id=uid,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=current_ip(),
    )
    db.session.add(row)
    db.session.commit()
    return row
