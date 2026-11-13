"""Read-only MQTT measurements for BE WAVE."""

from homeassistant.components.sensor import SensorEntity, SensorStateClass

from .mqtt_entity import BeWaveMqttEntity, async_setup_mqtt_platform
from .mqtt_models import numeric_value


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    async_setup_mqtt_platform(
        hass, entry, async_add_entities, "sensor", BeWaveMqttSensor
    )


class BeWaveMqttSensor(BeWaveMqttEntity, SensorEntity):
    """A numeric measurement or firmware string from the status payload."""

    def __init__(self, hub, device, field) -> None:
        super().__init__(hub, device, field)
        if field.unit:
            self._attr_native_unit_of_measurement = field.unit
        if field.key != "fw_version":
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        value = self.device.values.get(self.field.key)
        if self.field.key == "fw_version":
            return value if isinstance(value, str) else None
        return numeric_value(value)
