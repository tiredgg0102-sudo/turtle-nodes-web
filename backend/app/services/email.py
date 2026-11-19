"""Email delivery (optional, SMTP). Gracefully disabled when not configured."""

import logging
import smtplib
from email.message import EmailMessage
from typing import Optional

from app.config import settings

logger = logging.getLogger("hosting.services.email")


def is_configured() -> bool:
    return bool(settings.SMTP_HOST and settings.SMTP_FROM_EMAIL)


def send(to_email: str, subject: str, body: str) -> bool:
    if not is_configured():
        logger.debug("Email not configured; skipping send to %s", to_email)
        return False
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    msg["To"] = to_email
    msg.set_content(body)
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20) as smtp:
            smtp.starttls()
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            smtp.send_message(msg)
        logger.info("Email sent to %s: %s", to_email, subject)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to send email to %s: %s", to_email, exc)
        return False
