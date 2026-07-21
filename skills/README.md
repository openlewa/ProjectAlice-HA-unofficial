# ☂ Persona Shell Umbrella

Catalog of HACS repositories compatible with **Persona Shell HA**.

This directory is **not** a legacy Project Alice skill folder and must not contain runtime code copied from old Alice skills.

Each entry should list:

- name
- HACS repository URL
- type: `extension`, `persona_pack`, `wakeword_pack`, `game`, or `utility`
- supported languages
- status
- short description

Extensions **auto-enable** when installed via HACS. Persona packs register a single persona each.

## Registered entries

| Name | Type | Languages | Status | Description |
| --- | --- | --- | --- | --- |
| Facility Protocol (Containment Alarm) | extension | de, en, fr, it, es, zh, ja, ko, pt | in-repo (`Containment Alarm Skill/`) | Containment security routine: Green/Yellow/Red levels, voice PIN, acoustic alarm limits. Persona-agnostic; talks use active persona voice. |

Local path: `Containment Alarm Skill/`  
Planned: dedicated HACS repo when ready.

## Planned entries

| Name | Type | Status |
| --- | --- | --- |
| Persona Shell base integration | platform | in-repo (`custom_components/alice`) |
| Persona `redqueen` (Alice / Red Queen) | persona_pack | in base / legacy |
| Persona `takoma` | persona_pack | planned |
| Wakeword pack `redqueen` | wakeword_pack | planned (Hey Alice, Hey Red Queen) |
| Wakeword pack `takoma` | wakeword_pack | planned (Hey Takoma) |
| Extension `public_security` | extension | planned |

## Persona vs extension

| Kind | Owns | Independent of |
|---|---|---|
| **Persona pack** | `sentences/<persona_id>/`, `talks/<persona_id>/`, moods, wakeword | Which extensions are installed |
| **Extension** | services, entities, extension `sentences/` | Which persona is active |

Sentence export includes **only the active persona** plus enabled extension sentences.
