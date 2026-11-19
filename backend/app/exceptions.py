"""Centralized application exceptions."""

from typing import Any, Dict, Optional


class AppError(Exception):
    """Base application error."""

    def __init__(
        self,
        message: str,
        code: str = "error",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class NotFound(AppError):
    def __init__(self, message: str = "Not found", code: Optional[str] = None, status_code: int = 404, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, code=code or "not_found", status_code=status_code, details=details)


class Unauthorized(AppError):
    def __init__(self, message: str = "Unauthorized", code: Optional[str] = None, status_code: int = 401, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, code=code or "unauthorized", status_code=status_code, details=details)


class Forbidden(AppError):
    def __init__(self, message: str = "Forbidden", code: Optional[str] = None, status_code: int = 403, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, code=code or "forbidden", status_code=status_code, details=details)


class Conflict(AppError):
    def __init__(self, message: str = "Conflict", code: Optional[str] = None, status_code: int = 409, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, code=code or "conflict", status_code=status_code, details=details)


class ValidationError(AppError):
    def __init__(self, message: str = "Validation error", code: Optional[str] = None, status_code: int = 422, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, code=code or "validation_error", status_code=status_code, details=details)


class ExternalServiceError(AppError):
    def __init__(self, message: str = "External service error", code: Optional[str] = None, status_code: int = 502, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, code=code or "external_service_error", status_code=status_code, details=details)


class ProvisioningError(AppError):
    def __init__(self, message: str = "Provisioning error", code: Optional[str] = None, status_code: int = 422, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, code=code or "provisioning_error", status_code=status_code, details=details)
