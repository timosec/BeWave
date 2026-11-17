# BE WAVE via MQTT — versie 0.11.0

Deze Home Assistant-integratie voegt schakelaars en functionele melders toe.
Eén BE WAVE-hoofdapparaat bevat aparte subapparaten. Per apparaat verschijnen
de bedieningen en detecties die het apparaat meldt. Extra informatie is standaard uitgeschakeld. Er zijn geen virtuele
IP-apparaten nodig voor ondersteunde fysieke componenten.

Dit is een custom integration voor Home Assistant, geen afzonderlijk Supervisor-add-onproces.

## Zelf extra informatie inschakelen

Detectie-/alarmcontacten en schakelaars blijven standaard actief. Extra informatie,
zoals temperatuur, luchtvochtigheid, batterij, signaal, voedingsspanning, firmware,
fouttellers en alarmstatussen, wordt als **uitgeschakelde entiteit** toegevoegd.
Alleen bekende velden die de hub voor dat apparaat meldt worden aangemaakt.

1. Open het BE WAVE-apparaat en toon de uitgeschakelde entiteiten. Of open
   **Instellingen → Apparaten en diensten → Entiteiten**, filter op BE WAVE en
   laat uitgeschakelde entiteiten zien.
2. Open bijvoorbeeld **Temperatuur**, klik op het tandwiel en zet **Ingeschakeld** aan.
3. Sla op. Home Assistant kan ongeveer 30 seconden nodig hebben om de entiteit te
   laden; daarna levert het volgende live MQTT-bericht de waarde.

Dit kan apart per entiteit en apparaat. Eigen namen, entiteit-ID’s en de keuze
actief/inactief blijven behouden na een herstart. Bestaande actieve schakelaars
blijven werken. Al eerder ingestelde actieve of inactieve entiteiten worden niet
teruggezet. Alleen nieuw toegevoegde extra informatie start standaard uitgeschakeld.

Uitgeschakelde entiteiten hebben geen actieve Home Assistant-status of geschiedenis.
De kleine apparaatcache bewaart alleen metadata, geen meetgeschiedenis. De eigen
optionele foutlog blijft standaard uitgeschakeld.

## Taal en activiteit

Open **BE WAVE → Configureren → Taal / Language**. Kies **Nederlands**, **English**
of **Home Assistant** (de systeemtaal). Dit verandert functienamen zoals Beweging/Motion,
de zoekknop en menukeuzes direct. Eigen apparaatnamen, zelf aangepaste entiteitsnamen
en entiteit-ID’s blijven behouden. Titels en uitleg van formulieren en statusteksten
zoals “Gedetecteerd” volgen de profieltaal van Home Assistant. Kies daar ook English
voor een volledig Engelse interface.

MQTT-instellingen opslaan herstart de integratie niet meer: actuele sensorstanden
blijven behouden. Korte statusberichten met serienummer maar zonder kanaal worden
gekoppeld aan het bekende kanaal op dat topic. Dat voorkomt onbedoelde duplicaten
op kanaal 0. Herhaalde gelijke metingen veroorzaken geen extra statuswijzigingen.
Melders worden niet door een inactiviteitstimer onbeschikbaar gemaakt.

Bij een echte MQTT-verbindingsonderbreking blijft “Niet beschikbaar” zichtbaar.
Na opnieuw verbinden is een vers statusbericht nodig. Een oude melding “geen beweging”
wordt niet als actuele status gepresenteerd.

Ontbreekt beweging nog? Luister in **Instellingen → Apparaten en diensten → MQTT →
Configureren** naar **bewave/devices/+/tx** (of de eigen statusprefix). Verzamel het
exacte topic met een bericht in rust en tijdens beweging voor dezelfde melder.
Daarmee is vast te stellen welke detectievelden de hub werkelijk verstuurt.
Een screenshot van Activiteit laat dat niet zien. De standaard fysieke melders gebruiken
hun specifieke veld zoals `motion`, `magnetic` of `smoke`; `violation` is alleen een
bestaande terugval en wordt niet opgeteld bij een bekend specifiek detectieveld.

