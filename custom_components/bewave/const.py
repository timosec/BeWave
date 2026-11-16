"""Constants for the BeWave integration."""

DOMAIN = "bewave"
CONF_LANGUAGE = "language"
CONF_TRANSPORT = "transport"
CONF_TOPIC_PREFIX = "topic_prefix"
CONF_COMMAND_PREFIX = "command_prefix"
CONF_REMEMBER_DEVICES = "remember_devices"
CONF_KEEP_LOG = "keep_log"
CONF_RETENTION_DAYS = "retention_days"
CONF_MAX_LOG_MB = "max_log_mb"
DEFAULT_RETENTION_DAYS = 30
DEFAULT_MAX_LOG_MB = 5
TRANSPORT_MQTT = "mqtt"
DEFAULT_TOPIC_PREFIX = "bewave"
MQTT_PLATFORMS = ["switch", "binary_sensor", "button"]
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
