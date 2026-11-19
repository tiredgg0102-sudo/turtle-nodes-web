"""Common schemas."""

from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Message(BaseModel):
    message: str


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    per_page: int
    pages: int


class ErrorDetail(BaseModel):
    error: bool
    code: str
    message: str
    details: Optional[dict[str, Any]] = None
