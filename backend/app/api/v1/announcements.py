"""Announcement endpoints."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.v1.deps import AdminOnly, CustomerOrStaff, StaffOnly, csrf_protect
from app.config import settings
from app.database import get_db
from app.exceptions import NotFound
from app.logging import setup_logging
from app.models.announcement import Announcement
from app.models.user import User
from app.schemas.announcement import AnnouncementCreate, AnnouncementOut, AnnouncementUpdate
from app.services.notifications import notify_announcement

logger = setup_logging() if False else __import__("logging").getLogger("hosting.api.announcements")

router = APIRouter(prefix="/announcements", tags=["announcements"])


@router.get("", response_model=list[AnnouncementOut])
def list_announcements(
    current_user=Depends(CustomerOrStaff),
    db: Session = Depends(get_db),
    active_only: bool = Query(default=True),
):
    q = db.query(Announcement)
    if active_only:
        q = q.filter_by(active=True)
    return q.order_by(Announcement.created_at.desc()).all()


@router.post("", response_model=AnnouncementOut, status_code=201)
def create_announcement(
    payload: AnnouncementCreate,
    current_user=Depends(StaffOnly),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    announcement = Announcement(
        title=payload.title,
        content=payload.content,
        active=payload.active,
        published_by=current_user.id,
    )
    if payload.active:
        from datetime import datetime, timezone
        announcement.published_at = datetime.now(timezone.utc)
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    if payload.active:
        notify_announcement(db, announcement)
    return announcement


@router.patch("/{announcement_id}", response_model=AnnouncementOut)
def update_announcement(
    announcement_id: int,
    payload: AnnouncementUpdate,
    current_user=Depends(StaffOnly),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    announcement = db.get(Announcement, announcement_id)
    if not announcement:
        raise NotFound(message="Announcement not found")
    data = payload.model_dump(exclude_unset=True)
    if "active" in data and data["active"] and not announcement.active:
        from datetime import datetime, timezone
        announcement.published_at = datetime.now(timezone.utc)
    for key, value in data.items():
        setattr(announcement, key, value)
    db.commit()
    db.refresh(announcement)
    if announcement.active:
        notify_announcement(db, announcement)
    return announcement
