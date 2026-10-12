from functools import wraps

from flask import abort
from flask_login import current_user


def role_required(*roles):
    """Allow only authenticated users whose role is in `roles`."""

    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            if current_user.role not in roles:
                abort(403)
            if not current_user.is_active:
                abort(403)
            return fn(*args, **kwargs)

        return wrapped

    return decorator
