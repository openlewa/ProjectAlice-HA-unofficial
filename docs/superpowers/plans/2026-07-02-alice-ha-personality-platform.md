# Alice Home Assistant Personality Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved Alice Home Assistant personality platform as a HACS-installable base integration with modular Alice Extensions, starting with the standalone Containment Alarm app.

**Architecture:** Alice lives in `custom_components/alice` as the conversation agent, RedQueen engine, extension registry, and sentence aggregation layer. Feature apps such as Containment Alarm ship as separate HACS integrations in their own folders and register through `alice_extension.json`.

**Tech Stack:** Home Assistant custom integrations, HACS, YAML sentence/talk packs, Python 3.11+, pytest.

---

## Phase 0: Repository Foundations

### Task 0.1: Containment Alarm standalone app

**Files:**
- Create: `Containment Alarm Skill/custom_components/alice_containment_alarm/*`
- Create: `Containment Alarm Skill/README.md`
- Create: `Containment Alarm Skill/LICENSE`
- Create: `Containment Alarm Skill/hacs.json`
- Test: `Containment Alarm Skill/tests/test_containment.py`

- [x] Package containment logic as `alice_containment_alarm`
- [x] Add `alice_extension.json`, sentences, talks, services, entities
- [x] Add README and LICENSE for separate repo extraction
- [x] Add unit tests for state machine and PIN hashing

### Task 0.2: Alice base scaffold

**Files:**
- Create: `custom_components/alice/*`
- Create: `hacs.json`
- Test: `tests/test_redqueen.py`

- [x] Add HACS-compatible Alice integration scaffold
- [x] Add conversation agent skeleton
- [x] Add RedQueen mood model with `amorous`
- [x] Add extension discovery and sentence collection
- [x] Route containment voice commands to the extension service

---

## Phase 1: Core Personality

### Task 1.1: User Memory

**Files:**
- Create: `custom_components/alice/user_memory.py`
- Modify: `custom_components/alice/__init__.py`
- Test: `tests/test_user_memory.py`

- [x] Store preferred name, title, role, voice/style, relationship, and permissions per user
- [x] Fall back to configured speaker identity when Assist cannot resolve a user

### Task 1.2: Talk/Persona Engine

**Files:**
- Create: `custom_components/alice/talk_engine.py`
- Create: `custom_components/alice/talks/de.yaml`
- Create: `custom_components/alice/talks/en.yaml`
- Test: `tests/test_talk_engine.py`

- [ ] Select deterministic response variants by language, mood, situation, and user
- [ ] Support base talks for greeting, success, error, not understood, confirmation, and warnings

### Task 1.3: Optional LLM Adapter

**Files:**
- Create: `custom_components/alice/llm_adapter.py`
- Modify: `custom_components/alice/config_flow.py`
- Test: `tests/test_llm_adapter.py`

- [ ] Add optional response enrichment behind persona and safety constraints
- [ ] Always fall back to templates when the configured LLM is unavailable

---

## Phase 2: Security and Containment

### Task 2.1: Containment media and siren outputs

**Files:**
- Modify: `Containment Alarm Skill/custom_components/alice_containment_alarm/__init__.py`
- Modify: `Containment Alarm Skill/custom_components/alice_containment_alarm/containment.py`
- Test: `Containment Alarm Skill/tests/test_media_outputs.py`

- [ ] Play 10-second warning tone at configured volume and restore previous media player volume
- [ ] Control optional external sirens/switches on Security Level Red
- [ ] Hard-stop acoustic outputs after 10 minutes while keeping silent alerts active

### Task 2.2: Voice PIN listening integration

**Files:**
- Modify: `custom_components/alice/conversation.py`
- Modify: `Containment Alarm Skill/custom_components/alice_containment_alarm/containment.py`
- Test: `Containment Alarm Skill/tests/test_voice_pin.py`

- [ ] Start Assist listening after alarm announcement
- [ ] Enforce 6-second window and 3 attempts
- [ ] Deactivate alarm on correct PIN regardless of user role

### Task 2.3: Security entities in Alice base

**Files:**
- Modify: `custom_components/alice/sensor.py`
- Create: `custom_components/alice/binary_sensor.py`
- Test: `tests/test_security_entities.py`

- [ ] Expose `sensor.alice_security_level`
- [ ] Expose `binary_sensor.alice_containment_mode` when extension is installed
- [x] Keep `sensor.alice_status` transitions between `Idle`, `STT`, `Thinking`, and `TTS`

---

## Phase 3: Automation Builder and Extensions

### Task 3.1: Automation draft flow

**Files:**
- Create: `custom_components/alice/automation_builder/*`
- Test: `tests/test_automation_builder.py`

- [ ] Parse common German/English automation phrases
- [ ] Resolve entities and areas with follow-up questions on ambiguity
- [ ] Require summary and confirmation before saving

### Task 3.2: Role-based validation

**Files:**
- Modify: `custom_components/alice/automation_builder/validator.py`
- Test: `tests/test_automation_permissions.py`

- [ ] Enforce Kids, Operator, Administrator, and Commander scopes
- [ ] Block or escalate risky automations

### Task 3.3: Pack loader and sentence export

**Files:**
- Modify: `custom_components/alice/extension_registry.py`
- Create: `custom_components/alice/sentence_export.py`
- Test: `tests/test_sentence_export.py`

- [ ] Validate `alice_pack.json` manifests
- [ ] Write `/config/custom_sentences/<lang>/alice.yaml`
- [ ] Create repair issues for duplicate intents or incompatible pack versions

---

## Phase 4: Voice Assets and Diagnostics

### Task 4.1: Wakeword distribution process

**Files:**
- Create: `docs/wakeword-pack.md`
- Create: `packs/alice-wakeword-pack/README.md`

- [ ] Document `.tflite`/`.onnx` release artifacts for "Hey Alice" and "Hey Red Queen"
- [ ] Document threshold guidance and `/share/openwakeword` installation

### Task 4.2: Diagnostics and repairs

**Files:**
- Create: `custom_components/alice/diagnostics.py`
- Create: `custom_components/alice/repairs.py`
- Test: `tests/test_diagnostics.py`

- [ ] Report missing wakeword, missing custom sentences, unavailable siren, LLM unavailable, and open contacts during activation

### Task 4.3: HACS and documentation polish

**Files:**
- Modify: `README.md`
- Modify: `TODO.txt`

- [ ] Document HACS install for Alice and Containment Alarm
- [ ] Keep roadmap in `TODO.txt` current
- [ ] Add manifest/HACS validation checks in CI

---

## Verification Commands

```bash
python -m pytest "Containment Alarm Skill/tests" tests -q
python -c "import json; json.load(open('hacs.json')); json.load(open('custom_components/alice/manifest.json'))"
python -c "import json; json.load(open('Containment Alarm Skill/hacs.json')); json.load(open('Containment Alarm Skill/custom_components/alice_containment_alarm/alice_extension.json'))"
```

Expected result: all unit tests pass and manifest JSON files load without errors.
