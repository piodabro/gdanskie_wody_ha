from datetime import timedelta
import logging

import async_timeout

from homeassistant.components.light import LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback, HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from datetime import datetime

from .const import CONF_API_KEY, CONF_STATION, DOMAIN, SCAN_INTERVAL
from .gwody import GWMeasurements, GdanskieWodyAPI

_LOGGER = logging.getLogger(__name__)

class GWCoordinator(DataUpdateCoordinator[GWMeasurements]):
    """Gdanskie Wody data update coordinator."""

    def __init__(self, hass: HomeAssistant, * , entry: ConfigEntry):
        """Initialize my coordinator."""
        self._gw_api = GdanskieWodyAPI(entry.data[CONF_API_KEY], async_get_clientsession(hass))
        self._station = entry.data[CONF_STATION]

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(10):
                return await self._gw_api.async_get_measurement(self._station, datetime.utcnow())
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")