"""Service model (a purchased/active hosting service)."""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Service(Base, TimestampMixin):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("plans.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="provisioning", nullable=False)  # provisioning|active|suspended|offline|failed|deleted
    pterodactyl_server_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pterodactyl_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ram_mb: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cpu: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    storage_mb: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    node: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    suspended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    suspended_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    suspension_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="services")
    order: Mapped["Order"] = relationship("Order", back_populates="service")
    plan: Mapped["Plan"] = relationship("Plan", back_populates="services")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "pterodactyl_server_id": self.pterodactyl_server_id,
            "pterodactyl_user_id": self.pterodactyl_user_id,
            "ip_address": self.ip_address,
            "port": self.port,
            "resources": {
                "ram_mb": self.ram_mb,
                "cpu": self.cpu,
                "storage_mb": self.storage_mb,
            },
            "node": self.node,
            "location": self.location,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "suspended": self.status == "suspended",
        }
