from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import OklynCoordinatorEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([
        OklynPumpRunningBinarySensor(coordinator, entry),
        OklynAuxActiveBinarySensor(coordinator, entry, "aux", "Aux 1 Active"),
        OklynAuxActiveBinarySensor(coordinator, entry, "aux2", "Aux 2 Active"),
    ])


class OklynPumpRunningBinarySensor(OklynCoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Pump Running"
    _attr_icon = "mdi:pump"

    def __init__(self, coordinator, config_entry) -> None:
        super().__init__(coordinator, config_entry)
        self._attr_unique_id = f"{config_entry.entry_id}_pump_running"

    @property
    def is_on(self):
        return self.coordinator.data.get("pump", {}).get("status") == "on"

    @property
    def extra_state_attributes(self):
        payload = self.coordinator.data.get("pump", {})
        return {"mode": payload.get("pump"), "changed_at": payload.get("changed_at")}


class OklynAuxActiveBinarySensor(OklynCoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_icon = "mdi:flash-outline"

    def __init__(self, coordinator, config_entry, endpoint: str, name: str) -> None:
        super().__init__(coordinator, config_entry)
        self.endpoint = endpoint
        self._attr_name = name
        self._attr_unique_id = f"{config_entry.entry_id}_{endpoint}_active"

    @property
    def is_on(self):
        return self.coordinator.data.get(self.endpoint, {}).get("status") == "on"

    @property
    def extra_state_attributes(self):
        payload = self.coordinator.data.get(self.endpoint, {})
        return {"mode": payload.get("aux") or payload.get("aux2"), "changed_at": payload.get("changed_at")}
