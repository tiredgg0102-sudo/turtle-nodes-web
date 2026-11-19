"""User management endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.v1.deps import AdminOnly, CustomerOrStaff, StaffOnly, csrf_protect
from app.config import settings
from app.database import get_db
from app.exceptions import Conflict, Forbidden, NotFound, Unauthorized
from app.logging import setup_logging
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserRoleUpdate, UserStatusUpdate, UserUpdate
from app.security import hash_password
from app.dependencies import get_db_session

logger = setup_logging() if False else __import__("logging").getLogger("hosting.api.users")

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def list_users(
    current_user=Depends(AdminOnly),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    return db.query(User).offset(skip).limit(limit).all()


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, current_user=Depends(CustomerOrStaff), db: Session = Depends(get_db)):
    if not current_user.is_staff and current_user.id != user_id:
        raise Forbidden(message="Cannot view another user's profile")
    user = db.get(User, user_id)
    if not user:
        raise NotFound(message="User not found")
    return user


@router.patch("/me", response_model=UserOut)
def update_me(
    payload: UserUpdate,
    request: Request,
    current_user=Depends(CustomerOrStaff),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    user = db.get(User, current_user.id)
    if payload.email and payload.email != user.email and db.query(User).filter_by(email=payload.email).first():
        raise Conflict(message="Email already in use")
    if payload.username and payload.username != user.username and db.query(User).filter_by(username=payload.username).first():
        raise Conflict(message="Username already in use")
    if payload.email:
        user.email = payload.email
    if payload.username:
        user.username = payload.username
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}/role", response_model=UserOut)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    current_user=Depends(AdminOnly),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    user = db.get(User, user_id)
    if not user:
        raise NotFound(message="User not found")
    user.role = payload.role
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}/status", response_model=UserOut)
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    current_user=Depends(AdminOnly),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    user = db.get(User, user_id)
    if not user:
        raise NotFound(message="User not found")
    user.status = payload.status
    if payload.status == "suspended":
        from datetime import datetime

        user.suspended_at = datetime.utcnow()
        user.suspended_by = current_user.id
        user.suspension_reason = payload.reason
    else:
        user.suspended_at = None
        user.suspended_by = None
        user.suspension_reason = None
    db.commit()
    db.refresh(user)
    return user
