"""Bot-facing endpoints authenticated via BOT_API_KEY (no CSRF)."""

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.exceptions import Unauthorized, NotFound, Conflict
from app.logging import setup_logging
from app.models.order import Order
from app.models.user import User
from app.services.notifications import notify_order_approved, notify_order_rejected
from app.services.provisioning import enqueue_order

logger = setup_logging() if False else __import__("logging").getLogger("hosting.api.bot")

router = APIRouter(prefix="/bot", tags=["bot"])


def require_bot_key(x_bot_key: str | None = Header(default=None)) -> None:
    if not settings.BOT_API_KEY or x_bot_key != settings.BOT_API_KEY:
        raise Unauthorized(message="Invalid bot API key", code="invalid_bot_key")


@router.get("/orders/{order_reference}")
def bot_get_order(order_reference: str, db: Session = Depends(get_db), _=Depends(require_bot_key)):
    order = db.query(Order).filter_by(order_reference=order_reference).first()
    if not order:
        raise NotFound(message="Order not found")
    user = db.get(User, order.user_id)
    return {
        "order": order.to_dict(),
        "customer": {"id": user.id, "email": user.email, "username": user.username, "discord_id": user.discord_id} if user else None,
    }


@router.get("/orders")
def bot_list_orders(status: str | None = None, db: Session = Depends(get_db), _=Depends(require_bot_key)):
    q = db.query(Order)
    if status:
        q = q.filter_by(status=status)
    return [o.to_dict() for o in q.order_by(Order.created_at.desc()).limit(50).all()]


@router.post("/orders/{order_reference}/approve")
async def bot_approve(order_reference: str, db: Session = Depends(get_db), _=Depends(require_bot_key)):
    order = db.query(Order).filter_by(order_reference=order_reference).first()
    if not order:
        raise NotFound(message="Order not found")
    if order.status not in ("pending", "under_review"):
        raise Conflict(message="Order cannot be approved in current status")
    from datetime import datetime, timezone
    order.status = "approved"
    order.approved_at = datetime.now(timezone.utc)
    db.commit()
    enqueue_order(order.id)
    notify_order_approved(db, order)
    return {"success": True, "order": order.to_dict()}


@router.post("/orders/{order_reference}/reject")
def bot_reject(order_reference: str, reason: str = "", db: Session = Depends(get_db), _=Depends(require_bot_key)):
    order = db.query(Order).filter_by(order_reference=order_reference).first()
    if not order:
        raise NotFound(message="Order not found")
    if order.status not in ("pending", "under_review"):
        raise Conflict(message="Order cannot be rejected in current status")
    from datetime import datetime, timezone
    order.status = "rejected"
    order.rejected_at = datetime.now(timezone.utc)
    order.rejection_reason = reason
    db.commit()
    notify_order_rejected(db, order)
    return {"success": True, "order": order.to_dict()}


@router.get("/customers/{user_id}")
def bot_customer(user_id: int, db: Session = Depends(get_db), _=Depends(require_bot_key)):
    user = db.get(User, user_id)
    if not user:
        raise NotFound(message="Customer not found")
    return user.to_dict()


@router.get("/customers/by-discord/{discord_id}")
def bot_customer_by_discord(discord_id: str, db: Session = Depends(get_db), _=Depends(require_bot_key)):
    user = db.query(User).filter_by(discord_id=discord_id).first()
    if not user:
        raise NotFound(message="Customer not found")
    return user.to_dict()


@router.get("/services/{service_id}")
def bot_service(service_id: int, db: Session = Depends(get_db), _=Depends(require_bot_key)):
    from app.models.service import Service
    service = db.get(Service, service_id)
    if not service:
        raise NotFound(message="Service not found")
    return service.to_dict()
