"""Notification schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: int
    type: str
    title: str
    content: str
    read: bool
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
