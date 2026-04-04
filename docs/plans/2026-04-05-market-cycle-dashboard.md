# Market Cycle Dashboard Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a monthly Taiwan and US market-cycle dashboard that fetches practical macro indicators, classifies the current phase conservatively, and publishes a static site to Cloudflare Pages.

**Architecture:** A GitHub Actions workflow runs a Python pipeline that fetches source data, normalizes it into a common monthly schema, applies a conservative state machine, exports JSON, and builds a static frontend dashboard. The frontend reads generated JSON only and does not depend on a live backend.

**Tech Stack:** Python, pytest, pydantic or dataclasses, requests/httpx, static frontend, GitHub Actions, Cloudflare Pages

---

### Task 1: Scaffold the repository structure

**Files:**
- Create: `src/market_phase_detector/__init__.py`
- Create: `src/market_phase_detector/collectors/__init__.py`
- Create: `src/market_phase_detector/engine/__init__.py`
- Create: `src/market_phase_detector/models/__init__.py`
- Create: `src/market_phase_detector/exporters/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/engine/__init__.py`
- Create: `tests/collectors/__init__.py`
- Create: `frontend/src/.gitkeep`
- Create: `data/history/.gitkeep`

**Step 1: Write the failing test**

```python
from pathlib import Path

def test_project_structure_exists():
    assert Path("src/market_phase_detector/engine").exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests -k project_structure_exists -v`
Expected: FAIL because the directories and packages do not exist yet.

**Step 3: Write minimal implementation**

Create the package directories and `__init__.py` marker files.

**Step 4: Run test to verify it passes**

Run: `pytest tests -k project_structure_exists -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src tests frontend data
git commit -m "chore: scaffold project structure"
```

### Task 2: Define the normalized data models

**Files:**
- Create: `src/market_phase_detector/models/phases.py`
- Create: `tests/engine/test_models.py`

**Step 1: Write the failing test**

```python
from market_phase_detector.models.phases import DecisionRecord

def test_decision_record_has_phase_and_reasons():
    record = DecisionRecord(
        country="US",
        as_of="2026-03-31",
        candidate_phase="Boom",
        final_phase="Boom",
        watch="recession_risk",
        reasons=["Yield curve inverted"],
    )
    assert record.final_phase == "Boom"
    assert record.reasons == ["Yield curve inverted"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/test_models.py -v`
Expected: FAIL with import error.

**Step 3: Write minimal implementation**

Add normalized models for:

- monthly observations
- derived signals
- decision record
- country snapshot

Prefer typed dataclasses or pydantic models.

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/test_models.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/market_phase_detector/models tests/engine/test_models.py
git commit -m "feat: add normalized phase models"
```

### Task 3: Implement the phase state machine contract

**Files:**
- Create: `src/market_phase_detector/engine/state_machine.py`
- Create: `tests/engine/test_state_machine.py`

**Step 1: Write the failing test**

```python
from market_phase_detector.engine.state_machine import resolve_transition

def test_upgrade_requires_two_confirming_months():
    result = resolve_transition(
        previous_phase="Recovery",
        candidate_phase="Growth",
        previous_candidate_phase="Growth",
        stress_override=False,
    )
    assert result.final_phase == "Growth"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/test_state_machine.py -v`
Expected: FAIL because the resolver does not exist.

**Step 3: Write minimal implementation**

Implement a deterministic transition resolver with these rules:

- optimistic upgrades require two consecutive candidate confirmations
- pessimistic downgrades require two confirmations by default
- strong stress override can accelerate downgrade in one month
- unresolved transitions keep the previous phase and add a watch label

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/test_state_machine.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/market_phase_detector/engine tests/engine/test_state_machine.py
git commit -m "feat: add conservative phase state machine"
```

### Task 4: Build US signal derivation logic

**Files:**
- Create: `src/market_phase_detector/engine/us_rules.py`
- Create: `tests/engine/test_us_rules.py`

**Step 1: Write the failing test**

```python
from market_phase_detector.engine.us_rules import derive_us_candidate

def test_us_boom_candidate_when_activity_is_firm_but_risk_builds():
    candidate = derive_us_candidate(
        ism=52.0,
        claims_trend="stable",
        sahm_rule=0.28,
        yield_curve=-0.35,
        hy_spread=3.8,
    )
    assert candidate.phase == "Boom"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/test_us_rules.py -v`
