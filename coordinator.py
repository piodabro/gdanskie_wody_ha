from datetime import timedelta
import logging

import async_timeout

from homeassistant.components.light import LightEntity
from homeassistant.core import callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN
from .gwody import GdanskieWodyAPI

_LOGGER = logging.getLogger(__name__)

class GWCoordinator(DataUpdateCoordinator):
    """Gdanskie Wody data update coordinator."""

    def __init__(self, hass: HomeAssistant, gw_api: GdanskieWodyAPI):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Gdanskie Wody",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(hours=1),
        )
        self._gw_api = gw_api

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(10):
                return await self._gw_api.async_get_measurement()
        except ApiAuthError as err:
            # Raising ConfigEntryAuthFailed will cancel future updates
            # and start a config flow with SOURCE_REAUTH (async_step_reauth)
            raise ConfigEntryAuthFailed from err
        except ApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")