from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.helpers.entity import Entity
from .const import DOMAIN, SCAN_INTERVAL_MINUTES
from .api import VisaliaAPI

async def async_setup_entry(hass, entry, async_add_entities):
    username = entry.data["username"]
    password = entry.data["password"]
    api = VisaliaAPI(username, password)

    async def async_update_data():
        await api.authenticate()
        return await api.get_invoices()

    coordinator = DataUpdateCoordinator(
        hass,
        name="visalia_energy",
        update_method=async_update_data,
        update_interval=timedelta(minutes=SCAN_INTERVAL_MINUTES),
    )

    await coordinator.async_config_entry_first_refresh()

    invoices = coordinator.data
    last = invoices["results"][0] if invoices["results"] else {}
    values = [float(f["total"]) for f in invoices["results"] if f.get("total")]
    avg = sum(values) / len(values) if values else 0

    sensors = [
        VisaliaSensor(coordinator, "Última factura", last.get("total"), "€"),
        VisaliaSensor(coordinator, "Media facturas", avg, "€"),
        VisaliaSensor(coordinator, "Facturas totales", len(values), "unidades"),
        VisaliaSensor(coordinator, "Fecha última factura", last.get("invoiced_date"), None),
    ]
    async_add_entities(sensors, update_before_add=True)

class VisaliaSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, name, value, unit):
        super().__init__(coordinator)
        self._attr_name = name
        self._state = value
        self._attr_unit_of_measurement = unit

    @property
    def state(self):
        return self._state

    async def async_update(self):
        await self.coordinator.async_request_refresh()
        invoices = self.coordinator.data
        # No cambio de estado aquí para mantenerlo simple
