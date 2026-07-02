"""Localized conversation phrases for Alice."""

from __future__ import annotations

from .const import SUPPORTED_LANGUAGES

MOOD_QUERIES: dict[str, set[str]] = {
    "de": {"wie ist deine laune"},
    "en": {"what is your mood"},
    "fr": {"quelle est ton humeur", "quelle est votre humeur"},
    "it": {"qual è il tuo umore"},
    "es": {"cuál es tu estado de ánimo", "cual es tu estado de animo"},
    "zh": {"你的心情怎么样", "你的心情如何"},
    "ja": {"今の気分は", "気分はどう"},
    "ko": {"기분이 어때", "지금 기분은"},
    "pt": {"qual é o teu humor", "qual e o teu humor"},
}

ENABLE_CONTAINMENT: dict[str, set[str]] = {
    "de": {
        "aktiviere sperrmodus",
        "aktiviere containment modus",
        "sperrmodus an",
    },
    "en": {
        "enable containment mode",
        "activate containment mode",
        "turn on containment mode",
    },
    "fr": {
        "active le mode confinement",
        "active le mode containment",
        "mode confinement activé",
    },
    "it": {
        "attiva modalità contenimento",
        "attiva modalità containment",
        "modalità contenimento attiva",
    },
    "es": {
        "activa modo contención",
        "activa modo containment",
        "modo contención activado",
    },
    "zh": {
        "启用封锁模式",
        "启动 containment 模式",
        "开启封锁模式",
    },
    "ja": {
        "封じ込めモードを有効にして",
        "containment モードを有効にして",
        "封じ込めモードをオンにして",
    },
    "ko": {
        "봉쇄 모드 활성화",
        "containment 모드 활성화",
        "봉쇄 모드 켜",
    },
    "pt": {
        "ativar modo contenção",
        "ativar modo containment",
        "modo contenção ativado",
    },
}

DISABLE_CONTAINMENT: dict[str, set[str]] = {
    "de": {
        "deaktiviere sperrmodus",
        "sperrmodus aus",
        "beende sperrmodus",
    },
    "en": {
        "disable containment mode",
        "turn off containment mode",
        "deactivate containment mode",
    },
    "fr": {
        "désactive le mode confinement",
        "mode confinement désactivé",
        "arrête le mode confinement",
    },
    "it": {
        "disattiva modalità contenimento",
        "modalità contenimento disattivata",
        "termina modalità contenimento",
    },
    "es": {
        "desactiva modo contención",
        "modo contención desactivado",
        "finaliza modo contención",
    },
    "zh": {
        "关闭封锁模式",
        "停用 containment 模式",
        "结束封锁模式",
    },
    "ja": {
        "封じ込めモードを無効にして",
        "containment モードをオフにして",
        "封じ込めモードを終了して",
    },
    "ko": {
        "봉쇄 모드 비활성화",
        "containment 모드 끄기",
        "봉쇄 모드 종료",
    },
    "pt": {
        "desativar modo contenção",
        "modo contenção desativado",
        "encerrar modo contenção",
    },
}

ACK_PREFIXES: dict[str, tuple[str, ...]] = {
    "de": ("bestätige alarm mit pin ",),
    "en": ("confirm alarm with pin ",),
    "fr": ("confirmer l'alarme avec le code pin ",),
    "it": ("conferma allarme con pin ",),
    "es": ("confirmar alarma con pin ",),
    "zh": ("用 pin ", "我的 pin 是 "),
    "ja": ("pin ",),
    "ko": ("pin ",),
    "pt": ("confirmar alarme com pin ",),
}

MESSAGES: dict[str, dict[str, str]] = {
    "mood": {
        "de": "Meine Laune ist {mood}.",
        "en": "My mood is {mood}.",
        "fr": "Mon humeur est {mood}.",
        "it": "Il mio umore è {mood}.",
        "es": "Mi estado de ánimo es {mood}.",
        "zh": "我的心情是 {mood}。",
        "ja": "私の気分は {mood} です。",
        "ko": "내 기분은 {mood} 입니다.",
        "pt": "O meu humor é {mood}.",
    },
    "containment_missing": {
        "de": "Containment Alarm ist nicht installiert.",
        "en": "Containment Alarm is not installed.",
        "fr": "Containment Alarm n'est pas installé.",
        "it": "Containment Alarm non è installato.",
        "es": "Containment Alarm no está instalado.",
        "zh": "未安装 Containment Alarm。",
        "ja": "Containment Alarm がインストールされていません。",
        "ko": "Containment Alarm 이 설치되어 있지 않습니다.",
        "pt": "Containment Alarm não está instalado.",
    },
    "unknown_command": {
        "de": "Ich habe den Befehl noch nicht gelernt, Operator.",
        "en": "I have not learned that command yet, Operator.",
        "fr": "Je n'ai pas encore appris cette commande, Operator.",
        "it": "Non ho ancora imparato questo comando, Operator.",
        "es": "Aún no he aprendido ese comando, Operator.",
        "zh": "我还没有学会这个命令，Operator。",
        "ja": "そのコマンドはまだ学習していません、Operator。",
        "ko": "아직 그 명령을 배우지 못했습니다, Operator.",
        "pt": "Ainda não aprendi esse comando, Operator.",
    },
}


def normalize_language(language: str | None) -> str:
    """Return a supported language code."""
    if not language:
        return "de"
    code = language.split("-", 1)[0].lower()
    return code if code in SUPPORTED_LANGUAGES else "en"


def message(key: str, language: str, **kwargs: str) -> str:
    """Return a localized message template."""
    lang = normalize_language(language)
    template = MESSAGES[key].get(lang, MESSAGES[key]["en"])
    return template.format(**kwargs)


def matches_phrase(text: str, phrases: dict[str, set[str]]) -> bool:
    """Check whether text matches any supported language phrase set."""
    return any(text in language_phrases for language_phrases in phrases.values())


def extract_pin(text: str, language: str) -> str | None:
    """Extract a PIN from an acknowledgement phrase."""
    lang = normalize_language(language)
    lowered = text.lower()

    for prefix in ACK_PREFIXES.get(lang, ACK_PREFIXES["en"]):
        if lowered.startswith(prefix):
            pin = text[len(prefix) :].strip()
            if lang == "ja" and " で" in pin:
                pin = pin.split(" で", 1)[0].strip()
            elif lang == "ko" and " 으로" in pin:
                pin = pin.split(" 으로", 1)[0].strip()
            elif lang == "zh" and pin.endswith(" 确认警报"):
                pin = pin[: -len(" 确认警报")].strip()
            return pin or None

    if lang == "zh" and lowered.startswith("我的 pin 是 "):
        return text[len("我的 pin 是 ") :].strip()

    for prefixes in ACK_PREFIXES.values():
        for prefix in prefixes:
            if lowered.startswith(prefix):
                return text[len(prefix) :].strip()

    return None
