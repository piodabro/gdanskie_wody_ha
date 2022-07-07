"""Config flow for Gdańskie Wody integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import aiohttp

from .const import DOMAIN
from .const import API_HOST

# import requests
import json

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("api_key"): str,
        vol.Required("station"): int,
    }
)


class ApiConfigValidator:
    """Placeholder class to make tests pass.

    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self) -> None:
        """Initialize."""

    async def authenticate(self, hass: HomeAssistant, api_key: str) -> bool:
        """Test if we can authenticate with the host."""

        auth_header = {"Authorization" : "Bearer " + api_key}
        session: aiohttp.ClientSession = async_get_clientsession(hass)
        test_url = API_HOST + "stations"
        _LOGGER.info(test_url)

        result = await session.get(test_url, headers=auth_header)

        if(result.ok):
            res_json = await result.json()
            _LOGGER.info(res_json)
            if(res_json["status"] == "success"):
                return True
        
        return False


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data["username"], data["password"]
    # )

    validator = ApiConfigValidator()

    try:
        if not await validator.authenticate(hass, data["api_key"]):
            raise InvalidAuth
    except ConnectionError:
        raise CannotConnect
    except InvalidAuth:
        raise InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": "Gdańskie wody - " + str(data["station"])}


class GWConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Gdańskie Wody."""

    VERSION = 1

    # @staticmethod
    # @callback
    # def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
    #     """Create the options flow."""
    #     return GWOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            await self.async_set_unique_id("gdanskiewody-" + str(user_input["station"]))
            self._abort_if_unique_id_configured(
                updates={"station": user_input["station"]}
            )
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


# class GWOptionsFlowHandler(config_entries.OptionsFlow):
#     def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
#         """Initialize options flow."""
#         self.config_entry = config_entry

#     async def async_step_init(
#         self, user_input: dict[str, Any] | None = None
#     ) -> FlowResult:
#         """Manage the options."""
#         if user_input is not None:
#             return self.async_create_entry(title="", data=user_input)

#         return self.async_show_form(
#             step_id="init",
#             data_schema=vol.Schema(
#                 {
#                     vol.Required(
#                         "station",
#                         default=self.config_entry.options.get("station"),
#                     ): str
#                 }
#             ),
#         )