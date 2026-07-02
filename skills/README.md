# ☂ Alice Umbrella HACS Repositories

This directory is reserved for listing Alice-compatible HACS repositories.

It is not a legacy Project Alice skill directory and should not contain runtime code copied from old Alice skills.

Each listed addon should include:

- name
- HACS repository URL
- type: extension, pack, wakeword pack, persona pack, game, or utility
- supported languages
- status
- short description

## Registered entries

| Name | Type | Languages | Status | Description |
| --- | --- | --- | --- | --- |
| Alice Containment Alarm | extension | de, en | in-repo (`Containment Alarm Skill/`) | Configurable containment security routine with Green/Yellow/Red levels, voice PIN, and acoustic alarm limits. |

Repository path for local development: `Containment Alarm Skill/`

Planned separate repository: move the folder contents to a dedicated HACS repo when ready.

## Planned entries

- Alice base integration (`custom_components/alice`) — in main repository root
- Alice wakeword pack — not registered yet
- Alice persona packs — not registered yet
