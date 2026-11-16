Version **0.10.0** discovers native switches and functional detectors under a BE WAVE hub, including motion, magnetic contacts, vibration, smoke and other reported detections. Diagnostic entities are not created. Requires Home Assistant 2026.10.0 or newer.

**[Nederlandse installatiehandleiding](README-MQTT-NL.md)** · **[Release notes](RELEASE-NOTES-0.10.0.md)**

1. Replace `custom_components/bewave` and restart Home Assistant.
2. Configure Home Assistant’s MQTT integration.
3. Add **BE WAVE → MQTT**. Use the status base matching BE WAVE Publish topic and command base matching Subscribe topic; for example `bewave` and `bewave/command`.
4. Switches and functional detectors are added without battery, signal, firmware or error-counter entities.

5. <img width="1205" height="4365" alt="image" src="https://github.com/user-attachments/assets/68c5d3b4-9d55-42d4-80a0-5809bbaf31ee" />


Switches no longer expire after 180 seconds without status changes. A live state remains valid for the current MQTT session. After reconnect/reload a live update is required; a one-time SYNC request asks the hub for statuses. State updates remain driven by device feedback. Obsolete measurement/diagnostic entities are cleaned up only for this integration’s MQTT entry, preserving functional detectors.

See [the changelog](CHANGELOG.md), [protocol scope](PROTOCOL.md) and [tests](tests/). A real local MQTT test includes switching after a simulated day without status updates. Physical BE WAVE hardware is not controlled by the tests.

## Language and activity

Open **Configure → Taal / Language** and choose Home Assistant (system language),
Nederlands or English. This changes generated function names, the discovery button
and explicit menu/action choices in place. Custom device names, user-renamed entities
and entity IDs are preserved. Form titles/descriptions and state labels follow the
Home Assistant user's profile language; choose English in that profile for the full UI.

Saving MQTT display/command settings no longer reloads the integration or discards
live states. Short status updates with a serial but no channel use the known topic's
channel, preventing accidental channel-zero duplicates. Identical incoming readings
do not cause additional state changes; quiet detectors do not expire on inactivity.
A real MQTT disconnect still makes entities unavailable. On reconnect, fresh status
is required so old clear readings are never presented as current detection states.

If motion still does not register, collect the detector's exact MQTT topic and two
payloads (idle and during movement) from the MQTT listener. A screenshot of Activity
alone cannot establish whether the hub published a detection, a different field or
no message. Do not substitute generic alarm/tamper fields for motion without evidence.
Activity/history is managed by Home Assistant's recorder, separately from this
integration's small optional error log and cache.

## Storage and retention

**Configure → Storage, log and retention** shows measured own-cache and own-log sizes in MB/GB. Small device metadata caching is enabled by default; the optional own warning/error log is disabled. Choose retention (default 30 days) and a maximum own log size (default 5 MB), or clear the cache/log. Oldest log entries are discarded first; automatic pruning runs at setup and hourly. Removed-device exclusions are preserved, and clearing storage does not reload or delete live controls.

Only this connection’s own cache/log is managed. Local Home Assistant log-file sizes may be displayed read-only, but system journals and the shared history database are not cleared or constrained. No journal size is invented where it is unavailable.

## Device management

The MQTT options menu now includes **Search for new devices**, **Remove a device**, and **Restore a removed device**, alongside MQTT settings. The parent BE WAVE device also has a search button. Search requests `SYNC`; new supported devices appear when the hub publishes telemetry.

Individual devices can be deleted from Home Assistant’s device page. Removal persists in this connection’s cache and is not reversed by normal telemetry, restart or a search. Restore is an explicit per-device action. The physical BE WAVE configuration is not modified. Duplicate names are distinguished by model and identity in the selection menu. Legacy TCP device records can also be removed, including inactive orphan records.

## Legacy TCP configuration

The instructions below apply to the existing TCP mode, selected via **BE WAVE → TCP**.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=timosec&repository=Satel-BeWave-Virtual-IP-Device&category=Integration)

# BeWave custom integration

This custom integration models each configured BeWave zone as up to two Home Assistant entities:

- a **Button** entity that sends the configured trigger command to BeWave
- a **Binary Sensor** entity that reflects the latest feedback status from BeWave

## Configuration

For each zone, configure:

- **Name**: friendly zone name
- **HTTP command to BeWave**: exact trigger text to send when the button is pressed
- **HTTP output on request**: feedback text that means the zone is ON
- **HTTP output off request**: feedback text that means the zone is OFF
- **Listen port**: TCP port Home Assistant listens on for BeWave feedback

The integration still uses raw TCP under the hood, matching the original Homebridge plugin behavior:

- outgoing command to `<host>:5000`
- push feedback from BeWave back into Home Assistant

## Installation

1. Copy `custom_components/bewave` into your Home Assistant config folder.
2. Restart Home Assistant.
3. Add the BeWave integration via **Settings > Devices & Services**.
4. Configure one or more zones.

## Notes

- If the feedback fields are left empty, only the trigger button will be created.
- Existing old switch entities from earlier builds may remain in the entity registry and can be removed manually.

## Setup

<img width="730" height="383" alt="image" src="https://github.com/user-attachments/assets/42205247-fa12-4075-97ed-ee1e62825e04" />

Enter the IP address of the Hub.

<img width="733" height="385" alt="image" src="https://github.com/user-attachments/assets/d00784ef-0e9c-478b-82b7-75d6c91cbc77" />

First, configure the first zone:

<img width="729" height="985" alt="image" src="https://github.com/user-attachments/assets/5caddc44-c569-4e26-83be-69fce4cffa56" />

1: Zone name</br>
2: Command to send to the Bewave hub</br>
3: Status (ON) – used to receive the ON state from the Bewave hub</br>
5: Status (OFF) – used to receive the OFF state from the Bewave hub


<img width="730" height="449" alt="image" src="https://github.com/user-attachments/assets/1e29a376-2fb0-4ee3-9797-db2ac4e5dcb0" />

1: To add an new zone </br>
2: to save the zone

## Settings in the BeWave Hub: 

<img width="600" height="1203" alt="image" src="https://github.com/user-attachments/assets/d023a499-7045-416a-a7fd-33854acb9042" />

