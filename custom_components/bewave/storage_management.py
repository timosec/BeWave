"""Bounded optional BE WAVE logging and read-only storage accounting."""

from __future__ import annotations

import json
import math
from pathlib import Path
from time import time

from homeassistant.core import callback
from homeassistant.helpers.storage import Store

from .const import (
    CONF_KEEP_LOG,
    CONF_MAX_LOG_MB,
    CONF_REMEMBER_DEVICES,
    CONF_RETENTION_DAYS,
    DEFAULT_MAX_LOG_MB,
    DEFAULT_RETENTION_DAYS,
    DOMAIN,
)


def storage_options(options) -> dict:
    return {
        CONF_REMEMBER_DEVICES: options.get(CONF_REMEMBER_DEVICES, True),
        CONF_KEEP_LOG: options.get(CONF_KEEP_LOG, False),
        CONF_RETENTION_DAYS: options.get(CONF_RETENTION_DAYS, DEFAULT_RETENTION_DAYS),
        CONF_MAX_LOG_MB: options.get(CONF_MAX_LOG_MB, DEFAULT_MAX_LOG_MB),
    }


def recent_device_snapshots(records, days, now=None) -> list:
    """Trim the disk cache only, never the active device/entity registry."""
    now = time() if now is None else now
    cutoff = now - days * 86400
    result = []
    for raw in records:
        if not isinstance(raw, dict):
            continue
        seen = raw.get("last_seen", now)
        if isinstance(seen, (int, float)) and math.isfinite(seen) and seen >= cutoff:
            result.append({**raw, "last_seen": seen})
    return result


class BeWaveLog:
    """An opt-in small log, containing no routine MQTT payloads or state history."""

    def __init__(self, hass, entry_id, options):
        self.hass = hass
        self.store = Store(hass, 1, f"{DOMAIN}.log.{entry_id}")
        self.records = []
        self.dirty = False
        self.configure(options)

    def configure(self, options):
        values = storage_options(options)
        self.enabled = values[CONF_KEEP_LOG]
        self.retention_days = values[CONF_RETENTION_DAYS]
        self.max_bytes = values[CONF_MAX_LOG_MB] * 1_000_000

    async def async_load(self):
        stored = await self.store.async_load()
        if isinstance(stored, dict):
            self.records = [
                r
                for r in stored.get("events", [])
                if isinstance(r, dict)
                and isinstance(r.get("time"), (int, float))
                and math.isfinite(r["time"])
            ]
            await self.async_prune()

    @callback
    def _trim(self, now=None):
        now = time() if now is None else now
        cutoff = now - self.retention_days * 86400
        budget = max(0, self.max_bytes - 4096)
        kept = []
        used = 0
        for record in reversed(self.records):
            if record["time"] < cutoff:
                continue
            # Conservative allowance for the Store wrapper and pretty-printing.
            size = len(json.dumps(record, ensure_ascii=True, indent=2).encode()) + 128
            if used + size > budget:
                break
            kept.append(record)
            used += size
        kept.reverse()
        changed = kept != self.records
        self.records = kept
        self.dirty = self.dirty or changed
        return changed

    @callback
    def add(self, level, message):
        if not self.enabled or level not in {"warning", "error"}:
            return
        self.records.append(
            {"time": time(), "level": level, "message": str(message)[:1000]}
        )
        self.dirty = True
        self._trim()
        self.store.async_delay_save(self._data, 10)

    @callback
    def _data(self):
        self._trim()
        self.dirty = False
        return {"events": list(self.records)}

    async def async_prune(self):
        self._trim()
        await self.async_flush()

    async def async_flush(self):
        if self.dirty:
            await self.store.async_save(self._data())

    async def async_clear(self):
        self.records = []
        self.dirty = False
        await self.store.async_remove()


def _file_size(path):
    try:
        return path.stat().st_size if path.is_file() else None
    except OSError:
        return None


def format_bytes(size):
    if size is None:
        return "Niet uitleesbaar / unavailable"
    return f"{size / 1_000_000:.4f} MB ({size / 1_000_000_000:.6f} GB)"


def storage_report(config_dir, entry_id) -> dict:
    """Only stat explicitly scoped files; do not read/truncate system logs."""
    root = Path(config_dir)
    cache_size = _file_size(root / ".storage" / f"{DOMAIN}.mqtt.{entry_id}") or 0
    log_size = _file_size(root / ".storage" / f"{DOMAIN}.log.{entry_id}") or 0
    try:
        sizes = [
            size
            for p in root.glob("home-assistant.log*")
            if (size := _file_size(p)) is not None
        ]
        ha_log_size = sum(sizes) if sizes else None
    except OSError:
        ha_log_size = None
    return {
        "cache": format_bytes(cache_size),
        "own_log": format_bytes(log_size),
        "ha_log": format_bytes(ha_log_size),
        "cache_bytes": cache_size,
        "own_log_bytes": log_size,
        "ha_log_bytes": ha_log_size,
    }


async def async_storage_report(hass, entry_id):
    return await hass.async_add_executor_job(
        storage_report, hass.config.config_dir, entry_id
    )


async def async_apply_storage_options(hass, entry, preferences, action="save"):
    """Apply only this connection's cache/log settings; never touch system logs."""
    values = storage_options(preferences)
    clear_cache = action in {"clear_cache", "clear_both"}
    clear_log = action in {"clear_log", "clear_both"}
    if hub := hass.data.get(DOMAIN, {}).get(entry.entry_id):
        await hub.async_configure_storage(values)
        if clear_cache:
            await hub.async_clear_cache()
        if clear_log:
            await hub.log.async_clear()
    else:
        cache = Store(hass, 1, f"{DOMAIN}.mqtt.{entry.entry_id}")
        stored = await cache.async_load() or {"devices": [], "ignored": {}}
        stored["devices"] = (
            recent_device_snapshots(
                stored.get("devices", []), values[CONF_RETENTION_DAYS]
            )
            if values[CONF_REMEMBER_DEVICES] and not clear_cache
            else []
        )
        await cache.async_save(stored)
        log = BeWaveLog(hass, entry.entry_id, values)
        await log.async_load()
        if clear_log:
            await log.async_clear()
        else:
            await log.async_prune()
    # No integration reload is needed: current values and controls remain live.
    hass.config_entries.async_update_entry(entry, options={**entry.options, **values})
