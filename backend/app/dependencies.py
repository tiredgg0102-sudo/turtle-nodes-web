"""FastAPI dependencies."""

from typing import Generator, Optional

from fastapi import Cookie, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal, get_db
from app.exceptions import Forbidden, Unauthorized
from app.logging import setup_logging
from app.models.user import User
from app.security import decode_token

logger = setup_logging() if False else __import__("logging").getLogger("hosting.dependencies")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)


def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    request: Request,
    db: Session = Depends(get_db_session),
    access_token: Optional[str] = Cookie(default=None),
    authorization: Optional[str] = None,
) -> User:
    """Resolve the authenticated user from a JWT in a cookie or Authorization header."""
    token = access_token
    if not token and authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
    if not token:
        raise Unauthorized(message="Not authenticated", code="not_authenticated")

    try:
        payload = decode_token(token)
    except Unauthorized:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.warning("Token decode failed", extra={"error": str(exc)})
        raise Unauthorized(message="Not authenticated", code="not_authenticated")

    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise Unauthorized(message="Invalid token", code="invalid_token")

    user = db.get(User, int(user_id))
    if not user or not user.is_active:
        raise Unauthorized(message="User not found or inactive", code="user_inactive")
    return user


def require_roles(*allowed_roles: str):
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise Forbidden(message="Insufficient permissions", code="insufficient_permissions")
        return current_user

    return dependency


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def require_csrf(request: Request, csrf_token: Optional[str] = None) -> None:
    """Double-submit CSRF check for state-changing requests.

    The client must send the CSRF token (from the X-CSRF-TOKEN cookie) in the
    X-CSRF-TOKEN header. Safe methods are skipped.
    """
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return
    cookie_token = request.cookies.get("csrf_token")
    if not cookie_token or not csrf_token or cookie_token != csrf_token:
        raise Forbidden(message="CSRF token missing or invalid", code="csrf_invalid")
