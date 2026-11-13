"""Receive BE WAVE telemetry through Home Assistant's existing MQTT client."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Callable
from time import monotonic

from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.storage import Store

from .const import DOMAIN
from .mqtt_models import MqttDevice, binary_value, decode_message, device_identity

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
    ) -> None:
        self.hass = hass
        self.entry_id = entry_id
        self.prefix = prefix
        self.name = name
        self.command_prefix = command_prefix
        self.devices: dict[str, MqttDevice] = {}
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
        stored = await self._store.async_load()
        if not isinstance(stored, dict):
            return
        for raw in stored.get("devices", []):
            try:
                device = MqttDevice.restore(raw)
                decode_message(device.topic, {}, self.prefix)
            except (ValueError, KeyError, TypeError):
                continue
            if "on_off" not in device.values:
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
        self._schedule_sync()

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
            async with asyncio.timeout(5):
                await mqtt.async_publish(
                    self.hass,
                    f"{self.command_prefix}/system/rx",
                    json.dumps({"action": "SYNC"}),
                    qos=0,
                    retain=False,
                )
        except (HomeAssistantError, TimeoutError):
            _LOGGER.debug("BE WAVE status sync could not be sent")

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
            if "on_off" not in payload:
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
        if device.snapshot() != before:
            self._store.async_delay_save(self._snapshot, 10)
        self._notify()

    def field_available(self, device: MqttDevice, key: str) -> bool:
        # Relay statuses are often sent on change only. The last live state
        # remains usable for this broker session, without an idle timeout.
        return self.connected and device.updated.get(key) is not None

    async def async_set_output(self, device: MqttDevice, enabled: bool) -> None:
        """Send a non-retained command to the current device index, never a serial."""
        if (
            not self.field_available(device, "on_off")
            or binary_value(device.values.get("on_off")) is None
            or not mqtt.is_connected(self.hass)
            or self._routes.get(device.topic) != device.identity
        ):
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
            raise HomeAssistantError(
                "BE WAVE: MQTT-opdracht verzenden duurde te lang"
            ) from err
        # The received status remains authoritative. A successful publish is not
        # proof that the physical device executed the command.

    @callback
    def _snapshot(self) -> dict:
        return {"devices": [device.snapshot() for device in self.devices.values()]}
