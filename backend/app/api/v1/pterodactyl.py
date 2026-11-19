"""Pterodactyl integration endpoints (admin Application API + customer Client API)."""

from typing import Any

from fastapi import APIRouter, Body, Depends, Query, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.deps import AdminOnly, CustomerOrStaff, StaffOnly, csrf_protect
from app.config import settings
from app.database import get_db
from app.exceptions import Conflict, Forbidden, NotFound, Unauthorized
from app.logging import setup_logging
from app.models.pterodactyl import PterodactylConfig
from app.models.user import User
from app.schemas.pterodactyl import (
    PterodactylConfigCreate,
    PterodactylConfigOut,
    PterodactylConfigUpdate,
    TestConnectionRequest,
    TestConnectionResponse,
    ClientApiKeyConnect,
)
from app.services.pterodactyl import PterodactylAppClient, PterodactylClientClient
from app.security import decrypt_value, encrypt_value

logger = setup_logging() if False else __import__("logging").getLogger("hosting.api.pterodactyl")

router = APIRouter(prefix="/pterodactyl", tags=["pterodactyl"])


def _get_config(db: Session) -> PterodactylConfig | None:
    return db.query(PterodactylConfig).filter_by(active=True).first()


def _get_app_client(db: Session) -> PterodactylAppClient:
    cfg = _get_config(db)
    if not cfg or not cfg.app_api_key_encrypted:
        raise Unauthorized(message="Pterodactyl integration not configured", code="pterodactyl_not_configured")
    panel_url = cfg.panel_url or settings.PTERODACTYL_URL
    api_key = decrypt_value(cfg.app_api_key_encrypted) or settings.PTERODACTYL_APP_API_KEY
    if not panel_url or not api_key:
        raise Unauthorized(message="Pterodactyl credentials missing", code="pterodactyl_credentials_missing")
    return PterodactylAppClient(panel_url, api_key)


# -------- Admin: Configuration --------
@router.get("/config", response_model=PterodactylConfigOut)
def get_config(current_user=Depends(AdminOnly), db: Session = Depends(get_db)):
    cfg = _get_config(db)
    if not cfg:
        raise NotFound(message="Pterodactyl configuration not found", code="pterodactyl_config_not_found")
    return cfg


