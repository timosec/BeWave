"""Switch platform for BeWave."""

from __future__ import annotations

import logging
from collections.abc import Callable

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_call_later

from .const import CONF_TRANSPORT, DOMAIN, TRANSPORT_MQTT
from .mqtt_entity import BeWaveMqttEntity, async_setup_mqtt_platform
from .mqtt_models import binary_value
from .tcp import BeWaveHub

_LOGGER = logging.getLogger(__name__)

BeWaveConfigEntry = ConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BeWaveConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up BeWave switch entities."""
    if entry.data.get(CONF_TRANSPORT) == TRANSPORT_MQTT:
        async_setup_mqtt_platform(
            hass, entry, async_add_entities, "switch", BeWaveMqttSwitch
        )
        return
    hub: BeWaveHub = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(BeWaveSwitch(hub, device.id) for device in hub.devices)


class BeWaveMqttSwitch(BeWaveMqttEntity, SwitchEntity):
    """Switch a BE WAVE component that reports the on_off capability."""

    @property
    def available(self) -> bool:
        return (
            super().available
            and binary_value(self.device.values.get("on_off")) is not None
        )

    @property
    def is_on(self) -> bool | None:
        return binary_value(self.device.values.get("on_off"))

    async def async_turn_on(self, **kwargs) -> None:
        await self.hub.async_set_output(self.device, True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.hub.async_set_output(self.device, False)


class BeWaveSwitch(SwitchEntity):
    """Representation of a BeWave virtual device."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, hub: BeWaveHub, device_id: str) -> None:
        self._hub = hub
        self._device = hub.get_device(device_id)
        self._attr_unique_id = f"bewave_{self._device.unique_id}"
        self._attr_name = self._device.name
        self._attr_is_on = False
        self._unsubscribe: Callable[[], None] | None = None

    async def async_added_to_hass(self) -> None:
        """Register callbacks when entity is added."""

        @callback
        def _handle_state(new_state: bool) -> None:
            self._attr_is_on = new_state
            self.async_write_ha_state()

        self._unsubscribe = self._hub.subscribe(self._device.id, _handle_state)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister callbacks."""
        if self._unsubscribe:
            self._unsubscribe()
            self._unsubscribe = None

    async def async_turn_on(self, **kwargs) -> None:
        """Trigger the device."""
        _LOGGER.info(
            "BeWave switch %s sending command: %s",
            self._device.name,
            self._device.command_on,
        )
        await self._hub.async_send_command(self._device.command_on)

        if self._device.has_feedback:
            return

        self._attr_is_on = True
        self.async_write_ha_state()
        async_call_later(
            self.hass, self._device.momentary_reset_ms / 1000, self._reset_state
        )

    async def async_turn_off(self, **kwargs) -> None:
        """Mirror Homebridge behavior: trigger the same command on OFF."""
        _LOGGER.info("BeWave switch %s toggled OFF", self._device.name)
        await self.async_turn_on(**kwargs)

    @callback
    def _reset_state(self, *_args) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Expose BeWave config for debugging."""
        return {
            "bewave_command_on": self._device.command_on,
            "bewave_has_feedback": self._device.has_feedback,
            "bewave_listen_port": self._device.listen_port,
        }
