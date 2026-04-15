# Market Phase Detector Design System Design

**Date:** 2026-04-12

**Goal:** Define a project-specific design system for the Market Phase Detector frontend so the current static dashboard can grow without turning `frontend/src/app.js` and `frontend/src/styles.css` into an unbounded mix of layout, domain logic, and styling exceptions.

## Product Context

Market Phase Detector is not a generic dashboard and not a trading terminal. The frontend exists to help a reader answer three questions quickly:

1. What phase is each market in right now?
2. Why did the system make that judgment?
3. How do the site-wide phase and the author-specific lenses differ?

The design system therefore needs to optimize for:

- Fast scanning
- Explainability
- High data trust
- Stable growth of domain-specific UI

It should not optimize primarily for novelty, marketing flair, or generic SaaS patterns.

## Current Frontend Reality

The current frontend already contains a hidden design system. It is visible in:

- `frontend/src/styles.css`
- `frontend/src/app.js`

The existing UI already has stable concepts:

- Page shell and hero sections
- Status pills
- Country summary cards
- Observation chips
- Phase badges
- Lens rows
- History tables
- Izaax-specific transposed metric tables
- Decision side panels

The problem is not absence of structure. The problem is that the structure is implicit and spread across large template strings and CSS selectors instead of being formalized as reusable components and tokens.

## Design System Scope

### In Scope

- Design tokens for color, spacing, radius, shadow, typography, and semantic state
- Reusable UI primitives
- Market-analysis domain components
- Page composition patterns for landing and country pages
- Naming conventions for component extraction from the existing vanilla JS frontend

### Out of Scope

- Framework migration to React, Vue, or other component runtimes
- Full accessibility audit and remediation
- Data model redesign
- Rewriting the current site visual direction from scratch
- A general-purpose multi-product design system

## Recommended Approach

Use a lightweight project-internal design system with four layers:

1. `Foundation`
2. `Primitives`
3. `Domain Components`
4. `Page Compositions`

This keeps the current static-site architecture intact while giving the frontend explicit boundaries.

### Why This Approach

- It matches the current technical stack: static HTML, CSS, and vanilla JS.
- It avoids a disruptive framework rewrite.
- It makes the current UI easier to extend and test.
- It preserves the domain specificity that generic dashboard kits usually flatten away.

## Layer 1: Foundation

Foundation defines tokens and semantic rules. These are not page-specific.

### Color Tokens

Base surfaces:

- `color.bg.canvas`
- `color.bg.surface`
- `color.bg.surfaceStrong`
- `color.border.subtle`
- `color.border.strong`

Text:

- `color.text.primary`
- `color.text.secondary`
- `color.text.muted`

Brand and navigation:

- `color.brand.primary`
- `color.brand.secondary`

Country accents:

- `color.country.tw`
- `color.country.us`

Phase states:

- `color.phase.recovery`
- `color.phase.growth`
- `color.phase.boom`
- `color.phase.recession`

Signal states:

- `color.signal.positive`
- `color.signal.negative`
- `color.signal.neutral`
- `color.signal.mixed`

Data integrity states:

- `color.data.stale`
- `color.data.error`
- `color.data.partial`

### Semantic Color Rules

The most important rule is that phase color and operational warning color must remain distinct.

- `Recession` is a market state, not an application failure.
- Missing or stale data must never look like a market recession signal.
- A red operational alert and a recession badge must not be interchangeable.

### Spacing Tokens

- `space.1`
- `space.2`
- `space.3`
- `space.4`
- `space.5`
- `space.6`
- `space.7`
- `space.8`

These should replace one-off spacing values over time.

### Shape and Elevation Tokens

- `radius.sm`
- `radius.md`
- `radius.lg`
- `radius.pill`
- `shadow.surface`
- `shadow.focus`

### Typography Tokens

- `type.display`
- `type.heading`
- `type.body`
- `type.label`
- `type.mono`

The current serif-forward visual language is acceptable because it supports the editorial and research tone of the product. The design system should formalize it rather than accidentally losing it during future refactors.

## Layer 2: Primitives

Primitives are reusable UI building blocks with no direct business logic.

### Required Primitives

- `Button`
- `Link`
- `Card`
- `Badge`
- `Pill`
- `SectionHeading`
- `KeyValue`
- `Alert`
- `EmptyState`
- `Legend`
- `Table`
- `RangeSlider`
- `Tooltip`

### Notes

Not every primitive must be implemented immediately. The important thing is to establish names and responsibilities early so domain components stop redefining these patterns ad hoc.

## Layer 3: Domain Components

This layer is the heart of the system. These are components specific to Market Phase Detector and should be named accordingly.

### Core Domain Components

- `PhaseBadge`
- `StatusPill`
- `CountrySummaryCard`
- `SitePhasePanel`
- `ObservationChip`
- `DataFreshnessBar`
- `MethodNotice`
- `TheoryPhaseCard`
- `LensRow`
- `LensHeader`
- `LensDecisionPanel`
- `DecisionReasonList`
- `HistoryMetricTable`
- `TransposedMetricTable`
- `MonthSelector`
- `TransitionKeyChip`

### Component Intent

`PhaseBadge`
Shows the current cycle phase. It is a first-class domain element and should not be treated as a generic badge variant.

`CountrySummaryCard`
Summarizes country, phase, as-of date, and one key rationale. This is the landing-page entry point into the product.

