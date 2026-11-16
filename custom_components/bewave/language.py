"""Display language for BE WAVE function names; never rename user devices."""

from .const import CONF_LANGUAGE

ENGLISH_NAMES = {
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
