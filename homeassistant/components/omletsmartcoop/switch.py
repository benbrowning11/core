"""Support for OmletSmartcoop switches."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from smartcoop.api.models.action import Action
from smartcoop.api.models.device import Device

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import OmletEntity, OmletEntityDescription


@dataclass(kw_only=True, frozen=True)
class OmletSwitchEntityDescription(OmletEntityDescription, SwitchEntityDescription):
    """Describes OmletSmartcoop switch entity."""

    get_turn_on_action: Callable[[Device], None | Action] = lambda _: None
    get_turn_off_action: Callable[[Device], None | Action] = lambda _: None


SWITCH_DESCRIPTIONS: list[OmletSwitchEntityDescription] = []


async def async_setup_entry(
    hass: HomeAssistant,
    _: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch based on a config entry."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    async_add_entities(
        OmletSwitch(coordinator, key, description)
        for description in SWITCH_DESCRIPTIONS
        for key, device in coordinator.data.items()
        if description.exists_fn(device)
    )


class OmletSwitch(OmletEntity, SwitchEntity):
    """Representation of an OmletSmartcoop switch."""

    entity_description: OmletSwitchEntityDescription

    def __init__(
        self, coordinator, device_id, entity_description: OmletSwitchEntityDescription
    ) -> None:
        """Initialize the OmletSmartcoop switch."""
        super().__init__(coordinator, device_id, entity_description)

    @property
    def is_on(self) -> bool:
        """Return the reading of this switch."""
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
