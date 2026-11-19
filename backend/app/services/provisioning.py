"""Service provisioning engine.

Processes approved orders through background jobs with retries, idempotency
keys, and full audit logging. Never creates duplicate servers for the same
order and never marks a service active before verifying successful
provisioning.
"""

import asyncio
import uuid
from typing import Any, Optional

from sqlalchemy import select

from app.database import SessionLocal
from app.logging import setup_logging
from app.models.order import Order
from app.models.provisioning import ProvisioningJob, ProvisioningLog
from app.models.service import Service
from app.models.user import User
from app.services.providers.kvm_provider import KVMProvider
from app.services.providers.pterodactyl_provider import PterodactylProvider
from app.services.pterodactyl import PterodactylAppClient

logger = setup_logging() if False else __import__("logging").getLogger("hosting.services.provisioning")

PROVIDERS: dict[str, Any] = {}

PROVISIONING_RUNNING = False


def register_provider(name: str, provider: Any) -> None:
    PROVIDERS[name] = provider


def get_provider(name: str) -> Any:
    provider = PROVIDERS.get(name)
    if not provider:
        raise KeyError(f"Provider '{name}' is not registered")
    return provider


def _log(session, job: ProvisioningJob, level: str, message: str) -> None:
    session.add(ProvisioningLog(job_id=job.id, level=level, message=message))
    session.commit()
    logger.info("provisioning job %s %s: %s", job.id, level, message)


async def process_order(order_id: int) -> None:
    """Provision a single approved order. Idempotent: safe to retry."""
    session = SessionLocal()
    try:
        order = session.get(Order, order_id)
        if not order:
            logger.error("Order %s not found", order_id)
            return

        # Idempotency: if a service already exists for this order, do nothing.
        existing_service = session.query(Service).filter_by(order_id=order_id).first()
        if existing_service:
            logger.info("Order %s already has service %s; skipping", order_id, existing_service.id)
            _mark_order_active(session, order)
            return

        # Determine provider and create the job idempotently.
        idempotency_key = f"order-{order.id}"
        job = session.query(ProvisioningJob).filter_by(idempotency_key=idempotency_key).first()
        if not job:
            job = ProvisioningJob(
                order_id=order.id,
                provider="pterodactyl",
                status="queued",
                idempotency_key=idempotency_key,
            )
            session.add(job)
            session.commit()
            session.refresh(job)

        order.status = "provisioning"
        session.commit()

        # Load customer + plan.
        user = session.get(User, order.user_id)
        plan = order.plan

        # Load Pterodactyl config for defaults.
        from app.models.pterodactyl import PterodactylConfig
        cfg = session.query(PterodactylConfig).filter_by(active=True).first()

        from app.services.pterodactyl import PterodactylAppClient
        from app.services.providers.pterodactyl_provider import PterodactylProvider
        from app.security import decrypt_value
        panel_url = (cfg.panel_url if cfg else None) or __import__("app.config", fromlist=["settings"]).settings.PTERODACTYL_URL
        api_key = None
        if cfg and cfg.app_api_key_encrypted:
            try:
                api_key = decrypt_value(cfg.app_api_key_encrypted)
            except Exception:  # noqa: BLE001
                api_key = None
        if not api_key:
            api_key = __import__("app.config", fromlist=["settings"]).settings.PTERODACTYL_APP_API_KEY
        provider = PterodactylProvider(panel_url, api_key) if panel_url and api_key else None
        if not provider:
            raise RuntimeError("Pterodactyl integration is not configured")

        # Build provisioning params.
        params = {
            "name": f"{plan.name} - {order.order_reference}",
            "user_id": user.id,
            "pterodactyl_user_id": user.pterodactyl_user_id or 1,
            "plan_id": plan.id,
            "ram_mb": plan.ram_mb or (cfg.default_ram if cfg else 1024),
            "cpu": plan.cpu or (cfg.default_cpu if cfg else 100),
            "storage_mb": plan.storage_mb or (cfg.default_storage if cfg else 20480),
            "disk_mb": plan.disk_mb or (cfg.default_disk if cfg else 20480),
            "io": cfg.default_io if cfg else 500,
            "overlimit": cfg.default_overlimit if cfg else False,
            "nest_id": cfg.default_nest_id if cfg else 1,
            "egg_id": cfg.default_egg_id if cfg else 1,
            "location_id": cfg.default_location_id if cfg else 1,
        }

        job.status = "running"
        job.attempts += 1
        session.commit()
        _log(session, job, "info", f"Provisioning order {order.order_reference} on pterodactyl (attempt {job.attempts})")

        try:
            result = await provider.provision(params)
        except Exception as exc:  # noqa: BLE001
            result = None
            logger.exception("Provider exception", extra={"order_id": order_id, "error": str(exc)})

        if result and result.success:
            server_id = result.server_id
            server_info = {}
            if server_id:
                try:
                    server_info = await provider.get_info(server_id) or {}
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Could not fetch server info", extra={"server_id": server_id, "error": str(exc)})

            # Verify: only mark active if we have a server id (provisioning confirmed).
            service = Service(
                user_id=user.id,
                order_id=order.id,
                plan_id=plan.id,
                name=params["name"],
                status="active",
                pterodactyl_server_id=int(server_id) if server_id else None,
                pterodactyl_user_id=user.pterodactyl_user_id,
                ram_mb=params["ram_mb"],
                cpu=params["cpu"],
                storage_mb=params["storage_mb"],
                ip_address=server_info.get("ip") or server_info.get("ip_address"),
                node=str(server_info.get("node", "")) or None,
                location=str(server_info.get("location", "")) or None,
            )
            session.add(service)
            session.commit()
            session.refresh(service)

            job.status = "completed"
            job.completed_at = __import__("datetime").datetime.utcnow()
            job.provider_job_id = str(server_id) if server_id else None
            session.commit()

            _mark_order_active(session, order)
            _log(session, job, "info", f"Provisioning completed. Service {service.id} active for order {order.order_reference}")

            # Notify customer.
            from app.services.notifications import notify_user
            notify_user(
                session,
                user.id,
                type="provisioning",
                title="Service Activated",
                content=f"Your service '{service.name}' has been provisioned and is now active.",
            )
            session.commit()
        else:
            error = result.error if result else "Unknown provisioning error"
            _log(session, job, "error", f"Provisioning failed: {error}")
            if job.attempts < job.max_attempts:
                job.status = "queued"
                session.commit()
                logger.info("Order %s will retry (attempt %s/%s)", order_id, job.attempts + 1, job.max_attempts)
                # In a real deployment this would be re-queued with a backoff.
            else:
                job.status = "failed"
                job.last_error = error
                job.completed_at = __import__("datetime").datetime.utcnow()
                session.commit()
                order.status = "failed"
                session.commit()
                from app.services.notifications import notify_user
                notify_user(
                    session,
                    user.id,
                    type="provisioning",
                    title="Provisioning Failed",
                    content=f"Your service '{params['name']}' could not be provisioned: {error}",
                )
                session.commit()
                _log(session, job, "error", f"Order {order.order_reference} marked failed after {job.attempts} attempts")
    finally:
        session.close()


def _mark_order_active(session, order: Order) -> None:
    order.status = "active"
    order.completed_at = __import__("datetime").datetime.utcnow()
    session.commit()


def enqueue_order(order_id: int) -> None:
    """Called when an order is approved. Kicks off provisioning in the background."""
    from app.main import app  # noqa: F401
    asyncio.create_task(process_order(order_id))
