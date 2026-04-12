# Izaax Locked-Cycle Design

**Goal**

Rebuild the Taiwan and US Izaax section into a two-pane experience:

- left: a horizontally scrollable transposed table
- right: a fixed monthly decision panel

The section must explain why a selected month is classified into a phase, highlight only the indicators that truly caused that month's phase transition, and enforce Izaax's fixed business-cycle order:

`復甦 -> 成長 -> 榮景 -> 衰退`

**Why This Redesign Exists**

The old Izaax view had three problems:

1. the table width squeezed surrounding layout
2. the page showed phase pills separate from the table instead of tying the phase to the month column itself
3. the UI could not explain, for a selected month, why the phase was chosen or why a confusing month was held in place

---

## Product Rules

### 1. Locked cycle order

For Izaax, phase order is a hard rule, not a soft preference.

- allowed outcomes for a month are:
  - stay in the current phase
  - move forward exactly one phase
- disallowed:
  - moving backward
  - skipping directly across multiple phases

If raw signals imply a jump outside the ordered cycle, the month is treated as ambiguous and the system must apply a conservative resolution.

### 2. Ambiguous month policy

A month is ambiguous when either of these is true:

- key signals support different phases and no dominant signal cluster exists
- the raw signal outcome would break the fixed phase sequence

When a month is ambiguous:

- default decision: hold the current phase
- exception: advance exactly one phase only when the core transition signals are sufficiently concentrated toward the next phase

The right panel must show:

- that the month is ambiguous
- which signals support the displayed phase
- which signals conflict with it
- the final conservative decision and why it was chosen

### 3. Highlight semantics

Table highlighting is reserved for actual monthly transition drivers.

- if a month changed phase:
  - highlight only the indicators that truly caused the transition
- if a month did not change phase:
  - no transition highlight in the table
  - right panel still explains why the phase was maintained

---

## UI Design

### Layout

The Izaax block becomes a two-column layout.

- left column:
  - transposed metric table
  - independent horizontal scroll only for the table region
- right column:
  - fixed-width decision panel
  - does not move horizontally with the table

This prevents the explanation panel from being compressed by the table width.

### Month interaction

Selecting a month updates the right panel.

Selection can come from:

- clicking the month header inside the Izaax table
- optionally keeping the latest month selected by default on first load

The selected month column should have a clear visual state in the table.

### Right panel contents

For the selected month, the right panel shows:

1. month
2. final phase
3. cycle position
4. whether this month:
   - maintained phase
   - advanced one phase
   - was ambiguous and conservatively resolved
5. transition reason summary
6. supporting signals
7. conflicting signals, if any
8. conservative decision explanation, if ambiguity exists

### Table header

Each month column header must show both:

- month
- phase label

This replaces the standalone phase-pill strip.

---

## Data Design

The Izaax monthly model needs explicit month-level analysis, not just a final phase label.

Each month column should carry:

- `month`
- `phase`
- `phase_label`
- `transition_keys`
- `decision_mode`
  - `hold`
  - `advance`
  - `ambiguous_hold`
  - `ambiguous_advance`
- `supporting_signals`
- `conflicting_signals`
- `decision_summary`

The backend should compute month analysis from the history rows, using the previous resolved phase as the anchor.

---

## Verification

The work is complete only when all of the following are true:

1. Izaax table scrolls horizontally without compressing the right panel
2. clicking a month updates the right-side explanation
3. month headers display both month and phase
4. only real transition-causing indicators are highlighted
5. non-transition months show no transition highlight
6. ambiguous months are explicitly labeled and explained
7. phase outcomes never jump out of sequence on the Izaax timeline
