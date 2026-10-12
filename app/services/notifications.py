from app import db
from app.models import Notification


def notify(user_id, title, message, link=None):
    if not user_id:
        return None
    n = Notification(user_id=user_id, title=title, message=message, link=link)
    db.session.add(n)
    db.session.commit()
    return n


def notify_many(user_ids, title, message, link=None):
    for uid in {u for u in user_ids if u}:
        db.session.add(
            Notification(user_id=uid, title=title, message=message, link=link)
        )
    db.session.commit()
