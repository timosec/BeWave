# BE WAVE 0.6.0

## Nieuw

- Automatische aan/uit-schakelaars voor componenten met `on_off`.
- Apart instelbaar commando-basistopic, gelijk aan Subscribe topic in BE WAVE.
- Bevestiging van de getoonde schakelstand via binnenkomende statusberichten.

## Verbeterd

- Bewaarde brokerberichten gelden niet meer als actuele apparaatstatus.
- Geen opdrachten bij ontbrekende, ongeldige of verouderde apparaatstatus.
- Een gewijzigde BE WAVE-apparaatindex wordt ook voor bediening gevolgd.
- Documentatie opgeschoond en installatie- en bedieningsinstructies bijgewerkt.
- Extra tests met een echte lokale MQTT-broker, Home Assistant en een gesimuleerd apparaat.

## Instellen

| Instelling | BE WAVE-app | BE WAVE-integratie |
| --- | --- | --- |
| Status | Publish topic: `bewave` | Status-basistopic: `bewave` |
| Commando's | Subscribe topic: `bewave/command` | Commando-basistopic: `bewave/command` |

Gebruik dezelfde MQTT-broker. Kies bij een bestaande 0.5.0-koppeling in Home Assistant
**BE WAVE → Configureren** om het commando-basistopic te controleren.

Vervang `custom_components/bewave` door de meegeleverde versie en herstart
Home Assistant. De bestaande BE WAVE-configuratie blijft behouden.

## Afbakening

Vereist Home Assistant 2026.10.0 of nieuwer. Aan/uit wordt toegevoegd voor
componenten die `on_off` melden. Alarmgroepen, helderheidsregeling en
thermostaatbediening zijn geen onderdeel van deze release.

De test met een lokale broker vervangt geen praktijktest met de eigen BE WAVE-hub.
