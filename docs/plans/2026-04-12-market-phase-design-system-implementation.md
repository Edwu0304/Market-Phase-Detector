# Market Phase Design System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor the Market Phase Detector frontend into a lightweight project-internal design system with explicit tokens, primitives, domain components, and page compositions while preserving the current static-site behavior.

**Architecture:** Keep the existing vanilla JS static frontend, but split rendering and formatting responsibilities into small modules. Treat design-system work as a controlled extraction from the current `frontend/src/app.js` and `frontend/src/styles.css`, not as a visual redesign or framework migration.

**Tech Stack:** Vanilla JavaScript, static HTML, CSS, existing Python data export pipeline, pytest contract tests

---

### Task 1: Lock Current Frontend Behavior with Focused UI Contracts

**Files:**
- Modify: `tests/test_frontend_entrypoint.py`
- Modify: `tests/test_lens_ui_contract.py`
- Modify: `tests/test_visual_contract.py`
- Reference: `frontend/src/app.js`

**Step 1: Write the failing tests**

Add or tighten tests that assert:

- Landing page renders a country summary entry for Taiwan and United States
- Country page renders a lens stack container
- Izaax view renders a transposed table container and side panel
- Fatal load errors render the existing failure message shell

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_frontend_entrypoint.py tests/test_lens_ui_contract.py tests/test_visual_contract.py -v`

Expected: At least one assertion fails because the new contracts are not fully represented yet.

**Step 3: Write minimal implementation**

No application refactor yet. Adjust only test fixtures or selectors if needed so the tests target stable user-facing structure instead of incidental markup.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_frontend_entrypoint.py tests/test_lens_ui_contract.py tests/test_visual_contract.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add tests/test_frontend_entrypoint.py tests/test_lens_ui_contract.py tests/test_visual_contract.py
git commit -m "test: lock frontend design-system contracts"
```

### Task 2: Extract Tokens and Formatting Helpers

**Files:**
- Create: `frontend/src/tokens.js`
- Create: `frontend/src/formatters.js`
- Modify: `frontend/src/app.js`
- Test: `tests/test_frontend_entrypoint.py`

**Step 1: Write the failing test**

Add a test that exercises shared phase labels and key metric label formatting through the rendered output so the extraction remains behavior-preserving.

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_frontend_entrypoint.py -v`

Expected: FAIL after referencing extracted helpers that do not yet exist.

**Step 3: Write minimal implementation**

Create `frontend/src/tokens.js` for:

- phase label map
- phase tone helper
- metric label map

Create `frontend/src/formatters.js` for:

- direction formatting
- scalar formatting

Update `frontend/src/app.js` to import and use these helpers without changing rendered behavior.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_frontend_entrypoint.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/tokens.js frontend/src/formatters.js frontend/src/app.js tests/test_frontend_entrypoint.py
git commit -m "refactor: extract frontend tokens and formatters"
```

### Task 3: Extract Shared Primitives

**Files:**
- Create: `frontend/src/primitives/badges.js`
- Create: `frontend/src/primitives/headings.js`
- Create: `frontend/src/primitives/states.js`
- Modify: `frontend/src/app.js`
- Modify: `frontend/src/styles.css`
- Test: `tests/test_frontend_entrypoint.py`

**Step 1: Write the failing test**

Add tests that assert shared output for:

- phase badge markup
- section heading structure
- status pill rendering

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_frontend_entrypoint.py -v`

Expected: FAIL because extracted primitive helpers are not in place.

**Step 3: Write minimal implementation**

Create primitive render helpers:

- `renderPhaseBadge`
- `renderSectionHeading`
- `renderStatusPill`

Update `frontend/src/app.js` to replace repeated inline template fragments with these helpers.

In `frontend/src/styles.css`, group the related primitive styles into clearly labeled sections without changing visual output.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_frontend_entrypoint.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/primitives/badges.js frontend/src/primitives/headings.js frontend/src/primitives/states.js frontend/src/app.js frontend/src/styles.css tests/test_frontend_entrypoint.py
git commit -m "refactor: extract shared frontend primitives"
```

### Task 4: Split Landing Page Composition from Country Page Composition

