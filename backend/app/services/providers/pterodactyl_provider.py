"""Pterodactyl infrastructure provider."""

import hashlib
from typing import Any

from app.services.providers.base import BaseProvider, ProvisionResult
from app.services.pterodactyl import PterodactylAppClient


class PterodactylProvider(BaseProvider):
    name = "pterodactyl"

    def __init__(self, panel_url: str, app_api_key: str) -> None:
        self.client = PterodactylAppClient(panel_url, app_api_key)

    def _server_payload(self, params: dict[str, Any]) -> dict[str, Any]:
        name = params.get("name") or f"server-{hashlib.sha1(str(params).encode()).hexdigest()[:8]}"
        return {
            "name": name,
            "user": params.get("pterodactyl_user_id") or params.get("user_id", 1),
            "nest": params.get("nest_id") or 1,
            "egg": params.get("egg_id") or 1,
            "docker_image": params.get("docker_image") or "parkervcp/yolks:java_17",
            "limits": {
                "memory": params.get("ram_mb") or 1024,
                "swap": -1,
                "disk": params.get("storage_mb") or 20480,
                "io": params.get("io") or 500,
                "cpu": params.get("cpu") or 100,
            },
            "allocation": {
                "default": params.get("allocation") or "auto",
            },
            "deploy": {
                "locations": [params.get("location_id") or 1],
                "dedicated_ip": False,
            },
            "start_on_completion": True,
            "oom_disabled": False,
        }

    async def provision(self, params: dict[str, Any]) -> ProvisionResult:
        try:
            payload = self._server_payload(params)
            data = await self.client.create_server(payload)
            return ProvisionResult(
                success=True,
                server_id=data.get("attributes", {}).get("id") if isinstance(data, dict) else None,
                details=data,
            )
        except Exception as exc:  # noqa: BLE001
            return ProvisionResult(success=False, error=str(exc))

    async def suspend(self, server_id: Any) -> ProvisionResult:
        try:
            await self.client.suspend_server(int(server_id))
            return ProvisionResult(success=True)
        except Exception as exc:  # noqa: BLE001
            return ProvisionResult(success=False, error=str(exc))

    async def unsuspend(self, server_id: Any) -> ProvisionResult:
        try:
            await self.client.unsuspend_server(int(server_id))
            return ProvisionResult(success=True)
        except Exception as exc:  # noqa: BLE001
            return ProvisionResult(success=False, error=str(exc))

    async def delete(self, server_id: Any) -> ProvisionResult:
        try:
            await self.client.delete_server(int(server_id))
            return ProvisionResult(success=True)
        except Exception as exc:  # noqa: BLE001
            return ProvisionResult(success=False, error=str(exc))

    async def get_info(self, server_id: Any) -> dict[str, Any]:
        try:
            return await self.client.get_server(int(server_id)) or {}
        except Exception as exc:  # noqa: BLE001
            return {"error": str(exc)}

    async def health(self) -> dict[str, Any]:
        try:
            await self.client.test_connection()
            return {"healthy": True}
        except Exception as exc:  # noqa: BLE001
            return {"healthy": False, "error": str(exc)}


class KVMProvider(BaseProvider):
    """Placeholder KVM VPS provider.

    KVM VPS provisioning is intentionally NOT implemented by default because
    Pterodactyl cannot provision KVM virtual machines. Wire a real KVM
    provider (e.g. Proxmox, OpenStack, libvirt) here before offering KVM VPS.
    """

    name = "kvm"

    async def provision(self, params: dict[str, Any]) -> ProvisionResult:
        return ProvisionResult(
            success=False,
            error="KVM VPS provider is not implemented. No compatible KVM infrastructure provider is wired.",
        )

    async def suspend(self, server_id: Any) -> ProvisionResult:
        return ProvisionResult(success=False, error="KVM provider not implemented")

    async def unsuspend(self, server_id: Any) -> ProvisionResult:
        return ProvisionResult(success=False, error="KVM provider not implemented")

    async def delete(self, server_id: Any) -> ProvisionResult:
        return ProvisionResult(success=False, error="KVM provider not implemented")

    async def get_info(self, server_id: Any) -> dict[str, Any]:
        return {"error": "KVM provider not implemented"}

    async def health(self) -> dict[str, Any]:
        return {"healthy": False, "error": "KVM provider not implemented"}
