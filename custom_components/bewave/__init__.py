"""The BeWave integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant

from .const import (
    CONF_COMMAND_PREFIX,
    CONF_DEVICES,
    CONF_EXPIRE_AFTER,
    CONF_TOPIC_PREFIX,
    CONF_TRANSPORT,
    DEFAULT_EXPIRE_AFTER,
    DOMAIN,
    MQTT_PLATFORMS,
    PLATFORMS,
    TRANSPORT_MQTT,
)

BeWaveConfigEntry = ConfigEntry


async def async_setup_entry(hass: HomeAssistant, entry: BeWaveConfigEntry) -> bool:
    """Set up BeWave from a config entry."""
    if entry.data.get(CONF_TRANSPORT) == TRANSPORT_MQTT:
        return await _async_setup_mqtt_entry(hass, entry)

    from .models import normalize_device
    from .tcp import BeWaveHub

    hass.data.setdefault(DOMAIN, {})

    raw_devices = entry.options.get(CONF_DEVICES, entry.data.get(CONF_DEVICES, []))
    devices = [
        normalize_device(device, idx + 1) for idx, device in enumerate(raw_devices)
    ]

    hub = BeWaveHub(hass, entry.data[CONF_HOST], devices)
    hub.identity_host = entry.data.get("entity_host", entry.data[CONF_HOST])
    await hub.async_start()

    hass.data[DOMAIN][entry.entry_id] = hub
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: BeWaveConfigEntry) -> bool:
    """Unload a config entry."""
    platforms = (
        MQTT_PLATFORMS
        if entry.data.get(CONF_TRANSPORT) == TRANSPORT_MQTT
        else PLATFORMS
    )
    unload_ok = await hass.config_entries.async_unload_platforms(entry, platforms)
    if unload_ok:
        hub = hass.data[DOMAIN].pop(entry.entry_id)
        await hub.async_stop()
    return unload_ok


async def _async_setup_mqtt_entry(
    hass: HomeAssistant, entry: BeWaveConfigEntry
) -> bool:
    """Set up MQTT without changing or migrating existing TCP installations."""
    from homeassistant.components import mqtt
    from homeassistant.exceptions import ConfigEntryNotReady
    from homeassistant.helpers import device_registry as dr

    from .mqtt_hub import BeWaveMqttHub

    if not await mqtt.async_wait_for_mqtt_client(hass):
        raise ConfigEntryNotReady("Configure the Home Assistant MQTT integration first")

    hub = BeWaveMqttHub(
        hass,
        entry.entry_id,
        entry.data[CONF_TOPIC_PREFIX],
        entry.options.get("name", entry.data.get("name", "BE WAVE")),
        entry.options.get(
            CONF_EXPIRE_AFTER, entry.data.get(CONF_EXPIRE_AFTER, DEFAULT_EXPIRE_AFTER)
        ),
        entry.options.get(
            CONF_COMMAND_PREFIX,
            entry.data.get(
                CONF_COMMAND_PREFIX, f"{entry.data[CONF_TOPIC_PREFIX]}/command"
            ),
        ),
    )
    await hub.async_load()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = hub
    parent = dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, hub.hub_identifier)},
        manufacturer="SATEL",
        model="BE WAVE MQTT",
        name=hub.name,
    )
    hub.hub_device_id = parent.id
    try:
        await hass.config_entries.async_forward_entry_setups(entry, MQTT_PLATFORMS)
        await hub.async_start()
    except Exception:
        await hub.async_stop()
        await hass.config_entries.async_unload_platforms(entry, MQTT_PLATFORMS)
        hass.data[DOMAIN].pop(entry.entry_id, None)
        raise
    return True
