# Strategy Map Redesign Design

**Date:** 2026-04-05

**Goal:** Rebuild the product as a strategy-map handbook that shows the current cycle from four simultaneous viewpoints: the site's unified operating phase plus three independent author-specific phase interpretations.

## Why Redesign

The current UI is too thin for the job.

It shows a site-level phase and supporting indicators, but it does not convincingly answer the real user question:

- In Izaax's framework, where are we now?
- In Urakami's framework, where are we now?
- In Howard Marks's framework, where are we now?
- What indicators justify each of those answers?
- How did those indicators look in prior months?

The current implementation also does not create enough visual hierarchy or enough interaction depth to feel like a serious cycle handbook.

## Product Direction

The redesign should behave like a strategy map, not a generic dashboard.

It should feel like:

- a macro field manual
- a market-cycle atlas
- a multi-lens strategy terminal

The visual tone should be intentional and information-dense without becoming terminal-style clutter.

## Core Product Model

The redesigned product has four analytical layers:

1. **Unified site phase**
2. **Izaax phase**
3. **Urakami phase**
4. **Howard Marks phase**

The unified site phase remains the headline operating framework:

- `Recovery 復甦`
- `Growth 成長`
- `Boom 榮景`
- `Recession 衰退`

But each author lens must be interpreted independently. The product must allow disagreement across lenses.

Example:

- Site phase: `Growth 成長`
- Izaax lens: `Recovery 復甦`
- Urakami lens: `Boom 榮景`
- Marks lens: `Late-cycle risk / Boom 榮景`

This divergence is not a bug. It is a feature and should be surfaced visually.

## Analytical Principle

The site must explicitly continue to state:

- The three authors do not share an identical native phase model
- The site's four-phase framework is a unified operating layer
- Each author lens is a separate interpretation engine mapped into the site experience

However, unlike the current version, the author sections will no longer be passive explanations only. They will be active analytical modules with their own states, signals, history, and strategy text.

## Page Architecture

The site still uses three top-level pages:

- `/`
- `/tw/`
- `/us/`

But the role of each page changes materially.

### Landing Page

The landing page becomes the master strategy map.

It should contain:

- a high-impact hero describing the product as a unified cycle map
- a clear method notice explaining unified phase vs interpretive lenses
- a site-phase summary panel
- three author overview panels shown side by side
- current author-specific phase for Taiwan and the United States
- a visual representation of lens divergence
- entry cards into `/tw/` and `/us/`

The landing page should make it obvious that the product is multi-lens and not merely country-summary-first.

### Country Pages

Each country page becomes a full strategy manual.

Structure:

1. headline area
2. site-level phase rail
3. current site-level reasons and country macro summary
4. three author panels in parallel
5. observation and historical sections

The author panels are the center of gravity.

## Author Panel Design

Each author panel must stand on its own.

Each panel includes:

- current lens-specific phase
- short phase definition
- current indicators with actual values
- position bars or gauges showing current location within the author's cycle logic
- one independent month slider
- historical readout for the selected month
- current strategy text
- historical strategy text for the selected month

### Independent Time Axis

Each author panel has its own time slider.

Dragging the slider should:

- update only that author's panel
- change that author's displayed phase for the selected month
- change that author's indicator values
- change that author's strategy and observed phenomena text
- show a historical context label, for example `Historical View: 2025-12`

The page header must remain the current country state. It should not pretend the whole page is now in the historical month.

## Information Model

The redesign requires a new data contract.

### Current Country Payload

For each country, the frontend needs:

- site-level current phase snapshot
- lens-level current phase snapshot for all three authors
- lens-level metric collections
- lens-level history series

### Lens Snapshot Shape

Each author lens should expose a structure like:

```json
{
  "lens": "marks",
  "phase": "Boom",
  "phase_label": "Boom 榮景",
  "as_of": "2026-02",
  "confidence": "medium",
  "reasons": [
    "Credit spreads remain contained",
    "Risk appetite is still elevated",
    "Valuation pressure is not yet washed out"
  ],
  "metrics": [
    {
      "key": "hy_spread",
      "label": "High Yield Spread",
      "value": 3.6,
      "display": "3.6%",
      "direction": "tight",
      "status": "hot"
    }
  ]
}
```

