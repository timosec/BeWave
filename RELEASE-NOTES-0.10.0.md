# BE WAVE 0.10.0 — taal en statusupdates

- Nieuw: **Configureren → Taal / Language → Nederlands / English / Home Assistant**.
- Functienamen, de zoekknop en menukeuzes veranderen direct. Eigen namen en ID’s blijven behouden.
- Formulierteksten en Gedetecteerd/Niet gedetecteerd volgen de profieltaal van Home Assistant.
- Opslaan van MQTT-instellingen behoudt de verbinding en live standen.
- Korte berichten met serienummer zonder kanaal worden bij een bekende route aan het juiste kanaal gekoppeld.
- Geen inactiviteitsverval voor melders; echte MQTT-uitval blijft zichtbaar.

Vervang de volledige map `custom_components/bewave` en herstart Home Assistant.
Verwijder de integratie of apparaten niet. Er is geen nieuwe configuratie nodig.

72 tests geslaagd op Home Assistant 2026.10.4, inclusief een lokale echte MQTT-broker
met gesimuleerde hub. Nederlands/Engels wisselen, behoud van eigen namen en live standen,
detectorstatussen aan/uit, herhaalde berichten, kanaalloze updates en reconnect zijn getest.
De fysieke BE WAVE-hub is niet bediend. Ontbrekende bewegingsmeldingen bij de gebruiker
zijn pas te verklaren met MQTT-payloads tijdens rust en beweging op hetzelfde topic.
