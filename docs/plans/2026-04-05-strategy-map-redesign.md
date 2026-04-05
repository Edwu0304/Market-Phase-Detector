# Strategy Map Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rebuild the market-cycle site into a strategy-map handbook with one site-level phase plus three independent author-lens phase engines, each with real metrics and its own historical slider.

**Architecture:** Keep the static-site deployment model, but redesign the data contract so the backend exports site-level snapshots, lens-level snapshots, and lens-level monthly histories. The frontend becomes a multi-page strategy-map app that renders the current state and per-lens historical views without requiring a backend.

**Tech Stack:** Python, pytest, static HTML/CSS/JS, Cloudflare Pages, Wrangler

---

### Task 1: Freeze the new contract with failing tests

**Files:**
- Modify: `tests/test_content_payload.py`
- Modify: `tests/test_pipeline.py`
- Modify: `tests/test_json_exporter.py`
- Create: `tests/test_lens_payload.py`

**Step 1: Write the failing test**

Add tests that require:

- a top-level `lenses` section per country
- three author entries: `izaax`, `urakami`, `marks`
- a `history` list per lens
- a `metrics` collection per lens

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_lens_payload.py tests/test_pipeline.py tests/test_content_payload.py -v`

Expected: FAIL because the current payload does not expose the full lens contract.

**Step 3: Write minimal implementation**

Only create placeholders in the pipeline or fixtures needed to make the contract explicit.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_lens_payload.py tests/test_pipeline.py tests/test_content_payload.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add tests/test_lens_payload.py tests/test_pipeline.py tests/test_content_payload.py
git commit -m "test: define lens payload contract"
```

### Task 2: Add lens models and serialization

**Files:**
- Modify: `src/market_phase_detector/pipeline.py`
- Modify: `src/market_phase_detector/exporters/json_exporter.py`
- Create: `src/market_phase_detector/models/lenses.py`
- Modify: `tests/test_json_exporter.py`

**Step 1: Write the failing test**

Add tests that verify:

- latest payload writes lens snapshots
- history files include lens history rows
- site content and country payloads remain serializable

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_json_exporter.py -v`

Expected: FAIL because the exporter does not yet include lens data.

**Step 3: Write minimal implementation**

Add typed lens models or normalized dictionaries for:

- `LensMetric`
- `LensDecision`
- `LensHistoryRow`
- `CountryLensBundle`

Then extend exporter logic to preserve them.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_json_exporter.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add src/market_phase_detector/models src/market_phase_detector/pipeline.py src/market_phase_detector/exporters/json_exporter.py tests/test_json_exporter.py
git commit -m "feat: add lens serialization contract"
```

### Task 3: Define metric groups for each author

**Files:**
- Create: `src/market_phase_detector/lenses/metric_sets.py`
- Create: `tests/test_lens_metric_sets.py`

**Step 1: Write the failing test**

Add tests that require:

- Izaax metrics contain macro turning-point inputs
- Urakami metrics contain rates/market-mechanism inputs
- Marks metrics contain risk/credit inputs

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_lens_metric_sets.py -v`

Expected: FAIL because metric groups are not defined.

**Step 3: Write minimal implementation**

Define metric-group metadata:

- metric ids
- labels
- display formats
- phase-zone rules or status thresholds

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_lens_metric_sets.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add src/market_phase_detector/lenses/metric_sets.py tests/test_lens_metric_sets.py
git commit -m "feat: define author lens metric groups"
```

### Task 4: Build Izaax lens engine

**Files:**
- Create: `src/market_phase_detector/lenses/izaax.py`
- Create: `tests/test_izaax_lens.py`

**Step 1: Write the failing test**

Add tests that verify:

- lens phase can be derived from macro-oriented inputs
- output includes current metrics
- output includes reasons

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_izaax_lens.py -v`

Expected: FAIL because the engine does not exist.

**Step 3: Write minimal implementation**

Implement the Izaax lens using:

- leading trend or industrial activity proxy
- coincident direction
- labor stress
- export/production direction

Return a lens snapshot and history row builder.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_izaax_lens.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add src/market_phase_detector/lenses/izaax.py tests/test_izaax_lens.py
git commit -m "feat: add izaax lens engine"
```

### Task 5: Build Urakami lens engine

