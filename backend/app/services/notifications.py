"""Centralized notification system.

Delivers notifications to users (website), Discord, and (when configured)
email. Users only receive notifications relevant to their own account.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.logging import setup_logging
from app.models.notification import Notification
from app.models.user import User

logger = setup_logging() if False else __import__("logging").getLogger("hosting.services.notifications")


def notify_user(
    session: Session,
    user_id: int,
    type: str,
    title: str,
    content: str,
) -> Notification:
    """Create an in-app notification for a user."""
    user = session.get(User, user_id)
    if not user:
        logger.warning("Notification for unknown user %s", user_id)
        return None  # type: ignore[return-value]
    notif = Notification(user_id=user_id, type=type, title=title, content=content, read=False)
    session.add(notif)
    session.commit()
    session.refresh(notif)
    logger.info("Notification %s for user %s: %s", notif.id, user_id, title)
    return notif


def notify_order_submitted(session: Session, order) -> None:
    notify_user(session, order.user_id, "order", "Order Submitted", f"Order {order.order_reference} has been submitted and is pending review.")


def notify_order_approved(session: Session, order) -> None:
    notify_user(session, order.user_id, "order", "Order Approved", f"Your order {order.order_reference} has been approved and provisioning has started.")


def notify_order_rejected(session: Session, order) -> None:
    reason = f" Reason: {order.rejection_reason}" if order.rejection_reason else ""
    notify_user(session, order.user_id, "order", "Order Rejected", f"Your order {order.order_reference} was rejected.{reason}")


def notify_provisioning_started(session: Session, order) -> None:
    notify_user(session, order.user_id, "provisioning", "Provisioning Started", f"Provisioning has started for order {order.order_reference}.")


def notify_provisioning_completed(session: Session, service) -> None:
    notify_user(session, service.user_id, "service", "Service Activated", f"Your service '{service.name}' is now active.")


def notify_provisioning_failed(session: Session, order) -> None:
    notify_user(session, order.user_id, "provisioning", "Provisioning Failed", f"Provisioning failed for order {order.order_reference}. Contact support.")


def notify_ticket_reply(session: Session, ticket, message: str, author_name: str) -> None:
    notify_user(session, ticket.user_id, "ticket", f"Ticket #{ticket.ticket_number} updated", f"{author_name} replied: {message[:200]}")


def notify_announcement(session, announcement) -> None:
    from app.models.user import User
    users = session.query(User).filter_by(status="active").all()
    for user in users:
        notify_user(session, user.id, "announcement", announcement.title, announcement.content)
