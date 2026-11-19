"""Service schemas."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ServiceOut(BaseModel):
    id: int
    name: str
    status: str
    pterodactyl_server_id: Optional[int] = None
    ip_address: Optional[str] = None
    port: Optional[int] = None
    resources: dict[str, Any]
    node: Optional[str] = None
    location: Optional[str] = None
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    suspended: bool = False

    class Config:
        from_attributes = True


class ServicePowerAction(BaseModel):
    action: str = Field(pattern="^(start|stop|restart)$")
