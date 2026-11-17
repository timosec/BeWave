# BE WAVE 0.11.0 — zelf extra informatie kiezen

Detectie-/alarmcontacten en schakelaars blijven standaard actief. Extra informatie
zoals temperatuur, luchtvochtigheid, batterij, signaal, spanning, firmware,
fouttellers en alarmstatussen wordt herkend als uitgeschakelde, alleen-lezen entiteit.
Alleen ondersteunde velden die daadwerkelijk worden gemeld, worden toegevoegd.

## Een meting inschakelen

Open het apparaat en toon uitgeschakelde entiteiten, of open Instellingen →
Apparaten en diensten → Entiteiten en filter op BE WAVE inclusief uitgeschakeld.
Open de gewenste entiteit → tandwiel → Ingeschakeld → opslaan. Laden kan ongeveer
30 seconden duren; de volgende live terugmelding geeft de actuele waarde.

De keuze wordt per entiteit en apparaat onthouden. Bestaande gebruikerskeuzes,
namen, ID’s, detecties en schakelaars blijven behouden. Extra informatie wordt
niet langer verwijderd tijdens opstarten. Een uitgeschakelde entiteit heeft geen
actieve HA-status of geschiedenis. Meetwaarden worden niet door BE WAVE zelf
naar de apparaatcache of eigen foutlog geschreven.

Vervang de volledige map custom_components/bewave en herstart Home Assistant.
De integratie en apparaten hoeven niet verwijderd te worden.

75 tests geslaagd op Home Assistant 2026.10.4, inclusief echte lokale MQTT met een
gesimuleerde hub. Tests dekken zelf temperatuur activeren, beschikbaar komen na
HA’s uitgestelde herlaadactie, gebruikerskeuzes na herstart, optionele tekst- en
getalwaarden, ongeldige waarden, detecties en bestaande schakelbediening.
De fysieke BE WAVE-hub is niet door deze tests bediend.
