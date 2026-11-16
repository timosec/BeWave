"""Button platform for BeWave."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_TRANSPORT, DOMAIN, TRANSPORT_MQTT
from .entity import BeWaveBaseEntity
from .language import function_name
from .tcp import BeWaveHub

_LOGGER = logging.getLogger(__name__)

BeWaveConfigEntry = ConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BeWaveConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up BeWave button entities."""
    if entry.data.get(CONF_TRANSPORT) == TRANSPORT_MQTT:
        async_add_entities([BeWaveDiscoverButton(hass.data[DOMAIN][entry.entry_id])])
        return
    hub: BeWaveHub = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        BeWaveTriggerButton(hub, hub.get_device(device.id)) for device in hub.devices
    )


class BeWaveDiscoverButton(ButtonEntity):
    """Ask the MQTT hub to publish new device statuses."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_icon = "mdi:magnify"

    def __init__(self, hub):
        self._hub = hub
        self._attr_unique_id = f"mqtt_{hub.entry_id}_discover"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, hub.hub_identifier)},
            "name": hub.name,
            "manufacturer": "SATEL",
            "model": "BE WAVE MQTT",
        }

    @property
    def name(self):
        return function_name(
            self._hub.hass, self._hub.display_options, "Zoeken naar nieuwe apparaten"
        )

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.async_on_remove(self._hub.subscribe(self.async_write_ha_state))

    async def async_press(self):
        await self._hub.async_request_discovery()


class BeWaveTriggerButton(BeWaveBaseEntity, ButtonEntity):
    """Button that sends the configured BeWave command."""

    _attr_name = "Trigger"
    _attr_icon = "mdi:gesture-tap-button"

    def __init__(self, hub: BeWaveHub, device) -> None:
        super().__init__(hub, device)
        self._attr_unique_id = (
            f"bewave_{hub.identity_host}_{self._device.unique_id}_trigger"
        )

    async def async_press(self) -> None:
        """Send the configured trigger command to BeWave."""
        _LOGGER.debug(
            "BeWave knop %s sending command: %s",
            self._device.name,
            self._device.command_on,
        )
        await self._hub.async_send_command(self._device.command_on)

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Expose BeWave config for debugging."""
        return {
            "bewave_command_on": self._device.command_on,
            "bewave_has_feedback": self._device.has_feedback,
            "bewave_listen_port": self._device.listen_port,
        }
