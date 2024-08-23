"""Platform for light integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
import logging
from typing import Any

from smartcoop.api.models.action import Action
from smartcoop.api.models.device import Device

from homeassistant.components.light import (
    ColorMode,
    LightEntity,
    LightEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import OmletEntity, OmletEntityDescription

_LOGGER = logging.getLogger(__name__)


@dataclass(kw_only=True, frozen=True)
class OmletLightEntityDescription(OmletEntityDescription, LightEntityDescription):
    """Describes OmletSmartcoop Light entity."""

    get_turn_on_action: Callable[[Device], None | Action] = lambda _: None
    get_turn_off_action: Callable[[Device], None | Action] = lambda _: None
    color_mode: ColorMode = ColorMode.ONOFF
    supported_color_modes: set[ColorMode] = field(default_factory=set[ColorMode])


LIGHT_DESCRIPTIONS = [
    OmletLightEntityDescription(
        key="OmletAutodoorLight",
        name="Light",
        icon="mdi:lightbulb",
        get_turn_on_action=lambda device: [
            action for action in device.actions if action.name == "on"
        ][0],
        get_turn_off_action=lambda device: [
            action for action in device.actions if action.name == "off"
        ][0],
        value_fn=lambda device: device.state.light.state == "on",
        exists_fn=lambda device: device.state.light is not None,
        supported_color_modes={ColorMode.ONOFF},
    )
]


async def async_setup_entry(
    hass: HomeAssistant,
    _: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up light based on a config entry."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    async_add_entities(
        OmletLight(coordinator, key, description)
        for description in LIGHT_DESCRIPTIONS
        for key, device in coordinator.data.items()
        if description.exists_fn(device)
    )


class OmletLight(OmletEntity, LightEntity):
    """Representation of an OmletSmartcoop Light."""

    entity_description: OmletLightEntityDescription

    def __init__(
        self, coordinator, device_id, entity_description: OmletLightEntityDescription
    ) -> None:
        """Initialize an OmletSmartcoop Light."""
        super().__init__(coordinator, device_id, entity_description)
        self.color_mode = entity_description.color_mode
        self.supported_color_modes = entity_description.supported_color_modes

    @property
    def is_on(self) -> bool:
        """Return the state of the light."""
        return self.entity_description.value_fn(self.omlet_device)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn device on."""
        await self.coordinator.perform_action(
            self.entity_description.get_turn_on_action(self.omlet_device)
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn device off."""
        await self.coordinator.perform_action(
            self.entity_description.get_turn_off_action(self.omlet_device)
        )
        await self.coordinator.async_request_refresh()
