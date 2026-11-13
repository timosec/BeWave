# Changelog

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

MQTT commands and automatic migration from Node-RED MQTT entity IDs are not included.
