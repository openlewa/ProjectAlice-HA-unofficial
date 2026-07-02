DOMAIN = "alice"

CONF_DEFAULT_LANGUAGE = "default_language"
CONF_DEFAULT_PERSONA = "default_persona"
CONF_SARCASM_LEVEL = "sarcasm_level"
CONF_LLM_ENABLED = "llm_enabled"
CONF_AMBIENT_CHATTER = "ambient_chatter"

DEFAULT_LANGUAGE = "de"
DEFAULT_PERSONA = "redqueen"
DEFAULT_SARCASM_LEVEL = 50

SUPPORTED_LANGUAGES = ["de", "en", "fr", "it", "es", "zh", "ja", "ko", "pt"]

STATUS_IDLE = "Idle"
STATUS_THINKING = "Thinking"

MOOD_FRIENDLY = "friendly"
MOOD_PLAYFUL = "playful"
MOOD_BORED = "bored"
MOOD_LONELY = "lonely"
MOOD_SARCASTIC = "sarcastic"
MOOD_WATCHFUL = "watchful"
MOOD_ALARMED = "alarmed"
MOOD_TIRED = "tired"
MOOD_VAIN = "vain"
MOOD_AMOROUS = "amorous"

MOODS = [
    MOOD_FRIENDLY,
    MOOD_PLAYFUL,
    MOOD_BORED,
    MOOD_LONELY,
    MOOD_SARCASTIC,
    MOOD_WATCHFUL,
    MOOD_ALARMED,
    MOOD_TIRED,
    MOOD_VAIN,
    MOOD_AMOROUS,
]

SERVICE_SET_MOOD = "set_mood"
SERVICE_REBUILD_SENTENCES = "rebuild_custom_sentences"
SERVICE_RELOAD_PACKS = "reload_packs"

STORAGE_KEY = f"{DOMAIN}.storage"
STORAGE_VERSION = 1
