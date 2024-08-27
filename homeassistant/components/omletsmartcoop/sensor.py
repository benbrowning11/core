"""Support for OmletSmartcoop sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from smartcoop.api.models.device import Device

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN
from .entity import OmletEntity, OmletEntityDescription


@dataclass(kw_only=True, frozen=True)
class OmletSensorEntityDescription(OmletEntityDescription, SensorEntityDescription):
    """Describes OmletSmartcoop sensor entity."""

    value_fn: Callable[[Device], StateType]


SENSOR_DESCRIPTIONS = [
    OmletSensorEntityDescription(
        key="battery",
        name="Battery Level",
        device_class=SensorDeviceClass.BATTERY,
        icon="mdi:battery",
        value_fn=lambda device: device.state.getStatusValue(
            ("general", "batteryLevel")
        ),
        exists_fn=lambda device: device.state.isSet("general.batteryLevel") is not None
        and device.state.isSet(("general", "powerSource"))
        and device.state.getStatusValue(("general", "powerSource")) != "external",
        unit_of_measurement=PERCENTAGE,
        native_unit_of_measurement=PERCENTAGE,
        state_class="measurement",
    )
]


async def async_setup_entry(
    hass: HomeAssistant,
    _: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor based on a config entry."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    async_add_entities(
        OmletSensor(coordinator, key, description)
        for description in SENSOR_DESCRIPTIONS
        for key, device in coordinator.data.items()
        if description.exists_fn(device)
    )


class OmletSensor(OmletEntity, SensorEntity):
    """Representation of an OmletSmartcoop sensor."""

    entity_description: OmletSensorEntityDescription

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._device = self.coordinator.data[self._device_id]
        self.native_value = self.entity_description.value_fn(self._device)
        self.async_write_ha_state()
