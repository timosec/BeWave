# Changelog

## 0.11.0

- Restore known temperature, humidity, battery, signal, voltage, firmware, input and diagnostic/alarm telemetry as optional read-only entities, disabled by default.
- Keep detection contacts and existing output controls enabled by default.
- Preserve user enable/disable choices, custom names and stable IDs; stop deleting measurement entities at setup.
- Add actual HA registry enable/reload tests, numeric/text parsing checks and disabled-state/history safeguards.

## 0.10.0

- Add explicit Dutch/English/system language selection for MQTT function names, discovery button and menu choices.
- Apply language and MQTT display/command options in place, preserving current states and entity IDs.
- Resolve serial-only partial updates using the established topic/channel instead of creating a spurious channel-zero device.
- Verify detector on/off transitions, unchanged-message handling, idle availability and genuine disconnect recovery.
- Document profile-language scope and the idle/detection MQTT samples needed to diagnose missing physical detections.

## 0.9.0

- Add own cache/log size reporting in MB and GB, with read-only local HA log-file totals when available.
- Add optional cache persistence, optional warnings/errors-only logging, retention days and maximum own log MB.
- Prune own retained data on startup, settings changes and hourly.
- Add cache/log clearing without deleting live controls or removed-device exclusions.
- Reduce routine TCP logging and rate-limit unmatched-feedback warnings.
- Preserve storage preferences when editing MQTT settings.
- Add storage scope, retention, size-bound, clear and translation tests.

## 0.8.0

- Allow individual device removal through Home Assistant’s device-page action.
- Add MQTT device management for removal, searching and explicit restoration.
- Persist removed-device exclusions across telemetry, restart and synchronization.
- Include old inactive device records in removal choices.
- Add a hub-level search button publishing only the existing SYNC request.
- Add offline removal, duplicate-name, restoration and translated-menu tests.

## 0.7.1

- Restore motion detectors, magnetic contacts and other functional detections filtered out by 0.7.0.
- Preserve functional detector entities during telemetry cleanup and cache restore.
- Keep diagnostics excluded and retain the inactivity-expiry fix.
- Use motion/smoke/CO classes where the reported detector type is known.
- Avoid redundant generic detection entities when specific detection fields are present.
- Add detector update and scope regression tests.

## 0.7.0

- Discover only devices/channels with `on_off`, exposing one switch each.
- Ignore diagnostic and measurement fields and remove old generated telemetry entities and empty child devices during upgrade.
- Preserve existing switch identities.
- Remove the 180-second idle expiry and its options field, including the effect of older saved expiry options.
- Request a one-time status SYNC after setup/reconnection.
- Keep live-feedback, disconnect and route-replacement protections.
- Add idle-output, upgrade-cleanup, old-cache filtering and synchronization regressions.

## 0.6.1

- Supply explicit MQTT/TCP menu labels, so missing or older cached translations cannot render empty options.
- Test menu labels and actual Home Assistant translation loading in Dutch and English.
- Keep MQTT control and existing configuration unchanged.

## 0.6.0

- Add native on/off switches for components reporting `on_off`.
- Add an editable command topic prefix, matching BE WAVE Subscribe topic.
- Publish non-retained QoS 0 commands to the current device index; use live feedback for the displayed state.
- Reject control when broker/device telemetry is offline, stale, invalid or has a replaced route.
- Prevent retained snapshots from being treated as live readings.
- Include a real local MQTT broker round-trip test and regression tests.
- Remove the transition guide and update installation/control instructions.

## 0.5.0

- Add native MQTT telemetry using Home Assistant's existing MQTT connection.
- Discover physical devices and fields from `<base>/devices/<index>/tx`.
- Group device channels as child devices under a BE WAVE hub.
- Keep discovered entity metadata across restarts, without restoring stale states.
- Mark stale/disconnected measurements unavailable; reject malformed values.
- Keep the existing virtual TCP zones and buttons available.
- Add an editable TCP host through options and reconfiguration, preserving entity identities.
- Link MQTT users to Home Assistant's broker settings for IP/credential changes.
- Fix repository documentation and issue URLs.
- Add protocol and Home Assistant integration tests.

Alarm-group commands are not included in this release.
