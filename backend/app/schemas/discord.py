"""Discord integration schemas."""

from typing import Any, Optional

from pydantic import BaseModel


class DiscordConfigOut(BaseModel):
    bot_configured: bool
    guild_id: Optional[str] = None
    staff_role_ids: list[str] = []
    order_channel_id: Optional[str] = None
    staff_channel_id: Optional[str] = None
    invite_url: Optional[str] = None


class OrderSubmitRequest(BaseModel):
    order_reference: str
