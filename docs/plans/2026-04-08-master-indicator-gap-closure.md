# Master Indicator Gap Closure Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Audit the three master lenses against the documented indicator set, update the briefing with explicit implementation gaps, and close the highest-value Taiwan indicator wiring gaps already backed by real data.

**Architecture:** Start from the runtime observation payload in `live_pipeline.py`, compare it with lens inputs and strategy documents, then fix mismatched or unwired fields before adding brand-new data sources. Treat documentation, tests, and code as one unit so the published master mapping matches what the product actually computes.

**Tech Stack:** Python, pytest, Markdown docs, existing collector/lens pipeline

---

### Task 1: Document the B-then-A gap inventory

**Files:**
- Modify: `docs/景氣循環投資策略指南 - Curated Briefing - 2026-04-05.md`
- Reference: `src/market_phase_detector/live_pipeline.py`
- Reference: `src/market_phase_detector/lenses/izaax.py`
- Reference: `src/market_phase_detector/lenses/urakami.py`
- Reference: `src/market_phase_detector/lenses/marks.py`

**Step 1: Write the failing doc expectation**

List three sections:
- `B. 已有資料但未接進判讀/頁面`
- `A. 文件提到但尚無資料來源或欄位`
- `優先實作順序`

**Step 2: Verify current doc is missing this structured inventory**

Run: review the current briefing and confirm it has narrative descriptions but no explicit implementation-gap table.
Expected: the gap inventory is absent.

**Step 3: Write minimal doc update**

Add a concise audit table mapping each master, target indicator, current runtime status, and next action.

**Step 4: Re-read the edited section**

Run: open the updated doc section.
Expected: the inventory is explicit and aligned to code.

**Step 5: Commit**

```bash
git add "docs/景氣循環投資策略指南 - Curated Briefing - 2026-04-05.md"
git commit -m "docs: add master indicator gap inventory"
```

### Task 2: Close runtime field mismatches for existing Taiwan data

**Files:**
- Modify: `src/market_phase_detector/live_pipeline.py`
- Modify: `src/market_phase_detector/lenses/izaax.py`
- Modify: `src/market_phase_detector/lenses/urakami.py`
- Modify: `src/market_phase_detector/lenses/marks.py`
- Test: `tests/test_izaax_lens.py`
- Test: `tests/test_urakami_lens.py`
- Test: `tests/test_marks_lens.py`
- Test: `tests/test_live_pipeline.py`

**Step 1: Write failing tests**

Cover these cases:
- `Izaax` uses real `unemployment_claims` / derived trend instead of a missing field.
- `Urakami` uses available `m2_yoy`, `yield_curve_spread`, `margin_amount`, and `pe_ratio`.
- `Marks` reads the actual `credit_spread`, `cci_total`, and `government_spending`.

**Step 2: Run targeted tests and verify failure**

Run: `pytest tests/test_izaax_lens.py tests/test_urakami_lens.py tests/test_marks_lens.py tests/test_live_pipeline.py -q`
Expected: failures showing mismatched field names or missing metric wiring.

**Step 3: Write minimal implementation**

Implement only:
- derived trend helpers in `live_pipeline.py` for claims, margin, and government spending where the data already exists
- field-name alignment in each lens
- metric payload updates so displayed metrics match runtime fields

**Step 4: Run targeted tests again**

Run: `pytest tests/test_izaax_lens.py tests/test_urakami_lens.py tests/test_marks_lens.py tests/test_live_pipeline.py -q`
Expected: PASS

**Step 5: Commit**

```bash
git add src/market_phase_detector/live_pipeline.py src/market_phase_detector/lenses/izaax.py src/market_phase_detector/lenses/urakami.py src/market_phase_detector/lenses/marks.py tests/test_izaax_lens.py tests/test_urakami_lens.py tests/test_marks_lens.py tests/test_live_pipeline.py
git commit -m "feat: wire existing master indicators into lens logic"
```

### Task 3: Add the missing collector-backed government spending data path if still referenced

**Files:**
- Modify: `src/market_phase_detector/collectors/tw_external.py`
- Modify: `src/market_phase_detector/live_pipeline.py`
- Test: `tests/test_tw_external_collector.py`
- Test: `tests/test_live_pipeline.py`

**Step 1: Write the failing test**

Add a test for the government-spending collector path or, if the source is still unresolved, a test asserting the field is intentionally omitted from lens logic.

**Step 2: Run test to verify failure**

Run: `pytest tests/test_tw_external_collector.py tests/test_live_pipeline.py -q`
Expected: FAIL for the chosen contract.

**Step 3: Write minimal implementation**

Either:
- implement the collector and history wiring if a stable source exists now
or
- remove the false-positive expectation from lens/runtime code and document it as an `A` gap

**Step 4: Run tests to verify pass**

Run: `pytest tests/test_tw_external_collector.py tests/test_live_pipeline.py -q`
Expected: PASS

**Step 5: Commit**

```bash
git add src/market_phase_detector/collectors/tw_external.py src/market_phase_detector/live_pipeline.py tests/test_tw_external_collector.py tests/test_live_pipeline.py
git commit -m "fix: reconcile government spending indicator contract"
```

### Task 4: Run final verification for the audited path

**Files:**
- Reference: `tests/test_tw_external_collector.py`
- Reference: `tests/test_izaax_lens.py`
- Reference: `tests/test_urakami_lens.py`
- Reference: `tests/test_marks_lens.py`
- Reference: `tests/test_live_pipeline.py`

**Step 1: Run the focused regression suite**

Run: `pytest tests/test_tw_external_collector.py tests/test_izaax_lens.py tests/test_urakami_lens.py tests/test_marks_lens.py tests/test_live_pipeline.py -q`
Expected: PASS

**Step 2: Run a live sanity check**

Run a small script with `PYTHONPATH=src` to print the latest Taiwan external fields consumed by the three lenses.
Expected: no `None` values for the newly wired indicators that claim to be implemented.

**Step 3: Summarize residual A gaps**

List any remaining indicators still documented but not implemented after this pass.

**Step 4: Commit**

```bash
git add .
git commit -m "chore: verify master indicator gap closure"
```