Het paneel Activiteit is de geschiedenis van Home Assistant en staat los van de eigen
optionele foutlog en apparaatcache van BE WAVE.

## Opslag, loggrootte en bewaartermijn

Open **BE WAVE → Configureren → Opslag, log en bewaartermijn**. Het scherm toont
het echte bestandsgebruik in MB en GB en biedt deze instellingen:

| Instelling | Standaard | Betekenis |
| --- | --- | --- |
| Apparaatcache op schijf bewaren | Aan | Alleen kleine apparaatmetadata, geen meetgeschiedenis |
| Eigen foutlog bewaren | Uit | Optioneel waarschuwingen en fouten van deze MQTT-koppeling bewaren |
| Bewaartermijn | 30 dagen | Oudere cachemetadata en eigen logmeldingen opruimen |
| Maximale grootte eigen foutlog | 5 MB | Bij bereiken van de limiet vervallen de oudste logmeldingen eerst |

De termijn is instelbaar van 1 tot 3650 dagen; de loglimiet van 1 tot 100 MB.
Nieuwe grenzen worden bij opslaan direct toegepast. Automatisch opruimen gebeurt
ook bij opstarten en ieder uur. De bewaartermijn is een aantal dagen; 30 dagen
is dus geen exacte kalendermaand.

De acties zijn **Instellingen opslaan**, **Apparaatcache wissen**, **Eigen BE WAVE-log wissen**
en **Apparaatcache en eigen log wissen**. Wissen laat de live bediening en apparaat-
registratie intact. Bewust verwijderde apparaten blijven uitgesloten: die lijst
is een instelling, geen tijdelijk logboek, en verloopt niet automatisch.

### Wat wordt bewaard?

De apparaatcache bevat alleen naam, identificatie, type, MQTT-topic, beschikbare
functienamen en een tijdstip voor de bewaartermijn. Actuele standen en normale
MQTT-payloads worden niet als een geschiedenis opgeslagen. De cache mag volledig
worden uitgezet; na een herstart worden de functies dan opnieuw aangemaakt bij
nieuwe berichten van de hub. De uitsluitingen blijven bewaard.

De eigen foutlog staat standaard uit en bewaart, als hij wordt aangezet, alleen
verbindingwaarschuwingen en verzendfouten. Normale statusberichten, debugregels
en routine-schakelacties worden niet in deze eigen log opgeslagen. De bestaande
TCP-koppeling schrijft routineberichten voortaan alleen op debugniveau en
herhaalde onbekende feedbackwaarschuwingen maximaal eenmaal per vijf minuten.

De cache staat in `/config/.storage/bewave.mqtt.<entry_id>` en de optionele eigen
log in `/config/.storage/bewave.log.<entry_id>` bij een standaardinstallatie.
Cache wissen laat het kleine bestand met uitsluitingen bestaan. Als cachebewaring
aan blijft staan, kan nieuwe apparaatmetadata later weer een cache opbouwen.

### Welke loggrootte is zichtbaar?

Het overzicht toont de eigen apparaatcache en foutlog. Daarnaast kan het de
som van lokale `home-assistant.log*`-bestanden in de configuratiemap tonen,
**uitsluitend ter informatie**. Op Home Assistant OS staan logs normaal in het
systeemjournaal; de integratie kan de grootte daarvan niet betrouwbaar uitlezen
en toont dan dat de grootte niet beschikbaar is, geen verzonnen 0 MB.

Deze instellingen wissen of begrenzen geen Home Assistant-systeemlogs, Docker-
logs, systeemjournaal, back-ups of recorder/historiedatabase. Ze gelden alleen
voor de eigen cache en optionele foutlog van deze BE WAVE MQTT-koppeling.

## Apparaten verwijderen en nieuwe apparaten zoeken

Ga bij de BE WAVE MQTT-koppeling naar **Configureren**:

| Optie | Werking |
| --- | --- |
| MQTT-instellingen | Naam en commando-basistopic wijzigen |
| Zoeken naar nieuwe apparaten | Een synchronisatie aanvragen bij BE WAVE |
| Apparaat verwijderen | Een gekozen apparaat uit deze Home Assistant-koppeling verwijderen |
| Verwijderd apparaat herstellen | Een eerder verwijderd apparaat opnieuw toelaten |

