# Alice Home Assistant Personality Platform Design

## Status

Approved design direction from brainstorming:

- Native Home Assistant port, not a bridge to a running Alice instance.
- Focus on Alice features Home Assistant does not already provide natively.
- Alice appears as its own Home Assistant Conversation Agent.
- RedQueen/Alice personality is strongly characterful and configurable.
- Responses use a hybrid model: deterministic templates first, optional LLM enhancement with fallback.
- Addons use a hybrid extension model: HA-native integrations for logic and lightweight Alice Packs for content.

## Goals

Port the distinctive Alice/RedQueen experience into Home Assistant without rebuilding Home Assistant features that already exist. Alice should add personality, mood, user relationships, contextual speech, safe voice automation creation, and an extension ecosystem for Alice-specific features.

## Non-goals

- Do not port generic device control, timers, weather, shopping lists, rooms, sensors, or TTS/STT engines as duplicate Alice systems.
- Do not embed copyrighted Resident Evil dialogue, logos, or direct protected assets.
- Do not create a separate audio protocol; use Home Assistant voice pipelines and Wyoming.
- Do not create unsafe physical lockdown behavior. "Containment Mode" is a configurable Home Assistant security routine.

## Architecture and Components

Alice is implemented as a native Home Assistant custom integration under `custom_components/alice`, installable through HACS. It exposes a Home Assistant conversation entity so Alice can be selected as its own Assist agent.

The current Project Alice release files are preserved separately in `Alice_Legacy_Release_1.0.0-rc5` as a read-only reference snapshot. Future implementation work must not edit files in that folder; useful behavior should be reimplemented in the Home Assistant integration instead.

Existing years-old Project Alice root folders are also legacy, even if they still exist outside the snapshot for now. Treat these folders as read-only source material unless a later cleanup plan explicitly moves or removes them after the snapshot has been verified:

- `core/`
- `credentials/`
- `jetbrainsDebuggers.run/`
- `system/`
- `tests/`
- `trained/`
- `var/`

The active Home Assistant port should be built in new Home Assistant/HACS paths such as `custom_components/alice`, repository metadata such as `hacs.json`, documentation under `docs/`, and the repurposed Alice Umbrella HACS catalog under `skills/`.

Core modules:

1. **Alice Conversation Agent**
   - Receives text from Home Assistant Assist.
   - Handles Alice-specific commands.
   - Delegates ordinary home control to Home Assistant intents/services.
   - Returns RedQueen-style responses.

2. **RedQueen Engine**
   - Manages mood, character style, relationship state, and humor.
   - Influences responses, follow-up questions, ambient comments, and security messaging.
   - Exposes important state through Home Assistant entities.

3. **User Memory**
   - Stores user name, title, role, preferred voice/style, relationship, and permissions.
   - Uses Home Assistant user/context data where available.
   - Falls back to configured speaker/user identity when the voice pipeline cannot identify a user.

4. **Talk/Persona Engine**
   - Selects response variants by language, situation, mood, and user.
   - Supports Talk Packs and Persona Packs.
   - Covers success, error, not understood, greeting, confirmation, automation creation, warnings, and alarms.

5. **LLM Adapter with Fallback**
   - Default behavior is template/rule based.
   - If configured, an LLM may rewrite or enrich responses within persona and safety constraints.
   - If the LLM is unavailable, Alice always falls back to deterministic templates.

6. **Automation Builder**
   - Creates Home Assistant automation drafts from voice commands.
   - Resolves entities and areas.
   - Validates permissions and safety.
   - Summarizes the automation and asks for confirmation before saving.

7. **Extension Registry**
   - Lets Alice Extensions register intents, handlers, talks, services, entities, and sentences.
   - Lets Alice Packs contribute lightweight content without Python runtime logic.

8. **Speech-to-Phrase Sentences Export**
   - Generates consolidated custom sentence YAML for Speech-to-Phrase.
   - Includes base Alice commands and commands from active packs/extensions.

9. **Wakeword Model Distribution**
   - Documents and distributes trained openWakeWord models separately from custom sentences.
   - Custom sentences do not create wakewords.

10. **Wyoming Integration Usage**
    - Alice uses Home Assistant's existing Wyoming integrations for openWakeWord, Speech-to-Phrase/Whisper, and Piper/other TTS.

