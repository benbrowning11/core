"""Support for OmletSmartcoop binary sensors."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import OmletEntity, OmletEntityDescription


@dataclass(kw_only=True, frozen=True)
class OmletBinarySensorEntityDescription(
    OmletEntityDescription, BinarySensorEntityDescription
):
    """Describes OmletSmartcoop binary sensor entity."""


BINARY_SENSOR_DESCRIPTIONS = [
    OmletBinarySensorEntityDescription(
        key="door_open",
        name="Door Sensor",
        device_class=BinarySensorDeviceClass.DOOR,
        icon="mdi:door",
        value_fn=lambda device: device.state.getStatusValue(("door", "state")),
        exists_fn=lambda device: device.state.isSet("door"),
    ),
    OmletBinarySensorEntityDescription(
        key="mains_powered",
        name="Mains Powered",
        device_class=BinarySensorDeviceClass.PLUG,
        icon="mdi:power-plug",
        value_fn=lambda device: device.state.getStatusValue(("general", "powerSource"))
        == "external",
        exists_fn=lambda device: device.state.isSet(("general", "powerSource")),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    _: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor based on a config entry."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    async_add_entities(
        OmletBinarySensor(coordinator, key, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
        for key, device in coordinator.data.items()
        if description.exists_fn(device)
    )


class OmletBinarySensor(OmletEntity, BinarySensorEntity):
    """Representation of an OmletSmartcoop binary sensor."""

    entity_description: OmletBinarySensorEntityDescription

    @property
    def is_on(self) -> bool:
        """Return the state of the binary sensor."""
        return self.entity_description.value_fn(self.omlet_device)
