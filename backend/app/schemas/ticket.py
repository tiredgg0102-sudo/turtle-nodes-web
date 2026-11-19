"""Ticket schemas."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    subject: str = Field(min_length=1, max_length=255)
    category: str = Field(default="general", max_length=100)
    priority: str = Field(default="normal", max_length=20)
    message: str = Field(min_length=1, max_length=10000)


class TicketMessageCreate(BaseModel):
    message: str = Field(min_length=1, max_length=10000)
    is_internal: bool = False


class TicketOut(BaseModel):
    id: int
    ticket_number: str
    user_id: int
    subject: str
    category: str
    status: str
    priority: str
    assigned_to: Optional[int] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TicketMessageOut(BaseModel):
    id: int
    ticket_id: int
    user_id: Optional[int] = None
    staff_id: Optional[int] = None
    message: str
    is_internal: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TicketUpdate(BaseModel):
    status: Optional[str] = Field(default=None, max_length=50)
    priority: Optional[str] = Field(default=None, max_length=20)
    assigned_to: Optional[int] = None
