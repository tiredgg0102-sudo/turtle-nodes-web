"""Pterodactyl integration schemas."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class PterodactylConfigBase(BaseModel):
    panel_url: str
    default_node_id: Optional[int] = None
    default_location_id: Optional[int] = None
    default_nest_id: Optional[int] = None
    default_egg_id: Optional[int] = None
    default_ram: int = Field(default=1024, ge=0)
    default_cpu: int = Field(default=100, ge=0)
    default_storage: int = Field(default=20480, ge=0)
    default_disk: int = Field(default=20480, ge=0)
    default_io: int = Field(default=500, ge=0)
    default_overlimit: bool = False
    active: bool = True


class PterodactylConfigCreate(PterodactylConfigBase):
    app_api_key: str = Field(min_length=1)


class PterodactylConfigUpdate(BaseModel):
    panel_url: Optional[str] = None
    app_api_key: Optional[str] = Field(default=None, min_length=1)
    default_node_id: Optional[int] = None
    default_location_id: Optional[int] = None
    default_nest_id: Optional[int] = None
    default_egg_id: Optional[int] = None
    default_ram: Optional[int] = Field(default=None, ge=0)
    default_cpu: Optional[int] = Field(default=None, ge=0)
    default_storage: Optional[int] = Field(default=None, ge=0)
    default_disk: Optional[int] = Field(default=None, ge=0)
    default_io: Optional[int] = Field(default=None, ge=0)
    default_overlimit: Optional[bool] = None
    active: Optional[bool] = None


class PterodactylConfigOut(PterodactylConfigBase):
    id: int
    app_api_key_set: bool
    created_at: Any
    updated_at: Any

    class Config:
        from_attributes = True


class TestConnectionRequest(BaseModel):
    panel_url: str
    app_api_key: str


class TestConnectionResponse(BaseModel):
    success: bool
    message: str
    version: Optional[str] = None


class ClientApiKeyConnect(BaseModel):
    client_api_key: str = Field(min_length=1)
    panel_url: Optional[str] = None