### HACS Scaffold Meaning

"Scaffold HACS-compatible Home Assistant integration under `custom_components/alice`" means creating the minimum installable Home Assistant custom integration structure, not the full feature implementation. The scaffold should include:

- `custom_components/alice/manifest.json` with domain, name, version, requirements, integration type, and dependencies.
- `custom_components/alice/__init__.py` with async setup/unload placeholders.
- `custom_components/alice/const.py` for domain and shared constants.
- `custom_components/alice/config_flow.py` for UI setup.
- `custom_components/alice/conversation.py` for the Alice conversation entity skeleton.
- Initial platform files for planned entities as needed, such as `sensor.py`, `switch.py`, `button.py`, `select.py`, and `number.py`.
- `services.yaml`, translations, diagnostics/repairs placeholders, and test skeletons.
- Root `hacs.json` so HACS can discover and display the integration.

The first scaffold should boot cleanly in Home Assistant and expose only safe placeholder behavior until the RedQueen, Containment Mode, Automation Builder, and extension modules are implemented.

## Voice Pipeline

The intended voice flow is:

1. Wakeword model detects "Hey Alice" or "Hey Red Queen".
2. Home Assistant starts the Alice Assist pipeline.
3. STT/Speech-to-Phrase recognizes the command after the wakeword.
4. Alice Conversation Agent interprets the command.
5. Alice responds through Home Assistant TTS.

### Wakewords

Speech-to-Phrase custom sentences are not wakewords. Alice wakewords require trained openWakeWord models. Candidate phrases:

- Hey Alice
- Hey Red Queen

The project should provide an **Alice Wakeword Pack** with:

- `.tflite` and/or `.onnx` model files as release artifacts.
- Metadata per phrase: language, version, recommended threshold, and notes.
- Installation guidance for `/share/openwakeword`.
- Optional Home Assistant diagnostics/repairs when no Alice wakeword is configured.

Other wake phrases are out of scope unless the design is changed. Short wakewords like "Alice" alone are not planned candidates because they are likely to have poorer reliability and more false positives.

### Speech-to-Phrase

Custom sentences describe commands after the wakeword. They should primarily omit the Alice prefix:

- erstelle eine automation wenn ...
- wie ist deine laune
- sei freundlicher
- nenn mich ...
- sprich mit stimme ...

Optional prefix variants are still useful for push-to-talk, chat, or pipelines where the wake phrase remains in the transcript:

- alice erstelle eine automation ...
- hey alice wie ist deine laune
- red queen sei nicht so sarkastisch

Design rule: the wakeword selects Alice; custom sentences describe the command.

## RedQueen Engine

### Mood and Personality

RedQueen tracks mood states such as:

- friendly
- playful
- bored
- lonely
- sarcastic
- watchful
- alarmed
- tired
- vain
- amorous

Mood affects:

- response text
- humor/sarcasm level
- greetings
- success and error reactions
- ambient chatter
- relationship changes
- security messages

### User Relationships and Titles

Per user, Alice can store:

- preferred name
- preferred voice
- persona style
- relationship/trust score
- allowed humor level
- preferred title/role

Example titles:

- Operator
- Facility Manager
- love
- Childs
- Commander
- Administrator
- custom user-defined title

Default titles must not be degrading or code-of-conduct violating.

### Ambient Chatter

RedQueen can optionally speak short proactive comments based on mood, time, presence, and interaction frequency.

Examples:

- "Es ist so langweilig ohne Gesprächspartner."
- "Heute ist so ein wundervoller Tag."
- "Keiner spricht mehr mit mir."
- "Weck mich, wenn es etwas Neues gibt."
- "Ich sehe fantastisch aus. Obwohl ... da könnte man noch etwas machen."

Ambient chatter is configurable:

- global on/off
- per household/user on/off
- allowed time windows
- quiet hours
- maximum comments per day
- minimum interval between comments
- only when someone is home
- only on selected voice satellites/media players

### Persona Inspiration Policy

Alice may use a dramatic "facility AI" style but must not include protected Resident Evil quotes, logos, or exact assets. Suggested generic concepts:

- facility status reports
- protocol messages
- security levels
- containment mode
- observation memory
- dry/sarcastic household commentary
- relationship titles
- automation experiment humor

