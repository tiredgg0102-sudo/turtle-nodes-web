"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1 import announcements, admin, auth, bot, categories, discord, notifications, orders, pterodactyl, services, system, tickets, users

router = APIRouter()

router.include_router(auth.router)
router.include_router(bot.router)
router.include_router(categories.router)
router.include_router(users.router)
router.include_router(orders.router)
router.include_router(services.router)
router.include_router(pterodactyl.router)
router.include_router(tickets.router)
router.include_router(announcements.router)
router.include_router(admin.router)
router.include_router(discord.router)
router.include_router(notifications.router)
router.include_router(system.router)

# Plans router imported separately to avoid unused-import ordering issues.
from app.api.v1 import plans  # noqa: E402

router.include_router(plans.router)

__all__ = ["router"]
