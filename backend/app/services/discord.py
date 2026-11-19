"""Discord notification helpers (webhook + bot token via Discord API).

Used to notify staff of new orders/tickets and customers of order updates.
Actual slash-command bot lives in the bot/ package.
"""

import logging

import httpx

from app.config import settings

logger = logging.getLogger("hosting.services.discord")


async def send_webhook_message(content: str, username: str = "Hosting Platform") -> bool:
    """Send a message to the configured Discord notifications webhook."""
    webhook_url = settings.DISCORD_NOTIFICATIONS_CHANNEL_ID  # placeholder: could be a webhook URL
    if not webhook_url or not webhook_url.startswith("http"):
        logger.debug("Discord webhook not configured; skipping")
        return False
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(webhook_url, json={"content": content, "username": username})
        return resp.status_code in (200, 204)
    except Exception as exc:  # noqa: BLE001
        logger.error("Discord webhook failed: %s", exc)
        return False


async def notify_staff_new_order(order_reference: str, customer_email: str, plan_name: str) -> None:
    await send_webhook_message(
        f"🆕 New Order #{order_reference}\nCustomer: {customer_email}\nPlan: {plan_name}\nAwaiting staff review.",
    )


async def notify_customer_discord(discord_id: str, content: str) -> bool:
    """Send a DM to a Discord user via the bot token (requires bot + user shared guild)."""
    if not settings.DISCORD_BOT_TOKEN or not discord_id:
        return False
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            # Open a DM channel.
            resp = await client.post(
                "https://discord.com/api/v10/users/@me/dms",
                headers={"Authorization": f"Bot {settings.DISCORD_BOT_TOKEN}", "Content-Type": "application/json"},
                json={"recipient_id": discord_id},
            )
            if resp.status_code not in (200, 201):
                logger.warning("Could not open Discord DM for %s: %s", discord_id, resp.status_code)
                return False
            channel_id = resp.json()["id"]
            await client.post(
                f"https://discord.com/api/v10/channels/{channel_id}/messages",
                headers={"Authorization": f"Bot {settings.DISCORD_BOT_TOKEN}", "Content-Type": "application/json"},
                json={"content": content},
            )
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Discord customer notification failed: %s", exc)
        return False
