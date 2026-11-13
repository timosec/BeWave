"""Native BE WAVE entities, linked to the parent MQTT hub."""

from __future__ import annotations

from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import Entity, EntityCategory

from .const import DOMAIN
from .mqtt_hub import BeWaveMqttHub
from .mqtt_models import Field, MqttDevice


class BeWaveMqttEntity(Entity):
    """Entity whose availability is tied to its own telemetry field."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, hub: BeWaveMqttHub, device: MqttDevice, field: Field) -> None:
        self.hub = hub
        self.device = device
        self.field = field
        self._attr_name = field.name
        self._attr_unique_id = f"mqtt_{hub.entry_id}_{device.identity}_{field.key}"
        if field.device_class:
            self._attr_device_class = field.device_class
        if field.diagnostic:
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def device_info(self) -> dr.ChildDeviceInfo:
        return dr.ChildDeviceInfo(
            identifiers={(DOMAIN, f"mqtt_{self.hub.entry_id}_{self.device.identity}")},
            name=self.device.name,
            parent_device_id=self.hub.hub_device_id,
        )

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "bewave_type": self.device.model,
            "bewave_device": self.device.identity,
            "bewave_topic": self.device.topic,
        }

    @property
    def available(self) -> bool:
        return self.hub.field_available(self.device, self.field.key)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(self.hub.subscribe(self._update))

    @callback
    def _update(self) -> None:
        # Refresh registry metadata when BE WAVE renames a device.
        registry = dr.async_get(self.hass)
        info = self.device_info
        identifier = next(iter(info["identifiers"]))
        if (
            entry := registry.async_get_child_device_by_identifier(
                identifier, self.hub.entry_id
            )
        ) and entry.name != self.device.name:
            registry.async_update_child_device(entry.id, name=self.device.name)
        self.async_write_ha_state()


@callback
def async_setup_mqtt_platform(
    hass, entry, async_add_entities, platform, entity_class
) -> None:
    """Add existing entities and discover fields that arrive later."""
    from .mqtt_models import FIELDS

    hub = hass.data[DOMAIN][entry.entry_id]
    known: set[tuple[str, str]] = set()

    @callback
    def discover() -> None:
        entities = []
        for device in hub.devices.values():
            for field in FIELDS:
                key = (device.identity, field.key)
                if (
                    field.platform != platform
                    or field.key not in device.values
                    or key in known
                ):
                    continue
                known.add(key)
                entities.append(entity_class(hub, device, field))
        if entities:
            async_add_entities(entities)

    entry.async_on_unload(hub.subscribe(discover))
    discover()
