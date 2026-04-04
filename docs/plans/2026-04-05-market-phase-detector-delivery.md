# Market Phase Detector Delivery

Date: 2026-04-05

## Goal

This project turns the article's market-cycle framework into a practical monthly handbook for Taiwan and the United States.

The delivered product has three operating goals:

1. Collect a compact set of official or durable indicators for Taiwan and the United States on a monthly cadence.
2. Use a conservative, explainable phase engine to classify the current market environment into one unified operating framework:
   - `Recovery 復甦`
   - `Growth 成長`
   - `Boom 榮景`
   - `Recession 衰退`
3. Publish the result as a mobile-friendly static website that can be hosted on Cloudflare Pages without depending on a local machine.

## Product Shape

The site is intentionally not a generic dashboard.

It is designed as a cycle-map handbook with three pages:

- `/` landing page
- `/tw/` Taiwan handbook
- `/us/` United States handbook

The landing page explains the unified framework and the three interpretive lenses:

- Izaax: macro and business-cycle data
- Urakami Kunio: market mechanism and interest-rate cycle
- Howard Marks: psychology, risk, valuation, and credit conditions

The site explicitly states that the three authors do not share one identical native phase model. The application first determines one unified operating phase, then maps each author as an interpretive lens.

## Data Design

### United States

The current live implementation uses FRED-backed series:

- `IPMAN`: leading industrial activity proxy
- `ICSA`: initial jobless claims
- `SAHMCURRENT`: recession pressure proxy
- `T10Y2Y`: yield-curve slope
- `BAMLH0A0HYM2`: high-yield spread

These are used for both latest and historical payloads.

### Taiwan

The current live implementation uses the official NDC ZIP dataset and extracts:

- business signal score
- leading index direction
- coincident index direction
- unemployment direction
- export year-over-year change

The parser supports both the current readable Chinese headers and the legacy mojibake-style headers found in earlier fixtures and some archived payloads, so latest and historical derivations share one path.

## Phase Engine

The phase engine is conservative and rule-based.

It does not use a score-only black box. Instead:

1. A country-specific rule set generates a candidate phase.
2. A state machine applies confirmation logic.
3. The final output may keep the previous phase and add a `watch` state when evidence is incomplete.

This keeps the product explainable and reduces noisy month-to-month switching.

## Output Artifacts

The CLI produces:

- `data/latest.json`
- `data/history/index.json`
- month snapshots such as `data/history/2026-04.json`
- `data/site-content.json`
- `dist/` static site bundle

`data/site-content.json` stores the handbook content for the landing page and the phase-specific author lenses. The country snapshots in `latest.json` and the history files store current observations, decision reasons, and the current handbook block for the resolved phase.

## Frontend Design

The frontend is implemented as a static multi-page site:

- `frontend/src/index.html`
- `frontend/src/tw/index.html`
- `frontend/src/us/index.html`
- `frontend/src/app.js`
- `frontend/src/styles.css`

The landing page presents:

- unified cycle-map hero
- method notice
- phase timeline
- Taiwan and United States entry cards

The country pages present:

- current phase and watch state
- phase rail
- current reasons
- three author handbook sections
- history timeline
- current observations

## Deployment Design

Cloudflare Pages is the production hosting target.

### Local deployment

1. `python -m market_phase_detector.cli`
2. `npx wrangler pages deploy dist --project-name market-phase-detector`

### CI deployment

The workflow at `.github/workflows/monthly-update.yml`:

1. installs Python dependencies
2. installs npm dependencies
3. runs `pytest -v`
4. builds the latest snapshots and site
5. deploys `dist/` to Cloudflare Pages with Wrangler

Required repository secrets:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

The Cloudflare config is stored in `wrangler.toml` with `pages_build_output_dir = "dist"`.

## Coverage Status

### Implemented

- landing page + Taiwan page + US page
- handbook content for all four unified phases
- latest payload generation
- historical payload generation
- Cloudflare Pages deployment flow
- tests for content, workflow, wrangler config, history export, and live-pipeline helpers

### Current indicator coverage

United States:

- leading activity change
- claims trend
- Sahm rule
- yield curve
- high-yield spread

Taiwan:

- business signal score
- leading trend
- coincident trend
- unemployment trend
- exports year-over-year

### Deliberately not included yet

- daily updates
- machine-learning phase classification
- paid data sources
- a full article-by-article reconstruction of every indicator mentioned in the source post
- country-specific custom page structures

## Verification Baseline

The current delivery is considered healthy when all of the following are true:

- `pytest -v` passes
- `python -m market_phase_detector.cli` completes successfully
- `dist/` contains `/`, `/tw/`, `/us/`, and `data/history`
- Cloudflare Pages accepts `dist/` for deployment
