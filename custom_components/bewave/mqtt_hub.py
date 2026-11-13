"""Receive BE WAVE telemetry through Home Assistant's existing MQTT client."""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import timedelta
from time import monotonic

from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store

from .const import DOMAIN
from .mqtt_models import MqttDevice, decode_message, device_identity

_LOGGER = logging.getLogger(__name__)


class BeWaveMqttHub:
    """Discover devices dynamically and fan out updates to native entities."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        prefix: str,
        name: str,
        expire_after: int,
    ) -> None:
        self.hass = hass
        self.entry_id = entry_id
        self.prefix = prefix
        self.name = name
        self.expire_after = expire_after
        self.devices: dict[str, MqttDevice] = {}
        self.connected = False
        self.hub_device_id: str | None = None
        self._routes: dict[str, str] = {}
        self._listeners: set[Callable[[], None]] = set()
        self._unsubs: list[Callable[[], None]] = []
        self._store = Store(hass, 1, f"{DOMAIN}.mqtt.{entry_id}")

    @property
    def hub_identifier(self) -> str:
        return f"mqtt_{self.entry_id}_hub"

    async def async_load(self) -> None:
        """Restore entity metadata before setting up platforms."""
        stored = await self._store.async_load()
        if not isinstance(stored, dict):
            return
        for raw in stored.get("devices", []):
            try:
                device = MqttDevice.restore(raw)
                decode_message(device.topic, {}, self.prefix)
            except (ValueError, KeyError, TypeError):
                continue
            self.devices[device.identity] = device
            self._routes[device.topic] = device.identity

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
        self._unsubs.append(
            async_track_time_interval(self.hass, self._tick, timedelta(seconds=15))
        )

    async def async_stop(self) -> None:
        """Remove subscriptions/timers and flush discovery metadata."""
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()
        self.connected = False
        self._listeners.clear()
        await self._store.async_save(self._snapshot())

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
            # Do not revive cached alarm/contact states on broker reconnect.
            for device in self.devices.values():
                device.updated.clear()
        self._notify()

    @callback
    def _tick(self, _now) -> None:
        self._notify()

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

        # A discovery message is not needed: the native integration creates
        # its own registry devices and entities from these telemetry fields.
        if identity not in self.devices:
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
        device.update(payload, monotonic())
        if device.snapshot() != before:
            self._store.async_delay_save(self._snapshot, 10)
        self._notify()

    def field_available(self, device: MqttDevice, key: str) -> bool:
        updated = device.updated.get(key)
        return (
            self.connected
            and updated is not None
            and monotonic() - updated <= self.expire_after
        )

    @callback
    def _snapshot(self) -> dict:
        return {"devices": [device.snapshot() for device in self.devices.values()]}
