"""Announcement schemas."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class AnnouncementBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    active: bool = True


class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    content: Optional[str] = Field(default=None, min_length=1)
    active: Optional[bool] = None


class AnnouncementOut(AnnouncementBase):
    id: int
    published_by: Optional[int] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
