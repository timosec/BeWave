"""Receive BE WAVE telemetry through Home Assistant's existing MQTT client."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Callable
from datetime import timedelta
from time import monotonic

from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_call_later, async_track_time_interval
from homeassistant.helpers.storage import Store

from .const import CONF_REMEMBER_DEVICES, CONF_RETENTION_DAYS, DOMAIN
from .mqtt_models import (
    FIELD_BY_KEY,
    MqttDevice,
    binary_value,
    decode_message,
    device_identity,
)
from .storage_management import BeWaveLog, recent_device_snapshots, storage_options

_LOGGER = logging.getLogger(__name__)


class BeWaveMqttHub:
    """Discover devices dynamically and fan out updates to native entities."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        prefix: str,
        name: str,
        command_prefix: str,
        options=None,
    ) -> None:
        self.hass = hass
        self.entry_id = entry_id
        self.prefix = prefix
        self.name = name
        self.command_prefix = command_prefix
        preferences = storage_options(options or {})
        self.remember_devices = preferences[CONF_REMEMBER_DEVICES]
        self.retention_days = preferences[CONF_RETENTION_DAYS]
        self.log = BeWaveLog(hass, entry_id, preferences)
        self._cache_cleared = False
        self._saved_signature = ""
        self.devices: dict[str, MqttDevice] = {}
        self.ignored: dict[str, dict[str, str]] = {}
        self.connected = False
        self.hub_device_id: str | None = None
        self._routes: dict[str, str] = {}
        self._listeners: set[Callable[[], None]] = set()
        self._unsubs: list[Callable[[], None]] = []
        self._cancel_sync: Callable[[], None] | None = None
        self._store = Store(hass, 1, f"{DOMAIN}.mqtt.{entry_id}")

    @property
    def hub_identifier(self) -> str:
        return f"mqtt_{self.entry_id}_hub"

    async def async_load(self) -> None:
        """Restore entity metadata before setting up platforms."""
        await self.log.async_load()
        stored = await self._store.async_load()
        if not isinstance(stored, dict):
            return
        ignored = stored.get("ignored", {})
        if isinstance(ignored, dict):
            self.ignored = {
                key: value
                for key, value in ignored.items()
                if isinstance(key, str) and isinstance(value, dict)
            }
        self._saved_signature = json.dumps(stored, sort_keys=True)
        records = (
            recent_device_snapshots(stored.get("devices", []), self.retention_days)
            if self.remember_devices
            else []
        )
        for raw in records:
            try:
                device = MqttDevice.restore(raw)
                decode_message(device.topic, {}, self.prefix)
            except (ValueError, KeyError, TypeError):
                continue
            if not device.values:
                continue
            if device.identity in self.ignored:
                continue
            self.devices[device.identity] = device
            self._routes[device.topic] = device.identity
        if stored.get("devices") and (
            not self.remember_devices or len(records) != len(stored["devices"])
        ):
            await self._store.async_save(self._store_data())

    async def async_start(self) -> None:
        """Subscribe after all platforms have installed discovery listeners."""
        self.connected = mqtt.is_connected(self.hass)
        self._unsubs.append(
            mqtt.async_subscribe_connection_status(self.hass, self._connection_changed)
        )
        self._unsubs.append(
            await mqtt.async_subscribe(
                self.hass, f"{self.prefix}/devices/+/tx", self._receive, qos=0
            )
        )
        self._schedule_sync()
        self._unsubs.append(
            async_track_time_interval(
                self.hass, self._prune_storage, timedelta(hours=1)
            )
        )

    async def async_stop(self) -> None:
        """Remove subscriptions/timers and flush discovery metadata."""
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()
        if self._cancel_sync:
            self._cancel_sync()
            self._cancel_sync = None
        self.connected = False
        self._listeners.clear()
        await self._store.async_save(self._store_data())
        await self.log.async_flush()

    @callback
    def subscribe(self, listener: Callable[[], None]) -> Callable[[], None]:
        self._listeners.add(listener)
        return lambda: self._listeners.discard(listener)

    @callback
    def _notify(self) -> None:
        for listener in tuple(self._listeners):
            listener()

    @callback
    def _connection_changed(self, connected: bool) -> None:
        self.connected = connected
        if not connected:
            self.log.add("warning", "MQTT-verbinding verbroken")
            # Do not revive cached alarm/contact states on broker reconnect.
            for device in self.devices.values():
                device.updated.clear()
            if self._cancel_sync:
                self._cancel_sync()
                self._cancel_sync = None
        else:
            self._schedule_sync()
        self._notify()

    @callback
    def _schedule_sync(self) -> None:
        """Request live statuses once subscriptions can be sent to the broker."""
        if not self.connected:
            return
        if self._cancel_sync:
            self._cancel_sync()
        self._cancel_sync = async_call_later(self.hass, 1, self._sync)

    async def _sync(self, _now) -> None:
        """Refresh devices after start/reconnect, without switching any output."""
        if self._cancel_sync:
            self._cancel_sync()
        self._cancel_sync = None
        if not self.connected or not mqtt.is_connected(self.hass):
            return
        try:
            await self.async_request_discovery()
        except (HomeAssistantError, TimeoutError):
            self.log.add(
                "warning", "Automatische synchronisatie kon niet worden verstuurd"
            )
            _LOGGER.debug("BE WAVE status sync could not be sent")

    async def async_request_discovery(self) -> None:
        """Ask for a fresh device inventory/status; never operate outputs."""
        if not self.connected or not mqtt.is_connected(self.hass):
            self.log.add(
                "warning", "Zoekopdracht niet verstuurd: MQTT is niet verbonden"
            )
            raise HomeAssistantError(
                "BE WAVE: MQTT is niet verbonden. Controleer de MQTT-integratie."
            )
        try:
            async with asyncio.timeout(5):
                await mqtt.async_publish(
                    self.hass,
                    f"{self.command_prefix}/system/rx",
                    json.dumps({"action": "SYNC"}),
                    qos=0,
                    retain=False,
                )
        except TimeoutError as err:
            self.log.add("error", "Time-out bij aanvragen van synchronisatie")
            raise HomeAssistantError(
                "BE WAVE: de zoekopdracht kon niet tijdig worden verstuurd"
            ) from err
        except HomeAssistantError:
            self.log.add("error", "MQTT kon de synchronisatie-aanvraag niet versturen")
            raise

    async def async_forget(
        self, identity: str, name: str = "", model: str = ""
    ) -> None:
        """Persist an exclusion so ordinary telemetry cannot recreate a device."""
        device = self.devices.pop(identity, None)
        if device:
            device.updated.clear()
            name = device.name
            model = device.model
        self.ignored[identity] = {"name": name or identity, "model": model}
        self._routes = {
            route: key for route, key in self._routes.items() if key != identity
        }
        await self._store.async_save(self._store_data())
        self._notify()

    async def async_restore(self, identity: str) -> None:
        """Allow an explicitly selected previously removed device again."""
        self.ignored.pop(identity, None)
        await self._store.async_save(self._store_data())

    @callback
    def _receive(self, message: mqtt.ReceiveMessage) -> None:
        try:
            _, payload = decode_message(message.topic, message.payload, self.prefix)
            if "sn" in payload:
                identity = device_identity(payload)
            else:
                identity = self._routes.get(message.topic)
                if identity is None:
                    return
        except (ValueError, TypeError):
            _LOGGER.debug("Ignoring invalid BE WAVE status on %s", message.topic)
            return

        if identity in self.ignored:
            return

        # A discovery message is not needed: the native integration creates
        # its own registry devices and entities from these telemetry fields.
        if identity not in self.devices:
            if not FIELD_BY_KEY.keys() & payload.keys():
                # A non-controllable device can replace a previously known
                # output at this index. Never keep the old command route live.
                previous = self._routes.pop(message.topic, None)
                if previous is not None:
                    self.devices[previous].updated.clear()
                    self._notify()
                return
            self.devices[identity] = MqttDevice(
                identity, message.topic, identity, "BE WAVE"
            )
        device = self.devices[identity]
        before = device.snapshot()
        previous_identity = self._routes.get(message.topic)
        if previous_identity is not None and previous_identity != identity:
            self.devices[previous_identity].updated.clear()
        # If a device moves to another topic, do not accept anonymous updates
        # from its old route as fresh values for this device.
        if device.topic != message.topic:
            self._routes.pop(device.topic, None)
        device.topic = message.topic
        self._routes[message.topic] = identity
        device.update(
            payload, None if getattr(message, "retain", False) else monotonic()
        )
        after = device.snapshot()
        metadata_changed = {k: v for k, v in after.items() if k != "last_seen"} != {
            k: v for k, v in before.items() if k != "last_seen"
        }
        hour_changed = int(after["last_seen"] // 3600) != int(
            before["last_seen"] // 3600
        )
        if self.remember_devices and (metadata_changed or hour_changed):
            self._cache_cleared = False
            self._store.async_delay_save(self._store_data, 10)
        self._notify()

    def field_available(self, device: MqttDevice, key: str) -> bool:
        # Relay statuses are often sent on change only. The last live state
        # remains usable for this broker session, without an idle timeout.
        return (
            self.connected
            and device.identity not in self.ignored
            and device.updated.get(key) is not None
        )

    async def async_set_output(self, device: MqttDevice, enabled: bool) -> None:
        """Send a non-retained command to the current device index, never a serial."""
        if (
            not self.field_available(device, "on_off")
            or binary_value(device.values.get("on_off")) is None
            or not mqtt.is_connected(self.hass)
            or self._routes.get(device.topic) != device.identity
        ):
            self.log.add(
                "warning",
                "Schakelopdracht niet verstuurd: geen geldige verbinding of actuele apparaatstatus",
            )
            raise HomeAssistantError(
                "BE WAVE: geen actuele verbinding/status voor dit apparaat"
            )

        index, _ = decode_message(device.topic, {}, self.prefix)
        topic = f"{self.command_prefix}/devices/{index}/rx"
        try:
            async with asyncio.timeout(5):
                await mqtt.async_publish(
                    self.hass,
                    topic,
                    json.dumps({"on_off": int(enabled)}),
                    qos=0,
                    retain=False,
                )
        except TimeoutError as err:
            self.log.add("error", "Time-out bij versturen van een schakelopdracht")
            raise HomeAssistantError(
                "BE WAVE: MQTT-opdracht verzenden duurde te lang"
            ) from err
        except HomeAssistantError:
            self.log.add("error", "MQTT kon de schakelopdracht niet versturen")
            raise
        # The received status remains authoritative. A successful publish is not
        # proof that the physical device executed the command.

    @callback
    def _snapshot(self) -> dict:
        return {
            "devices": recent_device_snapshots(
                [device.snapshot() for device in self.devices.values()],
                self.retention_days,
            )
            if self.remember_devices and not self._cache_cleared
            else [],
            "ignored": self.ignored,
        }

    @callback
    def _store_data(self):
        snapshot = self._snapshot()
        self._saved_signature = json.dumps(snapshot, sort_keys=True)
        return snapshot

    async def _prune_storage(self, _now=None):
        await self.log.async_prune()
        snapshot = self._snapshot()
        if json.dumps(snapshot, sort_keys=True) != self._saved_signature:
            await self._store.async_save(self._store_data())

    async def async_configure_storage(self, options):
        preferences = storage_options(options)
        self.remember_devices = preferences[CONF_REMEMBER_DEVICES]
        self.retention_days = preferences[CONF_RETENTION_DAYS]
        self.log.configure(preferences)
        await self._prune_storage()

    async def async_clear_cache(self):
        """Clear disk metadata, retaining live operation and intentional exclusions."""
        self._cache_cleared = True
        await self._store.async_save(self._store_data())