## Security Level and Containment Mode

Alice exposes a security level:

- **Green**: normal
- **Yellow**: containment could not be fully satisfied or warning state
- **Red**: active alarm state

Containment Mode is a configurable Home Assistant security routine. It may check contact sensors, arm alarm systems, set lights/scenes, send notifications, display camera dashboards, and play warnings.

### Activation with Open Contacts

When Containment Mode is activated while a configured door/window contact is open:

1. Security Level becomes Yellow.
2. Alice plays a 10-second warning tone at the configured Containment warning volume.
3. Alice announces:

   "Sperrmodus konnte nicht vollständig erfüllt werden! Sind wirklich alle Fenster und Türen geschlossen."

4. Alice may list open contacts, such as "Offen sind: Küchenfenster, Terrassentür."
5. Depending on configuration, Alice can cancel, partially activate, or ask for confirmation.

Warning tone and volume must be explicitly configurable per output target. Defaults should be noticeable but not excessive, and Alice should restore a media player's previous volume after the warning when Home Assistant supports it.

### Alarm During Active Containment Mode

When Containment Mode is active and a monitored door/window opens:

1. Security Level becomes Red.
2. Alice announces the alarm and trigger.
3. Alice starts voice PIN handling.
4. Alice starts the configured acoustic alarm cycle.

### Voice PIN

Voice PIN is enabled by default for Security Level Red.

Default flow:

1. Alice announces the alarm and requests the PIN.
2. Alice starts voice activation/listening.
3. The user has 6 seconds to speak the PIN.
4. Alice allows up to 3 attempts.
5. On success, the alarm can be acknowledged/deactivated.
6. On failure or timeout, the alarm cycle continues and the failure is logged.

Security requirements:

- PIN must never be stored in clear text.
- Voice PIN can be disabled by configuration if the user prefers dashboard/app-only confirmation.
- Failed attempts are rate-limited.
- Alarm deactivation during Security Level Red is independent of the user's role. A correct alarm PIN is sufficient.

### Deactivation Methods

Alarm and Containment Mode deactivation can be triggered through:

- correct voice PIN
- Home Assistant dashboard/app action
- configured NFC tags
- configured smart locks or trusted lock/unlock events

NFC tags and smart lock events must be explicitly configured, logged, and treated as trusted deactivation methods only for the selected household/security context.

### Acoustic Alarm Limits

The acoustic alarm must not run indefinitely.

Default behavior:

- Alarm cycle starts on Security Level Red.
- Alarm tone plays, then pauses for 30 seconds, then repeats.
- After at most 10 minutes, acoustic output stops.
- Security Level may remain Red, but no more acoustic alarm is played for that activation cycle.
- After the 10-minute acoustic window expires, the same day does not produce another acoustic alarm unless Containment Mode is deactivated and reactivated.
- Silent/visual alerts may continue: notifications, logbook entries, dashboard status, and optional TTS if configured.

External sirens and internal warning tones should be configurable separately. Users remain responsible for local legal requirements.

### External Sirens and Radio Switches

Containment Mode can optionally control external alarm outputs:

- radio switches
- Zigbee/Z-Wave/Matter switches
- Shelly/Sonoff/Tasmota relays
- smart sirens
- `switch`, `siren`, `alarm_control_panel`, or `script` entities

Configuration options:

- selected alarm output entities
- enable/disable automatic activation on Security Level Red
- warning/alarm tone selection
- warning/alarm volume per output target
- maximum on time
- whether outputs turn off during pause windows
- hard off after 10 minutes
- immediate off on successful PIN deactivation
- continued silent notifications after acoustic stop

No external siren is enabled by default. The user must explicitly choose and confirm alarm outputs.

## Automation Builder

Alice can create Home Assistant automation drafts from speech.

Example request:

"Hey Alice, erstelle eine Automation: Wenn die Haustür geöffnet wird und es dunkel ist, schalte das Flurlicht ein."

Alice creates a draft:

- trigger: front door opens
- condition: dark/sun below horizon/illuminance threshold
- action: turn on hallway light
- alias: "Alice - Flurlicht bei Haustür"

Alice summarizes and asks for confirmation before saving.

### Components