**Files:**
- Create: `src/market_phase_detector/lenses/urakami.py`
- Create: `tests/test_urakami_lens.py`

**Step 1: Write the failing test**

Add tests that verify:

- the lens can classify a rates-and-market state
- the output includes yield/market metrics and reasons

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_urakami_lens.py -v`

Expected: FAIL because the engine does not exist.

**Step 3: Write minimal implementation**

Implement the Urakami lens using current available proxies, such as:

- yield-curve
- credit/rates regime
- market leadership or a clearly labeled proxy

Keep room for later data-source refinement, but expose real values now.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_urakami_lens.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add src/market_phase_detector/lenses/urakami.py tests/test_urakami_lens.py
git commit -m "feat: add urakami lens engine"
```

### Task 6: Build Howard Marks lens engine

**Files:**
- Create: `src/market_phase_detector/lenses/marks.py`
- Create: `tests/test_marks_lens.py`

**Step 1: Write the failing test**

Add tests that verify:

- credit and risk inputs can produce a lens-specific phase
- the output includes real metric values and reasons

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_marks_lens.py -v`

Expected: FAIL because the engine does not exist.

**Step 3: Write minimal implementation**

Implement the Marks lens using:

- high-yield spread
- valuation/risk appetite proxy
- fear/complacency style proxy

Prefer explicit proxy labels over pretending the metric is exact.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_marks_lens.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add src/market_phase_detector/lenses/marks.py tests/test_marks_lens.py
git commit -m "feat: add marks lens engine"
```

### Task 7: Backfill lens history to at least 12 months

**Files:**
- Modify: `src/market_phase_detector/live_pipeline.py`
- Modify: `src/market_phase_detector/collectors/tw_official.py`
- Modify: `tests/test_live_pipeline.py`

**Step 1: Write the failing test**

Add tests that require:

- at least 12 months of history when data is available
- history rows to include lens-ready metrics

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_live_pipeline.py -v`

Expected: FAIL because current history is shorter and only site-oriented.

**Step 3: Write minimal implementation**

Expand history derivation so that:

- month indexing is stable
- history rows carry enough inputs for all lens engines
- missing months degrade gracefully

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_live_pipeline.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add src/market_phase_detector/live_pipeline.py src/market_phase_detector/collectors/tw_official.py tests/test_live_pipeline.py
git commit -m "feat: expand lens history backfill"
```

### Task 8: Assemble country lens bundles in the CLI pipeline

**Files:**
- Modify: `src/market_phase_detector/cli.py`
- Modify: `src/market_phase_detector/pipeline.py`
- Modify: `tests/test_cli.py`

**Step 1: Write the failing test**

Add tests that require:

- latest payload includes all three current lens bundles
- generated history payloads include month-indexed lens rows

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py tests/test_pipeline.py -v`

Expected: FAIL because CLI output does not yet assemble the new structure.

**Step 3: Write minimal implementation**

Update bundle generation to:

- compute site-level decision
- compute all three lens decisions
- attach history series for each lens

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py tests/test_pipeline.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add src/market_phase_detector/cli.py src/market_phase_detector/pipeline.py tests/test_cli.py tests/test_pipeline.py
git commit -m "feat: attach lens bundles to country payloads"
```

### Task 9: Redesign static content to support dynamic lens phases

**Files:**
- Modify: `src/market_phase_detector/strategy_content.py`
- Modify: `src/market_phase_detector/content.py`
- Create: `tests/test_strategy_templates.py`

**Step 1: Write the failing test**

Add tests that verify:

- strategy content can be selected by author and by lens phase
- strategy blocks exist for both current and historical rendering

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_strategy_templates.py -v`

Expected: FAIL because templates are still tied too closely to site-level phase display.

**Step 3: Write minimal implementation**

Restructure content so the frontend can resolve:

- author
- phase
- section content

without relying on the old single handbook block.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_strategy_templates.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add src/market_phase_detector/strategy_content.py src/market_phase_detector/content.py tests/test_strategy_templates.py
git commit -m "feat: restructure strategy templates for lens views"
```

### Task 10: Redesign the frontend shell and navigation

