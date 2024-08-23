"""Config flow for OmletSmartcoop integration."""

from __future__ import annotations

import logging

from smartcoop.api.omlet import Omlet  # codespell:ignore omlet
from smartcoop.client import SmartCoopClient
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_TOKEN

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class OmletConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OmletSmartcoop."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        config_entry = self._async_current_entries()
        if config_entry:
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            api_key = user_input[CONF_API_TOKEN]
            try:
                client = SmartCoopClient(client_secret=api_key)
                Omlet(client)  # codespell:ignore omlet
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input[CONF_API_TOKEN])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="OmletSmartcoop", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_TOKEN): str,
                }
            ),
            errors=errors,
        )
