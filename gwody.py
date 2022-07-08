import aiohttp
import asyncio
import logging
from datetime import datetime
from datetime import timedelta

from .const import API_STATIONS_URL
from .const import API_MEASUREMENTS_BASE_URL

_LOGGER = logging.getLogger(__name__)

class GdanskieWodyAPI:
    def __init__(self, api_key: str, session: aiohttp.ClientSession = None) -> None:
        self._api_key = api_key
        self._auth_header = {"Authorization" : "Bearer " + api_key}
        self._session = session

    async def async_get_stations(self):
        """Fetch station list with their features"""
        result = await self._session.get(API_STATIONS_URL, headers=self._auth_header)
        if(result.ok):
            return await result.json()
        
        return None

    async def async_get_measurement(self, station: int, date: datetime):
        """Fetch desired station measurement data
           NOTE: Gdanskie Wody API returns data for whole day starting at 6 AM ending at 6AM of the next date...
        """

        api_date = date
        if(date.hour < 6):
            api_date = date - timedelta(day = (date.day-1))

        date_str = api_date.strftime("%Y-%m-%d")
        result = await self._session.get(API_MEASUREMENTS_BASE_URL + f'{station}/rain/{date_str}')

        if result.ok:
            return await result.json()

        return None

