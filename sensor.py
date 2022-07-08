"""Platform for sensor integration."""
from __future__ import annotations
from dataclasses import dataclass
from collections.abc import Callable
from datetime import datetime

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

from .gwody import GWMeasurements
from .coordinator import GWCoordinator
from .const import CONF_STATION, DOMAIN

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    add_entities([RainSensorEntity()])

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Rain sensor based on a config entry."""
    coordinator: GWCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        RainSensorEntity(coordinator)
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

SENSORS: tuple[GWSensorEntityDescription, ...] = (
    GWSensorEntityDescription(
        key="rain",
        name="Rain",
        native_unit_of_measurement=PRECIPITATION_MILLIMETERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda meas: meas
    )
)

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
        return self.entity_description.value_fn(self.coordinator.data)

    def __init__(self, coordinator, description):
        super().__init__(coordinator)

    @callback
    def _handle_coordinator_update(self) -> None:
        return None

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._attr_native_value = 23