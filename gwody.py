import aiohttp
import asyncio
import logging

from .const import API_STATIONS_URL
from .const import API_MEASUREMENTS_BASE_URL

_LOGGER = logging.getLogger(__name__)

class GdanskieWodyAPI:
    def __init__(self, api_key: str, session: asyncio.ClientSession = None) -> None:
        self._api_key = api_key
        self._auth_header = {"Authorization" : "Bearer " + api_key}
        self._session = session

    async def async_get_stations(self) -> Any:
        result = await session.get(API_STATIONS_URL, headers=self._auth_header)
        if(result.ok):
            return result.json()
        
        return None

    async def async_get_measurement(self, station: int, ) -> Any:
