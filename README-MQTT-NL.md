# BE WAVE via MQTT — versie 0.5.0

Deze Home Assistant-integratie ontvangt de bestaande BE WAVE MQTT-statusberichten
en maakt automatisch apparaten en entiteiten aan. Geen Node-RED en geen virtuele
IP-apparaten nodig voor de metingen en statussen van fysieke apparaten.

Het is een **custom integration voor Home Assistant**, te installeren via HACS
of de map `custom_components`. Het is geen apart Supervisor-add-onproces.

## Wat wordt toegevoegd?

- Eén hoofdapparaat **BE WAVE** onder de BE WAVE-integratie.
- Eén subapparaat per serienummer en kanaal, met de naam uit de BE WAVE-app.
- Per apparaat alleen de ondersteunde velden die dat apparaat daadwerkelijk meldt.
- Ondersteuning voor later binnenkomende apparaten en extra velden.
- Naamwijzigingen in BE WAVE worden overgenomen; eigen namen in Home Assistant blijven behouden.

| BE WAVE-veld | Entiteit |
| --- | --- |
| `temperature` | Temperatuur (°C) |
| `battery` | Batterij (%) |
| `signal` | Signaal (%) |
| `voltage_supply` | Voedingsspanning (V) |
| `errors_count`, `errors_memory_count` | Fouten en foutgeheugen |
| `fw_version` | Firmwareversie |
| `magnetic` | Raamcontact |
| `vibration` | Trilling |
| `violation` | Detectie |
| `on_off` | Status |
| `alarm_armed` | Ingeschakeld |
| `alarm_detected`, `warning_alarm` | Alarm en waarschuwing |
| `block_unblock` | Geblokkeerd |

De binaire waarden worden als 0 = uit en 1 = aan weergegeven. Controleer de
betekenis bij het eigen apparaat, met name bij magneetcontacten en blokkering.
Onbekende of ongeldige waarden blijven onbekend en worden geen 0.

## Installeren

Vereist: **Home Assistant 2026.10.0 of nieuwer**, de Home Assistant MQTT-integratie
en een BE WAVE-versie met MQTT-ondersteuning.

1. Maak bij een bestaande installatie een kopie van `config/custom_components/bewave`.
2. Kopieer de meegeleverde map `custom_components/bewave` naar
   `config/custom_components/bewave`. Vervang de bestanden in die map.
3. Herstart Home Assistant.
4. Controleer bij **Instellingen → Apparaten & diensten → MQTT** of de brokerverbinding werkt.
5. Kies **Integratie toevoegen → BE WAVE → MQTT — automatisch apparaten toevoegen**.
6. Vul in:

   | Instelling | Waarde |
   | --- | --- |
   | Naam | BE WAVE |
   | MQTT-basistopic | `bewave` bij berichten zoals `bewave/devices/16/tx` |
   | Vervaltijd status | `180` seconden bij een pollinterval van `30` seconden |

7. Wacht op nieuwe statusberichten. Apparaten verschijnen onder de BE WAVE-integratie.

Gebruikersnaam, wachtwoord en brokeradres worden uitsluitend beheerd door de
MQTT-integratie van Home Assistant. Deze integratie gebruikt dezelfde verbinding.
Vul geen brokerwachtwoord in bij BE WAVE in Home Assistant.

## Instellingen in de BE WAVE-app

Behoud een MQTT-configuratie die al aantoonbaar statusberichten verstuurt.
Stel de server in op het adres van de MQTT-broker, niet automatisch op het adres
van de BE WAVE-hub. De gebruiker en het wachtwoord moeten op de broker bestaan.

De integratie luistert standaard naar `bewave/devices/+/tx`. Het ontvangen
bericht moet een JSON-object zijn met `sn`, optioneel `channel`, en statusvelden.
De eerste status van een apparaat moet een serienummer bevatten. Latere gedeeltelijke
updates op hetzelfde topic mogen het serienummer weglaten.

Gebruik voor meerdere hubs verschillende basistopics. De subscribe-instelling
voor BE WAVE-besturingscommando's wordt door deze alleen-lezen versie niet gebruikt.

## IP-adres wijzigen via Bewerken

### Bestaande TCP-koppeling

Ga naar **Instellingen → Apparaten & diensten → BE WAVE** en kies:

- **Configureren → Hub IP-adres wijzigen**, of
- het menu **⋮ → Opnieuw configureren**.

Voer het nieuwe IP-adres of de nieuwe hostnaam in en sla op. De koppeling wordt
herladen. De bestaande apparaat- en entiteits-ID's blijven gelijk, ook na een
tweede adreswijziging. De eerder ingestelde zones en commando's blijven behouden.

### MQTT-koppeling

Ga naar **Instellingen → Apparaten & diensten → MQTT → Opnieuw configureren**
om het brokeradres of de inloggegevens te wijzigen. BE WAVE gebruikt daarna
automatisch de bijgewerkte verbinding. De BE WAVE-instellingen bevatten ook een
link naar dit scherm. Wijzig zo nodig hetzelfde brokeradres in de BE WAVE-app.

De MQTT-versie heeft geen afzonderlijk BE WAVE-hub-IP-adres nodig.

## Herstarten en beschikbaarheid

Ontdekte apparaatnamen, types en veldnamen worden opgeslagen, zodat de entiteiten
na een herstart blijven bestaan. Meetwaarden en raam-/alarmstatussen worden niet
als actuele waarden uit een bestand hersteld. Ze worden pas beschikbaar na
nieuwe MQTT-berichten.

Wanneer de brokerverbinding wegvalt, worden entiteiten niet beschikbaar. Na
herverbinden is per veld een nieuw statusbericht nodig. Ook worden waarden niet
beschikbaar wanneer ze langer dan de ingestelde vervaltijd niet zijn bijgewerkt.
De controle gebeurt iedere 15 seconden. Een gedeeltelijk bericht ververst alleen
de velden die daadwerkelijk in dat bericht staan.

Pas de vervaltijd via **BE WAVE → Configureren** aan als het pollinterval langer is.

## Wat deze versie nog niet doet

De MQTT-koppeling toont statussen en metingen. Ze verstuurt nog geen opdrachten
voor relais, scènes of in-/uitschakelen van het alarm. Daarvoor moet eerst de
officiële BE WAVE-structuur voor commandotopics, payloads en antwoorden worden
vastgesteld. Er worden geen commando's afgeleid uit statusvelden.

Virtuele apparaten die al bestaan en zelf MQTT-statussen publiceren kunnen nog
steeds verschijnen. Ze hoeven niet nieuw te worden aangemaakt voor de ondersteunde
metingen en statussen van fysieke apparaten.

## Ontwikkeling en controle

De geautomatiseerde tests gebruiken Home Assistant 2026.10.4 met de MQTT-transportlaag
gemockt. Ze controleren onder andere apparaat- en subapparaatregistratie, nieuwe
velden, kanaalscheiding, topicwijzigingen, ongeldige gegevens, vervaltijd,
verbindingsverlies, herladen en TCP-adreswijzigingen met behoud van entiteiten.

Een praktijktest met de eigen BE WAVE-hub en MQTT-broker is nog nodig.

```sh
python -m pip install -r requirements-test.txt
python -m pytest -q
ruff check custom_components/bewave tests
```