**Files:**
- Modify: `frontend/src/index.html`
- Modify: `frontend/src/tw/index.html`
- Modify: `frontend/src/us/index.html`
- Modify: `frontend/src/app.js`
- Modify: `frontend/src/styles.css`
- Modify: `tests/test_frontend_entrypoint.py`

**Step 1: Write the failing test**

Add tests that verify:

- landing page renders lens-specific sections
- Taiwan and US pages still exist
- navigation includes links among all three pages

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_frontend_entrypoint.py -v`

Expected: FAIL because the frontend does not yet expose the new shell.

**Step 3: Write minimal implementation**

Implement:

- strategy-map landing
- persistent navigation
- current site summary area
- author-overview modules

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_frontend_entrypoint.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src tests/test_frontend_entrypoint.py
git commit -m "feat: rebuild strategy map shell"
```

### Task 11: Build per-lens panels with independent sliders

**Files:**
- Modify: `frontend/src/app.js`
- Modify: `frontend/src/styles.css`
- Create: `tests/test_lens_ui_contract.py`

**Step 1: Write the failing test**

Add tests that require:

- each lens panel has an independent slider state
- the selected month updates only that lens panel's displayed content
- the page header remains current

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_lens_ui_contract.py -v`

Expected: FAIL because slider-driven lens rendering does not exist.

**Step 3: Write minimal implementation**

Implement:

- one local history controller per lens
- phase badge updates
- metric bar updates
- historical-view badge
- strategy text updates

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_lens_ui_contract.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/app.js frontend/src/styles.css tests/test_lens_ui_contract.py
git commit -m "feat: add independent lens history sliders"
```

### Task 12: Upgrade visual design and interaction polish

**Files:**
- Modify: `frontend/src/styles.css`
- Modify: `frontend/src/app.js`
- Create: `tests/test_visual_contract.py`

**Step 1: Write the failing test**

Add tests or contract checks for:

- phase color classes
- visual grouping for current vs historical lens state
- required section names or DOM anchors

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_visual_contract.py -v`

Expected: FAIL because the current style system is too weak and not tied to the redesign contract.

**Step 3: Write minimal implementation**

Apply the strategy-map visual system:

- stronger typography
- richer background layers
- clearer current-state emphasis
- more deliberate phase and metric visuals
- mobile-safe spacing and controls

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_visual_contract.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/styles.css frontend/src/app.js tests/test_visual_contract.py
git commit -m "feat: polish strategy map visual system"
```

### Task 13: Re-verify Cloudflare deployment flow

**Files:**
- Modify: `README.md`
- Modify: `.github/workflows/monthly-update.yml`
- Modify: `tests/test_cloudflare_config.py`
- Modify: `tests/test_workflow_presence.py`

**Step 1: Write the failing test**

Add tests that require:

- the docs to mention the redesign pages and lens history behavior
- the workflow to continue deploying `dist/`

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cloudflare_config.py tests/test_workflow_presence.py -v`

Expected: FAIL if docs or workflow lag behind the redesign.

**Step 3: Write minimal implementation**

Update:

- Cloudflare deployment docs
- page descriptions
- operator expectations around history data and sliders

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_cloudflare_config.py tests/test_workflow_presence.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add README.md .github/workflows/monthly-update.yml tests/test_cloudflare_config.py tests/test_workflow_presence.py
git commit -m "docs: update cloudflare flow for strategy map redesign"
```

### Task 14: End-to-end verification and deployment

**Files:**
- Modify: as needed based on failures

**Step 1: Write the failing test**

No new unit test. This task is for full verification.

**Step 2: Run test to verify current state**

Run: `pytest -v`

Expected: PASS

Run: `python -m market_phase_detector.cli`

Expected: PASS and regenerate `data/latest.json`, `data/history`, and `data/site-content.json`

Run: `npx wrangler pages deploy dist --project-name market-phase-detector`

Expected: PASS and produce a Cloudflare Pages deployment URL

**Step 3: Write minimal implementation**

Fix any remaining contract, rendering, or deployment issues.

**Step 4: Run test to verify it passes**

Run all three commands again and confirm they succeed.

**Step 5: Commit**

```bash
git add .
git commit -m "chore: verify strategy map redesign end to end"
```

Plan complete and saved to `docs/plans/2026-04-05-strategy-map-redesign.md`. Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?