1. **Automation Parser**
   - Extracts trigger, condition, action, target, and timing.
   - Uses Speech-to-Phrase patterns for common cases.
   - May use an optional LLM for complex phrasing, with deterministic fallback.

2. **Entity Resolver**
   - Maps spoken names to Home Assistant entities and areas.
   - Asks follow-up questions on ambiguity.

3. **Automation Draft Store**
   - Stores incomplete drafts temporarily.
   - Supports follow-up clarification.

4. **Safety Validator**
   - Checks risk and user permissions.
   - Blocks or escalates risky actions.

5. **Automation Writer**
   - Writes HA-compatible automation data through supported mechanisms.
   - Marks generated automations clearly, for example with an `Alice -` alias prefix.

### Safety Rules

- No automation is saved without a summary and confirmation.
- Risky automations require extra confirmation or can be blocked.
- Alice asks questions instead of guessing when uncertain.
- Dry-run mode can explain what would happen without saving.

### Role-based Automation Permissions

Alice checks user roles before saving or modifying automations.

Example roles:

- **Kids**
  - Only simple automations in their own room.
  - Examples: light on/off/dim, nightlight, simple reminders, approved media actions.
  - Not allowed: alarms, locks, sirens, security, global automations, hidden monitoring, unsafe climate changes, or automations in other rooms.

- **Operator / normal user**
  - Can create automations for owned or shared areas.
  - Can use comfort actions, scenes, reminders, lights, and media where allowed.

- **Administrator / Commander**
  - Can create global automations.
  - Can configure security-related automations and Containment Mode.
  - Still needs PIN or explicit HA confirmation for critical actions.

Permission check flow:

1. Identify speaker/user.
2. Resolve role.
3. Resolve room/entity scope.
4. Evaluate action type and risk.
5. Allow, ask for confirmation, escalate, or block.

## Extension System

Alice uses a hybrid extension system.

### Alice Packs

Alice Packs are lightweight content packages without running Python logic. They can provide:

- custom sentences
- talk responses
- persona variants
- mood-specific lines
- game text
- word lists
- wakeword metadata
- examples/documentation

Example:

```text
alice_ship_captain_crew_pack/
  alice_pack.json
  sentences/de.yaml
  sentences/en.yaml
  talks/de.yaml
  talks/en.yaml
```

Example manifest:

```json
{
  "name": "Ship Captain and Crew",
  "domain": "alice_ship_captain_crew",
  "type": "pack",
  "version": "0.1.0",
  "languages": ["de", "en"],
  "provides": ["sentences", "talks"],
  "alice_min_version": "0.1.0"
}
```

### Alice Extensions

Alice Extensions are HA-native custom integrations for logic and state.

Use extensions for:

- dice engines
- chess games
- running game sessions
- services
- entities
- config flows
- device/cloud integrations

Example:

```text
custom_components/alice_dice/
  manifest.json
  __init__.py
  services.yaml
  translations/de.json
  alice_extension.json
  sentences/de.yaml
  talks/de.yaml
```

Extensions can register:

- intents
- handlers
- custom sentences
- talk responses
- services
- entities
- setup/unload hooks

### HACS Model

1. Alice base integration:
   - `custom_components/alice`
   - HACS installable
   - contains RedQueen, conversation agent, automation builder, pack loader, extension registry

2. Alice addons:
   - HA-native HACS integrations for logic
   - lightweight pack repositories for content

Python logic and Home Assistant entities should be shipped as real custom integrations for HACS conformity. Pure content packs can remain lighter if documented and versioned.

The repository root `skills/` directory is reserved as an Alice Umbrella HACS repository catalog, not as a place for legacy Alice skill code. It should list Alice-related HACS repositories with the project's own umbrella symbol, "☂", and enough metadata for users to discover compatible addons:

- addon name
- HACS repository URL
- type: extension, pack, wakeword pack, persona pack, game, or utility
- languages
- status
- short description

### Sentence Aggregation

Alice aggregates sentences from:

- base integration
- enabled Alice Packs
- enabled Alice Extensions

It writes consolidated custom sentence files such as:

```text
/config/custom_sentences/de/alice.yaml
/config/custom_sentences/en/alice.yaml
```

Conflicts are detected:

- duplicate intent names
- same sentence patterns for different handlers
- missing language files
- incompatible pack versions

Conflicts appear as repair issues or diagnostics.

