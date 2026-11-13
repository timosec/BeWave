"""Protocol parsing and descriptions for BE WAVE MQTT telemetry.

Keep this module independent of Home Assistant so protocol handling can be
tested without running Home Assistant or a live alarm installation.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Field:
    """A known, read-only telemetry field."""

    key: str
    name: str
    platform: str = "sensor"
    device_class: str | None = None
    unit: str | None = None
    diagnostic: bool = False


FIELDS = (
    Field("temperature", "Temperatuur", device_class="temperature", unit="°C"),
    Field("battery", "Batterij", device_class="battery", unit="%", diagnostic=True),
    Field("signal", "Signaal", unit="%", diagnostic=True),
    Field(
        "voltage_supply",
        "Voedingsspanning",
        device_class="voltage",
        unit="V",
        diagnostic=True,
    ),
    Field("errors_count", "Fouten", diagnostic=True),
    Field("errors_memory_count", "Foutgeheugen", diagnostic=True),
    Field("fw_version", "Firmwareversie", diagnostic=True),
    Field("magnetic", "Raamcontact", "binary_sensor", "window"),
    Field("vibration", "Trilling", "binary_sensor", "vibration"),
    Field("violation", "Detectie", "binary_sensor"),
    Field("on_off", "Status", "binary_sensor"),
    Field("alarm_armed", "Ingeschakeld", "binary_sensor"),
    Field("alarm_detected", "Alarm", "binary_sensor", "problem"),
    Field("warning_alarm", "Waarschuwing", "binary_sensor", "problem"),
    Field("block_unblock", "Geblokkeerd", "binary_sensor"),
    Field("on_off", "Schakelaar", "switch"),
)
FIELD_BY_KEY = {item.key: item for item in FIELDS}
METADATA = {"name", "type", "fw_version"}


def normalize_prefix(value: str) -> str:
    """Validate a concrete base topic, without wildcards or path ambiguity."""
    if not isinstance(value, str):
        raise TypeError("Expected a topic prefix")
    value = value.strip().strip("/")
    if (
        not value
        or any(c in value for c in ("+", "#", "\0"))
        or any(not part for part in value.split("/"))
        or len(value.encode("utf-8")) > 500
    ):
        raise ValueError("Invalid topic prefix")
    return value


def decode_message(topic: str, payload: Any, prefix: str) -> tuple[str, dict[str, Any]]:
    """Accept device status topics and a bounded JSON object only."""
    match = re.fullmatch(re.escape(prefix) + r"/devices/(\d+)/tx", topic)
    if not match:
        raise ValueError("Not a BE WAVE device status topic")
    if isinstance(payload, (str, bytes, bytearray)):
        if len(payload) > 65536:
            raise ValueError("Status message too large")
        try:
            payload = json.loads(payload)
        except (ValueError, UnicodeError) as err:
            raise ValueError("Invalid status JSON") from err
    if not isinstance(payload, dict):
        raise TypeError("Status must be a JSON object")
    return match[1], payload


def device_identity(payload: dict[str, Any]) -> str:
    """Use the physical serial and channel, rather than a mutable topic index."""
    sn = payload.get("sn")
    channel = payload.get("channel", 0)
    if isinstance(sn, bool) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", str(sn or "")):
        raise ValueError("Missing or invalid serial number")
    if isinstance(channel, bool) or not re.fullmatch(r"\d{1,6}", str(channel)):
        raise ValueError("Invalid channel")
    return f"{sn}_{int(channel)}"


def numeric_value(value: Any) -> float | None:
    """Invalid values remain unknown, never an invented zero."""
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        return None
    try:
        number = float(value)
    except (ValueError, TypeError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def binary_value(value: Any) -> bool | None:
    """Only documented numeric binary representations are interpreted."""
    if value in (0, "0", False):
        return False
    if value in (1, "1", True):
        return True
    return None


@dataclass
class MqttDevice:
    """State for one physical device/channel, including stale field times."""

    identity: str
    topic: str
    name: str
    model: str
    values: dict[str, Any] = field(default_factory=dict)
    updated: dict[str, float] = field(default_factory=dict)

    def update(self, payload: dict[str, Any], now: float | None) -> None:
        """Merge partial updates without refreshing absent measurements."""
        if isinstance(payload.get("name"), str) and payload["name"].strip():
            self.name = payload["name"].strip()[:200]
        if isinstance(payload.get("type"), str):
            self.model = payload["type"][:100]
        for key in FIELD_BY_KEY:
            if key in payload:
                if now is None:
                    # A broker-retained snapshot has no trustworthy sample age.
                    # Discover the field, but never overwrite a live reading.
                    self.values.setdefault(key, None)
                    continue
                value = payload[key]
                # Telemetry is scalar. Do not persist nested/arbitrary data.
                if value is not None and not isinstance(value, (str, int, float, bool)):
                    value = None
                self.values[key] = value
                self.updated[key] = now

    def snapshot(self) -> dict[str, Any]:
        """Persist discovery metadata only; restored states start unknown."""
        return {
            "identity": self.identity,
            "topic": self.topic,
            "name": self.name,
            "model": self.model,
            "fields": sorted(self.values),
        }

    @classmethod
    def restore(cls, raw: dict[str, Any]) -> MqttDevice:
        """Restore discovered entities, without making old readings live."""
        device = cls(raw["identity"], raw["topic"], raw["name"], raw["model"])
        device.values = {key: None for key in raw["fields"] if key in FIELD_BY_KEY}
        return device
