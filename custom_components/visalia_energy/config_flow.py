import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from .const import DOMAIN

class VisaliaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title=user_input["username"], data=user_input)

        schema = vol.Schema({
            vol.Required("username"): str,
            vol.Required("password"): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
