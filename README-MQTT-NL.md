# BE WAVE via MQTT — versie 0.7.0

Deze Home Assistant-integratie voegt alleen schakelbare BE WAVE-componenten toe.
Eén BE WAVE-hoofdapparaat bevat aparte subapparaten, met per apparaat één
**Schakelaar**. Er zijn geen virtuele IP-apparaten nodig voor ondersteunde
fysieke uitgangen.

Dit is een custom integration voor Home Assistant, geen afzonderlijk Supervisor-add-onproces.

## Wat wordt toegevoegd?

Alleen componenten die een `on_off`-veld melden worden herkend als schakelbaar.
Apparaten zonder dat veld worden overgeslagen. De integratie voegt geen
meet-, status- of diagnose-entiteiten toe voor temperatuur, batterij, signaal,
firmware, contacten, detectie of alarmstatus. BE WAVE kan zulke gegevens nog in
zijn JSON-berichten opnemen; de integratie slaat ze over en bewaart ze niet.

Bij meerdere kanalen krijgt ieder schakelbaar kanaal zijn eigen subapparaat.
De naam komt uit BE WAVE. Een eigen naam in Home Assistant blijft behouden.

## Installeren of bijwerken

Vereist: Home Assistant **2026.10.0 of nieuwer**, een werkende MQTT-integratie
in Home Assistant en een BE WAVE-versie met MQTT-ondersteuning.

1. Maak een kopie van de bestaande map `config/custom_components/bewave`.
2. Vervang de volledige map door `custom_components/bewave` uit de ZIP.
3. Herstart Home Assistant. Een bestaande BE WAVE-configuratie hoeft niet verwijderd te worden.
4. Alleen bij een nieuwe installatie: kies **Integratie toevoegen → BE WAVE → MQTT — automatisch schakelaars toevoegen**.
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

## Minder entiteiten bij bijwerken

Bij het starten van versie 0.7.0 worden de sensor- en binaire-sensorentiteiten
opgeruimd die eerdere MQTT-versies van deze BE WAVE-integratie zelf aanmaakten.
Lege subapparaten worden daarbij verwijderd. Bestaande schakelaars behouden hun
entiteits-ID's. De oude meetvelden worden ook uit de eigen apparaatcache gefilterd.

De opruiming raakt alleen entiteiten die bij deze MQTT-configuratie en de eigen
gegenereerde identificaties horen. Andere MQTT-integraties en de bestaande
TCP-koppeling worden niet opgeschoond.

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

Deze versie voegt alleen aan/uit toe. Helderheidsregeling, thermostaatbediening,
scènes en het in-/uitschakelen van alarmgroepen worden niet aangeboden.
De commandostructuur is vergeleken met een bestaande community-implementatie;
zie [PROTOCOL.md](PROTOCOL.md).

## Controle

De tests gebruiken Home Assistant 2026.10.4, met onder andere een echte lokale
MQTT-broker en een gesimuleerd BE WAVE-apparaat. Er wordt gecontroleerd dat een
schakelaar na een lange periode zonder updates nog kan schakelen, dat alleen
schakelaars worden aangemaakt en dat oude diagnose-entiteiten worden opgeruimd.
Ook configuratie, Nederlands/Engels, herladen, reconnect en IP-wijzigingen worden getest.

Een praktijktest met de eigen BE WAVE-hub blijft nodig.

```sh
python -m pip install -r requirements-test.txt
python -m pytest -q -W error
ruff check custom_components/bewave tests
```
