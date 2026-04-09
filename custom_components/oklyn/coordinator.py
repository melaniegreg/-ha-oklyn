from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import OklynApiError, OklynClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
MEASURES = ("ph", "orp", "water", "air", "salt")


class OklynDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, client: OklynClient, scan_interval: int) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=scan_interval))
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            data: dict[str, Any] = {"measures": {}}
            for measure in MEASURES:
                data["measures"][measure] = await self.client.get_measure(measure)
            data["pump"] = await self.client.get_pump()
            data["aux"] = await self.client.get_aux()
            data["aux2"] = await self.client.get_aux2()
            return data
        except OklynApiError as err:
            raise UpdateFailed(str(err)) from err