Expected: FAIL because the rule module does not exist.

**Step 3: Write minimal implementation**

Create US candidate derivation rules based on:

- ISM direction
- jobless-claims trend
- unemployment stress
- yield-curve inversion
- high-yield spread stress

Return both candidate phase and reasoning strings.

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/test_us_rules.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/market_phase_detector/engine/us_rules.py tests/engine/test_us_rules.py
git commit -m "feat: add US phase candidate rules"
```

### Task 5: Build Taiwan signal derivation logic

**Files:**
- Create: `src/market_phase_detector/engine/tw_rules.py`
- Create: `tests/engine/test_tw_rules.py`

**Step 1: Write the failing test**

```python
from market_phase_detector.engine.tw_rules import derive_tw_candidate

def test_tw_recovery_candidate_when_leading_data_turns_up():
    candidate = derive_tw_candidate(
        business_signal_score=18,
        leading_trend="improving",
        coincident_trend="stable",
        unemployment_trend="stable",
        exports_yoy=-2.5,
        exports_trend="improving",
    )
    assert candidate.phase == "Recovery"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/test_tw_rules.py -v`
Expected: FAIL because the rule module does not exist.

**Step 3: Write minimal implementation**

Create Taiwan candidate derivation rules based on:

- business climate signal score
- leading indicator trend
- coincident indicator trend
- unemployment trend
- export or export-order trend

Return both candidate phase and reasoning strings.

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/test_tw_rules.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/market_phase_detector/engine/tw_rules.py tests/engine/test_tw_rules.py
git commit -m "feat: add Taiwan phase candidate rules"
```

### Task 6: Implement collector interfaces and fixture-backed tests

**Files:**
- Create: `src/market_phase_detector/collectors/base.py`
- Create: `src/market_phase_detector/collectors/us_fred.py`
- Create: `src/market_phase_detector/collectors/tw_official.py`
- Create: `tests/collectors/test_us_fred.py`
- Create: `tests/collectors/test_tw_official.py`
- Create: `tests/fixtures/`

**Step 1: Write the failing test**

```python
from market_phase_detector.collectors.us_fred import parse_fred_payload

def test_parse_fred_payload_extracts_latest_value():
    payload = {
        "observations": [
            {"date": "2026-02-01", "value": "50.2"},
            {"date": "2026-03-01", "value": "49.8"},
        ]
    }
    assert parse_fred_payload(payload)["value"] == 49.8
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/collectors/test_us_fred.py -v`
Expected: FAIL because parser does not exist.

**Step 3: Write minimal implementation**

Implement collector helpers that:

- fetch raw data
- parse latest monthly value
- expose normalized fields required by the rule engine

Keep parsing logic testable without network calls by centering tests on fixtures and payload parsers.

**Step 4: Run test to verify it passes**

Run: `pytest tests/collectors/test_us_fred.py tests/collectors/test_tw_official.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/market_phase_detector/collectors tests/collectors tests/fixtures
git commit -m "feat: add data collector interfaces and parsers"
```

### Task 7: Wire the monthly pipeline

**Files:**
- Create: `src/market_phase_detector/pipeline.py`
- Create: `tests/test_pipeline.py`

**Step 1: Write the failing test**

```python
from market_phase_detector.pipeline import build_country_snapshot

def test_pipeline_returns_country_snapshot_with_decision():
    snapshot = build_country_snapshot(
        country="US",
        observations={"ism": 51.1},
        candidate_phase="Growth",
        final_phase="Growth",
        reasons=["ISM stable above 50"],
    )
    assert snapshot["decision"]["final_phase"] == "Growth"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_pipeline.py -v`
Expected: FAIL because pipeline builder does not exist.

**Step 3: Write minimal implementation**

Build the pipeline entry point that:

- gathers collector output
- derives candidate phase
- resolves final phase
- produces normalized country snapshots

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_pipeline.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/market_phase_detector/pipeline.py tests/test_pipeline.py
git commit -m "feat: add monthly phase pipeline"
```

### Task 8: Export dashboard JSON artifacts

**Files:**
- Create: `src/market_phase_detector/exporters/json_exporter.py`
- Create: `tests/test_json_exporter.py`
- Create: `data/latest.json`

**Step 1: Write the failing test**

```python
from pathlib import Path