`ObservationChip`
Shows a single metric label and its current value. It should support scalar values and directional strings consistently.

`LensRow`
Represents one author-specific analytical lens. This is a compositional component containing header, current state, interactive history, and explanatory side content.

`LensDecisionPanel`
Summarizes support, conflict, transition keys, stance, and narrative for one selected month. It is one of the most valuable components in the entire product because it turns a classification into an explanation.

`HistoryMetricTable`
Shows the standard month-by-metric table for most lenses.

`TransposedMetricTable`
Handles the Izaax case where indicators are rows and months are columns. This is specialized enough that it should remain its own domain component instead of being forced into the generic history table.

## Layer 4: Page Compositions

Page compositions define how domain components work together.

### Landing Page Composition

- Top navigation
- Hero with site framing
- Data freshness bar
- Country summary grid
- Data principles section
- Theory and handbook sections

### Country Page Composition

- Top navigation
- Country hero
- Site phase summary
- Observation strip
- Lens stack

### Lens Composition

- Lens header
- Current phase summary
- Interactive history control
- Primary table pane
- Explanatory side panel

### Failure Composition

The site should also define explicit patterns for:

- Full page load failure
- Partial data availability
- Missing lens payload
- Stale data warnings

## Component API Draft

These are suggested interfaces, not framework-specific signatures.

- `PhaseBadge({ phase, size, tone })`
- `StatusPill({ kind, label })`
- `SectionHeading({ eyebrow, title, description })`
- `CountrySummaryCard({ country, phase, asOf, summary, href })`
- `ObservationChip({ label, value, trend })`
- `DataFreshnessBar({ source, generatedAt, error })`
- `TheoryPhaseCard({ phase, definition, phenomena, indicators, strategy })`
- `LensHeader({ school, title, book, currentPhase, currentMonth })`
- `DecisionReasonList({ title, items })`
- `HistoryMetricTable({ rows, selectedIndex })`
- `TransposedMetricTable({ metricRows, monthColumns, selectedMonth, transitionKeys })`
- `LensDecisionPanel({ month, phase, summary, stance, supportingSignals, conflictingSignals, transitionMetrics, reasons })`
- `MonthSelector({ months, selectedMonth })`

## File Architecture Recommendation

The frontend should move from a single large rendering file toward a layered structure without changing frameworks.

Recommended structure:

```text
frontend/src/
  app.js
  styles.css
  tokens.js
  formatters.js
  primitives/
    badges.js
    cards.js
    headings.js
    states.js
    tables.js
  domain/
    landing.js
    country.js
    lens-common.js
    izaax.js
  pages/
    renderLanding.js
    renderCountry.js
```

### Responsibility Split

`app.js`

- Load JSON payloads
- Detect page mode
- Dispatch to page renderer
- Handle fatal load errors

`tokens.js`

- Phase labels
- Tone mappings
- Metric display label maps
- Shared semantic constants

`formatters.js`

- Scalar formatting
- Direction formatting
- Date and label formatting helpers

`primitives/*`

- Reusable small rendering helpers

`domain/*`

- Market-analysis components and lens-specific renderers

`pages/*`

- Page assembly only

## Naming Principles

### Prefer Semantic Names Over Visual Names

Good:

- `LensDecisionPanel`
- `CountrySummaryCard`
- `DataFreshnessBar`

Bad:

- `RightBox`
- `GreenChip`
- `InfoCard2`

### Keep Izaax Explicit

Izaax-specific rendering should stay explicit in naming because it is structurally different from the other lens flows. Hiding this difference behind fake generality will make the code harder to read.

## Visual Direction Rules

The current visual direction is credible: warm editorial background, serif typography, glassy surfaces, restrained accent color. The system should preserve the intent while cleaning up structure.

Guidelines:

- Keep strong editorial tone
- Keep phase colors readable and restrained
- Avoid generic dark-dashboard styling
- Do not let informational density collapse into card spam
- Preserve broad-screen readability for tables
- Maintain clear mobile fallbacks for stacked layouts

## Implementation Priorities

### Priority 1

- Extract shared tokens and formatters
- Formalize `PhaseBadge`, `StatusPill`, and `SectionHeading`
- Separate landing and country page renderers

### Priority 2

- Extract `CountrySummaryCard`, `ObservationChip`, and `DataFreshnessBar`
- Extract `LensHeader`, `DecisionReasonList`, and `HistoryMetricTable`

### Priority 3

- Isolate Izaax-specific renderer and transposed table logic
- Reduce CSS coupling by introducing component-scoped sections in `styles.css`

### Priority 4

- Add explicit empty and degraded-data states
- Add stronger UI contract coverage for component output

## Testing Implications

The design system does not require visual perfection tests first. It requires stable contracts.

Testing should focus on:

- Rendered text content and labels
- Required DOM structure for major domain components
- State class assignment for phases and data warnings
- Landing page versus country page output contracts
- Izaax transposed-table interaction behavior

## Success Criteria

This design system direction succeeds if:

- New UI additions use named domain components instead of ad hoc template fragments
- `app.js` becomes a real entrypoint instead of a full application dump
- Styling rules become easier to trace from token to component
- Izaax complexity is isolated instead of leaking into the whole frontend
- The product remains fast to scan and trustworthy to read

## Recommended Next Step

Create an implementation plan that converts this design into a sequence of small, testable refactors against the current `frontend/src` structure.
