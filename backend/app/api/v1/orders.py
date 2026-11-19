"""Order management endpoints."""

import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.v1.deps import AdminOnly, CustomerOrStaff, StaffOnly, csrf_protect
from app.config import settings
from app.database import get_db
from app.exceptions import Conflict, Forbidden, NotFound
from app.logging import setup_logging
from app.models.order import Order
from app.models.plan import Plan
from app.models.user import User
from app.schemas.order import OrderCreate, OrderOut, OrderReview, OrderStatusUpdate
from app.services.notifications import notify_order_submitted
from app.dependencies import get_db_session

logger = setup_logging() if False else __import__("logging").getLogger("hosting.api.orders")

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderOut, status_code=201)
def create_order(
    payload: OrderCreate,
    request: Request,
    current_user=Depends(CustomerOrStaff),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    plan = db.get(Plan, payload.plan_id)
    if not plan or not plan.active or not plan.available:
        raise NotFound(message="Plan not available", code="plan_unavailable")
    if current_user.status != "active":
        raise Forbidden(message="Account is not active", code="account_inactive")

    order_reference = f"HO-{secrets.token_hex(6).upper()}"
    order = Order(
        order_reference=order_reference,
        user_id=current_user.id,
        plan_id=plan.id,
        status="pending",
        total_price=plan.price,
        currency=plan.currency,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    notify_order_submitted(db, order)
    logger.info("Order created", extra={"order_reference": order_reference, "user_id": current_user.id})
    return order


@router.get("", response_model=list[OrderOut])
def list_orders(
    current_user=Depends(CustomerOrStaff),
    db: Session = Depends(get_db),
    status: str | None = Query(default=None),
):
    q = db.query(Order)
    if not current_user.is_staff:
        q = q.filter_by(user_id=current_user.id)
    if status:
        q = q.filter_by(status=status)
    return q.order_by(Order.created_at.desc()).all()


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, current_user=Depends(CustomerOrStaff), db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise NotFound(message="Order not found")
    if not current_user.is_staff and order.user_id != current_user.id:
        raise Forbidden(message="Cannot view this order")
    return order


@router.patch("/{order_id}/review", response_model=OrderOut)
async def review_order(
    order_id: int,
    payload: OrderReview,
    current_user=Depends(StaffOnly),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    order = db.get(Order, order_id)
    if not order:
        raise NotFound(message="Order not found")
    if order.status not in ("pending", "under_review"):
        raise Conflict(message=f"Order cannot be {payload.action}d in current status", code="invalid_order_status")
    if payload.action == "approve":
        order.status = "approved"
        order.approved_by = current_user.id
        order.approved_at = datetime.now(timezone.utc)
        # Start provisioning in background.
        from app.services.provisioning import enqueue_order
        enqueue_order(order.id)
    else:
        order.status = "rejected"
        order.rejected_by = current_user.id
        order.rejected_at = datetime.now(timezone.utc)
        order.rejection_reason = payload.reason
    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}/status", response_model=OrderOut)
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    current_user=Depends(AdminOnly),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    order = db.get(Order, order_id)
    if not order:
        raise NotFound(message="Order not found")
    valid = {"pending", "under_review", "awaiting_payment", "approved", "provisioning", "active", "rejected", "cancelled", "failed"}
    if payload.status not in valid:
        raise Conflict(message="Invalid order status", code="invalid_status")
    order.status = payload.status
    db.commit()
    db.refresh(order)
    return order
