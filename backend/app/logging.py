"""Structured logging with secret redaction."""

import logging
import re
from typing import Any, Dict

try:
    import json as _json
except Exception:  # pragma: no cover
    _json = None  # type: ignore


SECRET_PATTERNS = [
    re.compile(r"(authorization|api.key|api_key|secret|token|password|passwd|pwd)", re.IGNORECASE),
]


def redact(value: Any) -> Any:
    """Recursively redact secret-looking values from a data structure."""
    if isinstance(value, dict):
        return {k: ("***" if _is_secret(k) else redact(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, tuple):
        return tuple(redact(v) for v in value)
    return value


def _is_secret(key: Any) -> bool:
    if not isinstance(key, str):
        return False
    return any(p.search(key) for p in SECRET_PATTERNS)


class SecretRedactingFormatter(logging.Formatter):
    """Log formatter that redacts secret-looking keys in extra dicts."""

    def format(self, record: logging.LogRecord) -> str:
        if isinstance(record.__dict__.get("extra"), dict):
            record.extra = redact(record.__dict__["extra"])  # type: ignore
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """Minimal JSON log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        extra = {k: v for k, v in record.__dict__.items() if k not in logging.LogRecord(None, "", "", 0, "", None, None).__dict__}
        if extra:
            payload["extra"] = redact(extra)
        if _json is not None:
            return _json.dumps(payload)
        return str(payload)


def setup_logging() -> None:
    level = logging.DEBUG if __import__("app.config", fromlist=["settings"]).settings.APP_DEBUG else logging.INFO
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Quieten noisy third-party loggers.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "sqlalchemy.engine", "discord", "httpx"):
        logging.getLogger(name).setLevel(logging.WARNING)

    logging.getLogger("hosting").setLevel(level)
