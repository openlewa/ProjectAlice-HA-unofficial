# Persona Shell HA — Roadmap

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.
> Single source of truth for project direction and implementation tasks.  
> Formerly *Project Alice*. Repo target: **Persona-Shell-HA**.

## Vision

**Persona Shell** is a modular voice personality platform for Home Assistant.

*The Persona Shell is a modular voice personality platform. Load a persona from any sci-fi universe — each pack brings its own voice, mood, and style. The shell stays the same; the personality changes.*

| Axis | What it is | Examples |
|---|---|---|
| **Persona** | Voice, mood, sentences, talks | `redqueen` (Alice), `takoma` |
| **Extension** | Optional features, logic, extension sentences | `facility_protocol` (Containment) |

Personas and extensions are **independent**. Extensions activate automatically when installed via HACS.

## Resolved decisions

| Topic | Decision |
|---|---|
| Repo | **Persona-Shell-HA** (manual GitHub rename + description) |
| Alice | Same persona as **Red Queen** — `persona_id: redqueen`; “Hey Alice” = wakeword alias |
| Fresh install | **Persona picker** in config flow |
| Conversation | **One** `conversation` entity; persona switch per device |
| Per-device persona | **Satellite attribute** + **area config** |
| Wakewords | **Per persona pack** (e.g. Hey Alice, Hey Red Queen, Hey Takoma) |
| Extension naming | **Extension** only |
| Extension activation | **Auto-enable on HACS install** |
| Sentence paths | `sentences/<persona_id>/<lang>.yaml` |
| STT export | **Active persona only** + enabled extension sentences |
| Containment talks | Spoken with **active persona voice** (persona talk templates, not extension defaults) |
| Security / containment entities | **Extension** owns state; base exposes **mirror/shim** entities for stable automations |

## Architecture (short)

```text
Persona Shell
├── Persona Pack (1 pack = 1 persona)
│   sentences/<persona_id>/<lang>.yaml
│   talks/<persona_id>/<lang>.yaml
│   wakeword/ (optional)
├── Extension (HACS install → auto-enabled)
│   custom_components/<extension_id>/
└── One conversation entity + per-satellite/area persona override
```

**Export:** `base + sentences/<active_persona>/<lang> + Σ(extension sentences)`

## Catalog

See [☂ Persona Shell Umbrella](../../skills/README.md).

---

## Phase 0 — Branding & docs

- [x] Persona Shell branding direction
- [x] Consolidate roadmap into this file
- [x] Rename umbrella catalog
- [x] Update README umbrella + roadmap links
- [x] Update Containment extension README links

## Phase 1 — Scaffold (done)

- [x] Native Home Assistant port (not Alice bridge)
- [x] HACS scaffold `custom_components/alice` + `hacs.json`
- [x] Conversation agent skeleton
- [x] RedQueen mood/persona state model (incl. `amorous`)
- [x] User Memory (roles, titles, voice/style, relationship)
- [x] Extension registry (discovery + sentence path collection for **extensions**)
- [x] Containment extension extracted (`Containment Alarm Skill/`)
- [x] Containment state machine (initial)
- [x] `sensor.alice_status` (Idle, STT, Thinking, TTS)
- [x] Unit tests: RedQueen, user memory, conversation phrases, containment

## Phase 2 — Core personality

- [ ] Talk/Persona engine with template fallback
- [ ] Talk paths: `talks/<persona_id>/<lang>.yaml`
- [ ] Select responses by language, mood, situation, user, **active persona**
- [ ] Optional LLM adapter with deterministic fallback
- [ ] Ambient chatter scheduler (quiet hours, daily limits, per-user toggle)

## Phase 3 — Persona Shell runtime

- [ ] Config flow: **persona picker** on first install
- [ ] `persona_shell_extension.json` alias for `alice_extension.json`
- [ ] Persona pack loader + `persona.json` validation:
  - Discover installed persona packs (HACS / configured paths)
  - Validate manifest: `id`, `type: persona_pack`, languages, `persona_shell_min_version`
  - Load `sentences/<persona_id>/<lang>.yaml` and `talks/<persona_id>/<lang>.yaml` for installed packs
  - Track enabled vs installed packs; wire `reload_packs` service
