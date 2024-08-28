"""Support for OmletSmartcoop fan."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from smartcoop.api.models.action import Action
from smartcoop.api.models.device import Device

from homeassistant.components.fan import (
    FanEntity,
    FanEntityDescription,
    FanEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import OmletEntity, OmletEntityDescription


@dataclass(kw_only=True, frozen=True)
class OmletFanDescription(OmletEntityDescription, FanEntityDescription):
    """Describes OmletSmartcoop fan entity."""

    get_turn_on_action: Callable[[Device], None | Action] = lambda _: None
    get_turn_off_action: Callable[[Device], None | Action] = lambda _: None
    get_boost_action: Callable[[Device], None | Action] = lambda _: None
    available: Callable[[Device], bool] = lambda _: True
    supported_features: FanEntityFeature = FanEntityFeature(0)


FAN_DESCRIPTIONS: list[OmletFanDescription] = [
    OmletFanDescription(
        key="OmletFanSwitch",
        name="Fan",
        icon="mdi:fan",
        get_turn_on_action=lambda device: device.tryGetAction("on"),
        get_turn_off_action=lambda device: device.tryGetAction("off"),
        get_boost_action=lambda device: device.tryGetAction("boost"),
        value_fn=lambda device: device.state.getStatusValue(("fan", "state")),
        exists_fn=lambda device: device.state.isSet("fan"),
        supported_features=FanEntityFeature.TURN_OFF
        | FanEntityFeature.TURN_ON
        | FanEntityFeature.PRESET_MODE,
    )
]


async def async_setup_entry(
    hass: HomeAssistant,
    _: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up fan based on a config entry."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    async_add_entities(
        OmletFan(coordinator, key, description)
        for description in FAN_DESCRIPTIONS
        for key, device in coordinator.data.items()
        if description.exists_fn(device)
    )


ORDERED_FAN_SPEEDS: list[str] = ["on", "boost"]


class OmletFan(OmletEntity, FanEntity):
    """Representation of an OmletSmartcoop fan."""

    entity_description: OmletFanDescription

    def __init__(
        self, coordinator, device_id, entity_description: OmletFanDescription
    ) -> None:
        """Initialize the OmletSmartcoop fan."""
        super().__init__(coordinator, device_id, entity_description)
        self.supported_features = entity_description.supported_features

    @property
    def is_on(self) -> bool:
        """Return the reading of this fan."""
        return self.entity_description.value_fn(self.omlet_device) != "off"

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        state = self.entity_description.value_fn(self.omlet_device)
        return None if state == "off" else state

    @property
    def preset_modes(self) -> list[str]:
        """Return the list of available preset modes."""
        return ORDERED_FAN_SPEEDS

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        speed: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn device on."""
        func = (
            self.entity_description.get_boost_action
            if preset_mode == "boost"
            else self.entity_description.get_turn_on_action
        )
        await self.coordinator.perform_action(func(self.omlet_device))
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn device off."""
        await self.coordinator.perform_action(
            self.entity_description.get_turn_off_action(self.omlet_device)
        )
        await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        func = (
            self.entity_description.get_boost_action
            if preset_mode == "boost"
            else self.entity_description.get_turn_on_action
        )
        await self.coordinator.perform_action(func(self.omlet_device))
        await self.coordinator.async_request_refresh()

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return len(ORDERED_FAN_SPEEDS)
