"""The OmletSmartcoop integration."""

from __future__ import annotations

import logging

from smartcoop.api.omlet import Omlet  # codespell:ignore omlet
from smartcoop.client import SmartCoopClient
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_TOKEN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_validation import string
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .coordinator import OmletApiCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.COVER,
    Platform.FAN,
    Platform.LIGHT,
    Platform.SENSOR,
    Platform.SWITCH,
]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_API_TOKEN): string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the smartcoop integration."""

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the smartcoop integration from a config entry."""
    _LOGGER.info("Setting up smartcoop integration")
    client_secret = entry.data[CONF_API_TOKEN]
    client = SmartCoopClient(client_secret=client_secret)
    omlet = Omlet(client)  # codespell:ignore omlet

    coordinator = OmletApiCoordinator(hass, omlet)  # codespell:ignore omlet

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["coordinator"] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True
