"""Discord integration settings & status endpoints."""

from fastapi import APIRouter, Depends

from app.api.v1.deps import AdminOnly
from app.config import settings

router = APIRouter(prefix="/discord", tags=["discord"])


@router.get("/config")
def discord_config(current_user=Depends(AdminOnly)):
    return {
        "bot_configured": bool(settings.DISCORD_BOT_TOKEN),
        "guild_id": settings.DISCORD_GUILD_ID,
        "staff_role_ids": settings.DISCORD_STAFF_ROLE_IDS,
        "order_channel_id": settings.DISCORD_ORDER_CHANNEL_ID,
        "staff_channel_id": settings.DISCORD_STAFF_CHANNEL_ID,
        "notifications_channel_id": settings.DISCORD_NOTIFICATIONS_CHANNEL_ID,
        "invite_url": settings.DISCORD_INVITE_URL,
    }
