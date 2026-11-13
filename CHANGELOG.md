# Changelog

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
