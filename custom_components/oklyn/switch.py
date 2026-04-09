from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import OklynCoordinatorEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]
    async_add_entities([
        OklynAuxConditionalSwitch(coordinator, entry, client, "aux", "Aux 1"),
        OklynAuxConditionalSwitch(coordinator, entry, client, "aux2", "Aux 2"),
    ])


class OklynAuxConditionalSwitch(OklynCoordinatorEntity, SwitchEntity):
    _attr_icon = "mdi:toggle-switch-variant"

    def __init__(self, coordinator, config_entry, client, endpoint: str, name: str) -> None:
        super().__init__(coordinator, config_entry)
        self.client = client
        self.endpoint = endpoint
        self._attr_name = name
        self._attr_unique_id = f"{config_entry.entry_id}_{endpoint}_switch"

    @property
    def available(self):
        payload = self.coordinator.data.get(self.endpoint, {})
        command = payload.get("aux") or payload.get("aux2")
        return super().available and command in ("on", "off")

    @property
    def is_on(self):
        payload = self.coordinator.data.get(self.endpoint, {})
        return payload.get("status") == "on"

    @property
    def extra_state_attributes(self):
        payload = self.coordinator.data.get(self.endpoint, {})
        return {
            "command": payload.get("aux") or payload.get("aux2"),
            "changed_at": payload.get("changed_at"),
        }

    async def async_turn_on(self, **kwargs):
        if self.endpoint == "aux2":
            await self.client.set_aux2("on")
        else:
            await self.client.set_aux("on")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        if self.endpoint == "aux2":
            await self.client.set_aux2("off")
        else:
            await self.client.set_aux("off")
        await self.coordinator.async_request_refresh()