@router.post("/config", response_model=PterodactylConfigOut, status_code=201)
def set_config(
    payload: PterodactylConfigCreate,
    current_user=Depends(AdminOnly),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    existing = _get_config(db)
    if existing:
        existing.panel_url = payload.panel_url
        existing.app_api_key_encrypted = encrypt_value(payload.app_api_key)
        existing.default_node_id = payload.default_node_id
        existing.default_location_id = payload.default_location_id
        existing.default_nest_id = payload.default_nest_id
        existing.default_egg_id = payload.default_egg_id
        existing.default_ram = payload.default_ram
        existing.default_cpu = payload.default_cpu
        existing.default_storage = payload.default_storage
        existing.default_disk = payload.default_disk
        existing.default_io = payload.default_io
        existing.default_overlimit = payload.default_overlimit
        existing.active = payload.active
        db.commit()
        db.refresh(existing)
        return existing
    cfg = PterodactylConfig(
        panel_url=payload.panel_url,
        app_api_key_encrypted=encrypt_value(payload.app_api_key),
        default_node_id=payload.default_node_id,
        default_location_id=payload.default_location_id,
        default_nest_id=payload.default_nest_id,
        default_egg_id=payload.default_egg_id,
        default_ram=payload.default_ram,
        default_cpu=payload.default_cpu,
        default_storage=payload.default_storage,
        default_disk=payload.default_disk,
        default_io=payload.default_io,
        default_overlimit=payload.default_overlimit,
        active=payload.active,
    )
    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg


@router.patch("/config", response_model=PterodactylConfigOut)
def update_config(
    payload: PterodactylConfigUpdate,
    current_user=Depends(AdminOnly),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    cfg = _get_config(db)
    if not cfg:
        raise NotFound(message="Pterodactyl configuration not found", code="pterodactyl_config_not_found")
    data = payload.model_dump(exclude_unset=True)
    if "app_api_key" in data and data["app_api_key"]:
        cfg.app_api_key_encrypted = encrypt_value(data.pop("app_api_key"))
    for key, value in data.items():
        setattr(cfg, key, value)
    db.commit()
    db.refresh(cfg)
    return cfg


class _TestConnectionBody(BaseModel):
    panel_url: str
    app_api_key: str


@router.post("/config/test", response_model=TestConnectionResponse)
async def test_connection(
    body: _TestConnectionBody = Body(...),
    current_user=Depends(AdminOnly),
):
    client = PterodactylAppClient(body.panel_url, body.app_api_key)
    try:
        result = await client.test_connection()
        return TestConnectionResponse(success=True, message=result.get("message", "Connected"), version=result.get("version"))
    except Exception as exc:  # noqa: BLE001
        return TestConnectionResponse(success=False, message=str(exc))


# -------- Admin: panel resources --------
@router.get("/users")
async def app_list_users(current_user=Depends(AdminOnly), db: Session = Depends(get_db)):
    client = _get_app_client(db)
    return await client.list_users()


@router.get("/servers")
async def app_list_servers(current_user=Depends(AdminOnly), db: Session = Depends(get_db)):
    client = _get_app_client(db)
    return await client.list_servers()


@router.get("/servers/{server_id}")
async def app_get_server(server_id: int, current_user=Depends(AdminOnly), db: Session = Depends(get_db)):
    client = _get_app_client(db)
    return await client.get_server(server_id)


@router.post("/servers/{server_id}/suspend")
async def app_suspend(server_id: int, current_user=Depends(AdminOnly), db: Session = Depends(get_db), _csrf=Depends(csrf_protect)):
    client = _get_app_client(db)
    return await client.suspend_server(server_id)


@router.post("/servers/{server_id}/unsuspend")
async def app_unsuspend(server_id: int, current_user=Depends(AdminOnly), db: Session = Depends(get_db), _csrf=Depends(csrf_protect)):
    client = _get_app_client(db)
    return await client.unsuspend_server(server_id)


@router.delete("/servers/{server_id}", status_code=204)
async def app_delete_server(server_id: int, current_user=Depends(AdminOnly), db: Session = Depends(get_db), _csrf=Depends(csrf_protect)):
    client = _get_app_client(db)
    await client.delete_server(server_id)
    return None


@router.get("/nodes")
async def app_nodes(current_user=Depends(AdminOnly), db: Session = Depends(get_db)):
    client = _get_app_client(db)
    return await client.list_nodes()


@router.get("/locations")
async def app_locations(current_user=Depends(AdminOnly), db: Session = Depends(get_db)):
    client = _get_app_client(db)
    return await client.list_locations()


@router.get("/nests")
async def app_nests(current_user=Depends(AdminOnly), db: Session = Depends(get_db)):
    client = _get_app_client(db)
    return await client.list_nests()


@router.get("/nests/{nest_id}/eggs")
async def app_eggs(nest_id: int, current_user=Depends(AdminOnly), db: Session = Depends(get_db)):
    client = _get_app_client(db)
    return await client.list_eggs(nest_id)


@router.get("/servers/{server_id}/allocations")
async def app_allocations(server_id: int, current_user=Depends(AdminOnly), db: Session = Depends(get_db)):
    client = _get_app_client(db)
    return await client.list_allocations(server_id)


# -------- Customer: connect own Client API key --------
@router.post("/client/connect")
async def client_connect(
    payload: ClientApiKeyConnect,
    current_user=Depends(CustomerOrStaff),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    panel_url = payload.panel_url or settings.PTERODACTYL_URL
    if not panel_url:
        raise Unauthorized(message="Pterodactyl panel URL not configured", code="pterodactyl_no_panel_url")
    client = PterodactylClientClient(panel_url, payload.client_api_key)
    try:
        account = await client.validate()
    except Unauthorized:
        raise Unauthorized(message="Invalid Pterodactyl client API key", code="invalid_client_key")
    except Exception as exc:  # noqa: BLE001
        raise Unauthorized(message=f"Could not validate key: {exc}", code="client_validation_failed")

    # Store encrypted key on the user record (per-customer credentials).
    current_user.pterodactyl_client_api_key_encrypted = encrypt_value(payload.client_api_key)
    current_user.pterodactyl_panel_url = panel_url
    # Pterodactyl account id
    attrs = account.get("attributes", {}) if isinstance(account, dict) else {}
    current_user.pterodactyl_user_id = attrs.get("id")
    db.commit()
    db.refresh(current_user)
    return {"success": True, "message": "Pterodactyl account connected", "panel_user": attrs.get("username") or attrs.get("email")}


@router.post("/client/revoke")
def client_revoke(
    current_user=Depends(CustomerOrStaff),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    current_user.pterodactyl_client_api_key_encrypted = None
    current_user.pterodactyl_panel_url = None
    current_user.pterodactyl_user_id = None
    db.commit()
    return {"success": True, "message": "Pterodactyl connection revoked"}


@router.get("/client/servers")
async def client_list_servers(current_user=Depends(CustomerOrStaff), db: Session = Depends(get_db)):
    if not current_user.pterodactyl_client_api_key_encrypted:
        return {"servers": [], "connected": False}
    client = PterodactylClientClient(current_user.pterodactyl_panel_url or settings.PTERODACTYL_URL, decrypt_value(current_user.pterodactyl_client_api_key_encrypted))
    servers = await client.list_servers()
    # Filter to servers the customer owns (panel already enforces this).
    return {"servers": servers, "connected": True}


@router.get("/client/servers/{server_id}")
async def client_get_server(server_id: int, current_user=Depends(CustomerOrStaff), db: Session = Depends(get_db)):
    if not current_user.pterodactyl_client_api_key_encrypted:
        raise Forbidden(message="Pterodactyl account not connected", code="not_connected")
    client = PterodactylClientClient(current_user.pterodactyl_panel_url or settings.PTERODACTYL_URL, decrypt_value(current_user.pterodactyl_client_api_key_encrypted))
    return await client.get_server(server_id)


@router.get("/client/servers/{server_id}/resources")
async def client_server_resources(server_id: int, current_user=Depends(CustomerOrStaff), db: Session = Depends(get_db)):
    if not current_user.pterodactyl_client_api_key_encrypted:
        raise Forbidden(message="Pterodactyl account not connected", code="not_connected")
    client = PterodactylClientClient(current_user.pterodactyl_panel_url or settings.PTERODACTYL_URL, decrypt_value(current_user.pterodactyl_client_api_key_encrypted))
    return await client.get_resources(server_id)


@router.post("/client/servers/{server_id}/power")
async def client_power(
    server_id: int,
    payload: dict[str, Any] = Body(...),
    current_user=Depends(CustomerOrStaff),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    if not current_user.pterodactyl_client_api_key_encrypted:
        raise Forbidden(message="Pterodactyl account not connected", code="not_connected")
    signal = payload.get("signal")
    if signal not in ("start", "stop", "restart", "kill"):
        raise Conflict(message="Invalid signal", code="invalid_signal")
    client = PterodactylClientClient(current_user.pterodactyl_panel_url or settings.PTERODACTYL_URL, decrypt_value(current_user.pterodactyl_client_api_key_encrypted))
    result = await client.power_action(server_id, signal)
    return {"success": True, "signal": signal, "result": result}


@router.get("/client/servers/{server_id}/console")
async def client_console(server_id: int, current_user=Depends(CustomerOrStaff), db: Session = Depends(get_db)):
    if not current_user.pterodactyl_client_api_key_encrypted:
        raise Forbidden(message="Pterodactyl account not connected", code="not_connected")
    client = PterodactylClientClient(current_user.pterodactyl_panel_url or settings.PTERODACTYL_URL, decrypt_value(current_user.pterodactyl_client_api_key_encrypted))
    return await client.get_console(server_id)
