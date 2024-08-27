"""The smartcoop base entity."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from smartcoop.api.models.device import Device

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.typing import UNDEFINED
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import OmletApiCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(kw_only=True, frozen=True)
class OmletEntityDescription(EntityDescription):
    """OmletSmartcoop entity description."""

    name: str | None
    exists_fn: Callable[[Device], bool] = lambda _: False
    value_fn: Callable[[Device], Any] = lambda _: None
    available: Callable[[Device], bool] = lambda _: True


class OmletEntity(CoordinatorEntity):
    """Base entity for the smartcoop integration."""

    _attr_has_entity_name = True
    entity_description: OmletEntityDescription
    coordinator: OmletApiCoordinator

    def __init__(
        self,
        coordinator: OmletApiCoordinator,
        device_id: str,
        entity_description: OmletEntityDescription,
    ) -> None:
        """Initialize the entity with the API key."""
        super().__init__(coordinator, context=device_id)
        self._device_id = device_id
        self.entity_description = entity_description
        self._device = coordinator.get_device(device_id)
        self._attr_unique_id = f"{device_id}_{entity_description.key}"
        self._attr_name = entity_description.name

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._device = self.coordinator.data[self._device_id]
        self.async_write_ha_state()

    @property
    def omlet_device(self) -> Device:
        """Return the device."""
        return self._device

    @property
    def name(self) -> str | None:
        """Return the name of the entity."""
        suggested_name = super().name
        return None if suggested_name is UNDEFINED else suggested_name

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self.omlet_device.name,
            manufacturer="Omlet",  # codespell:ignore omlet
            model=self.omlet_device.deviceType,
            sw_version=self.omlet_device.state.getStatusValue(
                ("general", "firmwareVersionCurrent")
            ),
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.entity_description.available(self.omlet_device)
