"""System diagnostics & health endpoints."""

from fastapi import APIRouter, Depends

from app.api.v1.deps import AdminOnly
from app.config import settings

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health")
def system_health(current_user=Depends(AdminOnly)):
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "env": settings.APP_ENV,
        "database_configured": bool(settings.DATABASE_URL),
        "pterodactyl_configured": bool(settings.PTERODACTYL_URL and settings.PTERODACTYL_APP_API_KEY),
        "discord_configured": bool(settings.DISCORD_BOT_TOKEN and settings.DISCORD_GUILD_ID),
    }