Op het hoofdapparaat **BE WAVE** staat ook de knop **Zoeken naar nieuwe apparaten**.
Deze verstuurt alleen een synchronisatieverzoek; uitgangen worden niet geschakeld.
Nieuwe ondersteunde apparaten verschijnen zodra de hub hun MQTT-status verstuurt.
Zoeken is dus geen IP-netwerkscan en kan geen status afdwingen als de hub niet antwoordt.

Een individueel apparaat kan ook via de eigen apparaatpagina worden verwijderd.
De nieuwe versie staat de verwijderactie van Home Assistant toe, ook voor een oude,
inactieve vermelding. Bij twee gelijke namen toont het keuzemenu ook het type en de
identificatie, zodat de juiste oude vermelding geselecteerd kan worden.

Een verwijdering geldt voor deze Home Assistant-koppeling. Het apparaat wordt niet
uit de fysieke BE WAVE-installatie gewist. De koppeling onthoudt de verwijdering,
ook na een herstart: binnenkomende MQTT-berichten of opnieuw zoeken voegen dat
apparaat niet meteen weer toe. Met **Verwijderd apparaat herstellen** kan het later
weer worden toegelaten. Daarna verschijnt het bij een nieuw statusbericht.

Bestaande TCP-zoneapparaten kunnen eveneens via hun apparaatpagina worden
verwijderd. Automatisch zoeken is beschikbaar voor de MQTT-koppeling.

## Wat wordt toegevoegd?

| Functie | MQTT-veld |
| --- | --- |
| Aan/uit-schakelaar | `on_off` |
| Beweging | `motion`, of `violation` bij bekende bewegingsmelders |
| Magneetcontact | `magnetic` |
| Trilling | `vibration` |
| Rook | `smoke`, of `violation` bij ASD-melders |
| Gas / koolmonoxide | `gas`, met koolmonoxideklasse bij ACMD-melders |
| Waterdetectie | `flood` |
| Glasbreuk | `glass_break` |
| Algemene detectie | `violation` wanneer geen specifiek detectieveld beschikbaar is |

Batterij-, signaal-, firmware-, fout- en andere ondersteunde diagnosegegevens worden
standaard uitgeschakeld toegevoegd. Schakel alleen de gewenste informatie in;
ontvangen meetwaarden worden niet in de apparaatcache opgeslagen.

Bij meerdere kanalen krijgt ieder kanaal zijn eigen subapparaat. Een apparaat
met bijvoorbeeld zowel beweging als een schakelbare verlichting kan beide
functies tonen. De naam komt uit BE WAVE; een eigen Home Assistant-naam blijft behouden.

## Installeren of bijwerken

Vereist: Home Assistant **2026.10.0 of nieuwer**, een werkende MQTT-integratie
in Home Assistant en een BE WAVE-versie met MQTT-ondersteuning.

1. Maak een kopie van de bestaande map `config/custom_components/bewave`.
2. Vervang de volledige map door `custom_components/bewave` uit de ZIP.
3. Herstart Home Assistant. Een bestaande BE WAVE-configuratie hoeft niet verwijderd te worden.
4. Alleen bij een nieuwe installatie: kies **Integratie toevoegen → BE WAVE → MQTT — apparaten en melders toevoegen**.
5. Gebruik deze instellingen, of de overeenkomstige waarden van de eigen installatie:

| Instelling | BE WAVE-app | Home Assistant BE WAVE-integratie |
| --- | --- | --- |
| Status | Publish topic: `bewave` | Status-basistopic: `bewave` |
| Opdrachten | Subscribe topic: `bewave/command` | Commando-basistopic: `bewave/command` |

Home Assistant en BE WAVE moeten dezelfde MQTT-broker gebruiken. Brokeradres,
gebruiker en wachtwoord worden in Home Assistant beheerd door de MQTT-integratie.

## Geen blokkering meer na enkele minuten

