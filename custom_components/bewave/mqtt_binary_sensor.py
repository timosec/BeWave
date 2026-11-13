"""Native read-only BE WAVE contact and status entities."""

from homeassistant.components.binary_sensor import BinarySensorEntity

from .mqtt_entity import BeWaveMqttEntity
from .mqtt_models import binary_value


class BeWaveMqttBinarySensor(BeWaveMqttEntity, BinarySensorEntity):
    """Expose numeric 0/1 telemetry without inventing command semantics."""

    @property
    def is_on(self) -> bool | None:
        return binary_value(self.device.values.get(self.field.key))
