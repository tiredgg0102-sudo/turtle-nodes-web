"""User model."""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Boolean, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="customer", nullable=False)  # customer | staff | admin
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)  # active | suspended | deleted
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    email_verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_reset_expires: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    suspended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    suspended_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    suspension_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    discord_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    pterodactyl_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pterodactyl_client_api_key_encrypted: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    pterodactyl_panel_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    services: Mapped[list["Service"]] = relationship("Service", back_populates="user", cascade="all, delete-orphan")
    tickets: Mapped[list["Ticket"]] = relationship("Ticket", back_populates="user", cascade="all, delete-orphan", foreign_keys="Ticket.user_id")
    ticket_messages: Mapped[list["TicketMessage"]] = relationship("TicketMessage", back_populates="author", cascade="all, delete-orphan", foreign_keys="TicketMessage.user_id")
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    @property
    def is_active(self) -> bool:
        return self.status == "active"

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def is_staff(self) -> bool:
        return self.role in ("admin", "staff")

    def to_dict(self, include_sensitive: bool = False) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "role": self.role,
            "status": self.status,
            "email_verified": self.email_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "discord_id": self.discord_id,
            "pterodactyl_user_id": self.pterodactyl_user_id,
            "has_pterodactyl_connection": bool(self.pterodactyl_client_api_key_encrypted),
        }
        if include_sensitive:
            data["password_hash"] = self.password_hash
            data["email_verification_token"] = self.email_verification_token
        return data
