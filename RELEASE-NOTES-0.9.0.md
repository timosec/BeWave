# BE WAVE 0.9.0 — opslag en bewaartermijn

Open **BE WAVE → Configureren → Opslag, log en bewaartermijn**.

## Instellen

- Apparaatcache bewaren: aan/uit. Standaard alleen kleine metadata, geen meetgeschiedenis.
- Eigen foutlog bewaren: aan/uit, standaard uit. Alleen waarschuwingen en fouten.
- Bewaartermijn: bijvoorbeeld **30 dagen**, instelbaar van 1 tot 3650 dagen.
- Maximale eigen loggrootte: bijvoorbeeld **5 MB**, instelbaar van 1 tot 100 MB.

Oudere eigen gegevens worden opgeruimd bij opstarten en ieder uur. Gewijzigde
grenzen worden direct toegepast. Bij bereiken van de loglimiet vervallen de
oudste meldingen eerst. Normale MQTT-berichten worden niet als loggeschiedenis bewaard.

## Bekijken en wissen

Het scherm toont de gemeten cache- en eigen loggrootte in MB en GB. Je kunt de
apparaatcache, de eigen log of beide wissen. De apparaten, actuele bediening en
lijst met bewust verwijderde apparaten blijven behouden.

Lokale Home Assistant-logbestanden kunnen ter informatie worden gemeten. Wanneer
geen lokaal bestand beschikbaar is, zoals bij het systeemjournaal op Home
Assistant OS, wordt de grootte als niet uitleesbaar weergegeven.

De bewaartermijn en wisacties gelden alleen voor deze BE WAVE-koppeling. Ze
beheren geen systeemjournaal, andere integraties, back-ups of de gedeelde
Home Assistant-historiedatabase.

## Bijwerken

Vervang de volledige map `custom_components/bewave`, herstart Home Assistant en
vernieuw de browser met Ctrl+F5. Bestaande apparaten blijven geregistreerd.

## Controle

67 tests geslaagd op Home Assistant 2026.10.4, inclusief de eerdere MQTT-/schakel-
en detectietests. Extra controles dekken bewaartermijn, maximale bestandsgrootte,
uitschakelen en wissen van eigen logging, behoud van live bediening/uitsluitingen,
correcte gemeten bestandsgroottes en het ongemoeid laten van andere opslag.
De fysieke BE WAVE-hub is niet door deze tests bediend.
