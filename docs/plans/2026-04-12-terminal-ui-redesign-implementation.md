# Terminal UI Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refresh the Market Phase Detector frontend into a professional terminal-style analysis interface with a navigational landing page and high-contrast country workspaces.

**Architecture:** Keep the existing vanilla JS static frontend and current domain/page split. Implement the redesign by changing semantic markup in the landing and country page renderers, adding a few domain helpers where needed, and restructuring CSS to support a dark terminal-style visual language without changing routing or data contracts.

**Tech Stack:** Vanilla JavaScript modules, static HTML, CSS, Python site build pipeline, pytest contract tests, browser verification

---

### Task 1: Lock New Terminal UI Structure with Failing Contracts

**Files:**
- Modify: `tests/test_frontend_entrypoint.py`
- Modify: `tests/test_dashboard_contract.py`
- Modify: `tests/test_visual_contract.py`

**Step 1: Write the failing test**

Add checks for:

- landing hero terminal section
- country status band
- lens workspace container
- terminal theme section markers in CSS

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_frontend_entrypoint.py tests/test_dashboard_contract.py tests/test_visual_contract.py -q`
Expected: FAIL because the new UI markers do not exist yet.

**Step 3: Write minimal implementation**

No production code yet. Adjust only tests to reflect the approved redesign.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_frontend_entrypoint.py tests/test_dashboard_contract.py tests/test_visual_contract.py -q`
Expected: Still FAIL until implementation starts.

**Step 5: Commit**

```bash
git add tests/test_frontend_entrypoint.py tests/test_dashboard_contract.py tests/test_visual_contract.py
git commit -m "test: lock terminal ui redesign contracts"
```

### Task 2: Redesign Landing Page Markup

**Files:**
- Modify: `frontend/src/domain/landing.js`
- Modify: `frontend/src/pages/renderLanding.js`

**Step 1: Write the failing test**

Add tests for:

- terminal hero container
- market overview strip
- country gateway layout
- compressed lens framework strip

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_frontend_entrypoint.py tests/test_dashboard_contract.py -q`
Expected: FAIL

**Step 3: Write minimal implementation**

Replace editorial landing layout with:

- one hero status plane
- country gateway area
- compact framework strip

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_frontend_entrypoint.py tests/test_dashboard_contract.py -q`
Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/domain/landing.js frontend/src/pages/renderLanding.js tests/test_frontend_entrypoint.py tests/test_dashboard_contract.py
git commit -m "feat: redesign landing page as terminal entry"
```

### Task 3: Redesign Country Page Markup

**Files:**
- Modify: `frontend/src/domain/country.js`
- Modify: `frontend/src/pages/renderCountry.js`

**Step 1: Write the failing test**

Add tests for:

- top status band
- country command header
- lens workspace stack

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_lens_ui_contract.py tests/test_dashboard_contract.py -q`
Expected: FAIL

**Step 3: Write minimal implementation**

Introduce:

- status band above hero
- more explicit workspace section names
- stronger lens container semantics

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_lens_ui_contract.py tests/test_dashboard_contract.py -q`
Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/domain/country.js frontend/src/pages/renderCountry.js tests/test_lens_ui_contract.py tests/test_dashboard_contract.py
git commit -m "feat: redesign country page workspace layout"
```

### Task 4: Sharpen Lens Workspace Presentation

**Files:**
- Modify: `frontend/src/domain/lens.js`
- Modify: `frontend/src/pages/renderCountry.js`

**Step 1: Write the failing test**

Add tests for:

- lens workspace class names
- transition-highlight marker visibility
- Izaax workspace container names

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_frontend_entrypoint.py tests/test_lens_ui_contract.py -q`
Expected: FAIL

**Step 3: Write minimal implementation**

Update lens markup to:

- make the table the visual center
- clearly label the decision panel
- keep transition highlight semantics explicit

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_frontend_entrypoint.py tests/test_lens_ui_contract.py -q`
Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/domain/lens.js frontend/src/pages/renderCountry.js tests/test_frontend_entrypoint.py tests/test_lens_ui_contract.py
git commit -m "feat: refine lens workspaces for terminal layout"
```

### Task 5: Apply Terminal Theme Styling

**Files:**
- Modify: `frontend/src/styles.css`
- Test: `tests/test_visual_contract.py`

**Step 1: Write the failing test**

Add checks for:

- terminal hero classes
- status band classes
- workspace classes
- dark theme tokens

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_visual_contract.py -q`
Expected: FAIL

**Step 3: Write minimal implementation**

Restyle the page to use:

- dark terminal background
- compact header bands
- high-contrast workspaces
- restrained accent and phase colors

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_visual_contract.py -q`
Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/styles.css tests/test_visual_contract.py
git commit -m "feat: apply terminal theme styling"
```

### Task 6: Verify Full Frontend and Rebuild Dist

**Files:**
- Modify: `frontend/src/*` as needed
- Modify: `dist/*` via build pipeline

**Step 1: Write the failing test**

No additional unit test needed unless regressions appear.

**Step 2: Run test to verify integration**

Run: `pytest -q`
Expected: PASS

**Step 3: Write minimal implementation**

Apply only final integration fixes needed to keep data loading and rendering stable.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest -q
$env:PYTHONPATH='src'; python -m market_phase_detector.cli
```

Expected:

- `pytest -q` PASS
- `dist/` rebuilt successfully

**Step 5: Commit**

```bash
git add frontend/src dist tests
git commit -m "feat: ship terminal ui redesign"
```
