# BE WAVE via MQTT — versie 0.6.0

Deze Home Assistant-integratie ontvangt de bestaande BE WAVE MQTT-statusberichten
en maakt automatisch apparaten en entiteiten aan. Er zijn geen virtuele IP-apparaten nodig voor de ondersteunde metingen, statussen en aan/uit-bediening van fysieke apparaten.

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
| `on_off` | Aan/uit-schakelaar en status |
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
   | Status-basistopic | `bewave` bij berichten zoals `bewave/devices/16/tx` |
   | Commando-basistopic | `bewave/command`, gelijk aan Subscribe topic in de BE WAVE-app |
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

Gebruik voor meerdere hubs verschillende basistopics. Het commando-basistopic moet exact overeenkomen met Subscribe topic in de BE WAVE-app.

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
nieuwe, live MQTT-berichten. Bewaarde brokerberichten worden uitsluitend gebruikt om apparaten en velden te herkennen; hun waarden gelden niet als actuele status.

Wanneer de brokerverbinding wegvalt, worden entiteiten niet beschikbaar. Na
herverbinden is per veld een nieuw statusbericht nodig. Ook worden waarden niet
beschikbaar wanneer ze langer dan de ingestelde vervaltijd niet zijn bijgewerkt.
De controle gebeurt iedere 15 seconden. Een gedeeltelijk bericht ververst alleen
de velden die daadwerkelijk in dat bericht staan.

Pas de vervaltijd via **BE WAVE → Configureren** aan als het pollinterval langer is.

## Componenten aan- en uitschakelen

Componenten die een geldig `on_off`-veld melden, krijgen automatisch een
**Schakelaar** onder hun eigen subapparaat. Bijvoorbeeld een relaiskanaal dat
`on_off: 0` of `on_off: 1` verstuurt. Componenten zonder dit veld krijgen geen
schakelknop.

Stel voor de standaardconfiguratie in de BE WAVE-app in:

| Instelling | Waarde |
| --- | --- |
| Publish topic | `bewave` |
| Subscribe topic | `bewave/command` |

Gebruik in de BE WAVE-integratie dezelfde waarden als status- en commando-basistopic.
Behoud een afwijkende maar werkende configuratie en neem de bijbehorende waarden over.

Bij aan/uit wordt bijvoorbeeld op `bewave/command/devices/23/rx` een JSON-bericht
`{"on_off": 1}` of `{"on_off": 0}` verstuurd. Het getal 23 is de index uit het
ontvangen statustopic, niet het serienummer of kanaalnummer. Als BE WAVE de
apparaatindex verandert, gebruikt de schakelaar de nieuwe index.

Opdrachten worden niet bewaard door de broker (retain uit) en gebruiken QoS 0.
Er wordt alleen verzonden met een actieve MQTT-verbinding en een recente, geldige
apparaatstatus. Een publicatiefout wordt als fout teruggegeven. De getoonde
stand verandert pas nadat een statusbericht de wijziging bevestigt.

### Afbakening bediening

Deze versie ondersteunt aan/uit voor componenten met `on_off`. Dimmers worden
hiermee alleen aan/uit geschakeld; helderheidsregeling, thermostaatinstellingen,
scènes en het in-/uitschakelen van alarmgroepen zijn niet toegevoegd.

## Protocolreferentie

De commandostructuur is gecontroleerd aan de hand van de bestaande community-
implementatie [homebridge-bewave-mqtt](https://github.com/rmarobert/homebridge-bewave-mqtt).
Zie [PROTOCOL.md](PROTOCOL.md) voor de gebruikte referentie en afbakening.

## Ontwikkeling en controle

De tests gebruiken Home Assistant 2026.10.4. Naast afzonderlijke tests met een gemockte transportlaag is er een test met een echte lokale MQTT-broker en echte Home Assistant MQTT-verbinding. Een gesimuleerd BE WAVE-apparaat publiceert status, ontvangt de schakelopdracht en stuurt de terugmelding. Er worden geen opdrachten naar een fysieke installatie verstuurd.

Verder worden onder andere subapparaten, nieuwe velden, kanaalscheiding, topicwijzigingen, ongeldige gegevens, bewaarde brokerberichten, vervaltijd, verbindingsverlies, herladen en TCP-adreswijzigingen getest.

Een praktijktest met de eigen BE WAVE-hub en MQTT-broker is nog nodig.

```sh
python -m pip install -r requirements-test.txt
python -m pytest -q
ruff check custom_components/bewave tests
```
