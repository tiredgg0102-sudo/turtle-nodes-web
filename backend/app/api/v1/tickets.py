"""Support ticket endpoints."""

import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.v1.deps import AdminOnly, CustomerOrStaff, StaffOnly, csrf_protect
from app.config import settings
from app.database import get_db
from app.exceptions import Forbidden, NotFound
from app.logging import setup_logging
from app.models.ticket import Ticket, TicketMessage
from app.models.user import User
from app.schemas.ticket import (
    TicketCreate,
    TicketMessageCreate,
    TicketMessageOut,
    TicketOut,
    TicketUpdate,
)
from app.services.notifications import notify_ticket_reply

logger = setup_logging() if False else __import__("logging").getLogger("hosting.api.tickets")

router = APIRouter(prefix="/tickets", tags=["tickets"])


def _ticket_number(db: Session) -> str:
    while True:
        number = f"TK-{secrets.token_hex(4).upper()}"
        if not db.query(Ticket).filter_by(ticket_number=number).first():
            return number


@router.post("", response_model=TicketOut, status_code=201)
def create_ticket(
    payload: TicketCreate,
    request: Request,
    current_user=Depends(CustomerOrStaff),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    ticket = Ticket(
        ticket_number=_ticket_number(db),
        user_id=current_user.id,
        subject=payload.subject,
        category=payload.category,
        priority=payload.priority,
        status="open",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    # First message from the customer.
    msg = TicketMessage(ticket_id=ticket.id, user_id=current_user.id, message=payload.message, is_internal=False)
    db.add(msg)
    db.commit()
    logger.info("Ticket created", extra={"ticket_number": ticket.ticket_number, "user_id": current_user.id})
    return ticket


@router.get("", response_model=list[TicketOut])
def list_tickets(
    current_user=Depends(CustomerOrStaff),
    db: Session = Depends(get_db),
    status: str | None = Query(default=None),
):
    q = db.query(Ticket)
    if not current_user.is_staff:
        q = q.filter_by(user_id=current_user.id)
    if status:
        q = q.filter_by(status=status)
    return q.order_by(Ticket.created_at.desc()).all()


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int, current_user=Depends(CustomerOrStaff), db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise NotFound(message="Ticket not found")
    if not current_user.is_staff and ticket.user_id != current_user.id:
        raise Forbidden(message="Cannot view this ticket")
    return ticket


@router.get("/{ticket_id}/messages", response_model=list[TicketMessageOut])
def get_messages(
    ticket_id: int,
    current_user=Depends(CustomerOrStaff),
    db: Session = Depends(get_db),
    include_internal: bool = Query(default=False),
):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise NotFound(message="Ticket not found")
    if not current_user.is_staff and ticket.user_id != current_user.id:
        raise Forbidden(message="Cannot view this ticket")
    q = db.query(TicketMessage).filter_by(ticket_id=ticket_id)
    if not current_user.is_staff:
        q = q.filter_by(is_internal=False)
    elif not include_internal:
        q = q.filter_by(is_internal=False)
    return q.order_by(TicketMessage.created_at.asc()).all()


@router.post("/{ticket_id}/messages", response_model=TicketMessageOut, status_code=201)
def add_message(
    ticket_id: int,
    payload: TicketMessageCreate,
    request: Request,
    current_user=Depends(CustomerOrStaff),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise NotFound(message="Ticket not found")
    if not current_user.is_staff and ticket.user_id != current_user.id:
        raise Forbidden(message="Cannot reply to this ticket")

    is_internal = bool(payload.is_internal) and current_user.is_staff
    msg = TicketMessage(ticket_id=ticket_id, user_id=current_user.id if not is_internal else None,
                        staff_id=current_user.id if is_internal else None, message=payload.message, is_internal=is_internal)
    db.add(msg)

    # Update ticket status when a customer replies to a closed ticket.
    if not current_user.is_staff and ticket.status == "closed":
        ticket.status = "reopened"

    db.commit()
    db.refresh(msg)

    # Notify the other party.
    if current_user.is_staff:
        notify_ticket_reply(db, ticket, payload.message, current_user.username)
    else:
        notify_ticket_reply(db, ticket, payload.message, current_user.username)
    db.commit()
    return msg


@router.patch("/{ticket_id}", response_model=TicketOut)
def update_ticket(
    ticket_id: int,
    payload: TicketUpdate,
    current_user=Depends(StaffOnly),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise NotFound(message="Ticket not found")
    if payload.status:
        ticket.status = payload.status
        if payload.status == "closed":
            ticket.closed_at = datetime.now(timezone.utc)
        elif payload.status == "reopened":
            ticket.closed_at = None
    if payload.priority:
        ticket.priority = payload.priority
    if payload.assigned_to is not None:
        ticket.assigned_to = payload.assigned_to
    db.commit()
    db.refresh(ticket)
    return ticket
