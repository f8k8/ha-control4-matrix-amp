"""Config flow for Control4 Matrix Amp integration."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant, callback
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_NUM_INPUTS,
    CONF_NUM_OUTPUTS,
    CONF_PORT,
    DEFAULT_NAME,
    DEFAULT_NUM_INPUTS,
    DEFAULT_NUM_OUTPUTS,
    DEFAULT_PORT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class Control4MatrixAmpConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Control4 Matrix Amp."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the host is accessible (basic validation)
            try:
                # Create unique ID based on host
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, DEFAULT_NAME),
                    data=user_input,
                )
            except Exception as err:
                _LOGGER.error("Error setting up Control4 Matrix Amp: %s", err)
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Optional(CONF_NUM_INPUTS, default=DEFAULT_NUM_INPUTS): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=16)
                ),
                vol.Optional(CONF_NUM_OUTPUTS, default=DEFAULT_NUM_OUTPUTS): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=16)
                ),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return Control4MatrixAmpOptionsFlow(config_entry)


class Control4MatrixAmpOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Control4 Matrix Amp."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_NUM_INPUTS,
                        default=self.config_entry.data.get(
                            CONF_NUM_INPUTS, DEFAULT_NUM_INPUTS
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=16)),
                    vol.Optional(
                        CONF_NUM_OUTPUTS,
                        default=self.config_entry.data.get(
                            CONF_NUM_OUTPUTS, DEFAULT_NUM_OUTPUTS
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=16)),
                }
            ),
        )
