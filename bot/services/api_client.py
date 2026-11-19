"""HTTP client for the Hosting Platform backend (bot scope)."""

import os

import httpx

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BOT_API_KEY = os.getenv("BOT_API_KEY", "")

HEADERS = {"X-Bot-Key": BOT_API_KEY, "Content-Type": "application/json"}


class BackendClient:
    def __init__(self, base_url: str = BACKEND_URL, api_key: str = BOT_API_KEY) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = {"X-Bot-Key": api_key, "Content-Type": "application/json"}

    async def get_order(self, reference: str) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(f"{self.base_url}/api/v1/bot/orders/{reference}", headers=self.headers)
            r.raise_for_status()
            return r.json()

    async def list_orders(self, status: str | None = None) -> list:
        async with httpx.AsyncClient(timeout=20) as client:
            params = {"status": status} if status else {}
            r = await client.get(f"{self.base_url}/api/v1/bot/orders", headers=self.headers, params=params)
            r.raise_for_status()
            return r.json()

    async def approve_order(self, reference: str) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(f"{self.base_url}/api/v1/bot/orders/{reference}/approve", headers=self.headers)
            r.raise_for_status()
            return r.json()

    async def reject_order(self, reference: str, reason: str = "") -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(f"{self.base_url}/api/v1/bot/orders/{reference}/reject", headers=self.headers, params={"reason": reason})
            r.raise_for_status()
            return r.json()

    async def get_customer(self, user_id: int) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(f"{self.base_url}/api/v1/bot/customers/{user_id}", headers=self.headers)
            r.raise_for_status()
            return r.json()

    async def get_customer_by_discord(self, discord_id: str) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(f"{self.base_url}/api/v1/bot/customers/by-discord/{discord_id}", headers=self.headers)
            r.raise_for_status()
            return r.json()

    async def get_service(self, service_id: int) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(f"{self.base_url}/api/v1/bot/services/{service_id}", headers=self.headers)
            r.raise_for_status()
            return r.json()
