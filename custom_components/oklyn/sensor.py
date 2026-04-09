from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import UnitOfElectricPotential, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .entity import OklynCoordinatorEntity

SENSORS = (
    SensorEntityDescription(key="ph", name="pH", native_unit_of_measurement="pH", icon="mdi:ph"),
    SensorEntityDescription(key="orp", name="Redox", native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT, icon="mdi:flash"),
    SensorEntityDescription(key="water", name="Water Temperature", native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class="temperature"),
    SensorEntityDescription(key="air", name="Air Temperature", native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class="temperature"),
    SensorEntityDescription(key="salt", name="Salt", native_unit_of_measurement="g/L", icon="mdi:shaker-outline"),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities = [OklynMeasureSensor(coordinator, entry, description) for description in SENSORS]
    entities.extend([
        OklynAuxModeSensor(coordinator, entry, "aux", "Aux 1 Mode"),
        OklynAuxModeSensor(coordinator, entry, "aux2", "Aux 2 Mode"),
    ])
    async_add_entities(entities)


class OklynMeasureSensor(OklynCoordinatorEntity, SensorEntity):
    entity_description: SensorEntityDescription

    def __init__(self, coordinator, config_entry, description: SensorEntityDescription) -> None:
        super().__init__(coordinator, config_entry)
        self.entity_description = description
        self._attr_unique_id = f"{config_entry.entry_id}_{description.key}"
        self._attr_translation_key = description.key

    @property
    def native_value(self):
        payload = self.coordinator.data["measures"].get(self.entity_description.key, {})
        return payload.get("value")

    @property
    def extra_state_attributes(self):
        payload = self.coordinator.data["measures"].get(self.entity_description.key, {})
        return {
            "recorded": payload.get("recorded"),
            "status": payload.get("status"),
            "value_raw": payload.get("value_raw"),
        }


class OklynAuxModeSensor(OklynCoordinatorEntity, SensorEntity):
    _attr_icon = "mdi:tune-variant"

    def __init__(self, coordinator, config_entry, endpoint: str, name: str) -> None:
        super().__init__(coordinator, config_entry)
        self.endpoint = endpoint
        self._attr_name = name
        self._attr_unique_id = f"{config_entry.entry_id}_{endpoint}_mode"

    @property
    def native_value(self):
        payload = self.coordinator.data.get(self.endpoint, {})
        return payload.get("aux") or payload.get("aux2")

    @property
    def extra_state_attributes(self):
        payload = self.coordinator.data.get(self.endpoint, {})
        return {
            "status": payload.get("status"),
            "changed_at": payload.get("changed_at"),
        }
