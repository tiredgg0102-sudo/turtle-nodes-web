"""Security utilities: password hashing, JWT, encryption, CSRF, rate limiting."""

import secrets
import time
from collections import defaultdict, deque
from typing import Any, Dict, Optional

from cryptography.fernet import Fernet, InvalidToken
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.exceptions import AppError, Unauthorized
from app.logging import setup_logging

logger = setup_logging() if False else __import__("logging").getLogger("hosting.security")

# ------------------------------------------------------------------ Passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=settings.BCRYPT_ROUNDS)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ------------------------------------------------------------------ JWT tokens
def create_access_token(subject: str, expires_delta_seconds: Optional[int] = None) -> str:
    expire = time.time() + (expires_delta_seconds or settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    to_encode = {"sub": str(subject), "exp": int(expire), "type": "access"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str) -> str:
    expire = time.time() + settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    to_encode = {"sub": str(subject), "exp": int(expire), "type": "refresh"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise Unauthorized(message="Invalid or expired token", details={"reason": str(exc)})


# ------------------------------------------------------------------ Encryption (at rest)
def _get_fernet() -> Fernet:
    return Fernet(settings.ENCRYPTION_KEY.encode())


def encrypt_value(plaintext: str) -> str:
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt_value(ciphertext: str) -> str:
    try:
        return _get_fernet().decrypt(ciphertext.encode()).decode()
    except InvalidToken as exc:
        raise AppError(message="Failed to decrypt credential", code="decryption_error", status_code=500, details={"reason": str(exc)})


# ------------------------------------------------------------------ CSRF (double-submit)
def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


# ------------------------------------------------------------------ Rate limiting (in-memory sliding window)
class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: Dict[str, deque] = defaultdict(deque)

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        window = self._hits[key]
        while window and window[0] <= now - self.window_seconds:
            window.popleft()
        if len(window) >= self.max_requests:
            return False
        window.append(now)
        return True


_login_limiter = RateLimiter(settings.RATE_LIMIT_LOGIN, settings.RATE_LIMIT_WINDOW_SECONDS)
_register_limiter = RateLimiter(settings.RATE_LIMIT_REGISTER, settings.RATE_LIMIT_WINDOW_SECONDS)


def check_login_rate(key: str) -> None:
    if not _login_limiter.is_allowed(key):
        raise Unauthorized(message="Too many login attempts. Try again later.", code="rate_limited")


def check_register_rate(key: str) -> None:
    if not _register_limiter.is_allowed(key):
        raise Unauthorized(message="Too many registration attempts. Try again later.", code="rate_limited")
