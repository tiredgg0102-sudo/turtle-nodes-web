"""Plan schemas."""

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class PlanBase(BaseModel):
    category_id: int
    name: str = Field(min_length=1, max_length=150)
    slug: Optional[str] = Field(default=None, max_length=150)
    description: Optional[str] = None
    short_description: Optional[str] = Field(default=None, max_length=300)
    price: float = Field(ge=0)
    currency: str = Field(default="USD", max_length=10)
    billing_cycle: str = Field(default="monthly", max_length=20)
    ram_mb: int = Field(default=0, ge=0)
    cpu: int = Field(default=0, ge=0)
    storage_mb: int = Field(default=0, ge=0)
    disk_mb: int = Field(default=0, ge=0)
    features: Optional[List[str]] = None
    active: bool = True
    available: bool = True
    sort_order: int = Field(default=0, ge=0)
    featured: bool = False
    popular: bool = False


class PlanCreate(PlanBase):
    slug: str = Field(min_length=1, max_length=150)


class PlanUpdate(PlanBase):
    pass


class PlanOut(PlanBase):
    id: int
    created_at: Any
    updated_at: Any

    class Config:
        from_attributes = True
