"""KVM VPS provider (placeholder - not implemented).

KVM VPS provisioning is intentionally NOT implemented by default because
Pterodactyl cannot provision KVM virtual machines. Wire a real KVM
provider (e.g. Proxmox, OpenStack, libvirt) here before offering KVM VPS.
"""

from app.services.providers.base import BaseProvider, ProvisionResult


class KVMProvider(BaseProvider):
    name = "kvm"

    async def provision(self, params):
        return ProvisionResult(success=False, error="KVM VPS provider is not implemented. No compatible KVM infrastructure provider is wired.")

    async def suspend(self, server_id):
        return ProvisionResult(success=False, error="KVM provider not implemented")

    async def unsuspend(self, server_id):
        return ProvisionResult(success=False, error="KVM provider not implemented")

    async def delete(self, server_id):
        return ProvisionResult(success=False, error="KVM provider not implemented")

    async def get_info(self, server_id):
        return {"error": "KVM provider not implemented"}

    async def health(self):
        return {"healthy": False, "error": "KVM provider not implemented"}
