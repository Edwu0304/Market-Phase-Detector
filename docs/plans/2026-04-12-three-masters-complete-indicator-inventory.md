# Three Masters Complete Indicator Inventory

**Purpose**

This document replaces the previous simplified modeling approach.

The correct order is:

1. Identify the full set of indicators each master actually watches
2. Compare those against current project coverage
3. Identify missing indicators
4. Find real data sources for the missing indicators
5. Only then redesign the UI

---

## Martin Pring / 愛榭克

### Full indicator families to track

1. Bond market trend
2. Short-rate direction
3. Long-rate direction
4. Yield curve shape and steepening / flattening regime
5. Credit spread regime
6. Equity market trend
7. Equity market momentum
8. Market breadth / diffusion
9. Commodity trend
10. Industrial metals trend
11. Inflation expectation trend
12. Cross-market sequencing:
   - bonds before equities
   - equities before commodities
13. Business-cycle leading indicators
14. Labor stress / unemployment pressure
15. Production direction
16. Export / demand direction
17. Inventory cycle
18. Confidence / demand temperature

### Current project coverage

- Covered directly or approximately:
  - leading indicators
  - labor pressure
  - industrial production
  - exports
  - inventory ratio
  - consumer confidence
  - yield-curve spread
- Partially covered:
  - short / long rate regime
  - credit spreads
- Missing or under-modeled:
  - Pring-specific intermarket ratios beyond simple rank ordering
  - KST / Special K family
  - formal breadth/diffusion regime label for US

### Missing-data acquisition targets

1. Bond total-return or price trend series
2. Broad equity trend series
3. Commodity index or industrial metals series
4. Market breadth / diffusion proxy
5. Inflation-expectation proxy

---

## Urakami

### Full indicator families to track

1. Policy rate direction
2. Short-term rate direction
3. Long-term government yield direction
4. Yield curve slope
5. Yield curve regime:
   - bull steepening
   - bear steepening
   - flattening
   - inversion
6. Credit growth / contraction
7. Corporate-vs-government spread
8. Money supply / liquidity
9. EPS growth
10. PER / valuation expansion or compression
11. Bankruptcy / default pressure
12. Unemployment trend
13. Market leadership / sector rotation
14. Stock-price response relative to earnings phase

### Current project coverage

- Covered directly or approximately:
  - lending rate
  - yield-curve spread
  - credit change
  - M1B / M2
  - PE
- Partially covered:
  - stock response via market trend
- Missing or under-modeled:
  - Taiwan aggregate EPS-quality proxy beyond revenue growth
  - direct default / bankruptcy series

### Missing-data acquisition targets

1. Earnings growth proxy or listed-company aggregate EPS growth
2. Bankruptcy / insolvency / distress rate
3. Sector leadership rotation metrics
4. Explicit short-rate and long-rate regime state

---

## Howard Marks

### Full indicator families to track

1. Credit spread regime
2. High-yield market activity
3. Lending standards / covenant looseness
4. New issuance appetite
5. Financing availability
6. Investor psychology:
   - fear
   - greed
   - FOMO
   - despair
7. Risk appetite / willingness to own low-quality assets
8. Leverage intensity
9. Valuation extremes
10. Distress / forced selling
11. Liquidity stress
12. Narrative temperature:
   - “this time is different”
   - excessive pessimism

### Current project coverage

- Covered directly or approximately:
  - credit spreads
  - stock trend
  - margin balance
  - valuation proxy
- Partially covered:
  - credit growth
- Missing or under-modeled:
  - covenant looseness
  - direct issuance volume series for US
  - direct default-rate series with stable public access
  - explicit sentiment / psychology series
  - Taiwan direct funding-stress series

### Missing-data acquisition targets

1. High-yield issuance or activity proxy
2. Distress / default proxy
3. Funding stress / liquidity spread proxy
4. Sentiment / risk appetite proxy
5. Lending-standard proxy

---

## Priority Gaps To Solve First

The highest-value missing items across the three frameworks are:

1. Direct-vs-proxy labeling for every displayed row
2. Taiwan EPS-quality proxy better than revenue-only
3. US default-rate or issuance-volume series if a stable free source exists
4. Formal breadth/diffusion regime labels
5. Any remaining Taiwan financing-stress proxy

---

## Data-source Worklist

Next step is to assign a concrete source for each high-priority gap, with:

- source name
- country coverage
- frequency
- scrape/API feasibility
- whether it is direct or proxy
