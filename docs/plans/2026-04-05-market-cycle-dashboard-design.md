# Market Cycle Dashboard Design

**Date:** 2026-04-05

**Goal:** Build a practical monthly dashboard that classifies the current market cycle phase for Taiwan and the United States using a conservative, explainable rules engine and deploys the result as a static site on Cloudflare Pages.

## Product Intent

This project is a monthly market cycle monitor, not a trading signal engine and not a macro research warehouse. The product should answer one question clearly: where are Taiwan and the United States in the current cycle right now?

The first version is intentionally biased toward:

- Stable monthly updates
- Official or durable data sources
- Explainable rules instead of black-box scoring
- Low operational burden

The dashboard will show a single current phase per country:

- `Recovery`
- `Growth`
- `Boom`
- `Recession`

It may also show a secondary watch state when conditions are shifting but the evidence is not strong enough to change the main phase yet.

## Scope

### In Scope

- Monthly scheduled data collection
- Taiwan and United States cycle classification
- Conservative phase state machine
- Static dashboard with current phase, watch state, supporting signals, and recent history
- Deployment to Cloudflare Pages

### Out of Scope

- Daily or intraday updates
- Backtesting
- Automated portfolio recommendations
- Full reproduction of every indicator mentioned in the source article
- Machine learning classification
- Premium or fragile data sources unless clearly required later

## User Experience

The site is a single-page dashboard. The top section contains one summary card for Taiwan and one for the United States. Each card includes:

- Current phase
- Optional watch label
- Last updated date
- Short explanation of the main drivers

Below the cards, the dashboard shows:

- A 12-month phase timeline for each country
- Trend panels for core indicators
- A rule explanation section stating why the current phase was chosen
- Raw data dates so stale inputs are visible

The dashboard should optimize for fast reading. A user should understand the current state in under 30 seconds.

## Architecture

The system follows an offline monthly pipeline:

1. Scheduled runner starts in GitHub Actions
2. Python collectors fetch source data
3. Normalization layer maps country-specific data into a common schema
4. Rule engine derives signals and produces a candidate phase
5. State machine applies conservative transition rules and watch labels
6. Exporter writes versioned JSON for the dashboard
7. Frontend build publishes a static site to Cloudflare Pages

This avoids running scraping or classification inside Cloudflare. Cloudflare only serves the built site.

## Deployment Model

### GitHub Actions

GitHub Actions is the execution environment for:

- Monthly scheduled runs
- Manual reruns
- Dependency installation
- Data fetch and transformation
- Frontend build
- Deployment trigger

This is the recommended choice because the project is Python-heavy and needs reliable logs, retries, and artifact visibility.

### Cloudflare Pages

Cloudflare Pages hosts the static dashboard. It serves generated assets and JSON files. No live backend is required for the first version.

## Data Sources

## United States

Use FRED as the primary source because it standardizes official and market series behind a stable API.

Initial indicators:

- ISM manufacturing trend
- Initial jobless claims trend
- Sahm Rule or unemployment stress proxy
- Yield curve spread: `10Y-2Y` or `10Y-3M`
- High yield spread

These provide a practical balance of:

- Macro direction
- Labor stress
- Rate regime stress
- Credit stress

## Taiwan

Use official Taiwan sources as the default priority:

- National Development Council for business climate signal, leading index, coincident index
- Directorate-General of Budget, Accounting and Statistics for unemployment
- Export or export orders data from a stable official source

Initial indicators:

- Business climate monitoring signal
- Leading indicator trend
- Coincident indicator trend
- Unemployment trend
- Export or export orders year-over-year trend

PMI is useful but should only be included in the first version if the source is stable and simple to automate.

## Data Model

Use a normalized monthly schema per country with three layers:

1. `observations`
2. `derived_signals`
3. `decision`

Example shape:

```json
{
  "country": "US",
  "as_of": "2026-03-31",
  "observations": {
    "ism": 49.8,
    "initial_claims_trend": "rising",
    "sahm_rule": 0.32,
    "yield_curve_10y2y": -0.24,
    "hy_spread": 3.9
  },
  "derived_signals": {
    "macro_direction": "weakening",
    "labor_stress": "low",
    "credit_stress": "moderate",
    "overheating": false
  },
  "decision": {
    "candidate_phase": "Boom",
    "final_phase": "Boom",
    "watch": "recession_risk",
    "reasons": [
      "Yield curve remains inverted",
      "ISM has softened from prior months",
      "Credit stress has not widened enough to confirm recession"
    ]
  }
}
```