from market_phase_detector.exporters.json_exporter import write_latest_snapshot

def test_write_latest_snapshot_creates_json_file(tmp_path):
    target = tmp_path / "latest.json"
    write_latest_snapshot({"countries": []}, target)
    assert target.exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_json_exporter.py -v`
Expected: FAIL because exporter does not exist.

**Step 3: Write minimal implementation**

Add JSON export utilities that write:

- `data/latest.json`
- `data/history/YYYY-MM.json`

Use a stable contract that the frontend can consume directly.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_json_exporter.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/market_phase_detector/exporters tests/test_json_exporter.py data/latest.json
git commit -m "feat: export dashboard json artifacts"
```

### Task 9: Build the static dashboard frontend

**Files:**
- Create: `frontend/src/index.html`
- Create: `frontend/src/styles.css`
- Create: `frontend/src/app.js`
- Create: `tests/frontend/` if frontend tests are added

**Step 1: Write the failing test**

```python
from pathlib import Path

def test_frontend_entrypoint_exists():
    assert Path("frontend/src/index.html").exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests -k frontend_entrypoint_exists -v`
Expected: FAIL because the frontend file does not exist.

**Step 3: Write minimal implementation**

Build a simple static dashboard that:

- loads `data/latest.json`
- renders Taiwan and US cards
- shows watch labels
- shows reasons and recent history

Keep frontend dependencies minimal unless a framework is clearly justified.

**Step 4: Run test to verify it passes**

Run: `pytest tests -k frontend_entrypoint_exists -v`
Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src
git commit -m "feat: add static market cycle dashboard"
```

### Task 10: Add GitHub Actions monthly automation

**Files:**
- Create: `.github/workflows/monthly-update.yml`
- Create: `tests/test_workflow_presence.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

def test_monthly_workflow_exists():
    assert Path(".github/workflows/monthly-update.yml").exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_workflow_presence.py -v`
Expected: FAIL because workflow file does not exist.

**Step 3: Write minimal implementation**

Create a workflow that:

- runs monthly on a cron schedule
- supports manual dispatch
- installs Python dependencies
- runs the pipeline
- builds the frontend
- deploys the site artifacts

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_workflow_presence.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add .github/workflows/monthly-update.yml tests/test_workflow_presence.py
git commit -m "ci: add monthly dashboard update workflow"
```

### Task 11: Add deployment documentation and operator notes

**Files:**
- Create: `README.md`
- Create: `tests - optional, if docs checks exist`

**Step 1: Write the failing test**

If the repo includes docs or markdown validation, add a failing check. Otherwise skip test-first for this doc-only task.

**Step 2: Run test to verify it fails**

Skip if no doc validation exists.

**Step 3: Write minimal implementation**

Document:

- required environment variables
- how to run locally
- how to trigger a monthly update
- how to deploy to Cloudflare Pages
- how missing data affects phase transitions

**Step 4: Run test to verify it passes**

Run the existing docs validation if available.

**Step 5: Commit**

```bash
git add README.md
git commit -m "docs: add setup and operations guide"
```

### Task 12: Run end-to-end verification

**Files:**
- Modify: as needed based on verification outcomes

**Step 1: Write the failing test**

No new test. This task is verification and fix-forward only.

**Step 2: Run test to verify current failures**

Run: `pytest -v`
Expected: PASS for unit tests after previous tasks are complete.

Run: project build command for the frontend
Expected: PASS and generated static assets available.

Run: pipeline command against fixture data
Expected: PASS and emit `data/latest.json`.

**Step 3: Write minimal implementation**

Fix any failing tests, schema mismatches, or build issues found in verification.

**Step 4: Run test to verify it passes**

Run: `pytest -v`
Expected: PASS

Run: end-to-end local pipeline build
Expected: PASS

**Step 5: Commit**

```bash
git add .
git commit -m "chore: verify end-to-end market cycle dashboard flow"
```

## Notes for the Implementer

- Prefer deterministic unit tests with fixture payloads over live network tests.
- Keep phase logic explicit and auditable.
- Do not silently change phase on partial data.
- Preserve source dates in exported artifacts.
- Start with the smallest useful frontend possible.
