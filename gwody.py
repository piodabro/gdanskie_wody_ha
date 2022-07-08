from array import array
import aiohttp
import asyncio
import logging
from datetime import datetime
from datetime import timedelta

from homeassistant.backports.enum import StrEnum

from .const import API_STATIONS_URL
from .const import API_MEASUREMENTS_BASE_URL

_LOGGER = logging.getLogger(__name__)

class GWStatus(StrEnum):
    """Enumeration representing GW response status."""

    SUCCESS = "success" 
    ERROR = "error"
    NONE = "none"

class GWMeasurement:
    date: datetime
    value: float

    def __init__(self, data: list):
        self.date = data[0]
        self.value = float(data[1])

class GWMeasurements:
    """Represents GW API Measurements result"""

    status: GWStatus
    data: list = []
    message: str

    def __init__(self, status: GWStatus = GWStatus.NONE, data: list = [], message = ""):
        self.status = status

        for entry in data:
            self.data.append(GWMeasurement(entry))
        self.data = data
        self.message = message

    def get_current_measurement(self, date: datetime):
        self.data

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

    async def async_get_measurement(self, station: int, date: datetime) -> GWMeasurements | None:
        """Fetch desired station measurement data
           NOTE: Gdanskie Wody API returns data for whole day starting at 6 AM ending at 6AM of the next date...
        """

        api_date = date
        if(date.hour < 6):
            api_date = date - timedelta(day=1)

        date_str = api_date.strftime("%Y-%m-%d")
        result = await self._session.get(API_MEASUREMENTS_BASE_URL + f'{station}/rain/{date_str}')

        if result.ok:
            result_json = await result.json()
            if result_json["status"] == GWStatus.SUCCESS:
                result: GWMeasurements = GWMeasurements(status=result_json["status"], data=result_json["data"], message=result_json["message"])
                return result

        return None

