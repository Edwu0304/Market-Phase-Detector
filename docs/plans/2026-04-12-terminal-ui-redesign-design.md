# Market Phase Detector Terminal UI Redesign Design

**Date:** 2026-04-12

**Goal:** Redesign the frontend into a more professional terminal-style analysis interface while preserving the product's core purpose: explainable market-phase interpretation rather than trading execution.

## Visual Thesis

Institutional macro terminal, not retail trading app. The interface should feel like a disciplined analysis workspace: dark graphite surfaces, restrained accents, compact information bands, and clear state hierarchy.

## Content Plan

### Landing Page

- Hero status plane
- Country gateway cards
- Lens framework strip
- Supporting method and source sections

### Country Page

- Top status band
- Country summary block
- Lens workspaces
- Method and glossary support below the fold

## Interaction Thesis

- Landing hero fades and rises in as one status surface instead of multiple floating cards
- Country page sections use subtle staggered reveals to establish analytical hierarchy
- Lens tables and side panels use sharper hover and selected-state contrast rather than decorative animation

## Product Constraint

The redesign must not imply that a small set of global summary chips can explain every regime. Each lens should show the full indicator set that author uses, and each month should highlight the indicators that push the regime toward the next phase.

## Why This Matters

This product is closer to a rules-driven interpretation system than a generic dashboard. The UI should help a user answer:

1. What is the current phase?
2. Which lens is making that claim?
3. Which indicators are pushing the regime toward change?

## Approved Direction

Use a mixed layout:

- Landing page stays navigational and restrained
- Country pages become high-contrast analysis workspaces

Do not turn the full site into a dense trading terminal. The home page should still orient a first-time visitor.

## Landing Page Structure

### 1. Hero Status Plane

The first viewport becomes a single dark analysis surface.

Contents:

- Product label
- Strong headline
- One sentence positioning the site
- Site methodology note
- Two compact market state summaries for Taiwan and United States

This section should feel like a command center overview, not a card grid.

### 2. Country Gateway

Two large market entry blocks:

- Taiwan
- United States

Each block should show:

- Current phase
- Data month
- One short reason
- Clear entry affordance

### 3. Lens Framework Strip

Compress the author framework explanation into a lower-priority strip so the home page does not get dominated by handbook content.

## Country Page Structure

### 1. Top Status Band

Persistent-looking summary strip with:

- Country name
- Current phase
- Optional watch or regime pressure wording
- Data month
- Site-level conclusion

### 2. Country Command Header

Large header with:

- Country title
- Short explanation of how to read the page
- Site-level phase summary block

### 3. Lens Workspace Stack

Each lens becomes a discrete analysis workspace.

Contents:

- Lens identity and book context
- Full indicator table for that lens
- Right-side decision panel
- Highlighted transition-driving indicators for the selected month

The table is the main visual workspace. The decision panel is secondary but always visible.

## Lens Rules

### Full Indicator Visibility

Each lens must expose the full indicator set that author uses. The UI should not pretend there is one universal set of "top metrics."

### Transition Highlighting

Each month may highlight:

- indicators that would push the regime into the next phase
- indicators already responsible for the transition in that month

If there are no such indicators, the interface should remain unhighlighted rather than inventing urgency.

### Izaax

Izaax keeps the transposed table because it supports comparative monthly reading best. It should be visually aligned with the other lens workspaces even though its table structure is different.

## Visual System

### Color Direction

- Background: graphite, ink, slate
- Accent: cyan-teal for navigation and active emphasis
- Phase colors remain distinct but muted enough for product use
- Border and panel separation should rely more on tonal contrast than thick strokes

### Typography

- Sans-serif for headings, labels, and UI chrome
- Monospace for month labels, dates, and metric values where useful
- Body text stays compact and operational

### Surface Treatment

- Fewer soft editorial cards
- More planar workspace sections
- Stronger contrast between main workspace and side context

## Sections to De-Emphasize

- Long theory blocks on the home page
- Decorative glassmorphism
- Large editorial spacing where analysis density matters more

## Testing Impact

The redesign should preserve:

- route structure
- data loading
- lens interaction behavior
- history table updates
- Izaax selection behavior

The redesign should add stronger checks around:

- terminal-style section markers
- new hero and status-band structures
- lens workspace classes

## Success Criteria

The redesign succeeds if:

- the landing page feels like an analysis platform entry, not an article page
- country pages read like professional workspaces
- lens tables become the center of gravity
- transition-driving indicators are visually obvious
- no behavior regression is introduced
