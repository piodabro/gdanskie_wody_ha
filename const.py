"""Constants for the Gdańskie Wody integration."""

from homeassistant.components.light import SCAN_INTERVAL
from datetime import timedelta

DOMAIN = "gdanskie_wody"
API_HOST = "https://pomiary.gdanskiewody.pl/rest/"
API_STATIONS_URL = API_HOST + "stations"
API_MEASUREMENTS_BASE_URL = API_HOST + "measurements/"

CONF_API_KEY = "api_key"
CONF_STATION = "station"

SCAN_INTERVAL = timedelta(minutes=5)