- [ ] Sentence export: write `/config/custom_sentences/<lang>/persona_shell.yaml` — **active persona only** + enabled extension sentences
- [ ] Sentence conflict detection + repair issues (duplicate intents, incompatible pack versions)
- [ ] Service `set_active_persona` (default / satellite attribute / area)
- [ ] Per-satellite persona attribute on voice satellites
- [ ] Area-based persona config
- [ ] **Extensions auto-enable on HACS install**
- [ ] Containment talks routed through **active persona** talk engine

## Phase 4 — Security & containment (extension + base)

- [x] Extension entities: `sensor.*_security_level`, `binary_sensor.*_containment_mode`, open contacts (`alice_containment_alarm` domain)
- [ ] **Mirror/shim** on base integration when `facility_protocol` extension is installed (extension remains source of truth):
  - `sensor.persona_shell_security_level` ← mirrors extension security level (`green` / `yellow` / `red`)
  - `binary_sensor.persona_shell_containment_mode` ← mirrors extension containment active state
  - `unavailable` when extension not installed; subscribe to extension state changes (no duplicate logic)
  - Legacy shim during migration: `sensor.alice_security_level`, `binary_sensor.alice_containment_mode`
- [ ] Base integration reads mirrored state for persona talks / automations
- [ ] Voice PIN flow: announcement, 6s window, 3 attempts
- [ ] Acoustic alarm cycle: tone → 30s pause → repeat; **10 min max** acoustic output, then stop tones/sirens while **silent alerts stay active** (notifications, logbook, dashboard, optional TTS)
- [ ] External siren/switch outputs (optional, hard shutdown)
- [ ] Warning/alarm tone and volume selection
- [ ] NFC tag + smart lock deactivation listeners
- [ ] Rename extension catalog ID → `facility_protocol` (domain shim optional)

## Phase 5 — Automation builder

Voice-to-automation draft flow (not implemented). Partial groundwork exists in User Memory role checks (`can_create_global_automations`).

- [ ] Automation draft flow from voice
- [ ] **Parse common German/English automation phrases** (deterministic patterns first; optional LLM for complex phrasing)
  - e.g. triggers (door opens, at sunset), conditions (dark, someone home), actions (turn on light)
- [ ] Entity resolver + clarification on ambiguity
- [ ] Draft store for multi-turn follow-up
- [ ] Summary + confirmation before save
- [ ] Role-based validation (Kids, Operator, Administrator, Commander)
- [ ] Generated automation alias prefix: `Persona Shell -` (legacy: `Alice -`)

## Phase 6 — Wakewords & ecosystem

- [ ] Wakeword distribution docs + pack layout per persona
- [ ] `redqueen` pack: Hey Alice + Hey Red Queen models
- [ ] `takoma` pack: Hey Takoma model
- [ ] Community persona pack template repo
- [ ] Community extension template repo
- [ ] Diagnostics/repairs: missing wakeword, sentence export, extension conflicts

## Phase 7 — Domain migration (major release)

- [ ] New domain `persona_shell` + migration from `alice`
- [ ] Entity renames (`conversation.persona_shell`, …)
- [ ] Deprecation shim for one major release
- [ ] HACS metadata update

## Phase 8 — Tests & quality

- [ ] Talk engine tests
- [ ] LLM fallback tests
- [ ] Persona export tests (active persona only)
- [ ] Per-device persona resolution tests
- [ ] Containment + persona talk routing tests
- [ ] Security/containment mirror entity tests (available/unavailable, state sync from extension)
- [ ] Automation builder permission tests
- [ ] Automation phrase parser tests (DE/EN common patterns)
- [ ] Pack/extension conflict tests
- [ ] HACS/manifest validation

---

## Guardrails

- Build in `custom_components/alice` (until domain migration) and active metadata/docs only
- No copyrighted quotes, logos, or franchise “official edition” framing
- No clear-text PIN storage; acoustic alarm hard-limited to 10 minutes, then silent alerts only
- Extensions and external sirens off by default where safety-critical (except: **auto-enable extension on HACS install** per product decision — containment still requires explicit entity/output config)

## Legacy mapping

| Old | New |
|---|---|
| Project Alice | Persona Shell HA |
| Alice (character) | Persona `redqueen` (display: Red Queen / Alice) |
| Alice Extension | Extension |
| Alice Pack | Persona Pack (one persona each) |
| ☂ Alice Umbrella | ☂ Persona Shell Umbrella |
