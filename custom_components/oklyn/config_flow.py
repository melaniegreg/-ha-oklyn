from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OklynAuthError, OklynClient
from .const import CONF_API_TOKEN, CONF_DEVICE_ID, CONF_SCAN_INTERVAL, DEFAULT_DEVICE_ID, DEFAULT_SCAN_INTERVAL, DOMAIN


class OklynConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(f"oklyn_{user_input[CONF_DEVICE_ID]}")
            self._abort_if_unique_id_configured()
            client = OklynClient(async_get_clientsession(self.hass), user_input[CONF_API_TOKEN], user_input[CONF_DEVICE_ID])
            try:
                await client.validate()
            except OklynAuthError:
                errors["base"] = "invalid_auth"
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title=f"Oklyn ({user_input[CONF_DEVICE_ID]})", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_API_TOKEN): str,
            vol.Required(CONF_DEVICE_ID, default=DEFAULT_DEVICE_ID): str,
            vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=15, max=3600)),
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry):
        return OklynOptionsFlow()


class OklynOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        schema = vol.Schema({
            vol.Required(CONF_SCAN_INTERVAL, default=self.config_entry.options.get(CONF_SCAN_INTERVAL, self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))): vol.All(vol.Coerce(int), vol.Range(min=15, max=3600)),
        })
        return self.async_show_form(step_id="init", data_schema=schema)
