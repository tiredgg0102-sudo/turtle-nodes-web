"""Router-level dependencies (CSRF, roles)."""

from fastapi import Cookie, Header, Request

from app.dependencies import get_current_user, require_csrf, require_roles


def current_user(request: Request) -> object:
    return get_current_user(request)


def csrf_protect(request: Request, x_csrf_token: str | None = Header(default=None)) -> None:
    require_csrf(request, x_csrf_token)


AdminOnly = require_roles("admin")
StaffOnly = require_roles("admin", "staff")
CustomerOrStaff = require_roles("admin", "staff", "customer")
