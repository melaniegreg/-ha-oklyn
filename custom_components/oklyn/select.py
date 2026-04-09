from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import OklynCoordinatorEntity

PUMP_OPTIONS = ["off", "auto", "on"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]
    async_add_entities([OklynPumpModeSelect(coordinator, entry, client)])


class OklynPumpModeSelect(OklynCoordinatorEntity, SelectEntity):
    _attr_name = "Pump Mode"
    _attr_options = PUMP_OPTIONS
    _attr_icon = "mdi:pump"

    def __init__(self, coordinator, config_entry, client) -> None:
        super().__init__(coordinator, config_entry)
        self.client = client
        self._attr_unique_id = f"{config_entry.entry_id}_pump_mode"

    @property
    def current_option(self):
        return self.coordinator.data.get("pump", {}).get("pump")

    @property
    def extra_state_attributes(self):
        payload = self.coordinator.data.get("pump", {})
        return {
            "status": payload.get("status"),
            "changed_at": payload.get("changed_at"),
        }

    async def async_select_option(self, option: str) -> None:
        await self.client.set_pump(option)
        await self.coordinator.async_request_refresh()
