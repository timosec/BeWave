# BE WAVE 0.7.0

## Alleen schakelbare apparaten

Alleen apparaten/kanalen die `on_off` melden worden toegevoegd, met ieder één
Schakelaar. Temperatuur-, batterij-, signaal-, firmware-, detectie- en andere
diagnose-/statusentiteiten worden niet meer aangemaakt. Bijbehorende gegevens
uit de MQTT-berichten worden genegeerd en niet in de apparaatcache bewaard.

Bij het opstarten worden eerder door deze BE WAVE MQTT-koppeling aangemaakte
sensor- en binaire-sensorentiteiten opgeruimd. Lege subapparaten worden verwijderd.
Bestaande schakelaars behouden hun entiteits-ID's. Andere integraties en de
TCP-koppeling worden niet door deze opruiming geraakt.

## Opgelost: schakelen stopt na inactiviteit

De eerdere 180-secondenlimiet kon bediening blokkeren als een relais zijn status
alleen bij wijzigingen verstuurde. Deze limiet en het bijbehorende instellingenveld
zijn verwijderd. Ook een eerder opgeslagen `expire_after` wordt niet meer gebruikt.

Een live schakelstatus blijft geldig voor de huidige MQTT-sessie. Bij een
verbroken brokerverbinding wordt de schakelaar niet beschikbaar. Na opnieuw
verbinden wordt een live status gevraagd met een eenmalige SYNC-aanvraag.

## Bijwerken

1. Vervang de volledige map `custom_components/bewave` door die uit deze ZIP.
2. Herstart Home Assistant.
3. De bestaande configuratie en schakelaars kunnen blijven staan. De oude
   meet-/diagnose-entiteiten van deze koppeling worden automatisch opgeruimd.

Gebruik dezelfde status- en commandotopics als voorheen. Standaard zijn dat
`bewave` en `bewave/command`.

## Controle

37 geautomatiseerde tests geslaagd op Home Assistant 2026.10.4, inclusief:

- Schakelen na een gesimuleerde dag zonder updates via een echte lokale broker.
- Schakelen na een week zonder updates in de integratietest.
- Alleen schakelaars toevoegen, zonder meet-/diagnosevelden te bewaren.
- Opruimen van oude entiteiten en cache, met behoud van schakelaar-ID's.
- Reconnect, retained berichten, gewijzigde apparaatindex, configuratie en vertalingen.

De tests gebruiken een gesimuleerd BE WAVE-apparaat; de eigen fysieke installatie
moet nog worden gecontroleerd.
