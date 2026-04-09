from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

from .const import API_BASE


class OklynApiError(Exception):
    """General API error."""


class OklynAuthError(OklynApiError):
    """Authentication error."""


class OklynClient:
    def __init__(self, session: aiohttp.ClientSession, api_token: str, device_id: str) -> None:
        self._session = session
        self._api_token = api_token
        self._device_id = device_id

    @property
    def headers(self) -> dict[str, str]:
        return {"X-API-TOKEN": self._api_token}

    def _url(self, path: str) -> str:
        return f"{API_BASE}/device/{self._device_id}/{path}"

    async def _request(self, method: str, path: str, json_data: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            async with self._session.request(
                method,
                self._url(path),
                headers=self.headers,
                json=json_data,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as resp:
                if resp.status in (401, 403):
                    raise OklynAuthError(f"Authentication failed: {resp.status}")
                if resp.status >= 400:
                    text = await resp.text()
                    raise OklynApiError(f"API error {resp.status}: {text}")
                data = await resp.json()
                if not isinstance(data, dict):
                    raise OklynApiError("Unexpected response format")
                return data
        except asyncio.TimeoutError as err:
            raise OklynApiError("Timeout while contacting Oklyn API") from err
        except aiohttp.ClientError as err:
            raise OklynApiError(f"Client error while contacting Oklyn API: {err}") from err

    async def validate(self) -> None:
        await self.get_pump()

    async def get_measure(self, measure: str) -> dict[str, Any]:
        return await self._request("GET", f"data/{measure}")

    async def get_pump(self) -> dict[str, Any]:
        return await self._request("GET", "pump")

    async def set_pump(self, mode: str) -> None:
        await self._request("PUT", "pump", {"pump": mode})

    async def get_aux(self) -> dict[str, Any]:
        return await self._request("GET", "aux")

    async def set_aux(self, value: str) -> None:
        await self._request("PUT", "aux", {"aux": value})

    async def get_aux2(self) -> dict[str, Any]:
        return await self._request("GET", "aux2")

    async def set_aux2(self, value: str) -> None:
        await self._request("PUT", "aux2", {"aux": value})
