# Alice Containment Alarm

Alice Containment Alarm is a Home Assistant custom integration and Alice Extension that implements the configurable **Containment Mode** security routine from the [Alice Home Assistant Personality Platform design](../../docs/superpowers/specs/2026-06-10-alice-ha-personality-platform-design.md).

It is packaged as a standalone app so it can later be moved into its own repository and installed through HACS independently of the Alice base integration.

## Features

- **Security levels**: Green, Yellow, and Red
- **Containment activation** with open-contact detection and warning flow
- **Alarm on contact breach** while containment mode is active
- **Voice PIN acknowledgement** with hashed storage, 6-second listening window, and 3 attempts
- **Trusted deactivation** through configured NFC tags and smart lock unlock events
- **Acoustic alarm limits** with pause cycles and a 10-minute hard stop
- **Alice Extension manifest** (`alice_extension.json`) for sentence, talk, service, and entity registration
- **Resident Evil homage terminology** for containment/lockdown per language (facility protocol style, no direct copyrighted quotes)
- **Nine languages**: German, English, French, Italian, Spanish, Chinese, Japanese, Korean, and Portuguese

## Safety Notes

Containment Mode is a configurable Home Assistant security routine. It does not perform unsafe physical lockdown behavior. External sirens are disabled by default and must be explicitly configured.

## Requirements

- Home Assistant 2024.6 or newer
- Optional: Alice base integration (`custom_components/alice`) for unified Assist agent routing

## Installation

### HACS

1. Add this repository as a custom HACS integration.
2. Install **Alice Containment Alarm**.
3. Restart Home Assistant.
4. Add the integration under **Settings → Devices & Services**.

### Manual

Copy `custom_components/alice_containment_alarm` into your Home Assistant `custom_components` directory and restart Home Assistant.

## Configuration

During setup you can configure:

- monitored door/window contact sensors
- warning and alarm media players
- optional external alarm outputs (`switch`, `siren`, `script`, `alarm_control_panel`)
- warning and alarm volume
- voice PIN enable/disable
- trusted NFC tags and smart locks

Set an alarm PIN through the service:

```yaml
service: alice_containment_alarm.set_pin
data:
  pin: "1234"
```

## Services

| Service | Description |
| --- | --- |
| `alice_containment_alarm.enable_containment_mode` | Activates containment mode |
| `alice_containment_alarm.disable_containment_mode` | Deactivates containment mode |
| `alice_containment_alarm.acknowledge_alarm` | Acknowledges an active alarm with PIN |
| `alice_containment_alarm.set_pin` | Stores a hashed alarm PIN |

## Entities

| Entity | Description |
| --- | --- |
| `binary_sensor.*_containment_mode` | Whether containment mode is active |
| `sensor.*_security_level` | Current security level (`green`, `yellow`, `red`) |
| `sensor.*_open_contacts` | Count and list of open monitored contacts |
| `button.*_enable_containment_mode` | Enables containment mode |
| `button.*_disable_containment_mode` | Disables containment mode |
| `button.*_test_alarm_output` | Short alarm output test |

## Alice Integration

When the Alice base integration is installed, Alice discovers this extension through `alice_extension.json` and can:

- register containment intents and handlers
- merge `sentences/de.yaml` and `sentences/en.yaml` into custom Speech-to-Phrase exports
- use `talks/de.yaml` and `talks/en.yaml` for RedQueen-style responses

## Resident Evil Homage Terminology

Containment wording follows the facility-lockdown vocabulary used in Resident Evil localizations, without copying protected dialogue:

| Language | Primary term | RE-inspired context |
| --- | --- | --- |
| de | Sperrmodus / Sperrprotokoll | Hive abriegeln, versiegelte Anlage |
| en | Containment protocol | Seal the facility, Hive lockdown |
| fr | Protocole de confinement | Installation scellée |
| it | Protocollo di contenimento / Blocco | Struttura sigillata |
| es | Protocolo de contención | Bloqueo de la colmena |
| zh | 封锁协议 | 封锁设施 / 封锁蜂巢 |
| ja | 封鎖プロトコル | 施設封鎖 / ハイブ封鎖 |
| ko | 봉쇄 프로토콜 | 시설 봉쇄 / 하이브 봉쇄 |
| pt | Protocolo de contenção | Bloqueio da colmeia |

Voice examples:

- German: `aktiviere sperrmodus`, `aktiviere abriegelungsprotokoll`, `zugangscode 1234`
- English: `initiate containment protocol`, `seal the facility`, `access code 1234`
- French: `active le protocole de confinement`, `scelle l'installation`
- Italian: `attiva protocollo di contenimento`, `attiva blocco`
- Spanish: `activa protocolo de contención`, `bloquea la colmena`
- Chinese: `启动封锁协议`, `封锁设施`
- Japanese: `封鎖プロトコルを起動`, `施設を封鎖`
- Korean: `봉쇄 프로토콜 활성화`, `하이브 봉쇄`
- Portuguese: `ativar protocolo de contenção`, `bloquear a colmeia`

## Development

Run unit tests from the repository root:

```bash
python -m pytest "Containment Alarm Skill/tests" -q
```

Validate the Alice extension manifest:

```bash
python -c "import json; json.load(open('Containment Alarm Skill/custom_components/alice_containment_alarm/alice_extension.json'))"
```

## Separate Repository

This folder is intentionally self-contained:

- `custom_components/alice_containment_alarm/`
- `hacs.json`
- `README.md`
- `LICENSE`

To publish as its own repository, move the folder contents to a new git repository root and keep `custom_components/` at the top level.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
