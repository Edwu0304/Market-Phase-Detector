# Izaax Cycle Timeline Design

**Goal**

Align the Taiwan and US Izaax timeline UI with a fixed business-cycle narrative of `Recovery -> Growth -> Boom -> Recession`, and make the table emphasize the exact indicators that caused a monthly phase transition.

**Current Conflicts**

- The data model already uses the fixed cycle order, so there is no conflict in the sequence itself.
- The current Izaax transposed table highlights `next` transition keys for the current phase bundle, not the indicators that actually drove the selected month into its displayed phase.
- The standalone month phase pill strip duplicates information and does not behave like a meaningful cycle map.
- The Izaax table header shows only month labels, so the phase is visually detached from the corresponding month column.

**Scope**

- Modify only the Taiwan and US Izaax timeline experience.
- Keep English phase keys in data and logic.
- Show Chinese phase labels in the UI.
- Preserve existing non-Izaax lenses unless shared styling needs a small compatibility update.

**Design**

## 1. Fixed cycle narrative

- Remove the standalone phase-pill timeline above the Izaax table.
- Add a phase row directly into the transposed table header so each month column carries both:
  - month
  - current phase
- Use cycle-aware copy in the Izaax side panel:
  - current position in the cycle
  - previous phase
  - next phase

## 2. Transition emphasis

- For each historical month, highlight only the metrics referenced by that month's `transition_keys`.
- For non-transition months, still use the same month-specific keys as the "watch list" for the phase being held.
- The emphasis style should read as "important" rather than "danger":
  - stronger border
  - warmer background accent
  - selected-month reinforcement

## 3. Data changes

- Extend the Izaax transposed bundle so it carries per-month phase metadata and per-month transition key metadata aligned to each month column.
- Keep the existing top-level `current_phase`, `next_phase`, and `prev_phase` for summary copy.

**Implementation Notes**

- Source of truth for monthly transition keys should come from `build_izaax_history_row`, because that already computes `previous_phase`, `phase`, and `transition_keys` at the monthly level.
- The transposed bundle should be built from those monthly history rows rather than recomputing only from current observations.
- The header row should remain horizontally scrollable with the metric table.

**Validation**

- Confirm that both TW and US Izaax tables show a phase label inside the table header for every month.
- Confirm that the selected month highlights only the metrics from that month's `transition_keys`.
- Confirm the fixed sequence remains `復甦 -> 成長 -> 榮景 -> 衰退` in all Izaax summary copy.