### Lens History Shape

Each author lens also needs history rows such as:

```json
{
  "month": "2025-12",
  "phase": "Recovery",
  "metrics": {
    "hy_spread": 4.8,
    "yield_curve": -0.35
  },
  "strategy": {
    "definition": "...",
    "phenomena": "...",
    "indicators": "...",
    "action": "..."
  }
}
```

## Engine Redesign

The redesign requires three new lens engines in addition to the existing site engine.

## Izaax Lens

The Izaax lens should emphasize:

- leading indicators
- coincident activity
- labor stress
- production or external-demand direction

Purpose:

- identify macro turning points
- separate early recovery from confirmed expansion
- detect when strong growth starts to lose breadth

## Urakami Lens

The Urakami lens should emphasize:

- rates
- liquidity regime
- yield-curve shape
- market leadership
- late-cycle sensitivity to tightening

Purpose:

- interpret where the market mechanism sits in the funding and equity cycle
- distinguish easy mid-cycle conditions from mature late-cycle conditions

## Marks Lens

The Howard Marks lens should emphasize:

- credit spreads
- risk appetite
- valuation proxies
- market temperature
- fear vs complacency

Purpose:

- show whether risk is underpriced or overpriced
- capture when optimism becomes dangerous
- capture when pessimism becomes opportunity

## Phase Mapping for Lenses

Each lens still needs to render into a user-readable phase label.

But the label does not need to mean the same thing internally for each engine. The user-facing contract can remain:

- `Recovery 復甦`
- `Growth 成長`
- `Boom 榮景`
- `Recession 衰退`

The underlying logic can differ per author.

The UI must therefore show:

- the author name
- the author's current phase
- the author's current signals
- the author's own reasons

without implying that all three authors define the stages identically.

## Visual Design Direction

The visual system should move away from the current mild card-based dashboard.

Required characteristics:

- stronger typography contrast
- distinct phase color system
- richer backgrounds with subtle map-like layers
- more deliberate spacing and section rhythm
- clearer hierarchy between current state, lens state, and historical view
- mobile-safe interaction design

Recommended direction:

- editorial-meets-strategy-map
- warm neutral base with strong phase accents
- dense but readable
- no generic SaaS dashboard look

## Interaction Design

### Required

- per-lens month slider
- clear historical context badge
- current indicator bars or gauges
- current-vs-historical comparison language
- sticky or persistent navigation between site, Taiwan, and United States

### Optional Later

- animated phase transitions
- comparison mode for two months within the same lens
- tooltip glossary for terms and indicators

## Content Strategy

The content should no longer be a small static handbook block only.

For each author and each displayed month, the frontend should show:

- current phase label
- definition
- typical phenomena
- relevant indicators
- strategy/action guidance

This content can still use curated static text templates, but the selected phase and displayed indicators must be dynamic.

## Data Coverage Requirements

The redesign is not complete unless the frontend can show real values, not only labels.

Minimum requirement by lens:

### Izaax

- macro turning-point indicators
- growth/production or export indicators
- labor stress indicator

### Urakami

- yield-curve or rate indicator
- liquidity or market-regime indicator
- one market structure indicator

### Marks

- credit spread
- risk appetite or valuation proxy
- one sentiment/temperature proxy

If a perfect source is not yet available, the first pass can use defensible proxies, but the UI must still show real numbers.

## Historical Coverage

The current history output is not enough if it only supports site-level snapshots.

The redesign needs:

- lens-level monthly history
- stable month indexing for sliders
- enough months to make the slider useful

The practical minimum is 12 months. More is better if the source data is stable.

## Delivery Criteria

The redesign is successful only if:

- each author panel shows a real current phase
- each author panel shows real current metric values
- each author panel has an independent time slider
- dragging the slider updates that author's phase, metrics, and strategy text
- the site looks materially more designed than the current version
- the user can immediately see where Taiwan and the United States are in each author's framework

## Non-Goals

This redesign does not require:

- exact scholarly reconstruction of each book's native chapter taxonomy
- intraday updating
- user accounts
- server-side application logic

## Recommended Next Step

Write an implementation plan for:

- data-contract redesign
- lens-engine introduction
- history backfill expansion
- new frontend architecture
- visual redesign
- Cloudflare deployment verification
