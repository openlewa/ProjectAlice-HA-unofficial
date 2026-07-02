"""Constants for the Alice Containment Alarm extension."""

DOMAIN = "alice_containment_alarm"

CONF_CONTACT_SENSORS = "contact_sensors"
CONF_WARNING_MEDIA_PLAYERS = "warning_media_players"
CONF_ALARM_MEDIA_PLAYERS = "alarm_media_players"
CONF_EXTERNAL_SIRENS = "external_sirens"
CONF_WARNING_VOLUME = "warning_volume"
CONF_ALARM_VOLUME = "alarm_volume"
CONF_WARNING_DURATION = "warning_duration"
CONF_ALARM_CYCLE_PAUSE = "alarm_cycle_pause"
CONF_ALARM_MAX_DURATION = "alarm_max_duration"
CONF_VOICE_PIN_ENABLED = "voice_pin_enabled"
CONF_PIN_HASH = "pin_hash"
CONF_NFC_TAGS = "nfc_tags"
CONF_SMART_LOCKS = "smart_locks"

DEFAULT_WARNING_VOLUME = 0.6
DEFAULT_ALARM_VOLUME = 0.8
DEFAULT_WARNING_DURATION = 10
DEFAULT_ALARM_CYCLE_PAUSE = 30
DEFAULT_ALARM_MAX_DURATION = 600
DEFAULT_PIN_ATTEMPTS = 3
DEFAULT_PIN_TIMEOUT = 6

SECURITY_GREEN = "green"
SECURITY_YELLOW = "yellow"
SECURITY_RED = "red"

ATTR_SECURITY_LEVEL = "security_level"
ATTR_OPEN_CONTACTS = "open_contacts"
ATTR_ALARM_ACTIVE = "alarm_active"
ATTR_PIN_ATTEMPTS_REMAINING = "pin_attempts_remaining"

SERVICE_ENABLE = "enable_containment_mode"
SERVICE_DISABLE = "disable_containment_mode"
SERVICE_ACKNOWLEDGE_ALARM = "acknowledge_alarm"
SERVICE_SET_PIN = "set_pin"

STORAGE_KEY = f"{DOMAIN}.storage"
STORAGE_VERSION = 1
