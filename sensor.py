"""Platform for sensor integration."""
from __future__ import annotations
from dataclasses import dataclass
from collections.abc import Callable
from datetime import datetime
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PRECIPITATION_MILLIMETERS_PER_HOUR
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType, StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .gwody import GWMeasurement, GWMeasurements
from .coordinator import GWCoordinator
from .const import CONF_STATION, DOMAIN

_LOGGER = logging.getLogger(__name__)

# def setup_platform(
#     hass: HomeAssistant,
#     config: ConfigType,
#     add_entities: AddEntitiesCallback,
#     discovery_info: DiscoveryInfoType | None = None
# ) -> None:
#     """Set up the sensor platform."""
#     add_entities([RainSensorEntity()])

def get_meas_value(meas: GWMeasurements, date: datetime):
    if meas is not None:
        current = None
        _LOGGER.info(f"Dta len {len(meas.data)}")
        for dta in meas.data:
            _LOGGER.info(f"Dates: {dta.date} vs {date} -> {dta.date == date}")
            if dta.date == date:
                current = dta
                break
        # current = [dta for dta in meas.data if dta.date == date]
        if current is not None:
            _LOGGER.info(f"Read values are: {current.date} -> {current.value}")
            return current.value 
    _LOGGER.info(f"Read values are None")
    return None

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Rain sensor based on a config entry."""
    coordinator: GWCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensor_desc = GWSensorEntityDescription(
        key="rain",
        name=f"Rain_{coordinator.config_entry.data[CONF_STATION]}",
        native_unit_of_measurement=PRECIPITATION_MILLIMETERS_PER_HOUR,
        state_class=SensorStateClass.TOTAL,
        force_update=True,
        value_fn=get_meas_value  # lambda meas,date: [dta.value for dta in meas.data if dta.date == date].pop() if (meas is not None) else None
    )

    async_add_entities(
        [GWSensorEntity(coordinator, sensor_desc)]
    )

@dataclass
class GWSensorEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[[GWMeasurements, datetime], datetime | StateType]


@dataclass
class GWSensorEntityDescription(
    SensorEntityDescription, GWSensorEntityDescriptionMixin
):
    """Describes WLED sensor entity."""

    exists_fn: Callable[[GWMeasurements], bool] = lambda _: True

# SENSORS: tuple[GWSensorEntityDescription, ...] = (
    
# )

class GWSensorEntity(CoordinatorEntity[GWCoordinator], SensorEntity):
    """Representation of a GW Sensor."""

    entity_description: GWSensorEntityDescription

    def __init__(
        self,
        coordinator: GWCoordinator,
        description: GWSensorEntityDescription,
    ) -> None:
        """Initialize a GW sensor entity."""
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self._attr_name = f"{description.name}"
        self._attr_unique_id = f"gw_rain_{coordinator.config_entry.data[CONF_STATION]}"

    @property
    def native_value(self) -> datetime | StateType:
        """Return the state of the sensor."""
        date = datetime.utcnow()
        date = date.replace(minute=0, second=0, microsecond=0) # Returns a copy
        if self.last_reset is None or self.last_reset < date:
            prev_reset = self.last_reset
            self.entity_description.last_reset = date
            _LOGGER.info(f"Updated last_reset from {prev_reset} to {self.last_reset}")
        return self.entity_description.value_fn(self.coordinator.data, date)


    # def __init__(self, coordinator, description):
    #     super().__init__(coordinator)

    # @callback
    # def _handle_coordinator_update(self) -> None:
    #     return None

    # def update(self) -> None:
    #     """Fetch new state data for the sensor.

    #     This is the only method that should fetch new data for Home Assistant.
    #     """
    #     self._attr_native_value = 23