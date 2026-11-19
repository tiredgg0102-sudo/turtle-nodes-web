"""Authentication endpoints (register, login, logout, password reset)."""

import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Cookie, Depends, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.v1.deps import CustomerOrStaff, csrf_protect
from app.config import settings
from app.database import get_db
from app.exceptions import Conflict, Unauthorized, ValidationError
from app.logging import setup_logging
from app.models.user import User
from app.schemas.token import LoginRequest, LoginResponse, Token
from app.schemas.user import UserCreate, UserOut
from app.security import create_access_token, create_refresh_token, generate_csrf_token, hash_password, verify_password
from app.security import check_login_rate, check_register_rate
from app.dependencies import get_db_session

logger = setup_logging() if False else __import__("logging").getLogger("hosting.api.auth")

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookies(response: Response, access_token: str, csrf_token: str) -> None:
    secure = settings.COOKIE_SECURE
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=secure,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        domain=settings.COOKIE_DOMAIN,
    )
    response.set_cookie(
        "csrf_token",
        csrf_token,
        httponly=False,
        secure=secure,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        domain=settings.COOKIE_DOMAIN,
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie("access_token", path="/", domain=settings.COOKIE_DOMAIN)
    response.delete_cookie("csrf_token", path="/", domain=settings.COOKIE_DOMAIN)


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, request: Request, response: Response, db: Session = Depends(get_db)):
    check_register_rate(request.client.host if request.client else "unknown")
    if db.query(User).filter_by(email=payload.email).first():
        raise Conflict(message="Email already registered", code="email_taken")
    if db.query(User).filter_by(username=payload.username).first():
        raise Conflict(message="Username already taken", code="username_taken")

    user = User(
        email=payload.email,
        username=payload.username,
        password_hash=hash_password(payload.password),
        role="customer",
        status="active",
    )
    # Email verification token if required.
    if settings.EMAIL_VERIFICATION_REQUIRED:
        user.email_verification_token = secrets.token_urlsafe(32)
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(str(user.id))
    csrf_token = generate_csrf_token()
    _set_auth_cookies(response, access_token, csrf_token)

    logger.info("User registered", extra={"user_id": user.id, "email": user.email})
    return Token(access_token=access_token, token_type="bearer", expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, csrf_token=csrf_token)


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    check_login_rate(request.client.host if request.client else "unknown")
    user = db.query(User).filter_by(email=payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise Unauthorized(message="Invalid email or password", code="invalid_credentials")
    if user.status != "active":
        raise Unauthorized(message="Account is not active", code="account_inactive")

    user.last_login_at = datetime.utcnow()
    db.commit()

    access_token = create_access_token(str(user.id))
    csrf_token = generate_csrf_token()
    _set_auth_cookies(response, access_token, csrf_token)

    logger.info("User login", extra={"user_id": user.id, "email": user.email})
    return LoginResponse(
        user=user.to_dict(),
        token=Token(access_token=access_token, token_type="bearer", expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, csrf_token=csrf_token),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response, current_user=Depends(CustomerOrStaff)):
    _clear_auth_cookies(response)
    logger.info("User logout", extra={"user_id": current_user.id})
    return None


@router.get("/me", response_model=UserOut)
async def me(current_user=Depends(CustomerOrStaff)):
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh(response: Response, request: Request, refresh_token: str | None = Cookie(default=None), db: Session = Depends(get_db_session)):
    if not refresh_token:
        raise Unauthorized(message="No refresh token", code="no_refresh_token")
    from app.security import decode_token
    try:
        payload = decode_token(refresh_token)
    except Unauthorized:
        raise
    if payload.get("type") != "refresh":
        raise Unauthorized(message="Invalid token type", code="invalid_token_type")
    user_id = int(payload.get("sub"))
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise Unauthorized(message="User not found or inactive", code="user_inactive")

    access_token = create_access_token(str(user.id))
    csrf_token = generate_csrf_token()
    _set_auth_cookies(response, access_token, csrf_token)
    return Token(access_token=access_token, token_type="bearer", expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, csrf_token=csrf_token)
