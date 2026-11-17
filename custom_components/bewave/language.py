"""Display language for BE WAVE function names; never rename user devices."""

from .const import CONF_LANGUAGE

ENGLISH_NAMES = {
    "Luchtvochtigheid": "Humidity",
    "Temperatuur": "Temperature",
    "Batterij": "Battery",
    "Signaal": "Signal",
    "Voedingsspanning": "Supply voltage",
    "Firmwareversie": "Firmware version",
    "Firmware-update voortgang": "Firmware update progress",
    "Aantal fouten": "Error count",
    "Aantal opgeslagen fouten": "Stored error count",
    "Detectieteller": "Detection counter",
    "Ingangsstatus": "Input state",
    "Ingangsgevoeligheid": "Input sensitivity",
    "Verwarmingsoffset": "Heater offset",
    "Impulstijd rolluiksensor": "Blind sensor pulse time",
    "Aantal impulsen rolluiksensor": "Blind sensor pulse count",
    "Werkmodus": "Operating mode",
    "Inlooptijd actief": "Entry countdown active",
    "Uitlooptijd actief": "Exit countdown active",
    "Geblokkeerd": "Blocked",
    "Ingeschakeld": "Armed",
    "Alarm": "Alarm",
    "Waarschuwingsalarm": "Warning alarm",
    "Firmware actueel": "Firmware up to date",
    "Schakelaar": "Switch",
    "Beweging": "Motion",
    "Magneetcontact": "Contact",
    "Trilling": "Vibration",
    "Rook": "Smoke",
    "Gas": "Gas",
    "Waterdetectie": "Water detection",
    "Glasbreuk": "Glass break",
    "Detectie": "Detection",
    "Koolmonoxide": "Carbon monoxide",
    "Zoeken naar nieuwe apparaten": "Search for new devices",
}


def display_language(hass, options):
    """Resolve an explicit choice, or follow the Home Assistant system language."""
    selected = options.get(CONF_LANGUAGE, "auto")
    if selected in ("nl", "en"):
        return selected
    return "nl" if hass.config.language.startswith("nl") else "en"


def function_name(hass, options, dutch_name):
    if display_language(hass, options) == "nl":
        return dutch_name
    return ENGLISH_NAMES.get(dutch_name, dutch_name)
