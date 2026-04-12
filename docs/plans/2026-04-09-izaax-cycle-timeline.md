# Izaax Cycle Timeline Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rebuild the Taiwan and US Izaax timeline UI so each month column shows its phase inline, and only the actual phase-transition indicators for that month are strongly highlighted.

**Architecture:** Push month-level phase metadata and transition keys from the Python lens pipeline into the Izaax transposed bundle, then render that structure in the frontend table header and metric rows. Remove the redundant pill strip and move the cycle narrative into the Izaax table and side summary.

**Tech Stack:** Python dataclasses and lens builders, static JSON export pipeline, vanilla JavaScript frontend, CSS table styling.

---

### Task 1: Extend Izaax transposed data with month metadata

**Files:**
- Modify: `src/market_phase_detector/models/lenses.py`
- Modify: `src/market_phase_detector/lenses/izaax.py`

**Step 1: Add month metadata structure to the transposed bundle**

- Add a `month_columns` payload to the transposed bundle with, for each month:
  - `month`
  - `phase`
  - `phase_label`
  - `transition_keys`

**Step 2: Build month metadata from Izaax history rows**

- Reuse the same month-level logic as `build_izaax_history_row`.
- Avoid computing transition emphasis from `current_phase` only.

**Step 3: Keep current summary fields intact**

- Preserve:
  - `current_phase`
  - `current_phase_label`
  - `next_phase`
  - `prev_phase`
  - `phase_sequence`

**Step 4: Regenerate JSON shape through dataclass serialization**

- Ensure `to_dict()` includes the new month metadata for frontend consumption.

### Task 2: Render phase inline in the Izaax transposed table

**Files:**
- Modify: `frontend/src/app.js`
- Modify: `frontend/src/app-20260409.js`

**Step 1: Remove the standalone Izaax phase pill strip usage**

- Stop relying on the separate timeline pills for Izaax.
- Keep the generic timeline renderer intact for other lenses if still used elsewhere.

**Step 2: Render a dedicated phase header row in the Izaax table**

- For each month column, render:
  - month label
  - Chinese phase label
- Keep selected month styling on both lines.

**Step 3: Change row highlighting to use selected month transition keys**

- Determine the selected month column metadata.
- Highlight a metric row only if its `metric_id` is inside that month's `transition_keys`.

**Step 4: Update Izaax summary copy**

- Replace passive wording with cycle wording:
  - current stage
  - previous stage
  - next stage

### Task 3: Strengthen table emphasis styling

**Files:**
- Modify: `frontend/src/styles.css`

**Step 1: Add styles for the phase header row**

- Create a distinct visual layer for phase labels within the table header.
- Preserve horizontal scroll behavior and readable sticky left column behavior.

**Step 2: Add strong emphasis for active transition metrics**

- Use stronger border, background, and label weight.
- Make the emphasis read as "important signal" rather than error state.

**Step 3: Remove or neutralize redundant pill-strip styles if unused**

- Keep CSS minimal and avoid dead visual patterns.

### Task 4: Verify data and UI behavior

**Files:**
- Modify if needed: `data/latest.json`
- Modify if needed: generated site output files

**Step 1: Run the site/data generation path needed for local verification**

- Regenerate data if the frontend depends on updated bundle shape.

**Step 2: Verify Taiwan and US Izaax tables**

- Each month column shows its phase inline.
- Selected month highlights the right metrics.
- Cycle copy uses `復甦 -> 成長 -> 榮景 -> 衰退`.

**Step 3: Do a quick regression pass**

- Ensure non-Izaax lens cards still render.
- Ensure the selected-month behavior still works.
