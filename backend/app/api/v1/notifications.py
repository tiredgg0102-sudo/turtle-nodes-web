"""User notification endpoints."""

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import CustomerOrStaff
from app.database import SessionLocal

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
def list_notifications(current_user=Depends(CustomerOrStaff), unread_only: bool = Query(False), limit: int = Query(50, ge=1, le=200)):
    db = SessionLocal()
    try:
        q = db.query(__import__("app.models.notification", fromlist=["Notification"]).Notification).filter_by(user_id=current_user.id)
        if unread_only:
            q = q.filter_by(read=False)
        rows = q.order_by(__import__("app.models.notification", fromlist=["Notification"]).Notification.created_at.desc()).limit(limit).all()
        return [
            {
                "id": r.id,
                "type": r.type,
                "title": r.title,
                "content": r.content,
                "read": r.read,
                "read_at": r.read_at.isoformat() if r.read_at else None,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]
    finally:
        db.close()


@router.post("/{notification_id}/read")
def mark_read(notification_id: int, current_user=Depends(CustomerOrStaff)):
    from app.models.notification import Notification
    db = SessionLocal()
    try:
        notif = db.query(Notification).filter_by(id=notification_id, user_id=current_user.id).first()
        if not notif:
            from app.exceptions import NotFound
            raise NotFound(message="Notification not found")
        notif.read = True
        from datetime import datetime, timezone
        notif.read_at = datetime.now(timezone.utc)
        db.commit()
        return {"success": True}
    finally:
        db.close()