**Files:**
- Create: `frontend/src/pages/renderLanding.js`
- Create: `frontend/src/pages/renderCountry.js`
- Modify: `frontend/src/app.js`
- Test: `tests/test_frontend_entrypoint.py`

**Step 1: Write the failing test**

Add a test that verifies page dispatch:

- landing mode calls landing renderer path
- country mode calls country renderer path

Use rendered output assertions rather than direct implementation coupling.

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_frontend_entrypoint.py -v`

Expected: FAIL because page-specific renderers do not yet exist.

**Step 3: Write minimal implementation**

Move landing-specific assembly into `renderLanding.js`.
Move country-specific assembly into `renderCountry.js`.
Keep `frontend/src/app.js` limited to:

- body config
- JSON loading
- dispatch
- fatal error handling

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_frontend_entrypoint.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/pages/renderLanding.js frontend/src/pages/renderCountry.js frontend/src/app.js tests/test_frontend_entrypoint.py
git commit -m "refactor: separate landing and country page renderers"
```

### Task 5: Extract Landing Domain Components

**Files:**
- Create: `frontend/src/domain/landing.js`
- Modify: `frontend/src/pages/renderLanding.js`
- Modify: `frontend/src/styles.css`
- Test: `tests/test_dashboard_contract.py`
- Test: `tests/test_frontend_entrypoint.py`

**Step 1: Write the failing test**

Add or update tests for:

- country summary card output
- data freshness bar output
- theory phase section output

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_dashboard_contract.py tests/test_frontend_entrypoint.py -v`

Expected: FAIL because the landing-domain extraction is not implemented.

**Step 3: Write minimal implementation**

Create helpers for:

- `renderCountrySummaryCard`
- `renderDataFreshnessBar`
- `renderTheoryPhaseCard`

Update landing-page composition to use them.

Reorganize related CSS blocks under landing-domain sections.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_dashboard_contract.py tests/test_frontend_entrypoint.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/domain/landing.js frontend/src/pages/renderLanding.js frontend/src/styles.css tests/test_dashboard_contract.py tests/test_frontend_entrypoint.py
git commit -m "refactor: extract landing domain components"
```

### Task 6: Extract Shared Country and Lens Components

**Files:**
- Create: `frontend/src/domain/country.js`
- Create: `frontend/src/domain/lens-common.js`
- Modify: `frontend/src/pages/renderCountry.js`
- Modify: `frontend/src/styles.css`
- Test: `tests/test_lens_ui_contract.py`
- Test: `tests/test_dashboard_contract.py`

**Step 1: Write the failing test**

Add tests that assert:

- observation chip rendering
- lens header rendering
- decision reason list rendering
- history metric table rendering

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_lens_ui_contract.py tests/test_dashboard_contract.py -v`

Expected: FAIL because these render helpers are not extracted yet.

**Step 3: Write minimal implementation**

Create country and shared lens helpers for:

- `renderObservationChip`
- `renderLensHeader`
- `renderDecisionReasonList`
- `renderHistoryMetricTable`

Move only shared lens behavior here. Do not move Izaax-specific logic yet.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_lens_ui_contract.py tests/test_dashboard_contract.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/domain/country.js frontend/src/domain/lens-common.js frontend/src/pages/renderCountry.js frontend/src/styles.css tests/test_lens_ui_contract.py tests/test_dashboard_contract.py
git commit -m "refactor: extract shared country and lens components"
```

### Task 7: Isolate Izaax Renderer

**Files:**
- Create: `frontend/src/domain/izaax.js`
- Modify: `frontend/src/pages/renderCountry.js`
- Modify: `frontend/src/styles.css`
- Test: `tests/test_lens_ui_contract.py`
- Test: `tests/test_izaax_lens.py`

**Step 1: Write the failing test**

Add tests that assert:

- transposed month headers render
- selected month updates the side panel
- transition-key markup remains present

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_lens_ui_contract.py tests/test_izaax_lens.py -v`

Expected: FAIL because Izaax logic has not been isolated yet.

**Step 3: Write minimal implementation**

Move Izaax-only functions into `frontend/src/domain/izaax.js`:

- transposed table rendering
- decision panel rendering
- month-selection interaction wiring

Keep the main country renderer responsible only for selecting the correct lens renderer.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_lens_ui_contract.py tests/test_izaax_lens.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/domain/izaax.js frontend/src/pages/renderCountry.js frontend/src/styles.css tests/test_lens_ui_contract.py tests/test_izaax_lens.py
git commit -m "refactor: isolate izaax lens renderer"
```