## Phase Engine

The engine should be rule-based and conservative. It has two logical layers:

1. `macro candidate`
2. `risk overlay`

### Macro Candidate

The macro candidate is determined from the economic direction implied by the country data.

Indicative logic:

- `Recovery`: weak base, but leading conditions improve and deterioration stops
- `Growth`: leading and coincident conditions are both stable or improving
- `Boom`: activity remains strong but late-cycle strain appears
- `Recession`: coincident weakness and stress indicators confirm contraction

### Risk Overlay

The risk overlay does not create a separate phase. It only:

- Blocks an optimistic upgrade
- Accelerates a downgrade when stress is strong
- Produces a `watch` label when transition evidence is incomplete

### Conservative Transition Rules

The dashboard should not jump phases on one noisy month.

Baseline transition policy:

- Upgrade to a more optimistic phase only after 2 consecutive confirming months
- Downgrade to a worse phase after 2 confirming months by default
- Allow 1-month downgrade only when stress evidence is strong and cross-confirmed
- Keep the prior phase when evidence is mixed, but surface a watch label

### Watch Labels

Watch labels communicate directional risk without changing the headline phase.

Initial set:

- `overheating`
- `recession_risk`
- `recovery_not_confirmed`
- `insufficient_confirmation`

## Country-Specific Rule Draft

## United States

Inputs:

- ISM manufacturing
- Initial jobless claims trend
- Sahm Rule or unemployment stress
- Yield curve spread
- High yield spread

Rule intent:

- `Recovery`: ISM rebounds from low levels and labor deterioration stops
- `Growth`: ISM stable around expansion line, labor stable, credit stress contained
- `Boom`: activity still firm but curve inversion or late-cycle labor/credit warnings appear
- `Recession`: labor stress rises, ISM weakens, and credit pressure confirms

## Taiwan

Inputs:

- Business climate signal
- Leading indicator trend
- Coincident indicator trend
- Unemployment trend
- Export or export orders trend

Rule intent:

- `Recovery`: leading indicator improves from weakness and exports stop deteriorating
- `Growth`: leading and coincident indicators improve together, labor remains stable
- `Boom`: signal is hot or elevated while leading conditions flatten and demand shows late-cycle fatigue
- `Recession`: leading and coincident indicators weaken together and external demand deteriorates

## Failure Handling

The system must tolerate source gaps.

Rules:

- Record the source date of every indicator
- If one non-critical indicator is missing, continue with a degraded decision
- If critical confirmation inputs are missing, keep the prior phase and set `watch=insufficient_confirmation`
- Never fabricate a phase transition from incomplete evidence

## Repository Layout

Recommended structure:

```text
docs/
  plans/
src/
  market_phase_detector/
    collectors/
    engine/
    models/
    exporters/
frontend/
  src/
data/
  latest.json
  history/
.github/
  workflows/
```

## Frontend Design

The frontend should remain intentionally simple:

- Single-page dashboard
- Two country summary cards above the fold
- Clear phase labels with neutral, readable color coding
- Small trend charts or sparklines for the last 12 months
- Explanation text tied to the exact rules that fired

Do not optimize for novelty. Optimize for clarity, trust, and fast monthly review.

## Testing Strategy

The system should be validated at three levels:

- Collector tests with fixture payloads
- Rule engine tests for phase and watch transitions
- Export contract tests to protect dashboard input shape

Front-end testing can stay minimal in v1 if the dashboard is mostly static and data-driven.

## Risks

- Taiwan sources may publish on different schedules, causing apparent mismatches within the same month
- Some indicators revise historical values, which can shift interpretation
- PMI or other optional indicators may be hard to automate reliably
- Overly aggressive logic may cause phase churn; conservative transitions are required

## Success Criteria

The first version succeeds if:

- Monthly automation completes without manual intervention in normal conditions
- Taiwan and United States each receive a current phase and supporting explanation
- The dashboard makes the phase decision understandable at a glance
- Missing data does not cause silent or misleading transitions

## Recommended Next Step

Create an implementation plan that converts this design into:

- A minimal project skeleton
- Data collectors for the first indicator set
- A deterministic phase engine
- Static dashboard rendering
- GitHub Actions and Cloudflare Pages deployment
