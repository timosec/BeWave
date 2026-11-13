"""The BeWave integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant

from .const import (
    CONF_COMMAND_PREFIX,
    CONF_DEVICES,
    CONF_TOPIC_PREFIX,
    CONF_TRANSPORT,
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
    _async_remove_mqtt_read_only_entities(hass, entry, hub)
    try:
        await hass.config_entries.async_forward_entry_setups(entry, MQTT_PLATFORMS)
        await hub.async_start()
    except Exception:
        await hub.async_stop()
        await hass.config_entries.async_unload_platforms(entry, MQTT_PLATFORMS)
        hass.data[DOMAIN].pop(entry.entry_id, None)
        raise
    return True


def _async_remove_mqtt_read_only_entities(hass, entry, hub) -> None:
    """Remove obsolete telemetry, preserving switches and functional detectors."""
    from homeassistant.helpers import device_registry as dr
    from homeassistant.helpers import entity_registry as er

    from .mqtt_models import FUNCTIONAL_BINARY_KEYS

    entities = er.async_get(hass)
    prefix = f"mqtt_{entry.entry_id}_"
    for entity in tuple(er.async_entries_for_config_entry(entities, entry.entry_id)):
        if (
            entity.platform == DOMAIN
            and entity.unique_id.startswith(prefix)
            and (
                entity.domain == "sensor"
                or (
                    entity.domain == "binary_sensor"
                    and not any(
                        entity.unique_id.endswith(f"_{key}")
                        for key in FUNCTIONAL_BINARY_KEYS
                    )
                )
            )
        ):
            entities.async_remove(entity.entity_id)

    devices = dr.async_get(hass)
    for child in tuple(dr.async_entries_for_parent_device(devices, hub.hub_device_id)):
        if (
            child.config_entry_id == entry.entry_id
            and any(
                domain == DOMAIN and identifier.startswith(prefix)
                for domain, identifier in child.identifiers
            )
            and not er.async_entries_for_device(
                entities, child.id, include_disabled_entities=True
            )
        ):
            devices.async_remove_device(child.id)
