"""Order schemas."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    plan_id: int


class OrderOut(BaseModel):
    id: int
    order_reference: str
    user_id: int
    plan_id: int
    status: str
    total_price: float
    currency: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderReview(BaseModel):
    action: str = Field(pattern="^(approve|reject)$")
    reason: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    status: str
