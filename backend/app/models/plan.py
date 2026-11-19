"""Hosting plan model."""

from typing import Any, Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Plan(Base, TimestampMixin):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    short_description: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    billing_cycle: Mapped[str] = mapped_column(String(20), default="monthly", nullable=False)  # monthly | yearly | one_time
    ram_mb: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cpu: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    storage_mb: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    disk_mb: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    features: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of feature strings
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  # orderable
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    popular: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    category: Mapped["Category"] = relationship("Category", back_populates="plans")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="plan")
    services: Mapped[list["Service"]] = relationship("Service", back_populates="plan")

    def to_dict(self, include_resources: bool = True) -> dict[str, Any]:
        import json

        features_list = []
        if self.features:
            try:
                features_list = json.loads(self.features)
            except Exception:  # noqa: BLE001
                features_list = [self.features]

        data: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "short_description": self.short_description,
            "price": self.price,
            "currency": self.currency,
            "billing_cycle": self.billing_cycle,
            "active": self.active,
            "available": self.available,
            "sort_order": self.sort_order,
            "featured": self.featured,
            "popular": self.popular,
            "features": features_list,
            "category_id": self.category_id,
        }
        if include_resources:
            data["resources"] = {
                "ram_mb": self.ram_mb,
                "cpu": self.cpu,
                "storage_mb": self.storage_mb,
                "disk_mb": self.disk_mb,
            }
        return data
