"""Abstract base class for infrastructure providers."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class ProvisionResult:
    def __init__(self, success: bool, server_id: Optional[Any] = None, details: Optional[dict] = None, error: Optional[str] = None) -> None:
        self.success = success
        self.server_id = server_id
        self.details = details or {}
        self.error = error


class BaseProvider(ABC):
    """Every provider must implement provision, suspend, unsuspend, delete, get_info."""

    name: str = "base"

    @abstractmethod
    async def provision(self, params: dict[str, Any]) -> ProvisionResult:
        ...

    @abstractmethod
    async def suspend(self, server_id: Any) -> ProvisionResult:
        ...

    @abstractmethod
    async def unsuspend(self, server_id: Any) -> ProvisionResult:
        ...

    @abstractmethod
    async def delete(self, server_id: Any) -> ProvisionResult:
        ...

    @abstractmethod
    async def get_info(self, server_id: Any) -> dict[str, Any]:
        ...

    @abstractmethod
    async def health(self) -> dict[str, Any]:
        ...
