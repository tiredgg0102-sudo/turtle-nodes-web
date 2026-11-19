"""User schemas."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(default=None, min_length=3, max_length=100)


class UserOut(UserBase):
    id: int
    role: str
    status: str
    email_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    discord_id: Optional[str] = None
    pterodactyl_user_id: Optional[int] = None
    has_pterodactyl_connection: bool = False

    class Config:
        from_attributes = True


class UserProfile(UserOut):
    pass


class UserRoleUpdate(BaseModel):
    role: str = Field(pattern="^(customer|staff|admin)$")


class UserStatusUpdate(BaseModel):
    status: str = Field(pattern="^(active|suspended)$")
    reason: Optional[str] = None
