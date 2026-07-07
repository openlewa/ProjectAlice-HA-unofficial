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
        "aktiviere sperrprotokoll",
        "aktiviere abriegelungsprotokoll",
        "hive abriegeln",
        "sperrmodus an",
    },
    "en": {
        "initiate containment protocol",
        "activate containment protocol",
        "seal the facility",
        "activate hive lockdown",
        "enable containment mode",
        "turn on containment mode",
    },
    "fr": {
        "active le protocole de confinement",
        "active le mode confinement",
        "scelle l'installation",
        "confinement de la ruche",
        "mode confinement activé",
    },
    "it": {
        "attiva protocollo di contenimento",
        "attiva modalità contenimento",
        "attiva blocco",
        "sigilla la struttura",
        "modalità contenimento attiva",
    },
    "es": {
        "activa protocolo de contención",
        "activa modo contención",
        "bloquea la colmena",
        "sella la instalación",
        "modo contención activado",
    },
    "zh": {
        "启动封锁协议",
        "启用封锁模式",
        "封锁设施",
        "封锁蜂巢",
        "开启封锁模式",
    },
    "ja": {
        "封鎖プロトコルを起動",
        "封鎖モードを有効にして",
        "施設を封鎖",
        "ハイブを封鎖",
        "封じ込めモードをオンにして",
    },
    "ko": {
        "봉쇄 프로토콜 활성화",
        "봉쇄 모드 활성화",
        "시설 봉쇄",
        "하이브 봉쇄",
        "봉쇄 모드 켜",
    },
    "pt": {
        "ativar protocolo de contenção",
        "ativar modo contenção",
        "bloquear a colmeia",
        "selar a instalação",
        "modo contenção ativado",
    },
}

DISABLE_CONTAINMENT: dict[str, set[str]] = {
    "de": {
        "deaktiviere sperrmodus",
        "beende sperrprotokoll",
        "beende abriegelungsprotokoll",
        "sperrmodus aus",
        "beende sperrmodus",
    },
    "en": {
        "disable containment protocol",
        "lift hive lockdown",
        "deactivate containment mode",
        "end containment protocol",
        "turn off containment mode",
    },
    "fr": {
        "désactive le protocole de confinement",
        "lève le confinement",
        "arrête le mode confinement",
        "mode confinement désactivé",
    },
    "it": {
        "disattiva protocollo di contenimento",
        "disattiva blocco",
        "termina modalità contenimento",
        "modalità contenimento disattivata",
    },
    "es": {
        "desactiva protocolo de contención",
        "levanta el bloqueo",
        "finaliza modo contención",
        "modo contención desactivado",
    },
    "zh": {
        "解除封锁协议",
        "关闭封锁模式",
        "结束设施封锁",
        "停用 containment 模式",
    },
    "ja": {
        "封鎖プロトコルを解除",
        "封鎖モードを無効にして",
        "施設封鎖を終了",
        "封じ込めモードを終了して",
    },
    "ko": {
        "봉쇄 프로토콜 해제",
        "봉쇄 모드 비활성화",
        "시설 봉쇄 종료",
        "containment 모드 끄기",
    },
    "pt": {
        "desativar protocolo de contenção",
        "levantar bloqueio",
        "encerrar modo contenção",
        "modo contenção desativado",
    },
}

ACK_PREFIXES: dict[str, tuple[str, ...]] = {
    "de": ("bestätige alarm mit pin ", "zugangscode "),
    "en": ("confirm alarm with pin ", "access code "),
    "fr": ("confirmer l'alarme avec le code pin ", "code d'accès "),
    "it": ("conferma allarme con pin ", "codice di accesso "),
    "es": ("confirmar alarma con pin ", "código de acceso "),
    "zh": ("用 pin ", "访问代码 "),
    "ja": ("pin ", "アクセスコード "),
    "ko": ("pin ", "접근 코드 "),
    "pt": ("confirmar alarme com pin ", "código de acesso "),
}

SET_NAME_PREFIXES: dict[str, tuple[str, ...]] = {
    "de": ("nenn mich ",),
    "en": ("call me ",),
    "fr": ("appelle-moi ",),
    "it": ("chiamami ",),
    "es": ("llámame ", "llamame "),
    "zh": ("叫我",),
    "ja": ("私を",),
    "ko": ("나를 ",),
    "pt": ("chama-me ",),
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
        "de": "Das Sperrprotokoll ist nicht installiert.",
        "en": "Containment protocol is not installed.",
        "fr": "Le protocole de confinement n'est pas installé.",
        "it": "Il protocollo di contenimento non è installato.",
        "es": "El protocolo de contención no está instalado.",
        "zh": "封锁协议未安装。",
        "ja": "封鎖プロトコルがインストールされていません。",
        "ko": "봉쇄 프로토콜이 설치되어 있지 않습니다.",
        "pt": "O protocolo de contenção não está instalado.",
    },
    "unknown_command": {
        "de": "Ich habe den Befehl noch nicht gelernt, {name}.",
        "en": "I have not learned that command yet, {name}.",
        "fr": "Je n'ai pas encore appris cette commande, {name}.",
        "it": "Non ho ancora imparato questo comando, {name}.",
        "es": "Aún no he aprendido ese comando, {name}.",
        "zh": "我还没有学会这个命令，{name}。",
        "ja": "そのコマンドはまだ学習していません、{name}。",
        "ko": "아직 그 명령을 배우지 못했습니다, {name}.",
        "pt": "Ainda não aprendi esse comando, {name}.",
    },
    "name_saved": {
        "de": "Verstanden. Ich nenne dich ab jetzt {name}.",
        "en": "Understood. I will call you {name} from now on.",
        "fr": "Compris. Je t'appellerai {name} à partir de maintenant.",
        "it": "Capito. Ti chiamerò {name} d'ora in poi.",
        "es": "Entendido. Te llamaré {name} a partir de ahora.",
        "zh": "明白。从现在起我会叫你 {name}。",
        "ja": "了解しました。これから {name} とお呼びします。",
        "ko": "알겠습니다. 이제부터 {name}(이)라고 부르겠습니다.",
        "pt": "Entendido. Vou chamar-te {name} a partir de agora.",
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


def extract_preferred_name(text: str, language: str) -> str | None:
    """Extract a preferred name from a set-name phrase."""
    lang = normalize_language(language)
    lowered = text.lower()

    for prefix in SET_NAME_PREFIXES.get(lang, SET_NAME_PREFIXES["en"]):
        if lowered.startswith(prefix):
            name = text[len(prefix) :].strip()
            return name or None

    if lang == "zh" and text.startswith("叫我"):
        name = text[len("叫我") :].strip()
        return name or None

    if lang == "ja" and text.startswith("私を"):
        name = text[len("私を") :].strip()
        if name.endswith("と呼んで"):
            name = name[: -len("と呼んで")].strip()
        return name or None

    return None
