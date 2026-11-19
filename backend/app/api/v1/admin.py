"""Admin dashboard aggregation endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select

from app.api.v1.deps import AdminOnly
from app.config import settings
from app.database import SessionLocal
from app.logging import setup_logging
from app.models.announcement import Announcement
from app.models.audit_log import AuditLog
from app.models.category import Category
from app.models.notification import Notification
from app.models.order import Order
from app.models.plan import Plan
from app.models.provisioning import ProvisioningJob
from app.models.service import Service
from app.models.ticket import Ticket
from app.models.user import User

logger = setup_logging() if False else __import__("logging").getLogger("hosting.api.admin")

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/overview")
def admin_overview(current_user=Depends(AdminOnly)):
    db = SessionLocal()
    try:
        return {
            "total_customers": db.query(User).filter_by(role="customer").count(),
            "total_staff": db.query(User).filter(User.role.in_(("staff", "admin"))).count(),
            "active_services": db.query(Service).filter_by(status="active").count(),
            "pending_orders": db.query(Order).filter_by(status="pending").count(),
            "total_orders": db.query(Order).count(),
            "open_tickets": db.query(Ticket).filter_by(status="open").count(),
            "total_tickets": db.query(Ticket).count(),
            "failed_provisioning": db.query(ProvisioningJob).filter_by(status="failed").count(),
            "plans": db.query(Plan).count(),
            "categories": db.query(Category).count(),
        }
    finally:
        db.close()


@router.get("/stats")
def admin_stats(current_user=Depends(AdminOnly)):
    db = SessionLocal()
    try:
        services_by_status = db.query(Service.status, func.count(Service.id)).group_by(Service.status).all()
        orders_by_status = db.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
        tickets_by_status = db.query(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status).all()
        users_by_role = db.query(User.role, func.count(User.id)).group_by(User.role).all()
        return {
            "services_by_status": [{"status": s, "count": c} for s, c in services_by_status],
            "orders_by_status": [{"status": s, "count": c} for s, c in orders_by_status],
            "tickets_by_status": [{"status": s, "count": c} for s, c in tickets_by_status],
            "users_by_role": [{"role": r, "count": c} for r, c in users_by_role],
        }
    finally:
        db.close()


@router.get("/recent-activities")
def recent_activities(current_user=Depends(AdminOnly), limit: int = Query(20, ge=1, le=100)):
    db = SessionLocal()
    try:
        rows = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
        return [
            {
                "id": r.id,
                "user_id": r.user_id,
                "action": r.action,
                "resource_type": r.resource_type,
                "resource_id": r.resource_id,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]
    finally:
        db.close()
