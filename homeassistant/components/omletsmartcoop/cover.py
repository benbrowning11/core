"""Support for OmletSmartcoop cover."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from smartcoop.api.models.action import Action
from smartcoop.api.models.device import Device

from homeassistant.components.cover import (
    CoverDeviceClass,
    CoverEntity,
    CoverEntityDescription,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import OmletEntity, OmletEntityDescription


@dataclass(kw_only=True, frozen=True)
class OmletCoverEntityDescription(OmletEntityDescription, CoverEntityDescription):
    """Describes OmletSmartcoop cover entity."""

    get_open_action: Callable[[Device], None | Action] = lambda _: None
    get_close_action: Callable[[Device], None | Action] = lambda _: None
    supported_features: CoverEntityFeature | None = None


COVER_DESCRIPTIONS = [
    OmletCoverEntityDescription(
        key="SmartAutodoor",
        name="Door",
        device_class=CoverDeviceClass.DOOR,
        icon="mdi:door",
        supported_features=CoverEntityFeature.CLOSE | CoverEntityFeature.OPEN,
        get_open_action=lambda device: device.tryGetAction("open"),
        get_close_action=lambda device: device.tryGetAction("close"),
        value_fn=lambda device: device.state.getStatusValue(("door", "state")),
        exists_fn=lambda device: device.state.isSet("door"),
    )
]


async def async_setup_entry(
    hass: HomeAssistant,
    _: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up cover based on a config entry."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    async_add_entities(
        OmletCover(coordinator, key, description)
        for description in COVER_DESCRIPTIONS
        for key, device in coordinator.data.items()
        if description.exists_fn(device)
    )


class OmletCover(OmletEntity, CoverEntity):
    """Representation of an OmletSmartcoop cover/door."""

    entity_description: OmletCoverEntityDescription

    def __init__(
        self, coordinator, device_id, entity_description: OmletCoverEntityDescription
    ) -> None:
        """Initialize the OmletSmartcoop cover."""
        super().__init__(coordinator, device_id, entity_description)
        self._attr_supported_features = entity_description.supported_features

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Turn the entity on."""

        await self.coordinator.perform_action(
            self.entity_description.get_open_action(self.omlet_device)
        )
        await self.coordinator.async_request_refresh()

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await self.coordinator.perform_action(
            self.entity_description.get_close_action(self.omlet_device)
        )
        await self.coordinator.async_request_refresh()

    @property
    def is_closing(self) -> bool:
        """Is cover closing."""
        return self.entity_description.value_fn(self.omlet_device) == "closepending"

    @property
    def is_opening(self) -> bool:
        """Is cover opening."""
        return self.entity_description.value_fn(self.omlet_device) == "openpending"

    @property
    def is_closed(self) -> bool:
        """Is cover closed."""
        return self.entity_description.value_fn(self.omlet_device) == "closed"