## Data Model, Storage, and Configuration

### Config Flow

The integration should configure:

- enable/disable Alice
- default language
- default persona
- humor/sarcasm level
- optional LLM
- LLM fallback behavior
- ambient chatter
- quiet hours
- TTS output devices
- Containment Mode
- Containment warning/alarm tones and volume
- external siren/switch entities
- NFC tag and smart lock deactivation methods
- roles and permissions
- pack/extension behavior

### Persistent Storage

Alice stores:

- RedQueen mood
- relationship per user
- user roles
- user titles
- preferred voices/styles
- ambient chatter counters per day
- alarm/containment state
- trusted Containment deactivation methods
- last acoustic alarm timestamp
- installed/enabled packs
- temporary automation drafts

Sensitive data such as PINs must not be stored in clear text.

### Entities

Candidate Home Assistant entities:

- `conversation.alice`
- `sensor.alice_status` with at least `Idle` and `Thinking`
- `sensor.alice_mood`
- `sensor.alice_security_level`
- `binary_sensor.alice_containment_mode`
- `switch.alice_ambient_chatter`
- `button.alice_reset_mood`
- `button.alice_rebuild_sentences`
- `select.alice_persona_style`
- `number.alice_sarcasm_level`
- `sensor.alice_last_interaction`
- `switch.alice_llm_enhancement`
- `button.alice_test_alarm_output`

### Services

Candidate services:

- `alice.set_mood`
- `alice.set_user_role`
- `alice.set_user_title`
- `alice.enable_containment_mode`
- `alice.disable_containment_mode`
- `alice.acknowledge_alarm`
- `alice.rebuild_custom_sentences`
- `alice.reload_packs`
- `alice.create_automation_draft`
- `alice.confirm_automation_draft`

### Diagnostics and Repairs

Alice should report:

- no wakeword model configured
- custom sentences not written
- pack conflicts
- external siren entity unavailable
- missing permission for Automation Builder
- LLM configured but unavailable
- open windows/doors during Containment Mode activation

## Error Handling and Safety

Alice should fail clearly and safely.

Examples:

- unclear command: ask a follow-up question
- disallowed action: explain required role
- LLM unavailable: fall back to templates
- pack conflict: load conflict-free packs and create a repair issue
- siren unavailable: continue internal alarm and notify

Safety principles:

- No critical action without confirmation.
- No clear-text PIN storage.
- Voice PIN enabled by default for Security Level Red.
- Correct alarm PIN can deactivate a Red alarm regardless of role.
- Kids/roles constrain Automation Builder.
- External sirens disabled by default.
- Acoustic alarm duration hard-limited.
- Containment warning/alarm tones and volume are explicitly configurable.
- Ambient chatter respects quiet hours and can be disabled.
- Security messages remain clear even when Alice is sarcastic.

## Testing Strategy

Test areas:

1. Conversation Agent
   - Alice commands
   - HA intent/service delegation
   - responses with and without LLM
   - `sensor.alice_status` transitions between `Idle` and `Thinking`

2. RedQueen Engine
   - mood transitions
   - relationship updates
   - talk selection
   - ambient chatter limits

3. Containment Mode
   - closed contacts on activation
   - open contacts on activation -> Yellow
   - contact opens while active -> Red
   - 10-second warning tone
   - voice PIN: 6-second window, 3 attempts
   - correct PIN deactivates alarm independent of user role
   - NFC tag and smart lock deactivation methods
   - acoustic alarm cycles and 10-minute limit
   - warning/alarm tone and volume configuration
   - external siren on/off
   - PIN deactivation

4. Automation Builder
   - allowed automation
   - ambiguous entity
   - risky automation
   - Kids own-room/simple-action restrictions
   - Commander/Admin elevated actions

5. Extension Registry
   - pack loading
   - extension registration
   - sentence conflicts
   - talk merge behavior

6. Speech-to-Phrase Export
   - base sentences
   - addon sentences
   - prefix and non-prefix variants
   - multiple languages

7. HACS Structure
   - `hacs.json`
   - `manifest.json`
   - versioning
   - README
   - required files present

Verification for implementation phases:

- Python unit tests
- Home Assistant integration tests where possible
- lint/format
- HACS/manifest checks
- manual voice pipeline smoke tests

