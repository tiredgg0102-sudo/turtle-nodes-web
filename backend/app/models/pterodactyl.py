"""Pterodactyl integration configuration model."""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class PterodactylConfig(Base, TimestampMixin):
    __tablename__ = "pterodactyl_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    panel_url: Mapped[str] = mapped_column(String(500), nullable=False)
    app_api_key_encrypted: Mapped[str] = mapped_column(String(2000), nullable=False)
    default_node_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    default_location_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    default_nest_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    default_egg_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    default_ram: Mapped[int] = mapped_column(Integer, default=1024, nullable=False)
    default_cpu: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    default_storage: Mapped[int] = mapped_column(Integer, default=20480, nullable=False)
    default_disk: Mapped[int] = mapped_column(Integer, default=20480, nullable=False)
    default_io: Mapped[int] = mapped_column(Integer, default=500, nullable=False)
    default_overlimit: Mapped[bool] = mapped_column(default=False, nullable=False)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)

    def to_dict(self, include_key: bool = False) -> dict[str, Any]:
        return {
            "id": self.id,
            "panel_url": self.panel_url,
            "app_api_key_set": bool(self.app_api_key_encrypted),
            "default_node_id": self.default_node_id,
            "default_location_id": self.default_location_id,
            "default_nest_id": self.default_nest_id,
            "default_egg_id": self.default_egg_id,
            "default_ram": self.default_ram,
            "default_cpu": self.default_cpu,
            "default_storage": self.default_storage,
            "default_disk": self.default_disk,
            "default_io": self.default_io,
            "default_overlimit": self.default_overlimit,
            "active": self.active,
        }


