# Three Masters Indicator Model

**Purpose**

Before changing UI again, the project needs a content model that separates:

- what each master actually watches
- what this site can measure directly
- what is only a proxy
- what is currently missing

This document is the source model for later UI work.

---

## 1. Izaax / Martin Pring

### Original indicator categories

Based on the current project framing plus external research, the Pring-style cycle model should be represented as these original categories:

1. Leading indicators
2. Labor stress / unemployment pressure
3. Production and demand direction
4. Exports and global demand
5. Consumer confidence / demand temperature
6. Inventory cycle
7. Yield curve / recession warning
8. Cross-asset sequencing: bonds -> equities -> commodities

### Current site mapping

| Original category | Current site fields | Status |
|---|---|---|
| Leading indicators | `leading_index_change` | original-ish |
| Labor stress | `unemployment_trend`, `unemployment`, `unemployment_claims` | mixed proxy |
| Production and demand | `industrial_production_trend`, `overtime_trend`, `mfg_sales_trend` | mixed proxy |
| Exports | `exports_yoy` | original-ish |
| Confidence | `cci_level` | proxy |
| Inventory cycle | `inventory_sales_ratio`, `inventory_trend` | original-ish if sourced correctly |
| Recession warning | `yield_curve_spread`, `sahm_rule` | proxy / borrowed warning set |
| Cross-asset sequencing | not represented explicitly | missing |

### What should become the table's left-side structure

The Izaax table should not lead with engineering field names. It should lead with:

1. `愛謝克原始觀察面向`
2. `本站對應資料`
3. `是否代理`

Example rows:

- Leading indicators -> NDC leading index -> direct
- Labor stress -> unemployment / claims -> mixed proxy
- Production and demand -> industrial production / overtime / sales -> mixed proxy
- Confidence -> CCI -> proxy
- Inventory cycle -> inventory ratio -> direct-ish
- Yield curve / recession warning -> yield curve spread / Sahm Rule -> proxy

### Gaps

- Cross-asset sequencing is not modeled.
- The table still overstates some proxy indicators as if they were Pring originals.

---

## 2. Urakami

### Original indicator categories

The current code and external search suggest the intended Urakami-style model is:

1. Policy and short-rate direction
2. Long-rate and yield-curve shape
3. Credit expansion / contraction
4. Money supply and liquidity
5. Valuation pressure
6. Positioning / speculative leverage
7. Market leadership or sector rotation

### Current site mapping

| Original category | Current site fields | Status |
|---|---|---|
| Policy / short rates | `bank_lending_rate`, `rate_trend` | proxy |
| Yield curve | `yield_curve_spread` | proxy |
| Credit | `credit_change`, `credit_trend` | partial |
| Money supply | `m1b_change`, `m2_yoy`, `money_supply_trend` | proxy |
| Valuation | `pe_ratio` | proxy |
| Leverage / positioning | `margin_amount`, `margin_trend` | proxy |
| Market leadership / style rotation | not represented explicitly | missing |

### Gaps

- The current model mostly captures rates/liquidity, but not true style-rotation evidence.
- Some fields are implementation conveniences, not canonical Urakami signals.

---

## 3. Howard Marks

### Original indicator categories

Marks-style cycle analysis should be represented as:

1. Credit spread regime
2. Risk appetite / investor psychology
3. Financing availability and lending standards
4. Asset valuations
5. Leverage / speculative behavior
6. Distress and forced selling conditions
7. Inventory / demand deterioration only as secondary context, not the core lens

### Current site mapping

| Original category | Current site fields | Status |
|---|---|---|
| Credit spreads | `credit_spread`, `credit_spread_bbb` | direct-ish |
| Risk appetite | `stock_index_yoy`, `stock_trend` | proxy |
| Financing availability | `credit_change`, `credit_trend` | partial proxy |
| Valuation | `pe_ratio`, `cci_level` | proxy |
| Leverage | `margin_amount`, `margin_balance` | proxy |
| Distress | not represented directly | missing |
| Inventory / demand context | `inventory_change`, `government_spending` | weak proxy / not core |

### Gaps

- Current implementation leans too heavily on stock trend and inventory.
- Marks should be re-centered around credit conditions and psychology first.

---

## 4. Modeling Rules

These rules should be applied before any new UI design:

1. Every row shown in a master table must be tagged as one of:
   - `original`
   - `proxy`
   - `missing`
2. The UI must not present proxy rows as if they were original indicators.
3. Leftmost labels should represent the master's own observation categories first.
4. Implementation field names belong in secondary text, not primary labels.
5. Any later phase logic should explain when a phase decision is driven by proxies rather than direct signals.

---

## 5. Immediate Next Step

Before more Izaax UI changes, refactor the data model so each row can carry:

- `master_category`
- `site_metric_label`
- `source_type` (`original`, `proxy`, `missing`)
- `metric_ids`

Then rebuild the Izaax table using that structure.
