"""Define the OmletSmartcoop API coordinator."""

from asyncio import get_running_loop, timeout
from datetime import timedelta
import logging

from requests import exceptions as requests_exceptions
from smartcoop.api.models.device import Device
from smartcoop.api.omlet import Omlet  # codespell:ignore omlet

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class OmletApiCoordinator(DataUpdateCoordinator):
    """OmletSmartcoop API coordinator."""

    omlet: Omlet  # codespell:ignore omlet

    def __init__(
        self,
        hass: HomeAssistant,
        omlet: Omlet,  # codespell:ignore omlet
    ) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="OmletSmartcoop API Connection",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=30),
            # Set always_update to `False` if the data returned from the
            # api can be compared via `__eq__` to avoid duplicate updates
            # being dispatched to listeners
            always_update=True,
        )
        self.omlet = omlet  # codespell:ignore omlet

    def get_device(self, device_id) -> Device | None:
        """Get device by device_id."""
        return self.data.get(device_id)

    async def _async_setup(self):
        """Set up the coordinator."""
        return await self.async_fetch_data()

    async def _async_update_data(self):
        """Fetch data from OmletSmartcoop api. Performed in a single request."""
        return await self.async_fetch_data()

    async def async_fetch_data(self):
        """Fetch data from OmletSmartcoop api."""
        loop = get_running_loop()
        try:
            async with timeout(10):
                devices = await loop.run_in_executor(
                    None,
                    self.omlet.get_devices,  # codespell:ignore omlet
                )
                return {device.deviceId: device for device in devices}
        except requests_exceptions.HTTPError as err:
            if err.response.status_code == 401:
                raise ConfigEntryAuthFailed from err
            _LOGGER.error(err)

    async def perform_action(self, action):
        """Perform action on device."""
        loop = get_running_loop()
        try:
            async with timeout(10):
                await loop.run_in_executor(
                    None,
                    self.omlet.perform_action,  # codespell:ignore omlet
                    action,
                )
        except requests_exceptions.HTTPError as err:
            if err.response.status_code == 401:
                raise ConfigEntryAuthFailed from err
            _LOGGER.error(err)