### Task 8: Introduce Explicit Empty and Degraded States

**Files:**
- Modify: `frontend/src/primitives/states.js`
- Modify: `frontend/src/pages/renderLanding.js`
- Modify: `frontend/src/pages/renderCountry.js`
- Modify: `frontend/src/styles.css`
- Test: `tests/test_frontend_entrypoint.py`
- Test: `tests/test_dashboard_contract.py`

**Step 1: Write the failing test**

Add tests for:

- missing country payload
- missing lens payload
- degraded data with visible warning

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_frontend_entrypoint.py tests/test_dashboard_contract.py -v`

Expected: FAIL because these explicit degraded states are not rendered yet.

**Step 3: Write minimal implementation**

Add primitives for:

- `renderAlert`
- `renderEmptyState`

Use them where the current frontend would otherwise throw or silently omit context.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_frontend_entrypoint.py tests/test_dashboard_contract.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/primitives/states.js frontend/src/pages/renderLanding.js frontend/src/pages/renderCountry.js frontend/src/styles.css tests/test_frontend_entrypoint.py tests/test_dashboard_contract.py
git commit -m "feat: add explicit frontend degraded states"
```

### Task 9: Reorganize CSS by Token, Primitive, and Domain Sections

**Files:**
- Modify: `frontend/src/styles.css`
- Test: `tests/test_visual_contract.py`

**Step 1: Write the failing test**

If needed, add a small contract test that ensures major class names still exist for:

- phase badges
- country summary cards
- lens rows
- Izaax transposed table

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_visual_contract.py -v`

Expected: FAIL if selectors are renamed without preserving contract coverage.

**Step 3: Write minimal implementation**

Restructure `frontend/src/styles.css` into labeled sections:

- tokens
- base
- primitives
- landing domain
- country domain
- lens domain
- Izaax domain
- responsive rules

Do not use this task to redesign the visuals.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_visual_contract.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/styles.css tests/test_visual_contract.py
git commit -m "refactor: organize frontend styles by design-system layer"
```

### Task 10: Verify Full Frontend Build and Contracts

**Files:**
- Modify: `frontend/src/app.js`
- Modify: `frontend/src/*.js`
- Modify: `tests/*.py` as needed

**Step 1: Write the failing test**

No new test required unless a missing integration gap appears. Prefer running the full current suite that covers frontend rendering and payload contracts.

**Step 2: Run test to verify it fails if integration broke**

Run: `pytest tests/test_frontend_entrypoint.py tests/test_dashboard_contract.py tests/test_lens_ui_contract.py tests/test_izaax_lens.py tests/test_visual_contract.py -v`

Expected: PASS if integration is intact. If not, fix regressions before moving on.

**Step 3: Write minimal implementation**

Apply only integration fixes needed to keep the extracted modules consistent with the current payload shape and page routing.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_frontend_entrypoint.py tests/test_dashboard_contract.py tests/test_lens_ui_contract.py tests/test_izaax_lens.py tests/test_visual_contract.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src tests
git commit -m "refactor: complete market phase frontend design-system extraction"
```

## Notes for Execution

- Preserve the existing static HTML entrypoints in `frontend/src/index.html` and generated `dist/` expectations.
- Avoid framework migration.
- Keep Izaax-specific complexity isolated instead of pretending it matches the common lens path.
- Prefer contract and behavior preservation over CSS churn.
- If selector names must change, update tests in the same task rather than accumulating breakage.

## Verification Checklist

Run after major milestones:

```bash
pytest tests/test_frontend_entrypoint.py -v
pytest tests/test_dashboard_contract.py -v
pytest tests/test_lens_ui_contract.py -v
pytest tests/test_izaax_lens.py -v
pytest tests/test_visual_contract.py -v
```

Run before declaring the refactor complete:

```bash
pytest -q
```
