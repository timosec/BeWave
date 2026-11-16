"""User-controlled removal and restoration for native MQTT devices."""

from __future__ import annotations

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.storage import Store

from .const import DOMAIN


def mqtt_device_identity(entry, device) -> str | None:
    prefix = f"mqtt_{entry.entry_id}_"
    for domain, identifier in device.identifiers:
        if domain == DOMAIN and identifier.startswith(prefix):
            identity = identifier[len(prefix) :]
            if identity and identity != "hub":
                return identity
    return None


def mqtt_devices(hass, entry) -> dict[str, dict[str, str]]:
    """Include stale registry records, not only currently reporting devices."""
    result = {}
    registry = dr.async_get(hass)
    registered = [
        *dr.async_entries_for_config_entry(registry, entry.entry_id),
        *dr.async_child_entries_for_config_entry(registry, entry.entry_id),
    ]
    for device in registered:
        if identity := mqtt_device_identity(entry, device):
            result[identity] = {
                "name": device.name_by_user or device.name or identity,
                "model": "",
            }
    if hub := hass.data.get(DOMAIN, {}).get(entry.entry_id):
        for identity, device in hub.devices.items():
            result.setdefault(identity, {"name": device.name, "model": device.model})
            result[identity]["model"] = device.model
    return result


async def async_ignored_devices(hass, entry) -> dict:
    if hub := hass.data.get(DOMAIN, {}).get(entry.entry_id):
        return hub.ignored
    stored = await Store(hass, 1, f"{DOMAIN}.mqtt.{entry.entry_id}").async_load() or {}
    return stored.get("ignored", {})


async def async_forget_mqtt_device(
    hass, entry, identity, *, remove_registry=False, name=""
) -> None:
    """Forget the selected identity even when the integration is not loaded."""
    if hub := hass.data.get(DOMAIN, {}).get(entry.entry_id):
        await hub.async_forget(identity, name)
    else:
        store = Store(hass, 1, f"{DOMAIN}.mqtt.{entry.entry_id}")
        stored = await store.async_load() or {"devices": []}
        stored.setdefault("ignored", {})[identity] = {
            "name": name or identity,
            "model": "",
        }
        stored["devices"] = [
            d for d in stored.get("devices", []) if d.get("identity") != identity
        ]
        await store.async_save(stored)
    if remove_registry:
        registry = dr.async_get(hass)
        registered = [
            *dr.async_entries_for_config_entry(registry, entry.entry_id),
            *dr.async_child_entries_for_config_entry(registry, entry.entry_id),
        ]
        for device in registered:
            if mqtt_device_identity(entry, device) == identity:
                registry.async_remove_device(device.id)


async def async_restore_mqtt_device(hass, entry, identity) -> None:
    if hub := hass.data.get(DOMAIN, {}).get(entry.entry_id):
        await hub.async_restore(identity)
    else:
        store = Store(hass, 1, f"{DOMAIN}.mqtt.{entry.entry_id}")
        stored = await store.async_load() or {"devices": [], "ignored": {}}
        stored.setdefault("ignored", {}).pop(identity, None)
        await store.async_save(stored)
    # Reload to reset each platform's already-added entity set before discovery.
    hass.config_entries.async_schedule_reload(entry.entry_id)
