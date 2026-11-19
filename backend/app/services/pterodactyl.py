"""Pterodactyl panel integration (Application API + Client API).

All requests are made server-side. Application API keys are never exposed to
the frontend. Customer Client API keys are stored encrypted at rest.
"""

from typing import Any, Dict, List, Optional

import httpx

from app.config import settings
from app.exceptions import ExternalServiceError, Forbidden, NotFound, Unauthorized
from app.logging import setup_logging
from app.security import decrypt_value, encrypt_value

logger = setup_logging() if False else __import__("logging").getLogger("hosting.services.pterodactyl")


def _headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"{settings.APP_NAME}/{settings.APP_VERSION}",
    }


def _panel_base(panel_url: str) -> str:
    return panel_url.rstrip("/")


class PterodactylAppClient:
    """Client for the Pterodactyl Application API (admin scope)."""

    def __init__(self, panel_url: str, app_api_key: str, timeout: int | None = None) -> None:
        self.panel_url = _panel_base(panel_url)
        self.api_key = app_api_key
        self.timeout = timeout or settings.PTERODACTYL_API_TIMEOUT

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.panel_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.request(method, url, headers=_headers(self.api_key), **kwargs)
        except httpx.RequestError as exc:
            logger.error("Pterodactyl request failed", extra={"url": url, "error": str(exc)})
            raise ExternalServiceError(message="Unable to reach Pterodactyl panel", details={"url": url, "reason": str(exc)})
        return self._handle_response(resp, url)

    @staticmethod
    def _handle_response(resp: httpx.Response, url: str) -> Any:
        try:
            body = resp.json()
        except Exception:  # noqa: BLE001
            body = {}
        if resp.status_code == 401:
            raise Unauthorized(message="Pterodactyl API key is invalid", code="pterodactyl_unauthorized")
        if resp.status_code == 403:
            raise Forbidden(message="Pterodactyl API key lacks permission", code="pterodactyl_forbidden")
        if resp.status_code == 404:
            raise NotFound(message="Pterodactyl resource not found", code="pterodactyl_not_found")
        if resp.status_code >= 400:
            detail = body.get("error") or body.get("errors") or str(body)
            raise ExternalServiceError(
                message="Pterodactyl API error",
                code="pterodactyl_error",
                status_code=resp.status_code,
                details={"url": url, "status": resp.status_code, "detail": detail},
            )
        return body

    # ----- Application API operations -----
    async def test_connection(self) -> dict[str, Any]:
        """Perform an actual API request to verify credentials."""
        try:
            data = await self._request("GET", "/api/application/users")
        except Unauthorized:
            raise
        except ExternalServiceError:
            raise
        version = None
        try:
            # Try to fetch panel version if endpoint exists.
            version_data = await self._request("GET", "/api/application/servers")
            version = "ok"
        except Exception:  # noqa: BLE001
            version = None
        return {"success": True, "message": "Connected to Pterodactyl panel", "version": version, "users_count": len(data) if isinstance(data, list) else None}

    async def list_users(self) -> List[dict[str, Any]]:
        return await self._request("GET", "/api/application/users") or []

    async def list_servers(self) -> List[dict[str, Any]]:
        return await self._request("GET", "/api/application/servers") or []

    async def get_server(self, server_id: int) -> dict[str, Any]:
        return await self._request("GET", f"/api/application/servers/{server_id}") or {}

    async def create_server(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request("POST", "/api/application/servers", json=payload) or {}

    async def suspend_server(self, server_id: int) -> dict[str, Any]:
        return await self._request("POST", f"/api/application/servers/{server_id}/suspend") or {}

    async def unsuspend_server(self, server_id: int) -> dict[str, Any]:
        return await self._request("POST", f"/api/application/servers/{server_id}/unsuspend") or {}

    async def delete_server(self, server_id: int) -> dict[str, Any]:
        return await self._request("DELETE", f"/api/application/servers/{server_id}") or {}

    async def list_nodes(self) -> List[dict[str, Any]]:
        return await self._request("GET", "/api/application/nodes") or []

    async def list_locations(self) -> List[dict[str, Any]]:
        return await self._request("GET", "/api/application/locations") or []

    async def list_nests(self) -> List[dict[str, Any]]:
        return await self._request("GET", "/api/application/nests") or []

    async def list_eggs(self, nest_id: int) -> List[dict[str, Any]]:
        return await self._request("GET", f"/api/application/nests/{nest_id}/eggs") or []

    async def list_allocations(self, server_id: int) -> List[dict[str, Any]]:
        return await self._request("GET", f"/api/application/servers/{server_id}/allocations") or []


class PterodactylClientClient:
    """Client for the Pterodactyl Client API (customer scope)."""

    def __init__(self, panel_url: str, client_api_key: str, timeout: int | None = None) -> None:
        self.panel_url = _panel_base(panel_url)
        self.api_key = client_api_key
        self.timeout = timeout or settings.PTERODACTYL_API_TIMEOUT

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.panel_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.request(method, url, headers=_headers(self.api_key), **kwargs)
        except httpx.RequestError as exc:
            logger.error("Pterodactyl client request failed", extra={"url": url, "error": str(exc)})
            raise ExternalServiceError(message="Unable to reach Pterodactyl panel", details={"url": url, "reason": str(exc)})
        return self._handle_response(resp, url)

    @staticmethod
    def _handle_response(resp: httpx.Response, url: str) -> Any:
        try:
            body = resp.json()
        except Exception:  # noqa: BLE001
            body = {}
        if resp.status_code == 401:
            raise Unauthorized(message="Pterodactyl client API key is invalid", code="pterodactyl_client_unauthorized")
        if resp.status_code == 403:
            raise Forbidden(message="Not permitted to access this resource", code="pterodactyl_client_forbidden")
        if resp.status_code == 404:
            raise NotFound(message="Pterodactyl resource not found", code="pterodactyl_client_not_found")
        if resp.status_code >= 400:
            detail = body.get("error") or body.get("errors") or str(body)
            raise ExternalServiceError(
                message="Pterodactyl client API error",
                code="pterodactyl_client_error",
                status_code=resp.status_code,
                details={"url": url, "status": resp.status_code, "detail": detail},
            )
        return body

    async def validate(self) -> dict[str, Any]:
        """Validate credentials by fetching the authenticated account."""
        return await self._request("GET", "/api/client/account") or {}

    async def list_servers(self) -> List[dict[str, Any]]:
        return await self._request("GET", "/api/client/servers") or []

    async def get_server(self, server_id: int) -> dict[str, Any]:
        return await self._request("GET", f"/api/client/servers/{server_id}") or {}

    async def get_resources(self, server_id: int) -> dict[str, Any]:
        return await self._request("GET", f"/api/client/servers/{server_id}/resources") or {}

    async def power_action(self, server_id: int, signal: str) -> dict[str, Any]:
        """signal: start | stop | restart | kill"""
        return await self._request("POST", f"/api/client/servers/{server_id}/power", json={"signal": signal}) or {}

    async def get_console(self, server_id: int) -> dict[str, Any]:
        """Get console connection info (returns websocket/connection details where available)."""
        return await self._request("GET", f"/api/client/servers/{server_id}/console") or {}
