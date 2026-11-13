"""Constants for the BeWave integration."""

DOMAIN = "bewave"
CONF_TRANSPORT = "transport"
CONF_TOPIC_PREFIX = "topic_prefix"
CONF_EXPIRE_AFTER = "expire_after"
TRANSPORT_MQTT = "mqtt"
DEFAULT_TOPIC_PREFIX = "bewave"
DEFAULT_EXPIRE_AFTER = 180
MQTT_PLATFORMS = ["sensor", "binary_sensor"]
DEFAULT_TARGET_PORT = 5000
DEFAULT_LISTEN_PORT = 5000
DEFAULT_MOMENTARY_RESET_MS = 800
PLATFORMS = ["button", "binary_sensor"]

CONF_DEVICES = "devices"
CONF_COMMAND_ON = "command_on"
CONF_ON_MESSAGE = "on_message"
CONF_OFF_MESSAGE = "off_message"
CONF_LISTEN_PORT = "listen_port"
CONF_MOMENTARY_RESET_MS = "momentary_reset_ms"