De vorige versie blokkeerde bediening zodra een `on_off`-waarde meer dan
180 seconden niet was bijgewerkt. Sommige relais melden vooral wijzigingen,
waardoor een ongewijzigde schakelaar na verloop van tijd niet meer bediend kon worden.

Deze vervaltijd is verwijderd, inclusief het instellingenveld. De laatste live
schakelstatus blijft bruikbaar zolang dezelfde MQTT-verbinding actief is.
Ook een oude instelling `expire_after` uit een eerdere versie wordt niet meer gebruikt.

Wanneer de MQTT-verbinding wegvalt, wordt de schakelaar niet beschikbaar. Na een
herstart of opnieuw verbinden is een nieuwe live apparaatstatus nodig. De
integratie vraagt na het abonneren en na opnieuw verbinden één keer een
statussynchronisatie aan via `<commando-basistopic>/system/rx` met `{"action":"SYNC"}`.
De hub moet deze aanvraag ondersteunen en beantwoorden, of zelf nieuwe statusberichten sturen.

Een bewaard brokerbericht wordt gebruikt voor apparaatherkenning, maar geldt
niet als verse status na herstart of opnieuw verbinden. De getoonde stand
verandert uitsluitend op basis van een live terugmelding, niet omdat een
opdracht succesvol naar de broker is gepubliceerd.

## Bestaande entiteiten bij bijwerken

Meet- en diagnose-entiteiten worden niet meer verwijderd. Nieuw herkende extra
informatie begint uitgeschakeld. Bestaande gebruikerskeuzes, namen, ID’s,
functionele melders en schakelaars blijven behouden.

## IP-adres wijzigen

- **MQTT-broker:** ga naar **Instellingen → Apparaten & diensten → MQTT → Opnieuw configureren**.
  De BE WAVE-instellingen bevatten een link naar dit scherm. Pas zo nodig ook
  het brokeradres in de BE WAVE-app aan.
- **Bestaande TCP-koppeling:** kies bij BE WAVE **Configureren → Hub IP-adres wijzigen**
  of **⋮ → Opnieuw configureren**. De bestaande zones en entiteits-ID's blijven behouden.

De MQTT-koppeling heeft geen apart BE WAVE-hub-IP-adres nodig.

## Bediening en afbakening

Aan/uit verstuurt `{"on_off":1}` of `{"on_off":0}` naar het actuele
`<commando-basistopic>/devices/<index>/rx`. De index komt uit het ontvangen
statustopic, niet uit het serienummer. Verandert de index, dan wordt de nieuwe
route gebruikt. Een route die door een ander apparaat is overgenomen wordt ongeldig.

Opdrachten gebruiken QoS 0 en retain uit. Er wordt niet opnieuw geprobeerd of
opgeslagen voor later. Verzenden heeft een time-out van vijf seconden. Dat is
alleen een verzendlimiet, geen vervaltijd van de schakelaar.

Deze versie biedt aan/uit-bediening en functionele detectiestatussen. Helderheidsregeling, thermostaatbediening,
scènes en het in-/uitschakelen van alarmgroepen worden niet aangeboden.
De commandostructuur is vergeleken met een bestaande community-implementatie;
zie [PROTOCOL.md](PROTOCOL.md).

## Controle

De tests gebruiken Home Assistant 2026.10.4, met onder andere een echte lokale
MQTT-broker en een gesimuleerd BE WAVE-apparaat. Er wordt gecontroleerd dat een
schakelaar na een lange periode zonder updates nog kan schakelen, dat detecties actief en extra informatie uitgeschakeld worden toegevoegd. Ook het inschakelen van temperatuur, behoud van gebruikerskeuzes na herladen en het ontbreken van actieve standen voor uitgeschakelde entiteiten worden getest.
Ook configuratie, Nederlands/Engels, herladen, reconnect en IP-wijzigingen worden getest.

Een praktijktest met de eigen BE WAVE-hub blijft nodig.

```sh
python -m pip install -r requirements-test.txt
python -m pytest -q -W error
ruff check custom_components/bewave tests
```
